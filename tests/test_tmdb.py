import httpx

from movieplot.tmdb import CastMember, TmdbClient

DETAILS = {
    "id": 603,
    "imdb_id": "tt0133093",
    "title": "Matrix",
    "original_title": "The Matrix",
    "release_date": "1999-03-31",
    "overview": "Un pirate découvre la vérité.",
    "poster_path": "/matrix.jpg",
    "vote_average": 8.2,
    "credits": {
        "crew": [
            {"name": "Lana Wachowski", "job": "Director"},
            {"name": "Lilly Wachowski", "job": "Director"},
            {"name": "Joel Silver", "job": "Producer"},
        ],
        "cast": [
            {"name": f"Acteur {i}", "character": f"Rôle {i}", "order": i}
            for i in (6, 0, 3, 1, 2, 5, 4)
        ],
    },
}


def test_details_reads_director_and_top_cast() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json=DETAILS)

    http = httpx.Client(base_url="https://tmdb.test", transport=httpx.MockTransport(handler))
    movie = TmdbClient("cle", http=http).details(603)

    assert seen[0].url.params["append_to_response"] == "credits"
    assert movie.director == "Lana Wachowski, Lilly Wachowski"
    assert movie.cast == tuple(CastMember(f"Acteur {i}", f"Rôle {i}") for i in range(5))
    assert movie.poster_url == "https://image.tmdb.org/t/p/w500/matrix.jpg"
