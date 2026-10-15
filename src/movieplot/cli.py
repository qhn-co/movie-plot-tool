"""Ligne de commande : `movieplot migrate` et `movieplot preview "Titre"`.

`preview` génère une fiche sans l'enregistrer, pour essayer le prompt en local.
"""

from __future__ import annotations

import argparse
import json
import sys

from movieplot.config import Settings
from movieplot.db.migrate import upgrade
from movieplot.subtitles import OpenSubtitlesXmlRpc
from movieplot.summarizer import ClaudeSummarizer
from movieplot.tmdb import TmdbClient


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="movieplot")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("migrate", help="applique les migrations de la base")
    preview = commands.add_parser("preview", help="génère une fiche sans l'enregistrer")
    preview.add_argument("title")
    args = parser.parse_args(argv)

    settings = Settings.from_env()
    if args.command == "migrate":
        upgrade(settings.database_url)
        return 0

    catalog = TmdbClient(settings.tmdb_api_key)
    found = catalog.search(args.title, limit=1)
    if not found:
        print(f"Aucun film trouvé pour « {args.title} »", file=sys.stderr)
        return 1
    movie = catalog.details(found[0].tmdb_id)
    subtitles = OpenSubtitlesXmlRpc(
        settings.opensubtitles_username, settings.opensubtitles_password
    ).fetch_text(imdb_id=movie.imdb_id, title=movie.title)
    analysis = ClaudeSummarizer(settings.claude_model).summarize(movie, subtitles)
    print(json.dumps(analysis.model_dump(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
