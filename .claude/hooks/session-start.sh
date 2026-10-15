#!/bin/bash
# Prépare une session Claude Code cloud : dépendances Python et front, pour que
# `make check` tourne dès le départ. N'écrit jamais un fichier suivi par git
# (`npm ci` et `uv sync --frozen` respectent les verrous), et chaque étape échoue seule.
set -uo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}" || exit 0

uv sync --frozen --all-groups || echo "[session-start] uv sync a échoué"
(cd webapp && npm ci) || echo "[session-start] npm ci a échoué"
exit 0
