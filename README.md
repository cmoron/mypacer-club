# MyPacer Club

L'assistant automatisé pour les dirigeants de clubs d'athlétisme.
Ce script scrape les résultats de la Fédération Française d'Athlétisme (FFA) et génère un rapport email hebdomadaire professionnel.

## Prérequis

* Python 3.13+
* [uv](https://github.com/astral-sh/uv) (Gestionnaire de paquets ultra-rapide)
* Une clé API [Resend](https://resend.com) (Gratuit pour le tier hobby)

## Installation

```bash
# Cloner le repo
git clone <url-du-repo>
cd mypacer-club

# Installer les dépendances
uv sync
```

## Configuration

Créez un fichier `.env` à la racine :
```ini
RESEND_API_KEY=re_123456789...
RESEND_TO_EMAIL=votre.email@test.com
```

## Utilisation

### 1. Mode Développement (Preview Locale)

Génère un fichier HTML local pour valider le design sans envoyer d'email.

```bash
uv run -m mypacer_club.main --club 033033
# Ouvre ensuite le fichier preview_033033.html généré
```

### 2. Mode Production (Envoi Email)

Envoie le rapport par email. Nécessite les clés dans le `.env`.

```bash
uv run -m mypacer_club.main --club 033033 --to "destinataires@club.com"
```

### 3. Mode Offline (Samples)

Pour travailler sans réseau, sauvegarder puis réutiliser un fichier HTML local.

```bash
# Sauvegarder le HTML brut depuis athle.fr
uv run -m mypacer_club.main --club 033033 --save-sample samples/033033.html

# Travailler en local sans réseau
uv run -m mypacer_club.main --club 033033 --sample samples/033033.html
```

## Développement

```bash
# Linter
uv run ruff check src/mypacer_club/

# Formatter
uv run ruff format src/mypacer_club/

# Type checking
uv run -m mypy src/mypacer_club/
```

## Structure du Projet

```
src/mypacer_club/
├── __init__.py
├── main.py        # Point d'entrée CLI et orchestration
├── scraper.py     # Récupération et parsing HTML (BeautifulSoup)
├── analyzer.py    # Logique métier, filtrage des dates et highlights
└── reporter.py    # Génération du HTML (Mobile First) et envoi via Resend
```
