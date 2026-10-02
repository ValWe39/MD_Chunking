"""Overlap structurel entre chunks (FR-005, decision D6).

L'overlap est preleve dans la queue du chunk precedent, coupee a une
frontiere (paragraphe si possible, sinon phrase) ; il est limite a
``overlap_pct`` % du chunk et n'est applique qu'entre chunks d'une meme
partie. Les fenetres entierement redondantes sont filtrees (decision D2,
contournement du bug haystack #12686 : jamais de chunk compose
uniquement d'overlap deja couvert).
"""

from .models import Chunk
from .presets import Preset


def _tail_at_boundary(text: str, target: int) -> str | None:
    """Queue de ``text`` d'au plus ``target`` caracteres, coupee a la
    derniere frontiere de paragraphe, sinon de phrase."""
    if target <= 0 or len(text) <= target:
        return None
    # derniere frontiere de paragraphe dans la fenetre cible
    window = text[-target - 1 :]
    cut = window.rfind("\n\n")
    if cut >= 0:
        return window[cut + 2 :]
    # sinon frontiere de phrase
    import re

    last = None
    for m in re.finditer(r"(?<=[.!?…])\s+", window):
        last = m
    if last is not None and last.end() < len(window):
        return window[last.end() :]
    return None


def apply_overlap(chunks: list[Chunk], preset: Preset) -> list[Chunk]:
    """Applique l'overlap entre chunks consecutifs d'une meme partie.

    Le chunk receveur reste dans la fourchette : l'overlap est rogne
    pour ne jamais depasser ``chunk_max``.
    """
    if preset.overlap_pct <= 0:
        return chunks
    out: list[Chunk] = []
    for i, chunk in enumerate(chunks):
        if i == 0 or chunk.part != chunks[i - 1].part:
            out.append(chunk)
            continue
        prev = chunks[i - 1]
        target = round(prev.length * preset.overlap_pct / 100)
        budget = preset.chunk_max - chunk.length - 2
        target = min(target, budget)
        tail = _tail_at_boundary(prev.text, target)
        if not tail or tail in chunk.text:
            # fenetre vide ou deja entierement couverte (decision D2)
            out.append(chunk)
            continue
        out.append(
            Chunk(
                ref=chunk.ref,
                text=f"{tail}\n\n{chunk.text}",
                boundary=chunk.boundary,
                part=chunk.part,
                page=chunk.page,
                position_in_part=chunk.position_in_part,
                atomic=chunk.atomic,
            )
        )
    return out
