#!/bin/bash
# Installation (une seule fois) : double-clique sur ce fichier.
cd "$(dirname "$0")"

fail() { echo; echo "❌ $1"; echo; read -n 1 -s -r -p "Appuie sur une touche pour fermer."; exit 1; }

[ "$(uname -m)" = "arm64" ] || fail "Cet outil nécessite un Mac à puce Apple (M1 ou plus récent)."

command -v python3 >/dev/null || fail "Python 3 est requis. Installe-le depuis https://www.python.org/downloads/ puis relance ce fichier."
python3 -c 'import sys; sys.exit(sys.version_info < (3, 10))' || fail "Python 3.10 ou plus récent est requis : https://www.python.org/downloads/"

if ! command -v ffmpeg >/dev/null; then
  command -v brew >/dev/null || fail "ffmpeg est requis. Installe d'abord Homebrew (https://brew.sh), puis relance ce fichier."
  echo "Installation de ffmpeg…"
  brew install ffmpeg || fail "L'installation de ffmpeg a échoué."
fi

echo "Installation des composants Python…"
[ -d .venv ] || python3 -m venv .venv || fail "Impossible de créer l'environnement Python."
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -r requirements.txt || fail "L'installation des composants Python a échoué."

echo
echo "✅ Installation terminée."
echo "Double-clique maintenant sur lancer.command pour ouvrir l'outil."
echo "(Au premier webinaire, le modèle de transcription, 1,6 Go, se télécharge automatiquement.)"
echo
read -n 1 -s -r -p "Appuie sur une touche pour fermer."
