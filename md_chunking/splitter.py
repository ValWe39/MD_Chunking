"""Decoupage structurel : sections, paragraphes, phrases (FR-002 a FR-004).

Socle : ``MarkdownHeaderSplitter`` de haystack-ai (decision D1) pour le
decoupage par titres avec hierarchie en metadonnees. L'occupation
maximale (heuristique gloutonne, FR-004) et les unites atomiques (blocs
de code, tableaux) sont gerees ici, en caracteres (FR-002).
"""

import re

from haystack import Document
from haystack.components.preprocessors import MarkdownHeaderSplitter

from .models import Chunk, DocumentSource
from .presets import Preset

PAGE_BREAK = "\x0c"
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?…])\s+")
_FENCE_LINE = re.compile(r"^\s*```")
_TABLE_LINE = re.compile(r"^\s*\|")

_SPLITTER = MarkdownHeaderSplitter(keep_headers=True, secondary_split=None)


def _is_atomic(block: str) -> bool:
    """Bloc indivisible par nature : cloture de code ou tableau."""
    return bool(_FENCE_LINE.match(block) or _TABLE_LINE.match(block))


def _units(text: str) -> list[tuple[str, bool]]:
    """Decoupe une section en unites (texte, atomicite).

    Les blocs de code fences et les tableaux sont atomiques : jamais
    coupes en leur sein (edge case spec). Les paragraphes sont
    decoupables en phrases en dernier recours.
    """
    units: list[tuple[str, bool]] = []
    paragraph: list[str] = []
    fence: list[str] = []
    in_fence = False
    for line in text.split("\n"):
        if _FENCE_LINE.match(line):
            if in_fence:
                fence.append(line)
                units.append(("\n".join(fence), True))
                fence = []
                in_fence = False
            else:
                if paragraph:
                    units.append(("\n".join(paragraph), False))
                    paragraph = []
                fence = [line]
                in_fence = True
        elif in_fence:
            fence.append(line)
        elif line.strip():
            paragraph.append(line)
        elif paragraph:
            units.append(("\n".join(paragraph), False))
            paragraph = []
    if in_fence and fence:
        units.append(("\n".join(fence), True))
    if paragraph:
        units.append(("\n".join(paragraph), False))
    return [(b, a or _is_atomic(b)) for b, a in units]


def _split_sentences(text: str) -> list[str]:
    return [s for s in _SENTENCE_SPLIT.split(text) if s.strip()]


def _group(texts: list[str], boundary: str, atomic: bool = False) -> dict:
    return {"texts": texts, "boundary": boundary, "atomic": atomic}


def _size(group: dict) -> int:
    texts = group["texts"]
    if not texts:
        return 0
    return sum(len(t) for t in texts) + 2 * (len(texts) - 1)


def _pack(items: list[str], boundary: str, p: Preset) -> list[dict]:
    """Regroupe gloutonnement des blocets en chunks <= chunk_max."""
    out: list[dict] = []
    buf: list[str] = []
    buf_len = 0
    for text in items:
        size = len(text)
        if buf and buf_len + 2 + size > p.chunk_max:
            out.append(_group(buf, boundary))
            buf, buf_len = [], 0
        if buf:
            buf.append(text)
            buf_len += 2 + size
        else:
            buf = [text]
            buf_len = size
    if buf:
        out.append(_group(buf, boundary))
    return out


def _sentence_packs(text: str, p: Preset) -> list[dict]:
    """Decoupe un paragraphe trop long en chunks de phrases (FR-003).

    Une phrase unique plus longue que chunk_max reste indivisible et
    est signalee atomique (pas de split dur au milieu d'une phrase).
    """
    sentences = _split_sentences(text)
    packs: list[dict] = []
    for sentence in sentences:
        if len(sentence) > p.chunk_max:
            packs.append(_group([sentence], "phrase", atomic=True))
    sentences = [s for s in sentences if len(s) <= p.chunk_max]
    packs.extend(_pack(sentences, "phrase", p))
    return packs


