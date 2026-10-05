"""Tests unitaires du rendu de relecture (T020, FR-008, SC-004).

Feature 002 : estimation de tokens par chunk (FR-T01 a FR-T09).
Feature 004 : ratio reglable, defaut 3.5, division exacte (T004).
"""

from fractions import Fraction
from pathlib import Path

from md_chunking.normalizer import build_document
from md_chunking.presets import get_preset
from md_chunking.reviewer import (
    DEFAULT_RATIO_CHARS_PER_TOKEN,
    build_review,
    estimate_tokens,
)
from md_chunking.splitter import split_document

FIXTURES = Path(__file__).parents[1] / "fixtures"


def review_fixture(name: str = "article-propre.md") -> str:
    preset = get_preset("documentation")
    doc = build_document(FIXTURES / name)
    chunks = split_document(doc, preset)
    return build_review(doc, chunks)


def test_un_titre_par_chunk_avec_taille():
    review = review_fixture()
    lignes = review.split("\n")
    for numero in (1, 2, 3):
        assert any(ligne.startswith(f"## Chunk {numero} — ") for ligne in lignes)


def test_metadonnees_et_texte_integral():
    review = review_fixture()
    assert "- frontiere : " in review
    assert "- partie : " in review
    # le texte des chunks est integral, dans des blocs de code
    assert review.count("```") >= 6  # au moins 3 chunks -> 6 clotures


def test_rendu_deterministe():
    """SC-005 : aucun horodatage, sortie identique a l'execution pres."""
    assert review_fixture() == review_fixture("article-propre.md")


def test_document_sans_titre_utilise_le_nom_de_fichier():
    preset = get_preset("documentation")
    doc = build_document(FIXTURES / "sans-structure.md")
    chunks = split_document(doc, preset)
    review = build_review(doc, chunks)
    assert review.startswith("# Decoupage : sans-structure.md")


# --- Feature 002 : estimation de tokens (T003, T004, T007) ---


def chunks_fixture(name: str = "article-propre.md"):
    preset = get_preset("documentation")
    doc = build_document(FIXTURES / name)
    return doc, split_document(doc, preset)


# --- Feature 004 : ratio reglable, defaut 3.5 (T004) ---


def test_defaut_recale_a_3_5():
    """FR-001 : le defaut remplace le ratio 4 de la feature 002."""
    assert DEFAULT_RATIO_CHARS_PER_TOKEN == 3.5


def test_estimate_tokens_multiple_exact():
    """FR-001 : division, multiples exacts du defaut 3,5."""
    assert estimate_tokens("a" * 7) == 2
    assert estimate_tokens("a" * 14) == 4


def test_estimate_tokens_arrondi_superieur():
    """FR-001 : arrondi superieur, penche du cote du risque."""
    assert estimate_tokens("a") == 1
    assert estimate_tokens("a" * 4) == 2
    assert estimate_tokens("a" * 8) == 3


def test_estimate_tokens_ratio_explicite():
    """FR-002 : toute valeur valide remplace le defaut."""
    assert estimate_tokens("a" * 7, 3.5) == 2
    assert estimate_tokens("a" * 7, 2) == 4
    assert estimate_tokens("a" * 100, 10) == 10


def test_estimate_tokens_ratio_non_representable_exact():
    """FR-005 : division exacte via Fraction, meme pour 3,3."""
    assert estimate_tokens("a" * 33, 3.3) == 10
    assert estimate_tokens("a" * 34, 3.3) == 11
    assert Fraction(33) / Fraction(str(3.3)) == 10


def test_estimate_tokens_deterministe():
    """FR-T06 : fonction pure, meme texte -> meme valeur (SC-T04)."""
    assert estimate_tokens("texte constant") == estimate_tokens("texte constant")
    assert estimate_tokens("texte constant", 3.3) == estimate_tokens(
        "texte constant", 3.3
    )


def test_estimation_presente_pour_chaque_chunk():
    """FR-T01, SC-T01 : une ligne d'estimation par chunk, marquee
    approximative par le prefixe '≈'."""
    doc, chunks = chunks_fixture()
    review = build_review(doc, chunks)
    lignes = [
        ligne
        for ligne in review.split("\n")
        if ligne.startswith("- tokens (estimation) : ≈ ")
    ]
    assert len(lignes) == len(chunks)


def test_longueur_en_caracteres_conservee():
    """FR-T04 : l'en-tete de chunk garde sa longueur en caracteres,
    l'estimation ne la remplace pas."""
    review = review_fixture()
    assert "## Chunk 1 — " in review
    assert " car." in review


def test_mention_d_en_tete_approximative_et_modele_agnostique():
    """FR-004 : ratio effectif affiche, approximatif, sans nom de
    modele (FR-T09 : aucun signalement de seuil)."""
    review = review_fixture()
    assert "~3.5 caracteres par token" in review
    assert "approximation" in review
    assert "independante de tout modele" in review
    assert "gpt" not in review.lower()
    assert "claude" not in review.lower()
    assert "bert" not in review.lower()


def test_en_tete_ratio_explicite_arrondi_une_decimale():
    """FR-004 : l'en-tete affiche le ratio passe, arrondi a une
    decimale (clarification 2026-10-05)."""
    doc, chunks = chunks_fixture()
    assert "~3.2 caracteres par token" in build_review(doc, chunks, 3.2)
    assert "~3.3 caracteres par token" in build_review(doc, chunks, 3.333)
