import argparse
import os
from datetime import datetime
from typing import Any

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from . import scraper, analyzer, reporter


def main() -> None:
    parser = argparse.ArgumentParser(description="MyPacer Club Watcher")
    parser.add_argument("--club", required=True, help="ID Club (ex: 033033)")
    parser.add_argument("--to", help="Email destinataire")
    parser.add_argument("--sample", help="Fichier HTML local (skip le scraping)")
    parser.add_argument(
        "--save-sample", help="Sauvegarde le HTML brut scrapé dans ce fichier"
    )
    args = parser.parse_args()

    # Config
    api_key = os.getenv("RESEND_API_KEY")
    to_email = args.to or os.getenv("RESEND_TO_EMAIL")

    # 1. Scraping
    if args.sample:
        print(f"📂 Chargement du sample : {args.sample}")
        soup = scraper.load_local_page(args.sample)
        soups = [soup]
    else:
        year = datetime.now().year
        soups, raw_html = scraper.fetch_all_club_pages(args.club, year)
        print(f"🔄 Scraping du club {args.club} ({len(soups)} page(s))...")

        if args.save_sample:
            with open(args.save_sample, "w", encoding="utf-8") as f:
                f.write(raw_html)
            print(f"💾 Sample sauvegardé : {args.save_sample}")

    club_name = scraper.extract_club_name(soups[0], args.club)

    raw_data: list[dict[str, Any]] = []
    for s in soups:
        raw_data.extend(scraper.parse_raw_results(s))
    print(f"   -> {len(raw_data)} résultats bruts trouvés.")

    # 2. Analyse
    recent, highlights = analyzer.process_results(raw_data, days=7)
    print(f"   -> {len(recent)} résultats récents (7j).")
    print(f"   -> {len(highlights)} highlights qualifiés.")

    # 3. Reporting
    html_content = reporter.format_html_report(club_name, recent, highlights)

    if api_key and to_email:
        # Mode Production
        subject = f"Résultats {club_name} - {datetime.now().strftime('%d/%m')}"
        reporter.send_email(api_key, to_email, subject, html_content)
    else:
        # Mode Développement
        filename = f"preview_{args.club}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)

        print("-" * 50)
        print("ℹ️  MODE DEV (Pas d'email envoyé)")
        print(f"✅ Preview générée : {os.path.abspath(filename)}")
        print("💡 Pour envoyer un mail, configurez le .env ou utilisez --to")
        print("-" * 50)


if __name__ == "__main__":
    main()
