import pytest

from movieplot.config import ConfigError, Settings

GOOD_SECRET = "x" * 32
PG = "postgresql+psycopg://u:p@db/movieplot"


def test_development_needs_nothing() -> None:
    Settings().validate()


@pytest.mark.parametrize(
    "overrides",
    [
        {"admin_password": ""},
        {"session_secret": "trop-court"},
        {"session_secret": Settings.session_secret},
        {"database_url": "sqlite:///./movieplot.db"},
    ],
)
def test_deployed_app_refuses_unsafe_configuration(overrides: dict) -> None:
    values = {
        "environment": "production",
        "admin_password": "secret",
        "session_secret": GOOD_SECRET,
        "database_url": PG,
    } | overrides
    with pytest.raises(ConfigError):
        Settings(**values).validate()


def test_deployed_app_accepts_complete_configuration() -> None:
    Settings(
        environment="production", admin_password="s", session_secret=GOOD_SECRET, database_url=PG
    ).validate()
