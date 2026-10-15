from __future__ import annotations

from dataclasses import dataclass, field

import pytest
from fastapi.testclient import TestClient

from movieplot.analysis import Analysis
from movieplot.api.app import create_app
from movieplot.config import Settings
from movieplot.db.models import Base
from movieplot.db.session import make_engine, make_session_factory
from movieplot.service import FilmService
from movieplot.tmdb import CastMember, MovieDetails, MovieSummary

ADMIN_PASSWORD = "mot-de-passe-de-test"

INCEPTION = MovieDetails(
    tmdb_id=27205,
    imdb_id="tt1375666",
    title="Inception",
    original_title="Inception",
    release_date="2010-07-15",
    overview="Dom Cobb vole des secrets dans les rêves.",
    poster_url="https://image.tmdb.org/t/p/w500/inception.jpg",
    vote_average=8.4,
    director="Christopher Nolan",
    cast=(
        CastMember("Leonardo DiCaprio", "Dom Cobb"),
        CastMember("Elliot Page", "Ariadne"),
    ),
)


class FakeCatalog:
    def __init__(self) -> None:
        self.movies = {INCEPTION.tmdb_id: INCEPTION}

    def search(self, query: str, limit: int = 8) -> list[MovieSummary]:
        return [
            MovieSummary(m.tmdb_id, m.title, m.release_date[:4])
            for m in self.movies.values()
            if query.lower() in m.title.lower()
        ][:limit]

    def details(self, tmdb_id: int) -> MovieDetails:
        return self.movies[tmdb_id]


@dataclass
class FakeSubtitles:
    text: str | None = "We need to go deeper."
    fail: bool = False
    calls: list[tuple[str | None, str]] = field(default_factory=list)

    def fetch_text(self, *, imdb_id: str | None, title: str) -> str | None:
        self.calls.append((imdb_id, title))
        if self.fail:
            raise ConnectionError("OpenSubtitles indisponible")
        return self.text


@dataclass
class FakeSummarizer:
    received: list[str | None] = field(default_factory=list)

    def summarize(self, movie: MovieDetails, subtitles: str | None) -> Analysis:
        self.received.append(subtitles)
        return Analysis(
            hook=f"Le film où {movie.title} se passe dans les rêves.",
            memory_cues=["Paris se replie sur elle-même.", "Le couloir tourne."],
            synopsis=f"Synopsis de {movie.title}",
            timeline=["Étape 1", "Étape 2", "Étape 3", "Étape 4", "Étape 5"],
            ending="La toupie tourne.",
            context="Gros succès de 2010.",
        )


@pytest.fixture
def subtitles() -> FakeSubtitles:
    return FakeSubtitles()


@pytest.fixture
def summarizer() -> FakeSummarizer:
    return FakeSummarizer()


@pytest.fixture
def service(subtitles: FakeSubtitles, summarizer: FakeSummarizer) -> FilmService:
    engine = make_engine("sqlite://")
    Base.metadata.create_all(engine)
    return FilmService(
        sessions=make_session_factory(engine),
        catalog=FakeCatalog(),
        subtitles=subtitles,
        summarizer=summarizer,
        model_name="claude-test",
    )


@pytest.fixture
def client(service: FilmService) -> TestClient:
    settings = Settings(database_url="sqlite://", admin_password=ADMIN_PASSWORD)
    return TestClient(create_app(settings, service))


@pytest.fixture
def admin(client: TestClient) -> TestClient:
    response = client.post("/api/admin/session", json={"password": ADMIN_PASSWORD})
    assert response.status_code == 200
    return client
