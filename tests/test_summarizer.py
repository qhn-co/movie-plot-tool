from conftest import INCEPTION

from movieplot.summarizer import build_prompt


def test_prompt_carries_full_subtitles() -> None:
    long_text = "réplique\n" * 20_000
    assert long_text in build_prompt(INCEPTION, long_text)


def test_prompt_without_subtitles_says_so() -> None:
    assert "Aucun sous-titre" in build_prompt(INCEPTION, None)


def test_prompt_names_director_and_cast() -> None:
    prompt = build_prompt(INCEPTION, None)
    assert "réalisé par Christopher Nolan" in prompt
    assert "Avec : Leonardo DiCaprio (Dom Cobb), Elliot Page (Ariadne)" in prompt
