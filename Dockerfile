# Image unique : l'API FastAPI sert aussi le build React. Un seul conteneur, un seul commit
# déployé, pas de CORS.
#
# Aucun secret n'entre ici : jamais d'`ARG X` suivi d'`ENV X=${X}` pour une valeur
# sensible, elle deviendrait lisible par quiconque tire l'image. Les clés (TMDB,
# OpenSubtitles, Anthropic, admin, base) sont injectées au runtime par Coolify.

# --- 1. Le front ----------------------------------------------------------------------
FROM node:22-bookworm-slim AS web
WORKDIR /web
COPY webapp/package.json webapp/package-lock.json ./
RUN npm ci
COPY webapp/ ./
RUN npm run build

# --- 2. Le runtime Python -------------------------------------------------------------
FROM python:3.12-slim-bookworm AS runtime
COPY --from=ghcr.io/astral-sh/uv:0.11.13 /uv /usr/local/bin/uv

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project
COPY src/ ./src/
RUN uv sync --frozen --no-dev

COPY --from=web /web/dist ./webapp

RUN useradd --create-home --uid 10001 app
USER app

ARG MOVIEPLOT_COMMIT_SHA=""
LABEL org.opencontainers.image.revision="${MOVIEPLOT_COMMIT_SHA}" \
      org.opencontainers.image.source="https://github.com/qhn-co/movie-plot-tool"
ENV MOVIEPLOT_COMMIT_SHA="${MOVIEPLOT_COMMIT_SHA}" \
    MOVIEPLOT_WEBAPP_DIST=/app/webapp

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=4)"

# Les migrations passent avant le démarrage : un schéma en retard fait échouer le
# conteneur au lieu de servir des erreurs.
CMD ["sh", "-c", "movieplot migrate && exec uvicorn movieplot.api.app:create_app --factory --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips='*'"]
