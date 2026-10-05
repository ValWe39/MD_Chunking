"""Tests unitaires du nommage (feature 003, FR-002 a FR-005, FR-011)."""

import pytest

from md_chunking.naming import (
    build_output_name,
    decode_block,
    encode_block,
    extract_letters,
)


def test_extraction_nfkd_casse_neutralisee():
    """FR-005, FR-011 : accents ramenes a la base, casse neutre."""
    assert extract_letters("À LA DÉMOCRATIE", 5) == "alade"
    assert extract_letters("DÉMOCRATIE", 4) == extract_letters("democratie", 4)
    assert extract_letters("CONTEXTE", 3) == extract_letters("contexte", 3)


def test_extraction_ignore_espaces_symboles_chiffres():
    assert extract_letters("9.md - v2 !", 5) == "mdv"
    assert extract_letters(None, 5) == ""
    assert extract_letters("", 5) == ""
    # L'extension n'est pas retiree ici : l'appelant passe le stem.
    assert extract_letters("abc.md", 10) == "abcmd"
    assert extract_letters("abc", 10) == "abc"


def test_encodage_bijectif_valeurs_connues():
    """Bornes et exemples du contrat contracts/output-naming.md."""
    assert encode_block("conte", 8) == "01644557"
    assert encode_block("cont", 6) == "063252"
    assert encode_block("zzzzz", 8) == "12356630"
    assert encode_block("zzzz", 6) == "475254"
    assert encode_block("wxyz", 6) == "421148"
    assert encode_block("a", 8) == "00000001"
    assert encode_block("", 8) == "00000000"


def test_decodage_aller_retour_sans_perte():
    """FR-003 : bloc -> lettres -> bloc redonne la valeur initiale."""
    for lettres in ["conte", "cont", "zzzzz", "wxyz", "a", "z", "ab", "abcde"]:
        bloc = encode_block(lettres, 8)
        assert decode_block(bloc) == lettres


def test_padding_zero_a_gauche():
    """FR-004 : chiffres alignes a droite, remplissage a gauche."""
    assert encode_block("abc", 8) == "00000731"
    assert decode_block("00000731") == "abc"


def test_nom_complet_18_chiffres():
    """FR-002 : 8 + 6 + 4, exemple chiffré du contrat."""
    assert build_output_name("article-propre", "Article de reference", 1) == (
        "007871010302730001"
    )
    nom = build_output_name("contexte.md", "CONTEXTE", 42)
    assert len(nom) == 18
    assert nom.isdigit()


def test_nom_sans_lettres_ni_titre():
    """Blocs vides : 00000000 / 000000 (FR-004)."""
    assert build_output_name("9", None, 1).startswith("000000000000000001")
    assert build_output_name(None, None, 7) == "000000000000000007"


def test_nom_plus_de_cinq_lettres_tronque():
    assert build_output_name("abcdef", "abcdefg", 1) == (
        encode_block("abcde", 8) + encode_block("abcd", 6) + "0001"
    )


def test_occurrence_hors_bornes_rejetee():
    with pytest.raises(ValueError):
        build_output_name("abc", "abc", 10000)
    with pytest.raises(ValueError):
        build_output_name("abc", "abc", -1)
