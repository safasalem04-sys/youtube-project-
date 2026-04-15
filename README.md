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
python app.py
```

Ensuite, ouvrir le navigateur a l'adresse suivante :

```text
http://127.0.0.1:5000
```

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