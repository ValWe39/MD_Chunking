"""Tests unitaires de l'index JSON (T017, contrat chunk-json.md)."""

from pathlib import Path

from md_chunking.indexer import SCHEMA_VERSION, build_index
from md_chunking.models import DocumentSource
from md_chunking.normalizer import build_document
from md_chunking.presets import get_preset
from md_chunking.splitter import split_document

FIXTURES = Path(__file__).parents[1] / "fixtures"


def index_fixture(name: str = "article-propre.md") -> dict:
    preset = get_preset("documentation")
    doc = build_document(FIXTURES / name)
    chunks = split_document(doc, preset)
    return build_index(doc, preset, "documentation", chunks)


def test_schema_et_entete_document():
    index = index_fixture()
    assert index["schema_version"] == SCHEMA_VERSION == "1.0"
    assert index["document"]["path"].endswith("article-propre.md")
    assert index["document"]["title"] == "Article de reference"
    assert index["document"]["structure"] == "sections"
    assert index["document"]["typologie"] == "documentation"


def test_params_refletent_la_configuration():
    index = index_fixture()
    assert index["params"] == {
        "chunk_min": 100,
        "chunk_max": 1000,
        "overlap_pct": 15,
        "unit": "chars",
    }


def test_refs_sequentiels_uniques():
    index = index_fixture()
    refs = [c["ref"] for c in index["chunks"]]
    assert refs == list(range(1, len(refs) + 1))


def test_champs_obligatoires_par_chunk():
    index = index_fixture()
    for chunk in index["chunks"]:
        assert chunk["text"]
        assert chunk["length"] == len(chunk["text"])
        assert chunk["boundary"] in {"section", "paragraphe", "phrase"}
        assert isinstance(chunk["atomic"], bool)
        assert "page" not in chunk  # aucun saut de page balise


def test_champs_conditionnels_si_et_seulement_si():
    """FR-007 : present des que la balise existe, absent sinon, jamais
    devine."""
    index = index_fixture()
    au_moins_un_part = any("part" in c for c in index["chunks"])
    assert au_moins_un_part  # la fixture possede des sections balisees
    multi = [c for c in index["chunks"] if c.get("position_in_part") is not None]
    assert multi, "une partie decoupee en plusieurs chunks porte des positions"

    # document sans titre : champ absent
    preset = get_preset("documentation")
    doc = DocumentSource(
        path=Path("sans-titre.md"),
        raw_content="Texte.",
        normalized_content="Texte.\n\nSuite du texte sans titre.",
        title=None,
        structure="paragraphes",
    )
    chunks = split_document(doc, preset)
    index_sans_titre = build_index(doc, preset, "documentation", chunks)
    assert "title" not in index_sans_titre["document"]
    for c in index_sans_titre["chunks"]:
        assert "part" not in c
        assert "page" not in c


def test_invariants_sc001_et_sc002():
    """SC-001 : fourchette respectee sauf ecart atomique signale ;
    SC-002 : metadonnees obligatoires toujours presentes."""
    index = index_fixture()
    params = index["params"]
    for chunk in index["chunks"]:
        if chunk["atomic"]:
            continue
        assert params["chunk_min"] <= chunk["length"] <= params["chunk_max"]
        assert chunk["ref"] >= 1
        assert chunk["text"]
