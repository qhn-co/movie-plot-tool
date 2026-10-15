"""Client TMDB minimal : recherche d'un film et lecture de sa fiche, en français."""

from __future__ import annotations

from dataclasses import dataclass

import httpx

TMDB_API = "https://api.themoviedb.org/3"
POSTER_BASE = "https://image.tmdb.org/t/p/w500"


@dataclass(frozen=True)
class MovieSummary:
    tmdb_id: int
    title: str
    year: str


@dataclass(frozen=True)
class MovieDetails:
    tmdb_id: int
    imdb_id: str | None
    title: str
    original_title: str
    release_date: str
    overview: str
    poster_url: str | None
    vote_average: float


class TmdbClient:
    def __init__(self, api_key: str, http: httpx.Client | None = None) -> None:
        self._api_key = api_key
        self._http = http or httpx.Client(base_url=TMDB_API, timeout=15.0)

    def _get(self, path: str, **params: str | int) -> dict:
        response = self._http.get(
            path, params={"api_key": self._api_key, "language": "fr-FR", **params}
        )
        response.raise_for_status()
        return response.json()

    def search(self, query: str, limit: int = 8) -> list[MovieSummary]:
        results = self._get("/search/movie", query=query).get("results", [])
        return [
            MovieSummary(
                tmdb_id=item["id"],
                title=item.get("title") or item.get("original_title", ""),
                year=(item.get("release_date") or "")[:4],
            )
            for item in results[:limit]
        ]

    def details(self, tmdb_id: int) -> MovieDetails:
        data = self._get(f"/movie/{tmdb_id}")
        poster = data.get("poster_path")
        return MovieDetails(
            tmdb_id=data["id"],
            imdb_id=data.get("imdb_id") or None,
            title=data.get("title") or data.get("original_title", ""),
            original_title=data.get("original_title", ""),
            release_date=data.get("release_date") or "",
            overview=data.get("overview") or "",
            poster_url=f"{POSTER_BASE}{poster}" if poster else None,
            vote_average=float(data.get("vote_average") or 0.0),
        )
