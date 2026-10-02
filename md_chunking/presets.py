"""Presets par typologie (specs/001-md-chunking/data-model.md).

Valeurs par defaut modifiables (assumption de la spec) : les quatre
premiers reprennent les tailles de l'intake (overlap converti en
pourcentage), le cinquieme (livre) est une proposition maison ajoutee
a la suite de l'analyse des Exemples 3/4.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Preset:
    """Bornes d'un preset : tailles en caracteres, overlap en %."""

    name: str
    chunk_min: int
    chunk_max: int
    overlap_pct: int


PRESETS: dict[str, Preset] = {
    "documentation": Preset("documentation", 100, 1000, 15),
    "articles": Preset("articles", 150, 1500, 13),
    "conversations": Preset("conversations", 50, 500, 10),
    "code": Preset("code", 200, 2000, 15),
    "livre": Preset("livre", 150, 1200, 15),
}

DEFAULT_PRESET = "documentation"


def get_preset(name: str) -> Preset:
    """Retourne le preset demande ou echoue avec un message clair."""
    try:
        return PRESETS[name]
    except KeyError:
        connus = ", ".join(sorted(PRESETS))
        raise ValueError(
            f"typologie inconnue : {name} (typologies acceptees : {connus})"
        ) from None
