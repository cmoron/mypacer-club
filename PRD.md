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
* **Scraping :** `requests`, `beautifulsoup4`, `lxml`.
* **Emailing :** Resend API.
* **Configuration :** `python-dotenv` (.env).
* **Architecture :** Script "One-Shot" (Stateless). Pas de base de données persistante pour le MVP.

## 4. Règles Métier (Business Logic)

### A. Périmètre Temporel
* Analyse sur une fenêtre glissante de **7 jours** (pour couvrir le week-end précédent).
* Gestion intelligente du changement d'année (janvier traitant des résultats de décembre).

### B. Définition de l'Excellence ("Highlights")
Une performance est mise en avant dans la section "Excellence" SI :
1.  **C'est un Podium :** Place 1, 2 ou 3.
2.  **OU C'est une Qualification :** Indiquée par "Q" ou "q".
3.  **OU C'est un Niveau National/Inter :** Niveau commençant par "IA", "IB", "N" ou "IR".

**EXCEPTION CRITIQUE (Filtre Anti-Bruit) :**
Les places 1, 2, 3 obtenues dans des tours préliminaires (**Séries, Demi-finales, Qualifications, Tours**) ne comptent PAS comme des podiums et ne doivent pas être affichées comme des médailles.

### C. Structure du Rapport (Email)
1.  **Header :** Nom du club + Dashboard (Stats clés : nb athlètes, nb highlights, nb perfs nationales).
2.  **Section Highlights :** Liste des performances majeures avec médailles visuelles.
3.  **Section Liste Complète :** Tous les résultats, triés par Date > Ville > Nom.
4.  **Format :** HTML "Mobile Cards" (CSS inline) pour une lisibilité maximale sur smartphone.

## 5. Roadmap
* [x] MVP : Script CLI + Envoi Email via Resend.
* [ ] Déploiement : Automatisation via GitHub Actions (CRON).
* [ ] Multi-Club : Support d'un fichier de config JSON pour gérer plusieurs abonnés.
