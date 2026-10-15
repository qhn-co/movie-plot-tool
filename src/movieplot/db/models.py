"""Schéma de la base : une table `films`, une ligne par fiche."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def _now() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class Film(Base):
    __tablename__ = "films"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tmdb_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    imdb_id: Mapped[str | None] = mapped_column(String(20))
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    original_title: Mapped[str] = mapped_column(String(300), nullable=False, default="")
    release_date: Mapped[str] = mapped_column(String(10), nullable=False, default="")
    overview: Mapped[str] = mapped_column(Text, nullable=False, default="")
    poster_url: Mapped[str | None] = mapped_column(String(500))
    vote_average: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    director: Mapped[str | None] = mapped_column(String(300))
    cast: Mapped[list[dict[str, str]]] = mapped_column(JSON, nullable=False, default=list)
    analysis: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    had_subtitles: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )
