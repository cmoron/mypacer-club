import sys
from datetime import datetime
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
    nb_high = sum(1 for r in recent if r["niveau"].startswith(("N", "IR", "IA", "IB")))

    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f0f7ff; border-radius: 8px; margin-bottom: 25px; border: 1px solid #dbeafe;">
        <tr>
            <td align="center" style="padding: 15px; border-right: 1px solid #dbeafe;">
                <div style="font-size: 24px; font-weight: bold; color: #1e40af;">{nb_athletes}</div>
                <div style="font-size: 11px; text-transform: uppercase; color: #64748b;">Athlètes</div>
            </td>
            <td align="center" style="padding: 15px; border-right: 1px solid #dbeafe;">
                <div style="font-size: 24px; font-weight: bold; color: #1e40af;">{len(highlights)}</div>
                <div style="font-size: 11px; text-transform: uppercase; color: #64748b;">Highlights</div>
            </td>
            <td align="center" style="padding: 15px;">
                <div style="font-size: 24px; font-weight: bold; color: #1e40af;">{nb_high}</div>
                <div style="font-size: 11px; text-transform: uppercase; color: #64748b;">Perfs N/IR</div>
            </td>
        </tr>
    </table>
    """


def _generate_cards(items: list[dict[str, Any]], is_highlight: bool = False) -> str:
    """Génère la liste de cartes HTML."""
    html = '<div style="width: 100%;">'
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
                border_col, bg_card, medal = "#f59e0b", "#fffbeb", "🥇 "
            elif r["place"] == 2:
                border_col, bg_card, medal = "#94a3b8", "#f8fafc", "🥈 "
            elif r["place"] == 3:
                border_col, bg_card, medal = "#d97706", "#fff7ed", "🥉 "

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
        qualif = (
            '<span style="background:#dbeafe; color:#1e40af; padding:1px 4px; border-radius:3px; font-size:10px; font-weight:bold; margin-left:5px;">Q</span>'
            if r["qualif"]
            else ""
        )
        tour = (
            f" - <span style='color:#64748b; font-style:italic;'>{r['tour']}</span>"
            if r["tour"]
            else ""
        )

        html += f"""
        <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 8px; border-bottom: 1px solid #f1f5f9; background-color: {bg_card};">
            <tr>
                <td style="padding: 10px 10px 10px 15px; border-left: 3px solid {border_col};">
                    <div style="margin-bottom: 3px; font-size: 14px; font-weight: bold; color: #0f172a;">
                        {medal}{r["nom"]}
                    </div>
                    <div style="font-size: 13px; color: #475569;">
                        {r["epreuve"]}{tour}
                    </div>
                </td>
                <td align="right" style="padding: 10px; vertical-align: middle; width: 140px;">
                    <div style="font-size: 15px; font-weight: bold; color: #0f172a; margin-bottom: 4px;">
                        {r["perf"]}{qualif}
                    </div>
                    <div style="font-size: 11px; color: #64748b; white-space: nowrap;">
                        {meta_html}
                    </div>
                </td>
            </tr>
        </table>
        """
    html += "</div>"
    return html


def format_html_report(
    club_name: str, recent: list[dict[str, Any]], highlights: list[dict[str, Any]]
) -> str:
    """Assemble l'email complet."""
    today = datetime.now().strftime("%d/%m")

    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Résultats {club_name}</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #333; background-color: #ffffff; margin: 0; padding: 0;">
        <div style="max-width: 600px; margin: 0 auto; padding: 10px;">
            <div style="text-align:center; margin-bottom: 25px;">
                <h1 style="color: #111; font-size: 22px; margin-bottom: 5px; font-weight: 800; letter-spacing: -0.5px;">{club_name}</h1>
                <div style="color: #64748b; font-size: 14px;">Résultats de la semaine du {today}</div>
            </div>

            {_generate_dashboard(recent, highlights)}

            {'<h2 style="color: #1e40af; font-size: 15px; margin-top: 30px; margin-bottom: 15px; text-transform: uppercase; font-weight: 700; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px;">🏆 Podiums et performances</h2>' + _generate_cards(highlights, True) if highlights else ""}

            <h2 style="color: #1e40af; font-size: 15px; margin-top: 30px; margin-bottom: 15px; text-transform: uppercase; font-weight: 700; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px;">🏃 Tous les Résultats ({len(recent)})</h2>
            {_generate_cards(recent, False) if recent else '<p style="text-align:center; color:#666; font-style:italic;">Aucune compétition.</p>'}

            <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; color: #94a3b8; font-size: 11px; text-align: center;">
                <p>Généré par <strong>MyPacer Club</strong>.</p>
                <p>Données: www.athle.fr</p>
            </div>
        </div>
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
