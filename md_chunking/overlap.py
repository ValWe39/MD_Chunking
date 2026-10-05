"""Overlap structurel entre chunks (FR-005, decision D6 ; bug
chunking-quotes-words, regles 2 et 3).

L'overlap est preleve dans la queue du chunk precedent, coupee a une
frontiere (paragraphe si possible, sinon phrase, sinon mots en dernier
recours) ; il est limite a ``overlap_pct`` % du chunk et n'est applique
qu'entre chunks d'une meme partie. Les fenetres entierement redondantes
sont filtrees (decision D2, contournement du bug haystack #12686 :
jamais de chunk compose uniquement d'overlap deja couvert).

Regles du bug chunking-quotes-words :
- regle 2 : une queue coupee en pleine phrase ou en pleine citation
  porte le marqueur ``...``, compte dans le budget du receveur ;
- regle 3 : sans frontiere de phrase dans la fenetre cible, la queue
  descend aux frontieres de mots ; une queue plus courte que
  ``_MIN_TAIL`` caracteres est inutile et remplacee.
"""

from .models import Chunk
from .presets import Preset
from .splitter import MARKER, english_quote_count, quote_balance

_MIN_TAIL = 30  # caracteres minimum d'une queue d'overlap utile


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


def _word_tail(text: str, target: int) -> str | None:
    """Derniers mots complets de ``text`` tenant dans ``target``
    caracteres (dernier recours, regle 3)."""
    if target <= 0 or len(text) <= target:
        return None
    out: list[str] = []
    n = 0
    for w in reversed(text.split()):
        add = len(w) + (1 if out else 0)
        if n + add > target:
            break
        out.insert(0, w)
        n += add
    return " ".join(out) if out else None


def apply_overlap(chunks: list[Chunk], preset: Preset) -> list[Chunk]:
    """Applique l'overlap entre chunks consecutifs d'une meme partie.

    Le chunk receveur reste dans la fourchette : l'overlap est rogne
    pour ne jamais depasser ``chunk_max``, separateur et marqueurs
    compris.
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
        budget = preset.chunk_max - chunk.length - 2 - 2 * len(MARKER)
        target = min(target, budget)
        source = prev.text
        source = source.removesuffix(MARKER)
        tail = _tail_at_boundary(source, target)
        from_words = False
        if not tail or len(tail) < _MIN_TAIL:
            # dernier recours : frontieres de mots (regle 3)
            tail = _word_tail(source, target)
            from_words = True
        if not tail or len(tail) < _MIN_TAIL or tail in chunk.text:
            # fenetre vide, inutile ou deja entierement couverte (D2)
            out.append(chunk)
            continue
        if from_words:
            # queue coupee en pleine phrase (regle 2)
            tail = MARKER + tail
        if preset.guillemets:
            src_bal = quote_balance(source)
            tail_bal = quote_balance(tail)
            src_open = english_quote_count(source) % 2 == 1
            tail_open = english_quote_count(tail) % 2 == 1
            if not from_words and (
                (src_bal - tail_bal) > 0 or (src_open and not tail_open)
            ):
                # queue demarree en pleine citation (regle 1 etendue
                # a l'overlap : le fermant reste rattache a son extrait)
                tail = MARKER + tail
            if src_bal > 0 or src_open:
                # citation laissee ouverte en fin de chunk precedent
                tail = tail + MARKER
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
