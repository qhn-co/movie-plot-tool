"""Configuration lue dans l'environnement, une seule fois au démarrage.

Hors développement (`MOVIEPLOT_ENV` renseigné), l'application refuse de démarrer sans base
PostgreSQL, sans mot de passe admin ou sans clé de session : il n'existe pas d'exécution où
le site public tourne avec un espace admin ouvert.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_CLAUDE_MODEL = "claude-opus-5-5"
DEV_DATABASE_URL = "sqlite:///./movieplot.db"
MIN_SESSION_SECRET_LENGTH = 32


class ConfigError(RuntimeError):
    """Configuration incomplète ou incohérente : l'application ne doit pas démarrer."""


@dataclass(frozen=True)
class Settings:
    environment: str = ""
    database_url: str = DEV_DATABASE_URL
    tmdb_api_key: str = ""
    opensubtitles_username: str = ""
    opensubtitles_password: str = ""
    claude_model: str = DEFAULT_CLAUDE_MODEL
    admin_password: str = ""
    session_secret: str = "dev-only-session-secret-not-for-production"
    webapp_dist: Path | None = None
    commit_sha: str = ""

    @property
    def is_deployed(self) -> bool:
        return bool(self.environment)

    @classmethod
    def from_env(cls) -> Settings:
        env = os.environ.get
        dist = env("MOVIEPLOT_WEBAPP_DIST", "")
        settings = cls(
            environment=env("MOVIEPLOT_ENV", ""),
            database_url=env("DATABASE_URL", DEV_DATABASE_URL),
            tmdb_api_key=env("TMDB_API_KEY", ""),
            opensubtitles_username=env("OPENSUBTITLES_USERNAME", ""),
            opensubtitles_password=env("OPENSUBTITLES_PASSWORD", ""),
            claude_model=env("MOVIEPLOT_CLAUDE_MODEL", DEFAULT_CLAUDE_MODEL),
            admin_password=env("ADMIN_PASSWORD", ""),
            session_secret=env("SESSION_SECRET", cls.session_secret),
            webapp_dist=Path(dist) if dist else None,
            commit_sha=env("MOVIEPLOT_COMMIT_SHA", ""),
        )
        settings.validate()
        return settings

    def validate(self) -> None:
        if not self.is_deployed:
            return
        missing = [
            name
            for name, value in (
                ("ADMIN_PASSWORD", self.admin_password),
                ("SESSION_SECRET", self.session_secret),
                ("DATABASE_URL", self.database_url),
            )
            if not value
        ]
        if missing:
            raise ConfigError(f"Variables manquantes : {', '.join(missing)}")
        if self.session_secret == Settings.session_secret:
            raise ConfigError("SESSION_SECRET garde sa valeur de développement")
        if len(self.session_secret) < MIN_SESSION_SECRET_LENGTH:
            raise ConfigError(f"SESSION_SECRET doit faire au moins {MIN_SESSION_SECRET_LENGTH} caractères")
        if self.database_url.startswith("sqlite"):
            raise ConfigError("Hors développement, DATABASE_URL doit pointer vers PostgreSQL")
