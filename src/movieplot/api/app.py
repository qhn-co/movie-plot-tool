"""Assemblage de l'application FastAPI : API, session admin et fichiers du front."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from movieplot.api.auth import LoginThrottle
from movieplot.api.routes import admin, public, session_router
from movieplot.config import Settings
from movieplot.db.session import make_engine, make_session_factory
from movieplot.service import FilmService
from movieplot.subtitles import OpenSubtitlesXmlRpc
from movieplot.summarizer import ClaudeSummarizer
from movieplot.tmdb import TmdbClient

SESSION_MAX_AGE = 7 * 24 * 3600


def build_service(settings: Settings) -> FilmService:
    engine = make_engine(settings.database_url)
    return FilmService(
        sessions=make_session_factory(engine),
        catalog=TmdbClient(settings.tmdb_api_key),
        subtitles=OpenSubtitlesXmlRpc(
            settings.opensubtitles_username, settings.opensubtitles_password
        ),
        summarizer=ClaudeSummarizer(settings.claude_model),
        model_name=settings.claude_model,
    )


def create_app(settings: Settings | None = None, service: FilmService | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    settings.validate()
    app = FastAPI(title="Movie Plot", docs_url=None if settings.is_deployed else "/api/docs")
    app.state.settings = settings
    app.state.service = service or build_service(settings)
    app.state.throttle = LoginThrottle()
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.session_secret,
        session_cookie="movieplot_admin",
        max_age=SESSION_MAX_AGE,
        same_site="strict",
        https_only=settings.is_deployed,
    )
    app.include_router(public)
    app.include_router(session_router)
    app.include_router(admin)
    if settings.webapp_dist:
        _serve_webapp(app, settings.webapp_dist)
    return app


def _serve_webapp(app: FastAPI, dist: Path) -> None:
    """Sert le build Vite ; toute route inconnue hors `/api` rend `index.html` (routage SPA)."""
    index = dist / "index.html"
    app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str) -> FileResponse:
        if path.startswith("api/"):
            raise HTTPException(404)
        candidate = (dist / path).resolve()
        if path and candidate.is_file() and candidate.is_relative_to(dist.resolve()):
            return FileResponse(candidate)
        return FileResponse(index)
