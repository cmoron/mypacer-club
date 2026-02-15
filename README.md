# MyPacer Club 🏃‍♂️📊

L'assistant automatisé pour les dirigeants de clubs d'athlétisme.
Ce script scrape les résultats de la Fédération Française d'Athlétisme (FFA) et génère un rapport email hebdomadaire professionnel.

## Prérequis

* Python 3.12+
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

Créez un fichier .env à la racine :
```Ini, TOML
RESEND_API_KEY=re_123456789...
RESEND_TO_EMAIL=votre.email@test.com  # Pour les tests
```

## Utilisation

Le projet utilise `uv` pour l'exécution.

1. Mode Développement (Preview Locale)

Génère un fichier HTML local pour valider le design sans envoyer d'email.

```bash
uv run -m mypacer_club.main --club 033033
# Ouvre ensuite le fichier preview_033033.html généré
```

2. Mode Production (Envoi Email)

Envoie le rapport par email. Nécessite les clés dans le .env ou passées en argument.

```bash

# Utilise l'email défini dans le .env
uv run -m mypacer_club.main --club 033033 --apikey "re_..." --to "destinataires@club.com"
```

Structure du Projet

- src/scraper.py : Récupération et parsing HTML (BeautifulSoup).
- src/analyzer.py : Logique métier, filtrage des dates et détection des highlights.
- src/reporter.py : Génération du HTML (Mobile First) et envoi via Resend.
- src/main.py : Point d'entrée CLI et orchestration.
