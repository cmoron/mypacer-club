from datetime import datetime

from freezegun import freeze_time

from mypacer_club.analyzer import (
    _extract_highlights,
    _niveau_rank,
    parse_date,
    process_results,
)


# ── parse_date ──────────────────────────────────────────────────────


@freeze_time("2026-02-15")
class TestParseDate:
    def test_valid_dd_mm(self):
        assert parse_date("12/02") == datetime(2026, 2, 12)

    def test_single_digit_day_month(self):
        assert parse_date("3/1") == datetime(2026, 1, 3)

    def test_strips_whitespace(self):
        assert parse_date("  12/02  ") == datetime(2026, 2, 12)

    def test_empty_string(self):
        assert parse_date("") is None

    def test_garbage_string(self):
        assert parse_date("not-a-date") is None

    def test_too_many_parts(self):
        assert parse_date("12/02/2026") is None

    def test_invalid_day(self):
        assert parse_date("31/02") is None

    @freeze_time("2026-01-10")
    def test_january_with_december_date(self):
        """In January, a December date should be attributed to the previous year."""
        result = parse_date("15/12")
        assert result == datetime(2025, 12, 15)

    @freeze_time("2026-01-10")
    def test_january_with_january_date(self):
        """In January, a January date stays in current year."""
        result = parse_date("05/01")
        assert result == datetime(2026, 1, 5)

    @freeze_time("2026-01-10")
    def test_january_with_september_date_stays_current_year(self):
        """Month <= 9 in January is not shifted to previous year."""
        result = parse_date("15/09")
        assert result == datetime(2026, 9, 15)


# ── _niveau_rank ────────────────────────────────────────────────────


class TestNiveauRank:
    def test_ia_is_highest(self):
        assert _niveau_rank("IA1")[0] == 0

    def test_ib_is_second(self):
        assert _niveau_rank("IB2")[0] == 1

    def test_n_is_third(self):
        assert _niveau_rank("N3")[0] == 2

    def test_ir_is_fourth(self):
        assert _niveau_rank("IR1")[0] == 3

    def test_other_is_lowest(self):
        assert _niveau_rank("Dep")[0] == 4

    def test_empty_string(self):
        assert _niveau_rank("")[0] == 4

    def test_hierarchy_ordering(self):
        levels = ["IR1", "N2", "IB1", "IA3", "Dep"]
        sorted_levels = sorted(levels, key=_niveau_rank)
        assert sorted_levels == ["IA3", "IB1", "N2", "IR1", "Dep"]


# ── _extract_highlights ─────────────────────────────────────────────


class TestExtractHighlights:
    def test_podium_finale_is_highlight(self, make_result):
        results = [make_result(place=1, tour="Finale", niveau="")]
        hl = _extract_highlights(results)
        assert len(hl) == 1
        assert hl[0]["is_podium"] is True

    def test_podium_serie_excluded(self, make_result):
        results = [make_result(place=1, tour="Série 2", niveau="")]
        hl = _extract_highlights(results)
        assert len(hl) == 0

    def test_podium_demi_excluded(self, make_result):
        results = [make_result(place=2, tour="Demi-finale", niveau="")]
        hl = _extract_highlights(results)
        assert len(hl) == 0

    def test_podium_qualif_round_excluded(self, make_result):
        results = [make_result(place=3, tour="Qualif", niveau="")]
        hl = _extract_highlights(results)
        assert len(hl) == 0

    def test_qualification_q_is_highlight(self, make_result):
        results = [make_result(qualif="q", niveau="")]
        hl = _extract_highlights(results)
        assert len(hl) == 1

    def test_high_level_n_is_highlight(self, make_result):
        results = [make_result(niveau="N3")]
        hl = _extract_highlights(results)
        assert len(hl) == 1

    def test_high_level_ia_is_highlight(self, make_result):
        results = [make_result(niveau="IA1")]
        hl = _extract_highlights(results)
        assert len(hl) == 1

    def test_high_level_ib_is_highlight(self, make_result):
        results = [make_result(niveau="IB2")]
        hl = _extract_highlights(results)
        assert len(hl) == 1

    def test_high_level_ir_is_highlight(self, make_result):
        results = [make_result(niveau="IR1")]
        hl = _extract_highlights(results)
        assert len(hl) == 1

    def test_no_highlight_for_normal_result(self, make_result):
        results = [make_result(place=10, tour="Finale", niveau="Dep")]
        hl = _extract_highlights(results)
        assert len(hl) == 0

    def test_is_podium_flag_false_for_qualif_only(self, make_result):
        results = [make_result(qualif="q", place=None, niveau="")]
        hl = _extract_highlights(results)
        assert hl[0]["is_podium"] is False

    def test_sort_podiums_first_then_by_niveau(self, make_result):
        results = [
            make_result(nom="A", niveau="IA1", place=None),
            make_result(nom="B", place=1, tour="Finale", niveau=""),
            make_result(nom="C", niveau="N2", place=None),
        ]
        hl = _extract_highlights(results)
        assert hl[0]["nom"] == "B"  # podium first
        assert hl[1]["nom"] == "A"  # IA before N
        assert hl[2]["nom"] == "C"

    def test_empty_list(self):
        assert _extract_highlights([]) == []


# ── process_results ─────────────────────────────────────────────────


@freeze_time("2026-02-15")
class TestProcessResults:
    def test_filters_recent_7_days(self, make_result):
        results = [
            make_result(nom="Recent", date="12/02"),
            make_result(nom="Old", date="01/01"),
        ]
        recent, _ = process_results(results)
        assert len(recent) == 1
        assert recent[0]["nom"] == "Recent"

    def test_cutoff_is_inclusive(self, make_result):
        """A result exactly 7 days ago should be included."""
        results = [make_result(date="08/02")]
        recent, _ = process_results(results)
        assert len(recent) == 1

    def test_custom_days_parameter(self, make_result):
        results = [make_result(date="01/02")]
        recent, _ = process_results(results, days=30)
        assert len(recent) == 1

    def test_empty_input(self):
        recent, highlights = process_results([])
        assert recent == []
        assert highlights == []

    def test_chronological_sort(self, make_result):
        results = [
            make_result(nom="B", date="14/02", ville="Paris"),
            make_result(nom="A", date="12/02", ville="Paris"),
        ]
        recent, _ = process_results(results)
        assert recent[0]["nom"] == "A"
        assert recent[1]["nom"] == "B"

    def test_sort_by_ville_then_nom(self, make_result):
        results = [
            make_result(nom="B", date="12/02", ville="Paris"),
            make_result(nom="A", date="12/02", ville="Lyon"),
        ]
        recent, _ = process_results(results)
        assert recent[0]["ville"] == "Lyon"
        assert recent[1]["ville"] == "Paris"

    def test_highlights_returned(self, make_result):
        results = [make_result(date="12/02", place=1, tour="Finale")]
        _, highlights = process_results(results)
        assert len(highlights) == 1

    def test_dt_key_added(self, make_result):
        results = [make_result(date="12/02")]
        recent, _ = process_results(results)
        assert "_dt" in recent[0]
        assert isinstance(recent[0]["_dt"], datetime)
