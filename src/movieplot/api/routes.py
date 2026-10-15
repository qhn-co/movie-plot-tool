"""Routes de l'API : lecture publique des fiches publiées, gestion réservée à l'admin."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from movieplot.api.auth import SESSION_KEY, LoginThrottle, password_matches, require_admin
from movieplot.api.schemas import (
    AdminFilm,
    FilmCard,
    FilmPage,
    FilmUpdate,
    GenerateRequest,
    LoginRequest,
    SessionState,
    TmdbResult,
)
from movieplot.config import Settings
from movieplot.service import FilmNotFound, FilmService

log = logging.getLogger(__name__)

public = APIRouter(prefix="/api")
admin = APIRouter(prefix="/api/admin", dependencies=[Depends(require_admin)])
session_router = APIRouter(prefix="/api/admin/session")


def service(request: Request) -> FilmService:
    return request.app.state.service


def settings(request: Request) -> Settings:
    return request.app.state.settings


def throttle(request: Request) -> LoginThrottle:
    return request.app.state.throttle


@public.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@public.get("/version")
def version(cfg: Settings = Depends(settings)) -> dict[str, str]:
    return {"commit": cfg.commit_sha or "dev"}


@public.get("/films", response_model=list[FilmCard])
def list_films(svc: FilmService = Depends(service)) -> list:
    return svc.list_films(published_only=True)


@public.get("/films/{film_id}", response_model=FilmPage)
def get_film(film_id: int, svc: FilmService = Depends(service)) -> object:
    try:
        return svc.get_film(film_id, published_only=True)
    except FilmNotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Fiche introuvable") from None


@session_router.get("", response_model=SessionState)
def session_state(request: Request) -> SessionState:
    return SessionState(authenticated=request.session.get(SESSION_KEY) is True)


@session_router.post("", response_model=SessionState)
def login(
    body: LoginRequest,
    request: Request,
    cfg: Settings = Depends(settings),
    limiter: LoginThrottle = Depends(throttle),
) -> SessionState:
    if not cfg.admin_password:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Accès admin non configuré")
    client = request.client.host if request.client else "inconnu"
    if limiter.is_blocked(client):
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Trop de tentatives, réessayez plus tard")
    if not password_matches(cfg.admin_password, body.password):
        limiter.record_failure(client)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Mot de passe incorrect")
    limiter.reset(client)
    request.session[SESSION_KEY] = True
    return SessionState(authenticated=True)


@session_router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request) -> Response:
    request.session.clear()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@admin.get("/tmdb/search", response_model=list[TmdbResult])
def tmdb_search(q: str, svc: FilmService = Depends(service)) -> list:
    if len(q.strip()) < 2:
        return []
    try:
        return svc.catalog.search(q.strip())
    except Exception:  # noqa: BLE001
        log.exception("Recherche TMDB en échec")
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "TMDB ne répond pas") from None


@admin.get("/films", response_model=list[AdminFilm])
def admin_list(svc: FilmService = Depends(service)) -> list:
    return svc.list_films(published_only=False)


@admin.post("/films", response_model=AdminFilm, status_code=status.HTTP_201_CREATED)
def generate(body: GenerateRequest, svc: FilmService = Depends(service)) -> object:
    try:
        return svc.generate(body.tmdb_id)
    except Exception:  # noqa: BLE001
        log.exception("Génération en échec pour TMDB %s", body.tmdb_id)
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY, "La génération a échoué, voir les journaux du serveur"
        ) from None


@admin.patch("/films/{film_id}", response_model=AdminFilm)
def update(film_id: int, body: FilmUpdate, svc: FilmService = Depends(service)) -> object:
    try:
        film = svc.get_film(film_id, published_only=False)
        if body.analysis is not None:
            film = svc.update_analysis(film_id, body.analysis)
        if body.published is not None:
            film = svc.set_published(film_id, body.published)
        return film
    except FilmNotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Fiche introuvable") from None


@admin.delete("/films/{film_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(film_id: int, svc: FilmService = Depends(service)) -> Response:
    try:
        svc.delete(film_id)
    except FilmNotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Fiche introuvable") from None
    return Response(status_code=status.HTTP_204_NO_CONTENT)
