"""Rédaction de l'analyse d'un film par Claude, en sortie structurée.

Les sous-titres sont envoyés en entier : la fin du film est dans la dernière demi-heure,
et un extrait du début ne permet que de la deviner.
"""

from __future__ import annotations

from typing import Protocol

import anthropic

from movieplot.analysis import Analysis
from movieplot.tmdb import MovieDetails

SYSTEM_PROMPT = """\
Tu rédiges des fiches de films en français pour un site personnel dont le but est d'aider
quelqu'un à se rappeler un film et à savoir s'il l'a déjà vu.

Règles :
- Écris comme on raconte un film à un ami : phrases courtes, concrètes, sans jargon critique.
- Privilégie ce qui reste en mémoire : images fortes, scènes cultes, objets, lieux,
  musiques, gags, répliques. Une scène vaut mieux qu'un thème.
- N'écris que ce dont tu es sûr. Les sous-titres fournis font foi sur l'intrigue.
  Ne cite une réplique entre guillemets que si elle figure dans les sous-titres ou si tu
  es certain de son texte exact ; sinon, décris le moment sans guillemets.
- Ne mélange pas le film avec ses suites, son remake ou un homonyme.
- Les noms des personnages sont ceux de la version française quand elle est connue.
"""


class SummaryError(RuntimeError):
    """Claude n'a pas rendu d'analyse exploitable."""


class Summarizer(Protocol):
    def summarize(self, movie: MovieDetails, subtitles: str | None) -> Analysis: ...


def build_prompt(movie: MovieDetails, subtitles: str | None) -> str:
    heading = f"Film : {movie.title} ({movie.release_date[:4] or 'année inconnue'})"
    if movie.director:
        heading += f", réalisé par {movie.director}"
    parts = [heading, f"Titre original : {movie.original_title}"]
    if movie.cast:
        parts.append("Avec : " + ", ".join(member.label() for member in movie.cast))
    parts.append(f"Résumé TMDB : {movie.overview or 'aucun'}")
    if subtitles:
        parts.append(f"Sous-titres complets du film :\n<subtitles>\n{subtitles}\n</subtitles>")
    else:
        parts.append(
            "Aucun sous-titre disponible : appuie-toi sur le résumé et sur ce que tu sais du film."
        )
    parts.append("Rédige la fiche.")
    return "\n\n".join(parts)


class ClaudeSummarizer:
    def __init__(self, model: str, client: anthropic.Anthropic | None = None) -> None:
        self._model = model
        self._client = client or anthropic.Anthropic()

    def summarize(self, movie: MovieDetails, subtitles: str | None) -> Analysis:
        response = self._client.messages.parse(
            model=self._model,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": build_prompt(movie, subtitles)}],
            output_format=Analysis,
        )
        if response.stop_reason == "refusal":
            raise SummaryError("Claude a décliné la demande pour ce film")
        if response.parsed_output is None:
            raise SummaryError(f"Réponse inexploitable (stop_reason={response.stop_reason})")
        return response.parsed_output
