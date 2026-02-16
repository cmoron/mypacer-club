from unittest.mock import MagicMock, patch

from freezegun import freeze_time

from mypacer_club.reporter import (
    _generate_cards,
    _generate_congrats,
    _generate_dashboard,
    format_html_report,
    send_email,
)


# ── _generate_dashboard ─────────────────────────────────────────────


class TestGenerateDashboard:
    def test_athlete_count(self, make_result):
        recent = [
            make_result(nom="A"),
            make_result(nom="B"),
            make_result(nom="A"),  # duplicate
        ]
        html = _generate_dashboard(recent, [])
        assert ">2<" in html  # 2 unique athletes

    def test_highlights_count(self, make_result):
        recent = [make_result()]
        highlights = [make_result(), make_result()]
        html = _generate_dashboard(recent, highlights)
        # The "2" for highlights should appear in the HTML
        assert ">2<" in html

    def test_high_level_count(self, make_result):
        recent = [
            make_result(niveau="N3"),
            make_result(niveau="IR1"),
            make_result(niveau="IA2"),
            make_result(niveau="Dep"),
        ]
        html = _generate_dashboard(recent, [])
        assert ">3<" in html  # N3, IR1, IA2

    def test_empty_lists(self):
        html = _generate_dashboard([], [])
        assert ">0<" in html

    def test_niveau_national_label(self, make_result):
        html = _generate_dashboard([make_result()], [])
        assert "Perfs IR et Nat." in html


# ── _generate_congrats ──────────────────────────────────────────────


class TestGenerateCongrats:
    def test_with_highlights(self, make_result):
        recent = [make_result(nom="A"), make_result(nom="B")]
        highlights = [make_result()]
        html = _generate_congrats(recent, highlights)
        assert "Bravo" in html
        assert "performances remarquables" in html
        assert "2 athlètes" in html

    def test_without_highlights(self, make_result):
        recent = [make_result(nom="A"), make_result(nom="B")]
        html = _generate_congrats(recent, [])
        assert "en compétition" in html
        assert "Bravo" not in html

    def test_no_results(self):
        html = _generate_congrats([], [])
        assert html == ""


# ── _generate_cards ──────────────────────────────────────────────────


class TestGenerateCards:
    def test_name_rendered(self, make_result):
        items = [make_result(nom="DUPONT Marie")]
        html = _generate_cards(items)
        assert "DUPONT Marie" in html

    def test_epreuve_rendered(self, make_result):
        items = [make_result(epreuve="100m - Salle / SEF")]
        html = _generate_cards(items)
        assert "100m - Salle / SEF" in html

    def test_perf_rendered(self, make_result):
        items = [make_result(perf="11''45")]
        html = _generate_cards(items)
        assert "11''45" in html

    def test_gold_medal_highlight(self, make_result):
        items = [make_result(place=1, is_podium=True)]
        html = _generate_cards(items, is_highlight=True)
        assert "\U0001f947" in html  # gold medal emoji

    def test_silver_medal_highlight(self, make_result):
        items = [make_result(place=2, is_podium=True)]
        html = _generate_cards(items, is_highlight=True)
        assert "\U0001f948" in html  # silver medal emoji

    def test_bronze_medal_highlight(self, make_result):
        items = [make_result(place=3, is_podium=True)]
        html = _generate_cards(items, is_highlight=True)
        assert "\U0001f949" in html  # bronze medal emoji

    def test_no_medal_without_is_podium(self, make_result):
        items = [make_result(place=1, is_podium=False)]
        html = _generate_cards(items, is_highlight=True)
        assert "\U0001f947" not in html

    def test_no_medal_in_non_highlight_mode(self, make_result):
        items = [make_result(place=1, is_podium=True)]
        html = _generate_cards(items, is_highlight=False)
        assert "\U0001f947" not in html

    def test_qualif_badge(self, make_result):
        items = [make_result(qualif=True)]
        html = _generate_cards(items)
        assert ">Q<" in html

    def test_no_qualif_badge(self, make_result):
        items = [make_result(qualif=False)]
        html = _generate_cards(items)
        assert ">Q<" not in html

    def test_date_ville_header(self, make_result):
        items = [make_result(date="12/02", ville="Paris")]
        html = _generate_cards(items, is_highlight=False)
        assert "12/02" in html
        assert "Paris" in html

    def test_no_date_header_in_highlight_mode(self, make_result):
        items = [make_result(date="12/02", ville="Paris")]
        html = _generate_cards(items, is_highlight=True)
        # Should not contain the date/ville group header div
        assert "\U0001f4c5" not in html

    def test_bold_style_for_high_level(self, make_result):
        items = [make_result(niveau="N3")]
        html = _generate_cards(items)
        assert "font-weight:bold" in html

    def test_no_bold_for_low_level(self, make_result):
        items = [make_result(niveau="Dep")]
        html = _generate_cards(items)
        # The niveau span should not have bold style
        assert "font-weight:bold; color:#0f172a;" not in html


