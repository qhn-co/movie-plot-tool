from pathlib import Path

from sqlalchemy import create_engine, inspect

from movieplot.db.migrate import upgrade
from movieplot.db.models import Base


def test_migrations_match_models(tmp_path: Path) -> None:
    url = f"sqlite:///{tmp_path / 'm.db'}"
    upgrade(url)
    columns = {c["name"] for c in inspect(create_engine(url)).get_columns("films")}
    assert columns == {c.name for c in Base.metadata.tables["films"].columns}
