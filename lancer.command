#!/bin/bash
# Lance l'outil : double-clique sur ce fichier, puis laisse la fenêtre du Terminal ouverte.
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  echo "L'outil n'est pas encore installé : double-clique d'abord sur installer.command."
  read -n 1 -s -r -p "Appuie sur une touche pour fermer."
  exit 1
fi
(sleep 2 && open http://localhost:5050) &
echo "Synthèse de webinaire : http://localhost:5050"
echo "Laisse cette fenêtre ouverte pendant que tu utilises l'outil (ferme-la pour l'arrêter)."
.venv/bin/python app.py
