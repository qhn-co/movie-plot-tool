"""Contrats JSON de l'API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from movieplot.analysis import Analysis


class FilmCard(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    release_date: str
    poster_url: str | None
    vote_average: float


class FilmPage(FilmCard):
    original_title: str
    overview: str
    analysis: Analysis
    had_subtitles: bool


class AdminFilm(FilmPage):
    tmdb_id: int
    published: bool
    model: str
    updated_at: datetime


class TmdbResult(BaseModel):
    tmdb_id: int
    title: str
    year: str


class GenerateRequest(BaseModel):
    tmdb_id: int = Field(gt=0)


class FilmUpdate(BaseModel):
    published: bool | None = None
    analysis: Analysis | None = None


class LoginRequest(BaseModel):
    password: str


class SessionState(BaseModel):
    authenticated: bool
