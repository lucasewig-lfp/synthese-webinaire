# Synthèse de webinaire

Petit outil qui tourne sur ton Mac :

1. tu déposes l'enregistrement d'un webinaire (vidéo ou audio, ou une transcription `.txt` déjà faite) ;
2. tu ajoutes un ou plusieurs exemples de synthèse en PDF à imiter (ils restent enregistrés pour les fois suivantes) ;
3. tu ajoutes tes consignes ;
4. tu récupères un fichier **Word (.docx)** modifiable, ainsi que la transcription brute.

La transcription se fait sur ton Mac. La rédaction passe par ton propre abonnement Claude (Pro ou Max) via Claude Code : aucune clé API n'est nécessaire.

## Ce qu'il te faut

- un Mac à puce Apple (M1 ou plus récent) ;
- Python 3.10 ou plus récent (https://www.python.org/downloads/) ;
- un abonnement Claude Pro ou Max à ton nom.

## Installation (une seule fois, environ 5 minutes)

1. Sur cette page GitHub, clique sur le bouton vert **Code** → **Download ZIP**. Dézippe le dossier et range-le où tu veux (par exemple dans Documents).
2. **Clic droit** sur `installer.command` → **Ouvrir** → confirme **Ouvrir**. Le clic droit est nécessaire la première fois, car macOS bloque les fichiers téléchargés. Il installe ffmpeg si besoin, puis les composants Python.
3. Installe Claude Code et connecte-le à ton compte Claude. Ouvre l'app **Terminal** et colle ces deux commandes, l'une après l'autre. La seconde ouvre une page de connexion dans ton navigateur.

   ```
   curl -fsSL https://claude.ai/install.sh | bash
   ~/.local/bin/claude auth login
   ```

## Utilisation

**Clic droit** sur `lancer.command` → **Ouvrir** la première fois, puis un simple double-clic les fois suivantes. La page s'ouvre sur http://localhost:5050. Laisse la fenêtre du Terminal ouverte pendant que tu utilises l'outil.

Si l'encadré jaune « Connexion à Claude » s'affiche en haut de la page, c'est que l'étape 3 de l'installation n'est pas terminée.

## Bon à savoir

- **Durée** : quelques minutes de transcription pour 3 h de vidéo, puis quelques minutes de rédaction. Au premier webinaire, le modèle de transcription (1,6 Go) se télécharge.
- **Confidentialité** : seuls le texte transcrit et les PDF d'exemple sont envoyés à Claude. La vidéo ne quitte pas ton Mac et n'est pas conservée.
- **Coût** : rien en plus de ton abonnement. Chaque synthèse consomme une partie de ton quota Claude, comme une longue conversation.
- **Régénérer** : si la synthèse ne convient pas, change les consignes et clique sur « Régénérer ». Le webinaire n'est pas retranscrit.
- **Conseil** : indique dans tes consignes l'orthographe exacte des noms des intervenants. La transcription automatique les écorche souvent.
- **Google Docs** : dans Drive, Nouveau → Importer un fichier, puis Fichier → Enregistrer au format Google Docs.
- Les exemples PDF sont rangés dans `exemples/`. Chaque traitement est rangé dans `travaux/`, avec sa transcription, sa synthèse en Markdown et le `.docx`.
- **Toujours relire la synthèse avant diffusion**, en particulier les chiffres, les noms et les zones d'achat.

## Mettre à jour l'outil

Retélécharge le ZIP depuis cette page et remplace les fichiers de ton dossier. Ne touche pas aux dossiers `exemples/` et `travaux/`, qui contiennent tes exemples et tes synthèses. Relance ensuite `installer.command`.
