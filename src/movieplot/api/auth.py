"""Accès admin : un mot de passe unique, une session signée dans un cookie.

Le cookie est `SameSite=Strict` (aucune requête d'un autre site ne le porte, ce qui couvre
le CSRF) et `Secure` hors développement. Les échecs de connexion sont comptés par adresse
cliente ; derrière un proxy, l'adresse est celle du proxy et le blocage devient global :
grossier, mais visible. Sans `ADMIN_PASSWORD`, la connexion est fermée.
"""

from __future__ import annotations

import hmac
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status

MAX_FAILURES = 5
FAILURE_WINDOW_SECONDS = 15 * 60
SESSION_KEY = "admin"


class LoginThrottle:
    def __init__(self, max_failures: int = MAX_FAILURES, window: float = FAILURE_WINDOW_SECONDS):
        self._max = max_failures
        self._window = window
        self._failures: dict[str, deque[float]] = defaultdict(deque)

    def _recent(self, key: str, now: float) -> deque[float]:
        failures = self._failures[key]
        while failures and now - failures[0] > self._window:
            failures.popleft()
        return failures

    def is_blocked(self, key: str) -> bool:
        return len(self._recent(key, time.monotonic())) >= self._max

    def record_failure(self, key: str) -> None:
        self._recent(key, time.monotonic()).append(time.monotonic())

    def reset(self, key: str) -> None:
        self._failures.pop(key, None)


def password_matches(expected: str, given: str) -> bool:
    if not expected:
        return False
    return hmac.compare_digest(expected.encode(), given.encode())


def require_admin(request: Request) -> None:
    if request.session.get(SESSION_KEY) is not True:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Connexion admin requise")
