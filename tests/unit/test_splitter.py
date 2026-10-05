"""Tests unitaires du decoupage : guillemets, marqueurs de coupure,
recours aux mots (bug chunking-quotes-words, regles 1 a 3)."""

from pathlib import Path

from md_chunking.models import DocumentSource
from md_chunking.presets import Preset
from md_chunking.splitter import MARKER, _split_sentences, split_document

P = Preset("test", 30, 300, 15, True)
P_SANS = Preset("test", 30, 300, 15, False)

TEXTE_CITATION = (
    "Avant la citation. « Premiere phrase citee assez longue. "
    "Deuxieme phrase citee aussi. » Apres la citation. Suite encore."
)


def _doc(texte: str, structure: str = "paragraphes") -> DocumentSource:
    return DocumentSource(
        path=Path("test.md"),
        raw_content=texte,
        normalized_content=texte,
        structure=structure,
    )


def test_split_respecte_une_citation_multiphrases():
    """Regle 1 : aucune frontiere a l'interieur d'une citation
    ouverte, ni entre une ponctuation et le fermant qui la suit."""
    segments = _split_sentences(TEXTE_CITATION, respect_quotes=True)
    assert not any(s.startswith("»") for s in segments)
    cite = [s for s in segments if "«" in s]
    assert len(cite) == 1
    assert cite[0].count("«") == cite[0].count("»") == 1


def test_split_sans_guillemets_detache_le_fermant():
    """Sans l'option, l'ancien comportement (bug) produit un fragment
    commencant par le fermant orphelin."""
    segments = _split_sentences(TEXTE_CITATION, respect_quotes=False)
    assert any(s.startswith("»") for s in segments)


def test_split_respecte_les_guillemets_anglo_saxons():
    texte = 'He said. "First quoted part. Second quoted part." Then done.'
    segments = _split_sentences(texte, respect_quotes=True)
    cite = [s for s in segments if s.startswith('"')]
    assert len(cite) == 1
    assert cite[0].count('"') == 2


def test_guillemet_de_pouce_apres_chiffre_ignore():
    """Un guillemet de pouce (6") ne fait pas basculer l'etat."""
    texte = 'Une mesure de 6" posee. Suite du texte.'
    segments = _split_sentences(texte, respect_quotes=True)
    assert len(segments) == 2
    assert segments[0].endswith("posee.")


def test_phrase_trop_longue_descend_aux_mots_avec_marqueurs():
    """Regle 3 : dernier recours aux frontieres de mots ; regle 2 :
    coupure marquee, marqueurs comptes dans la taille."""
    mots = [f"motnumero{i:03d}assezlong" for i in range(60)]
    phrase = " ".join(mots)
    chunks = split_document(_doc(phrase, structure="phrases"), P)
    assert chunks
    for c in chunks:
        if not c.atomic:
            assert c.length <= P.chunk_max, f"chunk {c.ref} trop grand"
        assert c.boundary == "mot"
    assert chunks[0].text.endswith(MARKER)
    assert chunks[-1].text.startswith(MARKER)
    reconstitue = " ".join(
        "\n\n".join(c.text for c in chunks).replace(MARKER, " ").split()
    )
    assert reconstitue == phrase


def test_citation_tranchee_par_chunks_marquee():
    """Regle 2 : une citation coupee entre deux chunks porte « ... »
    en fin du premier et en tete du second."""
    a = (
        "« Debut de la tres longue citation qui se prolonge "
        + "avec des mots repetes et utiles " * 5
    )
    b = (
        "la fin de la citation arrive ici et se termine proprement. "
        "» Apres la citation la suite continue ici aussi."
    )
    chunks = split_document(_doc(a + "\n\n" + b), P)
    assert len(chunks) == 2
    premier, second = chunks
    assert "«" in premier.text and "»" not in premier.text
    assert premier.text.endswith(MARKER)
    assert second.text.startswith(MARKER)
    for c in chunks:
        if not c.atomic:
            assert c.length <= P.chunk_max


def test_option_desactivee_pas_de_marqueurs_de_citation():
    """--no-guillemets : regle 1 etendue inactive, aucun marqueur de
    citation ajoute."""
    a = (
        "« Debut de la tres longue citation qui se prolonge "
        + "avec des mots repetes et utiles " * 5
    )
    b = (
        "la fin de la citation arrive ici et se termine proprement. "
        "» Apres la citation la suite continue ici aussi."
    )
    chunks = split_document(_doc(a + "\n\n" + b), P_SANS)
    assert chunks
    for c in chunks:
        assert MARKER not in c.text


def test_citation_qui_tient_reste_entiere_et_sans_marqueur():
    cite = "« Une citation complete et courte. » Apres la citation."
    chunks = split_document(_doc(cite), P)
    assert len(chunks) == 1
    assert MARKER not in chunks[0].text
    assert chunks[0].text.count("«") == chunks[0].text.count("»") == 1


def test_unite_atomique_jamais_marquee():
    """Les guillemets d'un bloc de code ne sont pas de la prose :
    pas de marqueur, pas de desequilibre signale."""
    code = '```python\nx = "« guillemet orphelin"\n```'
    texte = code + "\n\n" + "Texte normal apres le code. " * 20
    chunks = split_document(_doc(texte), P)
    atomiques = [c for c in chunks if c.atomic]
    assert atomiques, "le bloc de code doit rester un chunk atomique"
    for c in atomiques:
        assert MARKER not in c.text
