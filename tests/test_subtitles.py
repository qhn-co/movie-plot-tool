import base64
import gzip

from movieplot.subtitles import OpenSubtitlesXmlRpc, decode_payload, srt_to_text

SRT = b"""1
00:00:01,000 --> 00:00:03,000
<i>We need to go deeper.</i>

2
00:00:04,000 --> 00:00:06,000
Dreams feel real while we're in them.
"""


def test_srt_to_text_keeps_only_dialogue() -> None:
    assert srt_to_text(SRT) == "We need to go deeper.\nDreams feel real while we're in them."


def test_decode_payload_handles_gzip() -> None:
    payload = base64.b64encode(gzip.compress(SRT)).decode()
    assert decode_payload(payload) == SRT


class FakeServer:
    def __init__(self) -> None:
        self.queries: list[dict] = []

    def LogIn(self, *args: str) -> dict:  # noqa: N802
        return {"token": "t"}

    def SearchSubtitles(self, token: str, queries: list[dict]) -> dict:  # noqa: N802
        self.queries.extend(queries)
        return {"data": [{"IDSubtitleFile": "42"}]}

    def DownloadSubtitles(self, token: str, ids: list[str]) -> dict:  # noqa: N802
        return {"data": [{"data": base64.b64encode(gzip.compress(SRT)).decode()}]}


def test_search_uses_imdb_number_when_known() -> None:
    server = FakeServer()
    text = OpenSubtitlesXmlRpc("u", "p", server).fetch_text(imdb_id="tt1375666", title="Inception")
    assert server.queries == [{"sublanguageid": "eng", "imdbid": "1375666"}]
    assert text is not None and text.startswith("We need to go deeper.")
