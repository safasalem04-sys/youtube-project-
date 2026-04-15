# Application de transcription YouTube

Cette application Python propose une interface web HTML pour :

- coller un lien YouTube
- recuperer la transcription de la video
- afficher la transcription dans le navigateur
- enregistrer automatiquement le resultat dans un fichier texte `.txt`
- consulter les derniers exports depuis l'interface
- voir des statistiques rapides sur la transcription extraite

## Technologies

- Python
- Flask
- youtube-transcript-api
- HTML / CSS

## Installation

1. Creer un environnement virtuel :

```powershell
python -m venv .venv
```

2. Activer l'environnement :

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Installer les dependances :

```powershell
pip install -r requirements.txt
```

## Lancer l'application

```powershell
py app.py
```

Ensuite, ouvrir le navigateur a l'adresse suivante :

```text
http://127.0.0.1:5000
```

## Heberger l'application en ligne

Si tu veux que l'application reste accessible meme quand ton ordinateur est eteint, il faut la deployer sur un hebergeur. Pour ce projet Flask, le plus simple est Render.

### Deploiement sur Render

1. Pousser le projet sur GitHub.
2. Aller sur Render puis creer un nouveau service `Web Service`.
3. Connecter le depot GitHub `youtube-project-`.
4. Verifier les parametres suivants :

```text
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

5. Lancer le deploiement.
6. Ouvrir l'URL publique fournie par Render.

### Limite importante en hebergement gratuit

Le dossier `transcriptions/` fonctionne localement, mais sur un hebergeur comme Render les fichiers ecrits sur le disque peuvent etre temporaires. Les exports peuvent donc disparaitre apres redemarrage du service. Si tu veux conserver l'historique de facon durable, il faudra ensuite ajouter une base de donnees ou un stockage externe.

## Fichiers importants

- `app.py` : logique Flask et recuperation de la transcription
- `templates/index.html` : interface web
- `static/css/style.css` : design de l'interface
- `transcriptions/` : fichiers texte generes

## Fonctionnalites supplementaires

- Historique local des derniers fichiers generes
- Sauvegarde de metadonnees utiles dans chaque export : URL source, langue, date et identifiant video
- Compteurs d'analyse rapide : mots, lignes et caracteres

## Limites

Cette application recupere les sous-titres disponibles sur YouTube. Si la video n'a pas de transcription ou si les sous-titres sont desactives, aucun texte ne pourra etre extrait.