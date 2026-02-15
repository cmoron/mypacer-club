from datetime import datetime, timedelta
import re
from typing import Any


def parse_date(date_str: str) -> datetime | None:
    """Convertit 'JJ/MM' en datetime avec gestion de l'année glissante."""
    today = datetime.now()
    match = re.match(r"^(\d{1,2})/(\d{1,2})$", date_str.strip())
    if not match:
        return None

    day, month = int(match.group(1)), int(match.group(2))
    year = today.year

    # Si on est en janvier et que la perf est de décembre -> Année N-1
    if today.month == 1 and month > 9:
        year -= 1

    try:
        return datetime(year, month, day)
    except ValueError:
        return None


def process_results(
    raw_results: list[dict[str, Any]], days: int = 7
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Filtre les résultats récents et extrait les highlights.
    Retourne: (recent, highlights)
    """
    today = datetime.now()
    cutoff = today - timedelta(days=days)

    recent = []
    for r in raw_results:
        dt = parse_date(r["date"])
        if dt and dt >= cutoff:
            r["_dt"] = dt  # Stocké pour le tri
            recent.append(r)

    # Tri Chronologique : Date > Ville > Nom
    recent.sort(key=lambda x: (x["_dt"] or datetime.min, x["ville"], x["nom"]))

    highlights = _extract_highlights(recent)
    return recent, highlights


def _niveau_rank(niveau: str) -> tuple[int, str]:
    """Hiérarchie sportive : IA > IB > N > IR."""
    if niveau.startswith("IA"):
        return (0, niveau)
    if niveau.startswith("IB"):
        return (1, niveau)
    if niveau.startswith("N"):
        return (2, niveau)
    if niveau.startswith("IR"):
        return (3, niveau)
    return (4, niveau)


def _extract_highlights(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Logique métier pour déterminer ce qui est une 'Grosse Perf'."""
    highlights = []

    # Mots-clés pour exclure les tours préliminaires des podiums
    exclusions = [
        "série",
        "serie",
        "demi",
        "semi",
        "qualif",
        "tour",
        "1/2",
        "1/4",
        "1/8",
    ]

    for r in results:
        tour_lower = r["tour"].lower()
        is_prelim = any(kw in tour_lower for kw in exclusions)

        # Règle 1: Podium (si Finale)
        is_podium = r["place"] is not None and r["place"] <= 3 and not is_prelim

        # Règle 2: Qualification
        is_qualif = r["qualif"]

        # Règle 3: Niveau National ou Inter
        is_high_level = r["niveau"].startswith(("N", "IR", "IA", "IB"))

        if is_podium or is_qualif or is_high_level:
            r["is_podium"] = is_podium
            highlights.append(r)

    # Tri Highlights : Médaillés d'abord (par place), puis le reste par niveau
    highlights.sort(
        key=lambda x: (
            not x.get("is_podium", False),  # Podiums en premier
            x["place"] if x.get("is_podium") else 99,  # Triés par place
            _niveau_rank(x["niveau"]),  # Puis par hiérarchie sportive
        )
    )
    return highlights
