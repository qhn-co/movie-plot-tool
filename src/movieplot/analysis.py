"""Le contenu éditorial d'une fiche, tel que Claude le produit et tel qu'il est stocké."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Analysis(BaseModel):
    synopsis: str = Field(description="Prémisse du film, en un paragraphe, sans révéler la fin.")
    timeline: list[str] = Field(
        description="Entre 5 et 10 étapes clés de l'intrigue, dans l'ordre chronologique."
    )
    ending: str = Field(description="Comment l'histoire se résout, fin comprise.")
    meta_analysis: str = Field(
        description="Thèmes, symboles, évolution des personnages, lecture critique."
    )
