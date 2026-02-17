import sys
from datetime import datetime, timedelta
from typing import Any

try:
    import resend
except ImportError:
    resend = None  # type: ignore


def _generate_dashboard(
    recent: list[dict[str, Any]], highlights: list[dict[str, Any]]
) -> str:
    """Génère les stats en haut du mail."""
    nb_athletes = len({r["nom"] for r in recent})
    nb_high = sum(1 for r in recent if r["niveau"].startswith(("N", "I")))

    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f0f7ff; border-radius: 8px; margin-bottom: 25px; border: 1px solid #dbeafe;">
        <tr>
            <td align="center" style="padding: 15px; border-right: 1px solid #dbeafe;">
                <div style="font-size: 24px; font-weight: bold; color: #1e40af;">{nb_athletes}</div>
                <div style="font-size: 13px; text-transform: uppercase; color: #475569;">Athlètes</div>
            </td>
            <td align="center" style="padding: 15px; border-right: 1px solid #dbeafe;">
                <div style="font-size: 24px; font-weight: bold; color: #1e40af;">{len(highlights)}</div>
                <div style="font-size: 13px; text-transform: uppercase; color: #475569;">Highlights</div>
            </td>
            <td align="center" style="padding: 15px;">
                <div style="font-size: 24px; font-weight: bold; color: #1e40af;">{nb_high}</div>
                <div style="font-size: 13px; text-transform: uppercase; color: #475569;">Perfs IR et Nat.</div>
            </td>
        </tr>
    </table>
    """


def _generate_congrats(
    recent: list[dict[str, Any]], highlights: list[dict[str, Any]]
) -> str:
    """Génère un bandeau motivationnel après le dashboard."""
    if not recent:
        return ""
    nb_athletes = len({r["nom"] for r in recent})
    if highlights:
        text = f"\U0001f389 Bravo ! {nb_athletes} athlètes en compétition, {len(highlights)} performances remarquables !"
    else:
        text = f"\U0001f4aa {nb_athletes} athlètes en compétition cette semaine !"
    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f0fdf4; border-radius: 8px; margin-bottom: 25px; border: 1px solid #bbf7d0;">
        <tr>
            <td align="center" style="padding: 12px; font-size: 14px; color: #166534;">
                {text}
            </td>
        </tr>
    </table>
    """


def _generate_cards(items: list[dict[str, Any]], is_highlight: bool = False) -> str:
    """Génère la liste de cartes HTML."""
    html = ""
    last_group = ""

    for r in items:
        # En-tête Date/Lieu
        current_group = f"{r['date']} - {r['ville']}"
        if current_group != last_group and not is_highlight:
            html += f"""
            <div style="background-color: #f1f5f9; color: #475569; padding: 6px 10px; font-size: 12px; font-weight: bold; margin-top: 15px; border-radius: 4px; text-transform: uppercase;">
                📅 {r["date"]} à {r["ville"]}
            </div>
            """
            last_group = current_group

        # Styles Carte
        bg_card = "#ffffff"
        border_col = "#e2e8f0"  # Gris défaut
        medal = ""

        if is_highlight and r.get("is_podium"):
            if r["place"] == 1:
                border_col, bg_card, medal = (
                    "#f59e0b",
                    "#fffbeb",
                    '<span style="font-size:18px">🥇</span> ',
                )
            elif r["place"] == 2:
                border_col, bg_card, medal = (
                    "#94a3b8",
                    "#f8fafc",
                    '<span style="font-size:18px">🥈</span> ',
                )
            elif r["place"] == 3:
                border_col, bg_card, medal = (
                    "#d97706",
                    "#fff7ed",
                    '<span style="font-size:18px">🥉</span> ',
                )

        # Métadonnées (Points • Niveau • Place)
        meta = []
        if r["points"]:
            meta.append(f"{r['points']} pts")
        if r["niveau"]:
            style = (
                "font-weight:bold; color:#0f172a;"
                if r["niveau"].startswith(("N", "IR", "IA", "IB"))
                else ""
            )
            meta.append(f"<span style='{style}'>{r['niveau']}</span>")
        if r["place"]:
            txt = "1er" if r["place"] == 1 else f"{r['place']}e"
            meta.append(f"<span style='color:#334155;'>{txt}</span>")

        meta_html = " &bull; ".join(meta)
        qualif = ""
        if r["qualif"]:
            q_label = r["qualif"].upper()
            if r["qualif"] == "qe":
                q_bg, q_color = "#f3e8ff", "#6b21a8"
            else:
                q_bg, q_color = "#dbeafe", "#1e40af"
            qualif = f'<span style="background:{q_bg}; color:{q_color}; padding:1px 4px; border-radius:3px; font-size:12px; font-weight:bold; margin-left:5px;">{q_label}</span>'
        tour = (
            f" - <span style='color:#64748b; font-style:italic;'>{r['tour']}</span>"
            if r["tour"]
            else ""
        )

        html += f"""
        <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 8px; border-bottom: 1px solid #f1f5f9; background-color: {bg_card};">
            <tr>
                <td style="padding: 10px 10px 10px 15px; border-left: 5px solid {border_col};">
                    <div style="margin-bottom: 3px; font-size: 14px; font-weight: bold; color: #0f172a;">
                        {medal}{r["nom"]}
                    </div>
                    <div style="font-size: 13px; color: #475569;">
                        {r["epreuve"]}{tour}
                    </div>
                </td>
                <td align="right" style="padding: 10px; vertical-align: middle; width: 35%;">
                    <div style="font-size: 15px; font-weight: bold; color: #0f172a; margin-bottom: 4px;">
                        {r["perf"]}{qualif}
                    </div>
                    <div style="font-size: 13px; color: #475569; line-height: 1.4;">
                        {meta_html}
                    </div>
                </td>
            </tr>
        </table>
        """
    return html


