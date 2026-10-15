from conftest import INCEPTION, FakeSubtitles, FakeSummarizer

from movieplot.service import FilmService


def test_generate_creates_unpublished_film(service: FilmService) -> None:
    film = service.generate(INCEPTION.tmdb_id)
    assert film.title == "Inception"
    assert film.published is False
    assert film.had_subtitles is True
    assert film.analysis["ending"] == "La toupie tourne."


def test_subtitles_are_searched_by_imdb_id(service: FilmService, subtitles: FakeSubtitles) -> None:
    service.generate(INCEPTION.tmdb_id)
    assert subtitles.calls == [("tt1375666", "Inception")]


def test_subtitle_outage_still_produces_a_film(
    service: FilmService, subtitles: FakeSubtitles, summarizer: FakeSummarizer
) -> None:
    subtitles.fail = True
    film = service.generate(INCEPTION.tmdb_id)
    assert film.had_subtitles is False
    assert summarizer.received == [None]


def test_regenerate_keeps_publication_and_single_row(service: FilmService) -> None:
    first = service.generate(INCEPTION.tmdb_id)
    service.set_published(first.id, True)
    second = service.generate(INCEPTION.tmdb_id)
    assert second.id == first.id
    assert second.published is True
    assert len(service.list_films(published_only=False)) == 1


def test_public_listing_hides_drafts(service: FilmService) -> None:
    film = service.generate(INCEPTION.tmdb_id)
    assert service.list_films(published_only=True) == []
    service.set_published(film.id, True)
    assert [f.id for f in service.list_films(published_only=True)] == [film.id]
