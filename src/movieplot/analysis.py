"""Le contenu éditorial d'une fiche, tel que Claude le produit et tel qu'il est stocké.

La fiche sert à se rappeler un film et à savoir si on l'a vu : les repères de mémoire
viennent avant l'intrigue, et la fin reste à part pour pouvoir être masquée.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Analysis(BaseModel):
    hook: str = Field(
        description="Une phrase qui commence par « Le film où… » et suffit à identifier le film."
    )
    memory_cues: list[str] = Field(
        description=(
            "Entre 5 et 8 scènes, images ou répliques marquantes, une phrase chacune, "
            "sans révéler la fin."
        )
    )
    synopsis: str = Field(description="Prémisse du film, en un paragraphe, sans révéler la fin.")
    timeline: list[str] = Field(
        description="Entre 5 et 10 étapes de l'intrigue, dans l'ordre, sans la fin."
    )
    ending: str = Field(description="Comment l'histoire se résout, en un paragraphe.")
    context: str = Field(
        description="Deux ou trois phrases : succès, suites ou remakes, ce qui a marqué."
    )
