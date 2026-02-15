from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from bs4 import BeautifulSoup

from mypacer_club.scraper import (
    extract_club_name,
    fetch_club_page,
    load_local_page,
    parse_raw_results,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_PATH = str(FIXTURES_DIR / "sample_table.html")


# ── load_local_page ─────────────────────────────────────────────────


class TestLoadLocalPage:
    def test_loads_valid_file(self):
        soup = load_local_page(SAMPLE_PATH)
        assert isinstance(soup, BeautifulSoup)
        assert soup.find("table", id="ctnResultats") is not None

    def test_file_not_found_exits(self):
        with pytest.raises(SystemExit):
            load_local_page("/nonexistent/path.html")


# ── fetch_club_page ─────────────────────────────────────────────────


class TestFetchClubPage:
    @patch("mypacer_club.scraper.requests.get")
    def test_success(self, mock_get: MagicMock):
        mock_response = MagicMock()
        mock_response.text = "<html><body>OK</body></html>"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        soup, raw = fetch_club_page("033033", 2026)

        assert isinstance(soup, BeautifulSoup)
        assert raw == "<html><body>OK</body></html>"
        mock_get.assert_called_once()
        call_url = mock_get.call_args[0][0]
        assert "033033" in call_url
        assert "2026" in call_url

    @patch("mypacer_club.scraper.requests.get")
    def test_http_error_exits(self, mock_get: MagicMock):
        import requests

        mock_get.side_effect = requests.ConnectionError("timeout")
        with pytest.raises(SystemExit):
            fetch_club_page("033033", 2026)


# ── extract_club_name ───────────────────────────────────────────────


class TestExtractClubName:
    def test_with_pipe(self, sample_soup: BeautifulSoup):
        name = extract_club_name(sample_soup, "033033")
        assert name == "US TALENCE"

    def test_without_pipe(self):
        html = '<div class="headers text-normal">CLUB SANS PIPE</div>'
        soup = BeautifulSoup(html, "lxml")
        assert extract_club_name(soup, "999") == "CLUB SANS PIPE"

    def test_no_header_div(self):
        soup = BeautifulSoup("<html><body></body></html>", "lxml")
        assert extract_club_name(soup, "033033") == "Club 033033"


# ── parse_raw_results ───────────────────────────────────────────────


class TestParseRawResults:
    def test_extracts_all_data_rows(self, sample_soup: BeautifulSoup):
        results = parse_raw_results(sample_soup)
        assert len(results) == 9

    def test_first_result_fields(self, sample_soup: BeautifulSoup):
        results = parse_raw_results(sample_soup)
        first = results[0]
        assert first["nom"] == "DUPONT Marie"
        assert first["epreuve"] == "100m - Salle / SEF"
        assert first["place"] == 1
        assert first["perf"] == "11''45"
        assert first["tour"] == "Finale"
        assert first["points"] == 1061 or first["points"] == 1100
        assert first["date"] == "12/02"
        assert first["ville"] == "Paris"

    def test_place_parsing(self, sample_soup: BeautifulSoup):
        results = parse_raw_results(sample_soup)
        places = [r["place"] for r in results]
        assert places[0] == 1  # DUPONT
        assert places[1] == 2  # KOVANOV
        assert places[2] == 3  # MARTIN

    def test_qualif_q_detected(self, sample_soup: BeautifulSoup):
        results = parse_raw_results(sample_soup)
        leroy = next(r for r in results if r["nom"] == "LEROY Emma")
        assert leroy["qualif"] is True

    def test_dq_not_confused_with_q(self, sample_soup: BeautifulSoup):
        results = parse_raw_results(sample_soup)
        lascaux = next(r for r in results if r["nom"] == "LASCAUX Alix")
        assert lascaux["qualif"] is False

    def test_points_parsed(self, sample_soup: BeautifulSoup):
        results = parse_raw_results(sample_soup)
        dupont = results[0]
        assert dupont["points"] == 1100

    def test_points_zero_when_empty(self, sample_soup: BeautifulSoup):
        results = parse_raw_results(sample_soup)
        lascaux = next(r for r in results if r["nom"] == "LASCAUX Alix")
        assert lascaux["points"] == 0

    def test_detail_rows_ignored(self, sample_soup: BeautifulSoup):
        """Detail-rows have < 9 direct cells and should be skipped."""
        results = parse_raw_results(sample_soup)
        noms = [r["nom"] for r in results]
        # Should not contain any artifact from detail-row inner tables
        assert all(isinstance(n, str) and len(n) > 0 for n in noms)

    def test_no_table_returns_empty(self):
        soup = BeautifulSoup("<html><body></body></html>", "lxml")
        assert parse_raw_results(soup) == []

    def test_empty_table_returns_empty(self):
        html = '<table id="ctnResultats"><tbody></tbody></table>'
        soup = BeautifulSoup(html, "lxml")
        assert parse_raw_results(soup) == []

    def test_link_in_name_extracts_text(self, sample_soup: BeautifulSoup):
        """Names with <a> links should still extract the text content."""
        results = parse_raw_results(sample_soup)
        kovanov = next(r for r in results if "KOVANOV" in r["nom"])
        assert kovanov["nom"] == "KOVANOV Danik"

    def test_niveau_extracted(self, sample_soup: BeautifulSoup):
        results = parse_raw_results(sample_soup)
        kovanov = next(r for r in results if "KOVANOV" in r["nom"])
        assert kovanov["niveau"] == "N2"
