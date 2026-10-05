"""Rendu Markdown annote pour relecture humaine (FR-008, SC-004).

Un titre par chunk, ses metadonnees en liste, son texte integral dans
un bloc. Aucun horodatage : le rendu est deterministe (SC-005).
"""

from math import ceil

from .models import Chunk, DocumentSource

RATIO_CHARS_PER_TOKEN = 4


def estimate_tokens(text: str) -> int:
    """Estimation de tokens d'un texte (FR-T02, FR-T06).

    Heuristique locale deterministe : division de la longueur par le
    ratio constant, arrondi superieur (penche du cote du risque).
    Approximative et modele-agnostique ; contrainte data-model
    (feature 002) : ratio entier, strictement positif, modifiable
    dans le code uniquement, sans parametre d'interface en v1.
    """
    return ceil(len(text) / RATIO_CHARS_PER_TOKEN)


def build_review(doc: DocumentSource, chunks: list[Chunk]) -> str:
    """Construit le contenu du fichier review.md d'un document."""
    lines = [f"# Decoupage : {doc.title or doc.path.name}"]
    lines.append(
        "> Tokens estimes a ~"
        f"{RATIO_CHARS_PER_TOKEN} caracteres par token : approximation "
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
        lines.append(f"- tokens (estimation) : ≈ {estimate_tokens(chunk.text)}")
        lines.append("")
        lines.append("```")
        lines.append(chunk.text)
        lines.append("```")
        lines.append("")
    return "\n".join(lines)
