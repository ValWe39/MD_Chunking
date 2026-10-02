"""Rendu Markdown annote pour relecture humaine (FR-008, SC-004).

Un titre par chunk, ses metadonnees en liste, son texte integral dans
un bloc. Aucun horodatage : le rendu est deterministe (SC-005).
"""

from .models import Chunk, DocumentSource


def build_review(doc: DocumentSource, chunks: list[Chunk]) -> str:
    """Construit le contenu du fichier review.md d'un document."""
    lines = [f"# Decoupage : {doc.title or doc.path.name}", ""]
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
        lines.append("")
        lines.append("```")
        lines.append(chunk.text)
        lines.append("```")
        lines.append("")
    return "\n".join(lines)
