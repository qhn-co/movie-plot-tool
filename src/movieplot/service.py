"""Les opérations sur les fiches : génération et publication côté admin, lecture côté public."""

from __future__ import annotations

import logging
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from movieplot.analysis import Analysis
from movieplot.db.models import Film
from movieplot.subtitles import SubtitleSource
from movieplot.summarizer import Summarizer
from movieplot.tmdb import MovieDetails, MovieSummary

log = logging.getLogger(__name__)


class MovieCatalog(Protocol):
    def search(self, query: str, limit: int = 8) -> list[MovieSummary]: ...

    def details(self, tmdb_id: int) -> MovieDetails: ...


class FilmNotFound(LookupError):
    pass


class FilmService:
    def __init__(
        self,
        sessions: sessionmaker[Session],
        catalog: MovieCatalog,
        subtitles: SubtitleSource,
        summarizer: Summarizer,
        model_name: str,
    ) -> None:
        self._sessions = sessions
        self.catalog = catalog
        self._subtitles = subtitles
        self._summarizer = summarizer
        self._model_name = model_name

    def generate(self, tmdb_id: int) -> Film:
        """Crée la fiche du film, ou la régénère si elle existe, sans changer sa publication."""
        movie = self.catalog.details(tmdb_id)
        text = self._fetch_subtitles(movie)
        analysis = self._summarizer.summarize(movie, text)
        with self._sessions.begin() as session:
            film = session.scalar(select(Film).where(Film.tmdb_id == tmdb_id))
            if film is None:
                film = Film(tmdb_id=tmdb_id, published=False)
                session.add(film)
            film.imdb_id = movie.imdb_id
            film.title = movie.title
            film.original_title = movie.original_title
            film.release_date = movie.release_date
            film.overview = movie.overview
            film.poster_url = movie.poster_url
            film.vote_average = movie.vote_average
            film.analysis = analysis.model_dump()
            film.had_subtitles = text is not None
            film.model = self._model_name
        return film

    def _fetch_subtitles(self, movie: MovieDetails) -> str | None:
        # Sans sous-titres, la fiche reste possible à partir du résumé TMDB : une panne
        # d'OpenSubtitles ne doit pas bloquer l'admin.
        try:
            return self._subtitles.fetch_text(imdb_id=movie.imdb_id, title=movie.title)
        except Exception:  # noqa: BLE001
            log.exception("Sous-titres indisponibles pour %s", movie.tmdb_id)
            return None

    def list_films(self, *, published_only: bool) -> list[Film]:
        query = select(Film).order_by(Film.title)
        if published_only:
            query = query.where(Film.published.is_(True))
        with self._sessions() as session:
            return list(session.scalars(query))

    def get_film(self, film_id: int, *, published_only: bool) -> Film:
        with self._sessions() as session:
            film = session.get(Film, film_id)
        if film is None or (published_only and not film.published):
            raise FilmNotFound(film_id)
        return film

    def set_published(self, film_id: int, published: bool) -> Film:
        with self._sessions.begin() as session:
            film = session.get(Film, film_id)
            if film is None:
                raise FilmNotFound(film_id)
            film.published = published
        return film

    def update_analysis(self, film_id: int, analysis: Analysis) -> Film:
        with self._sessions.begin() as session:
            film = session.get(Film, film_id)
            if film is None:
                raise FilmNotFound(film_id)
            film.analysis = analysis.model_dump()
        return film

    def delete(self, film_id: int) -> None:
        with self._sessions.begin() as session:
            film = session.get(Film, film_id)
            if film is None:
                raise FilmNotFound(film_id)
            session.delete(film)