# ── format_html_report ───────────────────────────────────────────────


@freeze_time("2026-02-17")
class TestFormatHtmlReport:
    def test_contains_club_name(self, make_result):
        html = format_html_report("US TALENCE", [make_result()], [])
        assert "US TALENCE" in html

    def test_contains_date(self, make_result):
        html = format_html_report("Club", [make_result()], [])
        assert "09/02" in html

    def test_highlights_section_present(self, make_result):
        hl = [make_result(is_podium=True, place=1)]
        html = format_html_report("Club", [make_result()], hl)
        assert "Podiums et hautes performances" in html

    def test_highlights_section_absent_when_empty(self, make_result):
        html = format_html_report("Club", [make_result()], [])
        assert "Podiums et hautes performances" not in html

    def test_no_competition_message(self):
        html = format_html_report("Club", [], [])
        assert "Aucune" in html

    def test_result_count_displayed(self, make_result):
        recent = [make_result(), make_result()]
        html = format_html_report("Club", recent, [])
        assert "Résultats (2)" in html

    def test_congrats_with_highlights(self, make_result):
        hl = [make_result(is_podium=True, place=1)]
        html = format_html_report("Club", [make_result()], hl)
        assert "Bravo" in html
        assert "performances remarquables" in html

    def test_congrats_without_highlights(self, make_result):
        html = format_html_report("Club", [make_result()], [])
        assert "en compétition" in html
        assert "Bravo" not in html

    def test_congrats_no_results(self):
        html = format_html_report("Club", [], [])
        assert "Bravo" not in html
        assert "en compétition" not in html

    def test_highlights_golden_background(self, make_result):
        hl = [make_result(is_podium=True, place=1)]
        html = format_html_report("Club", [make_result()], hl)
        assert "#fffbeb" in html

    def test_footer_cta(self, make_result):
        html = format_html_report("Club", [make_result()], [])
        assert "Partagez" in html


# ── send_email ───────────────────────────────────────────────────────


class TestSendEmail:
    @patch("mypacer_club.reporter.resend")
    def test_sends_via_resend(self, mock_resend: MagicMock):
        send_email("key123", "to@test.com", "Subject", "<p>Body</p>")
        mock_resend.Emails.send.assert_called_once()
        call_args = mock_resend.Emails.send.call_args[0][0]
        assert call_args["to"] == ["to@test.com"]
        assert call_args["subject"] == "Subject"
        assert call_args["html"] == "<p>Body</p>"

    @patch("mypacer_club.reporter.resend")
    def test_sets_api_key(self, mock_resend: MagicMock):
        send_email("my-api-key", "to@test.com", "Sub", "<p>x</p>")
        assert mock_resend.api_key == "my-api-key"

    @patch("mypacer_club.reporter.resend")
    def test_handles_send_exception(self, mock_resend: MagicMock, capsys):
        mock_resend.Emails.send.side_effect = Exception("API error")
        send_email("key", "to@test.com", "Sub", "<p>x</p>")
        captured = capsys.readouterr()
        assert "Erreur Resend" in captured.out

    @patch("mypacer_club.reporter.resend", None)
    def test_missing_resend_module(self, capsys):
        send_email("key", "to@test.com", "Sub", "<p>x</p>")
        captured = capsys.readouterr()
        assert "manquant" in captured.err
