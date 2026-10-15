"""Sous-titres OpenSubtitles, ramenés à du texte brut en mémoire.

On cherche par identifiant IMDb quand TMDB le fournit, pour résumer le bon film et pas un
homonyme. Rien n'est écrit sur disque. L'API utilisée est l'ancienne API XML-RPC ; son
remplacement par l'API REST est un chantier suivant.
"""

from __future__ import annotations

import base64
import gzip
import logging
import re
from typing import Any, Protocol
from xmlrpc.client import ServerProxy

log = logging.getLogger(__name__)

XMLRPC_URL = "https://api.opensubtitles.org/xml-rpc"
USER_AGENT = "movieplot v0.1"

_TIMESTAMP = re.compile(r"^\d{2}:\d{2}:\d{2}[,.]\d{3}\s*-->")
_TAG = re.compile(r"<[^>]+>|\{[^}]*\}")


class SubtitleSource(Protocol):
    def fetch_text(self, *, imdb_id: str | None, title: str) -> str | None: ...


def srt_to_text(raw: bytes) -> str:
    """Retire numéros, horodatages et balises d'un fichier SRT, garde les répliques."""
    try:
        content = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        content = raw.decode("latin-1")
    lines = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.isdigit() or _TIMESTAMP.match(line):
            continue
        lines.append(_TAG.sub("", line))
    return "\n".join(lines)


def decode_payload(data: str) -> bytes:
    """Décode la charge renvoyée par DownloadSubtitles : base64, souvent gzippée."""
    content = base64.b64decode(data)
    if content.startswith(b"\x1f\x8b"):
        content = gzip.decompress(content)
    return content


class OpenSubtitlesXmlRpc:
    def __init__(self, username: str, password: str, server: Any | None = None) -> None:
        self._username = username
        self._password = password
        self._server: Any = server or ServerProxy(XMLRPC_URL)

    def fetch_text(self, *, imdb_id: str | None, title: str) -> str | None:
        login = self._server.LogIn(self._username, self._password, "en", USER_AGENT)
        token = login.get("token")
        if not token:
            log.warning("Connexion OpenSubtitles refusée : %s", login.get("status"))
            return None
        query: dict[str, str] = {"sublanguageid": "eng"}
        if imdb_id:
            query["imdbid"] = imdb_id.removeprefix("tt")
        else:
            query["query"] = title
        found = self._server.SearchSubtitles(token, [query]).get("data") or []
        if not found:
            return None
        downloaded = self._server.DownloadSubtitles(token, [found[0]["IDSubtitleFile"]])
        files = downloaded.get("data") or []
        if not files:
            return None
        return srt_to_text(decode_payload(files[0]["data"]))
