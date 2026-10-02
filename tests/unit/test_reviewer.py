"""Tests unitaires du rendu de relecture (T020, FR-008, SC-004)."""

from pathlib import Path

from md_chunking.normalizer import build_document
from md_chunking.presets import get_preset
from md_chunking.reviewer import build_review
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
