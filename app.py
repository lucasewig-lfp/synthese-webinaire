"""Synthèse de webinaires — petite app web locale.

Lancement : .venv/bin/python app.py puis http://localhost:5050
"""

import threading
import time
import traceback
import uuid
from pathlib import Path

from flask import Flask, abort, jsonify, render_template, request, send_file
from werkzeug.utils import secure_filename

import pipeline

ROOT = Path(__file__).parent
JOBS_DIR = ROOT / "travaux"
EXAMPLES_DIR = ROOT / "exemples"
for d in (JOBS_DIR, EXAMPLES_DIR):
    d.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024**3  # vidéos de plusieurs heures

jobs: dict[str, dict] = {}


# ---------------------------------------------------------------- connexion Claude

NOT_READY = "Connecte d'abord Claude Code à ton compte Claude (encadré en haut de la page)."


@app.get("/api/claude")
def claude_status():
    return jsonify(pipeline.claude_status())


# ---------------------------------------------------------------- exemples

@app.get("/api/examples")
def list_examples():
    return jsonify(sorted(p.name for p in EXAMPLES_DIR.glob("*.pdf")))


@app.post("/api/examples")
def add_examples():
    added = []
    for f in request.files.getlist("files"):
        name = secure_filename(f.filename or "")
        if name.lower().endswith(".pdf"):
            f.save(EXAMPLES_DIR / name)
            added.append(name)
    return jsonify(all=sorted(p.name for p in EXAMPLES_DIR.glob("*.pdf")), added=added)


@app.delete("/api/examples/<name>")
def delete_example(name):
    (EXAMPLES_DIR / secure_filename(name)).unlink(missing_ok=True)
    return list_examples()


# ---------------------------------------------------------------- travaux

def run_job(job_id: str, media: Path | None, examples: list[Path], prompt: str, language: str):
    job = jobs[job_id]
    folder = JOBS_DIR / job_id

    def progress(step, pct):
        job.update(step=step, progress=pct)

    try:
        transcript_file = folder / "transcription.txt"
        if media is None:
            transcript = transcript_file.read_text(encoding="utf-8")
        elif media.suffix.lower() == ".txt":
            transcript = media.read_text(encoding="utf-8")
            transcript_file.write_text(transcript, encoding="utf-8")
        else:
            transcript = pipeline.transcribe(media, folder, language, progress)
            transcript_file.write_text(transcript, encoding="utf-8")
            media.unlink(missing_ok=True)  # on ne garde pas la vidéo
        job["has_transcript"] = True

        progress("Rédaction de la synthèse par Claude…", 82)
        markdown = pipeline.summarize(transcript, examples, prompt, folder)
        (folder / "synthese.md").write_text(markdown, encoding="utf-8")

        progress("Création du fichier Word…", 97)
        pipeline.markdown_to_docx(markdown, folder / "synthese.docx")
        job.update(status="done", step="Terminé", progress=100, preview=markdown)
    except Exception as e:  # noqa: BLE001 — on affiche l'erreur dans la page
        traceback.print_exc()
        job.update(status="error", step=str(e))


@app.post("/api/jobs")
def create_job():
    if not pipeline.claude_status()["logged_in"]:
        return jsonify(error=NOT_READY), 400
    upload = request.files.get("media")
    if not upload or not upload.filename:
        return jsonify(error="Ajoute le fichier du webinaire."), 400

    job_id = time.strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
    folder = JOBS_DIR / job_id
    folder.mkdir()
    media = folder / secure_filename(upload.filename)
    upload.save(media)

    examples = [EXAMPLES_DIR / secure_filename(n) for n in request.form.getlist("examples")]
    for f in request.files.getlist("new_examples"):
        name = secure_filename(f.filename or "")
        if name.lower().endswith(".pdf"):
            f.save(EXAMPLES_DIR / name)
            examples.append(EXAMPLES_DIR / name)
    examples = [p for p in dict.fromkeys(examples) if p.exists()]

    return _start(job_id, Path(upload.filename).stem, media, examples,
                  request.form.get("prompt", ""), request.form.get("language", "fr"))


@app.post("/api/jobs/<job_id>/regenerate")
def regenerate(job_id):
    """Refait la synthèse avec un autre prompt, sans retranscrire."""
    old = jobs.get(job_id) or abort(404)
    if not pipeline.claude_status()["logged_in"]:
        return jsonify(error=NOT_READY), 400
    data = request.json or {}
    new_id = job_id.split("~")[0] + "~" + uuid.uuid4().hex[:4]
    (JOBS_DIR / new_id).mkdir()
    (JOBS_DIR / new_id / "transcription.txt").write_bytes((JOBS_DIR / job_id / "transcription.txt").read_bytes())
    examples = [EXAMPLES_DIR / secure_filename(n) for n in data.get("examples", [])]
    return _start(new_id, old["name"], None, [p for p in examples if p.exists()],
                  data.get("prompt", ""), old["language"])


def _start(job_id, name, media, examples, prompt, language):
    jobs[job_id] = dict(id=job_id, name=name, status="running", step="En attente…", progress=0,
                        language=language, has_transcript=False, preview="")
    threading.Thread(target=run_job, args=(job_id, media, examples, prompt, language), daemon=True).start()
    return jsonify(id=job_id)


@app.get("/api/jobs/<job_id>")
def job_status(job_id):
    return jsonify(jobs.get(job_id) or abort(404))


@app.get("/api/jobs/<job_id>/<kind>")
def download(job_id, kind):
    job = jobs.get(job_id) or abort(404)
    files = {"docx": ("synthese.docx", f"Synthèse - {job['name']}.docx"),
             "md": ("synthese.md", f"Synthèse - {job['name']}.md"),
             "transcription": ("transcription.txt", f"Transcription - {job['name']}.txt")}
    if kind not in files:
        abort(404)
    src, download_name = files[kind]
    path = JOBS_DIR / job_id / src
    if not path.exists():
        abort(404)
    return send_file(path, as_attachment=True, download_name=download_name)


@app.get("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, threaded=True)
