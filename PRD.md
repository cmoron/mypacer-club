# Product: MyPacer Club (Micro-SaaS)

## 1. Vision & Positionnement
**MyPacer Club** est le module B2B de l'écosystème MyPacer.
C'est un outil d'automatisation destiné aux dirigeants et bénévoles de clubs d'athlétisme (FFA).
Il transforme la corvée de la collecte des résultats du week-end en une opportunité de communication automatique.

## 2. Proposition de Valeur
* **Gain de temps :** Automatise la recherche de résultats sur les bases fédérales (tâche manuelle de 30-60min/semaine).
* **Valorisation :** Met en avant les performances du club avec un design professionnel et mobile-first.
* **Simplicité :** Un email "clé en main" reçu le lundi matin, prêt à être transféré ou partagé.

## 3. Stack Technique
* **Langage :** Python 3.13+
* **Gestionnaire de paquets :** `uv` (remplace pip/venv).
* **Qualité Code :** `mypy` (mode strict), `ruff` (linter), GitHub Actions (CI).
* **Scraping :** `requests`, `beautifulsoup4`, `lxml`.
* **Emailing :** Resend API.
* **Architecture :** Script "One-Shot" (Stateless). Pas de base de données persistante pour le MVP.

## 4. Règles Métier (Business Logic)

### A. Périmètre Temporel & Technique
* **Ancrage Calendaire :** Le rapport couvre toujours la semaine se terminant le dimanche précédent. La date affichée est celle du lundi de ladite semaine, quel que soit le jour d'exécution du script (Lundi, Mardi ou Mercredi).
* **Pagination :** Le scraper gère la navigation multi-pages sur `bases.athle.fr` en parsant le sélecteur de pagination (`Page > 001/005`) et en bouclant sur toutes les pages via le paramètre `frmposition`.

### B. Définition de l'Excellence ("Highlights")
Une performance est mise en avant dans la section "Podiums et hautes performances" SI :
1.  **C'est un Podium :** Place 1, 2 ou 3 (Badge Or/Argent/Bronze).
2.  **OU C'est une Qualification :** Indiquée par `Q` (Directe), `q` (Repêchage), `QI` (Individuelle - Cross) ou `QE` (Équipe - Cross).
3.  **OU C'est un Niveau National/Inter :** Niveau commençant par "IA", "IB", "N" ou "I" (IR).

**EXCEPTION CRITIQUE (Filtre Anti-Bruit) :**
Les places 1, 2, 3 obtenues dans des tours préliminaires (**Séries, Demi-finales, Qualifications, Tours**) ne comptent PAS comme des podiums et ne doivent pas être affichées avec une médaille, même si le niveau de performance est élevé.

### C. Structure du Rapport (Email)
1.  **Preheader (Invisible) :** Résumé textuel pour l'aperçu mobile (ex: "20 athlètes · 6 highlights").
2.  **Header :** Nom du club + Dashboard (Stats clés : nb athlètes, nb highlights, nb perfs IR & Nat.).
3.  **Section Highlights :** Liste des performances majeures. Distinction visuelle entre un Podium (Cadre coloré + Médaille) et une Performance de haut niveau sans podium (Cadre blanc).
4.  **Section Liste Complète :** Tous les résultats, triés par Date > Ville > Nom.
5.  **Format :** HTML "Mobile Cards" (CSS inline, Tableaux) compatible Outlook/Gmail.

## 5. Roadmap
* [x] MVP : Script CLI + Envoi Email via Resend.
* [x] UX : Design Mobile First & Badges Qualifications (QI/QE).
* [ ] Déploiement : Automatisation via GitHub Actions (CRON).
* [ ] Multi-Club : Support d'un fichier de config JSON pour gérer plusieurs abonnés.
