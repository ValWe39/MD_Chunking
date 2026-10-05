"""Rendu Markdown annote pour relecture humaine (FR-008, SC-004).

Un titre par chunk, ses metadonnees en liste, son texte integral dans
un bloc. Aucun horodatage : le rendu est deterministe (SC-005).
"""

from fractions import Fraction
from math import ceil

from .models import Chunk, DocumentSource

DEFAULT_RATIO_CHARS_PER_TOKEN = 3.5


def estimate_tokens(text: str, ratio: float = DEFAULT_RATIO_CHARS_PER_TOKEN) -> int:
    """Estimation de tokens d'un texte (FR-001, FR-005 de la feature 004).

    Heuristique locale deterministe : division de la longueur du texte
    par le ratio, arrondi superieur (penche du cote du risque).
    Division exacte via Fraction construite depuis la representation
    decimale du ratio : aucun artefact binaire aux frontieres
    (research.md D2, feature 004). Approximative et modele-agnostique ;
    le ratio est transitoire, jamais stocke ni serialise (FR-008).
    """
    return ceil(Fraction(len(text)) / Fraction(str(ratio)))


def build_review(
    doc: DocumentSource,
    chunks: list[Chunk],
    ratio: float = DEFAULT_RATIO_CHARS_PER_TOKEN,
) -> str:
    """Construit le contenu du fichier review.md d'un document."""
    lines = [f"# Decoupage : {doc.title or doc.path.name}"]
    lines.append(
        "> Tokens estimes a ~"
        f"{ratio:.1f} caracteres par token : approximation "
        "locale, independante de tout modele d'embedding."
    )
    lines.append("")
    for chunk in chunks:
        header = f"## Chunk {chunk.ref} — {chunk.length} car."
        lines.append(header)
        lines.append("")
        lines.append(f"- frontiere : {chunk.boundary}")
        if chunk.part is not None:
            lines.append(f"- partie : {chunk.part}")
        if chunk.page is not None:
            lines.append(f"- page : {chunk.page}")
        if chunk.position_in_part is not None:
            lines.append(f"- position dans la partie : {chunk.position_in_part}")
        if chunk.atomic:
            lines.append("- entite atomique (bloc code ou tableau)")
        lines.append(f"- tokens (estimation) : ≈ {estimate_tokens(chunk.text, ratio)}")
        lines.append("")
        lines.append("```")
        lines.append(chunk.text)
        lines.append("```")
        lines.append("")
    return "\n".join(lines)
