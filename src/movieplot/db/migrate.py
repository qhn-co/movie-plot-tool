"""Applique les migrations Alembic jusqu'à la tête, sur la base de `DATABASE_URL`."""

from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config

MIGRATIONS = Path(__file__).parent / "migrations"


def alembic_config(database_url: str) -> Config:
    config = Config()
    config.set_main_option("script_location", str(MIGRATIONS))
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    return config


def upgrade(database_url: str) -> None:
    command.upgrade(alembic_config(database_url), "head")


def main() -> None:
    from movieplot.config import Settings

    upgrade(Settings.from_env().database_url)


if __name__ == "__main__":
    main()