def format_html_report(
    club_name: str, recent: list[dict[str, Any]], highlights: list[dict[str, Any]]
) -> str:
    """Assemble l'email complet."""

    # --- LOGIQUE ROBUSTE DE DATE ---
    # On veut afficher le "Lundi" de la semaine précédente,
    # peu importe si on lance le script le Lundi, Mardi ou Mercredi.
    today = datetime.now()

    # today.weekday() : Lundi=0, Mardi=1 ... Dimanche=6
    # Si on est Lundi (0) : On recule de 0 + 7 = 7 jours (Lundi dernier)
    # Si on est Mardi (1) : On recule de 1 + 7 = 8 jours (Lundi dernier)
    days_to_subtract = today.weekday() + 7
    start_of_week = today - timedelta(days=days_to_subtract)

    week_str = start_of_week.strftime("%d/%m")
    # -------------------------------

    nb_athletes = len({r["nom"] for r in recent})

    preheader = (
        f"{nb_athletes} athlètes \u00b7 {len(highlights)} highlights \u00b7 {club_name}"
    )

    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Résultats {club_name}</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #333; background-color: #ffffff; margin: 0; padding: 0;">
        <div style="display:none; max-height:0; overflow:hidden;">{preheader}</div>
        <div style="max-width: 600px; margin: 0 auto; padding: 10px;">

            <!-- Bouton copier : masqué par défaut, révélé par JS (invisible dans les emails) -->
            <div id="copy-wrapper" style="display:none; text-align:right; margin-bottom: 12px;">
                <button id="copy-btn" style="display:inline-flex; align-items:center; gap:6px; background-color:transparent; color:#1e40af; border:1px solid #bfdbfe; padding:6px 14px; border-radius:6px; font-size:13px; font-weight:500; font-family:inherit; cursor:pointer; letter-spacing:0.01em; transition:background-color 0.15s, border-color 0.15s, color 0.15s;">
                    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" style="flex-shrink:0;"><rect x="5" y="5" width="9" height="11" rx="1.5" stroke="currentColor" stroke-width="1.5"/><path d="M11 5V3.5A1.5 1.5 0 0 0 9.5 2h-7A1.5 1.5 0 0 0 1 3.5v7A1.5 1.5 0 0 0 2.5 12H4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
                    Copier
                </button>
            </div>

            <div id="report-content">
            <div style="text-align:center; margin-bottom: 25px;">
                <h1 style="color: #111; font-size: 22px; margin-bottom: 5px; font-weight: 800; letter-spacing: -0.5px;">{club_name}</h1>
                <div style="color: #475569; font-size: 14px;">Résultats de la semaine du {week_str}</div>
            </div>

            {_generate_dashboard(recent, highlights)}

            {_generate_congrats(recent, highlights)}

            {'<table width="100%" cellpadding="0" cellspacing="0" style="background-color: #fffbeb; border-radius: 8px; border: 1px solid #fde68a;"><tr><td style="padding: 15px;"><h2 style="color: #92400e; font-size: 15px; margin-top: 0; margin-bottom: 15px; text-transform: uppercase; font-weight: 700; border-bottom: 2px solid #fde68a; padding-bottom: 5px;">🏆 Podiums et hautes performances</h2>' + _generate_cards(highlights, True) + "</td></tr></table>" if highlights else ""}

            <h2 style="color: #1e40af; font-size: 15px; margin-top: 30px; margin-bottom: 15px; text-transform: uppercase; font-weight: 700; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px;">🏃 Tous les Résultats ({len(recent)})</h2>
            {_generate_cards(recent, False) if recent else '<p style="text-align:center; color:#666; font-style:italic;">Aucune compétition.</p>'}

            <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; color: #94a3b8; font-size: 13px; text-align: center;">
                <p style="font-size: 14px; color: #475569; font-weight: bold; margin-bottom: 10px;">📣 Partagez ces résultats avec vos athlètes !</p>
                <p>Généré par <strong>MyPacer Club</strong>.</p>
                <p>Données: www.athle.fr</p>
            </div>
            </div>
        </div>

        <script>
        (function() {{
            var wrapper = document.getElementById('copy-wrapper');
            var btn = document.getElementById('copy-btn');
            if (!wrapper || !btn) return;
            wrapper.style.display = 'block';

            var ICON_COPY = '<svg width="14" height="14" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" style="flex-shrink:0;"><rect x="5" y="5" width="9" height="11" rx="1.5" stroke="currentColor" stroke-width="1.5"/><path d="M11 5V3.5A1.5 1.5 0 0 0 9.5 2h-7A1.5 1.5 0 0 0 1 3.5v7A1.5 1.5 0 0 0 2.5 12H4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>';
            var ICON_CHECK = '<svg width="14" height="14" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" style="flex-shrink:0;"><path d="M2.5 8.5L6 12L13.5 4" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"/></svg>';

            btn.addEventListener('mouseenter', function() {{
                if (!btn.dataset.success) {{
                    btn.style.backgroundColor = '#eff6ff';
                    btn.style.borderColor = '#93c5fd';
                }}
            }});
            btn.addEventListener('mouseleave', function() {{
                if (!btn.dataset.success) {{
                    btn.style.backgroundColor = 'transparent';
                    btn.style.borderColor = '#bfdbfe';
                }}
            }});
            btn.addEventListener('mousedown', function() {{
                if (!btn.dataset.success) {{
                    btn.style.backgroundColor = '#dbeafe';
                }}
            }});
            btn.addEventListener('mouseup', function() {{
                if (!btn.dataset.success) {{
                    btn.style.backgroundColor = '#eff6ff';
                }}
            }});

            function setSuccess() {{
                btn.dataset.success = '1';
                btn.innerHTML = ICON_CHECK + 'Copié';
                btn.style.backgroundColor = '#f0fdf4';
                btn.style.borderColor = '#bbf7d0';
                btn.style.color = '#166534';
                setTimeout(function() {{
                    delete btn.dataset.success;
                    btn.innerHTML = ICON_COPY + 'Copier';
                    btn.style.backgroundColor = 'transparent';
                    btn.style.borderColor = '#bfdbfe';
                    btn.style.color = '#1e40af';
                }}, 2000);
            }}

            btn.addEventListener('click', function() {{
                var content = document.getElementById('report-content');
                if (!content) return;

                var html = content.innerHTML;
                var text = content.innerText;

                if (navigator.clipboard && navigator.clipboard.write) {{
                    navigator.clipboard.write([
                        new ClipboardItem({{
                            'text/html': new Blob([html], {{type: 'text/html'}}),
                            'text/plain': new Blob([text], {{type: 'text/plain'}})
                        }})
                    ]).then(setSuccess).catch(function() {{
                        fallbackCopy(text);
                    }});
                }} else {{
                    fallbackCopy(text);
                }}
            }});

            function fallbackCopy(text) {{
                var ta = document.createElement('textarea');
                ta.value = text;
                ta.style.position = 'fixed';
                ta.style.opacity = '0';
                document.body.appendChild(ta);
                ta.select();
                document.execCommand('copy');
                document.body.removeChild(ta);
                setSuccess();
            }}
        }})();
        </script>
    </body>
    </html>
    """


def send_email(api_key: str, to: str, subject: str, html: str) -> None:
    """Envoie via Resend."""
    if not resend:
        print("❌ Module 'resend' manquant.", file=sys.stderr)
        return

    resend.api_key = api_key
    print(f"📧 Envoi à {to}...")
    try:
        resend.Emails.send(
            {
                "from": "MyPacer Club <noreply@pioum.ovh>",  # Ou onboarding@resend.dev pour tester
                "to": [to],
                "subject": subject,
                "html": html,
            }
        )
        print("✅ Envoyé.")
    except Exception as e:
        print(f"❌ Erreur Resend: {e}")