def _fill(units: list[tuple[str, bool]], p: Preset, single_boundary: str) -> list[dict]:
    """Produit les chunks d'une section avec occupation maximale.

    - la section entiere tenant dans la fourchette donne un chunk unique
      de niveau section (FR-003, priorite aux sections) ;
    - sinon remplissage glouton des paragraphes (FR-004) ;
    - un tampon trop court est complete par le debut du paragraphe
      suivant, descendu en phrases si besoin (jamais de chunk sous
      chunk_min quand un decoupage coherent reste possible) ;
    - les unites atomiques (code, tableaux) ne sont ni coupees ni
      fusionnees au-dela de chunk_max, et sont signalees.
    """
    if not units:
        return []
    total = sum(len(t) for t, _ in units) + 2 * (len(units) - 1)
    if total <= p.chunk_max:
        return [_group([t for t, _ in units], single_boundary)]

    groups: list[dict] = []
    buf = _group([], "paragraphe")
    for text, atomic in units:
        if atomic:
            if buf["texts"]:
                groups.append(buf)
                buf = _group([], "paragraphe")
            groups.append(_group([text], "paragraphe", atomic=True))
            continue
        if len(text) > p.chunk_max:
            if buf["texts"]:
                groups.append(buf)
                buf = _group([], "paragraphe")
            groups.extend(_sentence_packs(text, p))
            continue
        buf_len = _size(buf)
        if buf["texts"] and buf_len + 2 + len(text) > p.chunk_max:
            if buf_len < p.chunk_min:
                # completer le chunk court avec le debut du paragraphe
                # suivant, descendu en phrases (dernier recours)
                sentences = _split_sentences(text)
                rest: list[str] = []
                for sentence in sentences:
                    if _size(buf) + 2 + len(sentence) <= p.chunk_max:
                        buf["texts"].append(sentence)
                    else:
                        rest.append(sentence)
                groups.append(buf)
                buf = _group([], "paragraphe")
                if rest:
                    groups.extend(_pack(rest, "phrase", p))
            else:
                groups.append(buf)
                buf = _group([text], "paragraphe")
        elif buf["texts"]:
            buf["texts"].append(text)
        else:
            buf = _group([text], "paragraphe")
    if buf["texts"]:
        groups.append(buf)
    return _repair(groups, p)


def _steal_sentences_from_prev(prev: dict, g: dict, p: Preset) -> None:
    """Deplace des phrases de la queue de la derniere unite du
    precedent vers g, le precedent restant >= chunk_min."""
    if not prev["texts"]:
        return
    sentences = _split_sentences(prev["texts"][-1])
    if len(sentences) < 2:
        return
    kept_head = prev["texts"][:-1]
    while sentences:
        kept = _group(kept_head + sentences[:-1], "phrase")
        if _size(kept) < p.chunk_min:
            break  # le donneur ne peut plus rien ceder proprement
        cand = sentences[-1]
        if _size(g) + 2 + len(cand) > p.chunk_max:
            break
        g["texts"].insert(0, sentences.pop())
        g["boundary"] = "phrase"
        if _size(g) >= p.chunk_min:
            break
    prev["texts"] = kept_head + sentences
    if len(sentences) > 1 or kept_head:
        prev["boundary"] = "phrase"


def _steal_sentences_from_next(nxt: dict, g: dict, p: Preset) -> None:
    """Deplace des phrases de la tete de la premiere unite du suivant
    vers g, le suivant restant >= chunk_min."""
    if not nxt["texts"]:
        return
    sentences = _split_sentences(nxt["texts"][0])
    if len(sentences) < 2:
        return
    kept_tail = nxt["texts"][1:]
    while sentences:
        kept = _group(sentences[1:] + kept_tail, "phrase")
        if _size(kept) < p.chunk_min:
            break
        cand = sentences[0]
        if _size(g) + 2 + len(cand) > p.chunk_max:
            break
        g["texts"].append(sentences.pop(0))
        g["boundary"] = "phrase"
        if _size(g) >= p.chunk_min:
            break
    nxt["texts"] = sentences + kept_tail
    if len(sentences) > 1 or kept_tail:
        nxt["boundary"] = "phrase"


