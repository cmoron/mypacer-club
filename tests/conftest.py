from pathlib import Path
from typing import Any

import pytest
from bs4 import BeautifulSoup

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_soup() -> BeautifulSoup:
    """BeautifulSoup from the minimal HTML fixture."""
    html = (FIXTURES_DIR / "sample_table.html").read_text(encoding="utf-8")
    return BeautifulSoup(html, "lxml")


@pytest.fixture
def make_result():
    """Factory for creating result dicts with sensible defaults."""

    def _make(
        nom: str = "DUPONT Marie",
        epreuve: str = "100m / SEF",
        perf: str = "11''45",
        tour: str = "",
        points: int = 0,
        place: int | None = None,
        qualif: str | None = None,
        niveau: str = "",
        date: str = "12/02",
        ville: str = "Paris",
        **overrides: Any,
    ) -> dict[str, Any]:
        result: dict[str, Any] = {
            "nom": nom,
            "epreuve": epreuve,
            "perf": perf,
            "tour": tour,
            "points": points,
            "place": place,
            "qualif": qualif,
            "niveau": niveau,
            "date": date,
            "ville": ville,
        }
        result.update(overrides)
        return result

    return _make
