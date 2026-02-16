import re
import sys
from typing import Any

import requests
from bs4 import BeautifulSoup, Tag

# Constantes
BASE_URL = (
    "https://www.athle.fr/bases/liste.aspx"
    "?frmbase=resultats&frmmode=1&frmclub={club_id}"
    "&frmespace=0&frmsaison={year}"
)
USER_AGENT = "Mozilla/5.0 (Compatible; MyPacerClub/1.0; +https://mypacer.fr)"


def load_local_page(filepath: str) -> BeautifulSoup:
    """Charge un fichier HTML local (mode --sample)."""
    try:
        with open(filepath, encoding="utf-8") as f:
            return BeautifulSoup(f.read(), "lxml")
    except FileNotFoundError:
        print(f"Fichier introuvable : {filepath}", file=sys.stderr)
        sys.exit(1)


def _get_total_pages(soup: BeautifulSoup) -> int:
    """Parse la pagination athle.fr et retourne le nombre total de pages."""
    span = soup.find("span", class_="select-text")
    if not span:
        return 1
    match = re.search(r"(\d+)/(\d+)", span.get_text())
    return int(match.group(2)) if match else 1


def fetch_club_page(
    club_id: str, year: int, position: int = 0
) -> tuple[BeautifulSoup, str]:
    """Récupère le HTML de la page résultats. Retourne (soup, html_brut)."""
    url = BASE_URL.format(club_id=club_id, year=year)
    if position > 0:
        url += f"&frmposition={position}"
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=40)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Erreur HTTP : {e}", file=sys.stderr)
        sys.exit(1)
    return BeautifulSoup(response.text, "lxml"), response.text


def fetch_all_club_pages(club_id: str, year: int) -> tuple[list[BeautifulSoup], str]:
    """Récupère toutes les pages de résultats. Retourne (soups, html_page1)."""
    first_soup, raw_html = fetch_club_page(club_id, year)
    total = _get_total_pages(first_soup)
    soups = [first_soup]
    for i in range(1, total):
        soup, _ = fetch_club_page(club_id, year, position=i)
        soups.append(soup)
    return soups, raw_html


def extract_club_name(soup: BeautifulSoup, default_id: str) -> str:
    """Récupère le nom propre du club (ex: US TALENCE)."""
    header_div = soup.find("div", class_="headers")
    if header_div:
        full_text = header_div.get_text(strip=True)
        return full_text.split("|")[0].strip() if "|" in full_text else full_text
    return f"Club {default_id}"


def parse_raw_results(soup: BeautifulSoup) -> list[dict[str, Any]]:
    """Transforme le tableau HTML en liste de dictionnaires bruts."""
    table = soup.find("table", id="ctnResultats")

    # On vérifie que c'est bien une balise Tag pour rassurer Mypy
    if not isinstance(table, Tag):
        return []

    # Initialisation explicite pour Mypy
    results: list[dict[str, Any]] = []
    rows = table.find_all("tr")

    for row in rows:
        if not isinstance(row, Tag):
            continue

        classes = row.get("class", [])
        if "headers" in classes or "mainheaders" in classes:
            continue

        cells = row.find_all("td")
        if len(cells) < 9:
            continue

        # Extraction des colonnes
        resultat_brut = cells[2].get_text(strip=True)

        place: int | None = None
        match_place = re.match(r"^(\d+)\.", resultat_brut)
        if match_place:
            place = int(match_place.group(1))

        qualif = bool(re.search(r"(?<![Dd])[Qq]\s*$", resultat_brut))

        perf = re.sub(r"^\d+\.\s*", "", resultat_brut)
        perf = re.sub(r"\s*(?<![Dd])[Qq]\s*$", "", perf).strip()

        # 1. Remplacement des double single quotes '' par double quote "
        perf = perf.replace("''", '"')

        # 2. Ajout espace avant temps réaction: 7"78(0.123) -> 7"78 (0.123)
        # On cherche un chiffre suivi d'une parenthèse ouvrante
        perf = re.sub(r"(\d)\(", r"\1 (", perf)

        points = 0
        try:
            points = int(cells[5].get_text(strip=True))
        except ValueError:
            pass

        # Construction du dict typé
        result_item: dict[str, Any] = {
            "nom": cells[0].get_text(strip=True),
            "epreuve": cells[1].get_text(strip=True),
            "tour": cells[3].get_text(strip=True),
            "perf": perf,
            "points": points,
            "place": place,
            "qualif": qualif,
            "niveau": cells[6].get_text(strip=True),
            "date": cells[7].get_text(strip=True),
            "ville": cells[8].get_text(strip=True),
        }
        results.append(result_item)

    return results