def _repair(groups: list[dict], p: Preset) -> list[dict]:
    """Repare les chunks trop courts (SC-001) sans jamais couper une
    phrase ni une unite atomique : fusion dans le precedent si le
    total tient, sinon vol d'unites entieres, sinon vol de phrases --
    chaque donneur restant lui-meme >= chunk_min."""
    out: list[dict] = []
    i = 0
    while i < len(groups):
        g = groups[i]
        if g["atomic"] or _size(g) >= p.chunk_min:
            out.append(g)
            i += 1
            continue
        # 1. fusion dans le precedent si le total tient
        if (
            out
            and not out[-1]["atomic"]
            and _size(out[-1]) + 2 + _size(g) <= p.chunk_max
        ):
            out[-1]["texts"].extend(g["texts"])
            i += 1
            continue
        # 2. vol depuis le precedent : unites entieres puis phrases
        if out and not out[-1]["atomic"] and out[-1]["texts"]:
            prev = out[-1]
            while (
                _size(g) < p.chunk_min
                and len(prev["texts"]) >= 2
                and _size(_group(prev["texts"][:-1], "paragraphe")) >= p.chunk_min
                and _size(g) + 2 + len(prev["texts"][-1]) <= p.chunk_max
            ):
                g["texts"].insert(0, prev["texts"].pop())
            if _size(g) < p.chunk_min:
                _steal_sentences_from_prev(prev, g, p)
            if _size(g) >= p.chunk_min:
                out.append(g)
                i += 1
                continue
        # 3. vol depuis le suivant : unites entieres puis phrases
        if i + 1 < len(groups):
            nxt = groups[i + 1]
            if not nxt["atomic"] and nxt["texts"]:
                while (
                    _size(g) < p.chunk_min
                    and len(nxt["texts"]) >= 2
                    and _size(_group(nxt["texts"][1:], "paragraphe")) >= p.chunk_min
                    and _size(g) + 2 + len(nxt["texts"][0]) <= p.chunk_max
                ):
                    g["texts"].append(nxt["texts"].pop(0))
                if _size(g) < p.chunk_min:
                    _steal_sentences_from_next(nxt, g, p)
        out.append(g)
        i += 1
    return out


def _part_of(meta: dict) -> str | None:
    header = meta.get("header")
    if header is None:
        return None
    parents = meta.get("parent_headers") or []
    return " > ".join([*parents, header])


def _section_pages(doc: DocumentSource, sections: list[str]) -> list[int | None]:
    """Page de chaque section : 1 + nombre de sauts de page avant son
    debut ; None si le document ne contient aucun saut de page balise."""
    if PAGE_BREAK not in doc.normalized_content:
        return [None] * len(sections)
    pages: list[int | None] = []
    pos = 0
    for text in sections:
        idx = doc.normalized_content.find(text, pos)
        if idx < 0:
            idx = pos
        pages.append(1 + doc.normalized_content.count(PAGE_BREAK, 0, idx))
        pos = idx + max(len(text), 1)
    return pages


def split_document(doc: DocumentSource, preset: Preset) -> list[Chunk]:
    """Decoupe un document en chunks conformes a la fourchette du preset.

    Ordre de priorite FR-003 : sections Markdown si disponibles, sinon
    paragraphes, sinon phrases en dernier recours.
    """
    if doc.structure == "sections":
        result = _SPLITTER.run(documents=[Document(content=doc.normalized_content)])
        sections = [(d.content, _part_of(d.meta)) for d in result["documents"]]
        single_boundary = "section"
    else:
        sections = [(doc.normalized_content, None)]
        single_boundary = "paragraphe" if doc.structure == "paragraphes" else "phrase"

    pages = _section_pages(doc, [t for t, _ in sections])

    raw: list[dict] = []
    for (text, part), page in zip(sections, pages):
        for group in _fill(_units(text), preset, single_boundary):
            raw.append({**group, "part": part, "page": page})

    chunks: list[Chunk] = []
    by_part: dict[str | None, list[int]] = {}
    for i, g in enumerate(raw):
        ref = i + 1
        chunks.append(
            Chunk(
                ref=ref,
                text="\n\n".join(g["texts"]),
                boundary=g["boundary"],
                part=g["part"],
                page=g["page"],
                atomic=g["atomic"],
            )
        )
        by_part.setdefault(g["part"], []).append(ref)

    for part, refs in by_part.items():
        if len(refs) > 1:
            for position, ref in enumerate(refs, start=1):
                chunks[ref - 1].position_in_part = position

    return chunks
