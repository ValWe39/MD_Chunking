"""Tests unitaires de l'overlap : dernier recours aux mots, queue
minimale, marqueurs de coupure (bug chunking-quotes-words, regles 2
et 3)."""

from md_chunking.models import Chunk
from md_chunking.overlap import apply_overlap
from md_chunking.presets import Preset
from md_chunking.splitter import MARKER

P = Preset("test", 30, 1000, 15, True)


def _chunk(ref: int, text: str, part: str = "partie") -> Chunk:
    return Chunk(ref=ref, text=text, boundary="phrase", part=part)


def test_queue_aux_mots_quand_la_phrase_est_trop_longue():
    """Regle 3 : sans frontiere de phrase dans la fenetre, la queue
    descend aux mots ; regle 2 : coupure marquee « ... »."""
    longue = (
        "Une phrase tres longue sans aucune ponctuation intermediaire "
        + "avec des mots repetes " * 30
    )
    prev = _chunk(1, longue)
    cur = _chunk(2, "Contenu du chunk suivant avec du texte.")
    out = apply_overlap([prev, cur], P)
    assert out[1].text.startswith(MARKER)
    assert out[1].length <= P.chunk_max
    queue = out[1].text.split("\n\n")[0]
    assert len(queue) > len(MARKER) + 30
    assert prev.text.rstrip().endswith(queue[len(MARKER) :])


def test_queue_minuscule_remplacee():
    """Une queue trop courte (ex. fermant orphelin) est remplacee par
    une queue utile aux frontieres de mots."""
    corps = "Mots pour allonger ce chunk au-dela de la cible. " * 8
    prev = _chunk(1, corps + "\n\nFin courte. »")
    cur = _chunk(2, "Contenu du chunk suivant avec du texte.")
    out = apply_overlap([prev, cur], P)
    assert out[1].text.startswith(MARKER)
    assert not out[1].text.startswith("Fin courte. »\n\n")


def test_queue_normale_entiere_sans_marqueur():
    """Une queue calée sur une frontiere complete ne porte pas de
    marqueur de coupure."""
    unite1 = "Mots repetes pour remplir la premiere unite. " * 9
    unite2 = "Seconde unite du chunk precedent tout aussi longue que la premiere."
    prev = _chunk(1, unite1 + "\n\n" + unite2)
    cur = _chunk(2, "Contenu du chunk suivant avec du texte.")
    out = apply_overlap([prev, cur], P)
    assert MARKER not in out[1].text
    assert out[1].text == unite2 + "\n\n" + cur.text


def test_receveur_plein_ne_depasse_jamais_chunk_max():
    """Le budget reserve le separateur et les marqueurs : jamais de
    depassement de la borne, aucune queue si budget epuise."""
    prev = _chunk(1, "y" * 500)
    cur = _chunk(2, "x" * 990)
    out = apply_overlap([prev, cur], P)
    assert out[1].text == cur.text
    assert out[1].length <= P.chunk_max


def test_pas_d_overlap_entre_parties():
    """Comportement inchange : l'overlap ne traverse pas les parties."""
    a = _chunk(1, "Texte du premier chunk de la premiere partie.", part="A")
    b = _chunk(2, "Texte du second chunk d'une autre partie.", part="B")
    out = apply_overlap([a, b], P)
    assert out[1].text == b.text


def test_queue_de_citation_marquee_des_deux_cotes():
    """Une queue coupant une citation porte « ... » en tete et le
    fermant reste rattache a son extrait."""
    corps = (
        "Phrase d'introduction du chunk precedent assez longue ici. "
        "Encore des mots pour atteindre une cible d'overlap utile. "
        "« Debut de citation qui se poursuit hors de la fenetre cible "
        "de l'overlap calculee sur le chunk precedent du document."
    )
    prev = _chunk(1, corps)
    cur = _chunk(2, "Contenu du chunk suivant avec du texte.")
    out = apply_overlap([prev, cur], P)
    queue = out[1].text.split("\n\n")[0]
    assert queue.startswith(MARKER)
    assert queue.endswith(MARKER)
