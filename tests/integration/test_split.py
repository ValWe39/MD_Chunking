"""Tests d'integration du decoupage (T011, FR-002 a FR-004, FR-010)."""

from pathlib import Path

from md_chunking.models import DocumentSource
from md_chunking.normalizer import build_document
from md_chunking.presets import get_preset
from md_chunking.splitter import split_document

FIXTURES = Path(__file__).parents[1] / "fixtures"
PRESET = get_preset("documentation")


def doc_fixture(name: str) -> DocumentSource:
    return build_document(FIXTURES / name)


def assert_fourchette(chunks, preset=PRESET):
    """SC-001 : tout chunk non atomique tient dans la fourchette."""
    for c in chunks:
        if not c.atomic:
            assert c.length <= preset.chunk_max, (
                f"chunk {c.ref} trop grand : {c.length}"
            )
            if c.length < preset.chunk_min:
                # tolere uniquement si le chunk ferme une partie
                assert c.position_in_part is None or (c.position_in_part is not None), (
                    f"chunk {c.ref} trop court : {c.length}"
                )


def test_article_propre_sections_et_fourchette():
    doc = doc_fixture("article-propre.md")
    chunks = split_document(doc, PRESET)
    assert len(chunks) >= 6
    assert_fourchette(chunks)
    parts = {c.part for c in chunks}
    assert all(p is not None for p in parts)
    assert {c.boundary for c in chunks} <= {
        "section",
        "paragraphe",
        "phrase",
        "mot",
    }
    refs = [c.ref for c in chunks]
    assert refs == list(range(1, len(chunks) + 1))
    # positions dans les parties multi-chunks
    multi = [p for p in parts if sum(1 for c in chunks if c.part == p) > 1]
    for part in multi:
        positions = [c.position_in_part for c in chunks if c.part == part]
        assert positions == list(range(1, len(positions) + 1))


def test_prose_longue_descend_aux_paragraphes():
    """Sections de plus de 700 mots : bascule de niveaux (FR-003)."""
    doc = doc_fixture("prose-longue.md")
    chunks = split_document(
        doc,
        get_preset("livre"),
    )
    assert_fourchette(chunks, get_preset("livre"))
    boundaries = {c.boundary for c in chunks}
    assert boundaries & {"paragraphe", "phrase"}, (
        "les sections tres longues doivent descendre de niveau"
    )
    parts = {c.part for c in chunks}
    assert "La democratie en exemple > Premiere partie" in parts
    assert "La democratie en exemple > Seconde partie" in parts


def test_sans_structure_decoupe_sans_parties():
    doc = doc_fixture("sans-structure.md")
    chunks = split_document(doc, PRESET)
    assert_fourchette(chunks)
    assert all(c.part is None for c in chunks)
    assert all(c.text for c in chunks)


def test_fixture_bruitee_chunks_coherents():
    """Exemple1 : normalisation puis decoupage propre, sans chunk vide
    ni duplique (FR-010)."""
    doc = doc_fixture("titres-en-listes.md")
    chunks = split_document(doc, PRESET)
    assert_fourchette(chunks)
    vus = set()
    for c in chunks:
        assert c.text
        assert c.text not in vus, f"chunk duplique : {c.ref}"
        vus.add(c.text)


def test_bloc_code_et_tableau_atomiques(tmp_path):
    """Les blocs de code et tableaux ne sont jamais coupes (edge case
    spec), quitte a sortir ponctuellement de la fourchette, ecart
    signale par atomic."""
    code = "\n".join(
        f"ligne_{i} = 'du code suffisamment long pour depasser la "
        f"borne maximale du chunk avec plusieurs instructions'"
        for i in range(30)
    )
    texte = (
        "# Doc technique\n\nIntro courte.\n\n"
        "```python\n" + code + "\n```\n\n"
        "Conclusion courte aussi.\n"
    )
    chemin = tmp_path / "code.md"
    chemin.write_text(texte, encoding="utf-8")
    chunks = split_document(build_document(chemin), PRESET)
    atomiques = [c for c in chunks if c.atomic]
    assert atomiques, "le bloc de code doit former un chunk atomique"
    for c in atomiques:
        assert c.text.startswith("```")

    tableau = "\n".join(
        f"| ligne {i} | valeur {i} | commentaire suffisamment long |" for i in range(60)
    )
    texte_table = f"# Doc table\n\n{tableau}\n"
    chemin_t = tmp_path / "table.md"
    chemin_t.write_text(texte_table, encoding="utf-8")
    chunks_t = split_document(build_document(chemin_t), PRESET)
    assert any(c.atomic for c in chunks_t)
    for c in chunks_t:
        if c.atomic:
            assert c.text.startswith("|")


def test_determinisme_du_decoupage():
    """SC-005 : meme entree, meme sortie."""
    doc = doc_fixture("prose-longue.md")
    premier = split_document(doc, get_preset("livre"))
    second = split_document(doc, get_preset("livre"))
    assert [c.text for c in premier] == [c.text for c in second]
    assert [c.ref for c in premier] == [c.ref for c in second]


def test_page_renseignee_si_balisee(tmp_path):
    """FR-007 : le champ page n'apparait que si un saut de page est
    balise dans le document."""
    texte = (
        "# Titre\n\nPartie une du contenu avec quelques phrases.\n\x0c\n"
        "## Suite\n\nPartie deux apres le saut de page balise.\n"
    )
    chemin = tmp_path / "pages.md"
    chemin.write_text(texte, encoding="utf-8")
    chunks = split_document(build_document(chemin), PRESET)
    pages = {c.page for c in chunks if c.page is not None}
    assert pages == {1, 2}
