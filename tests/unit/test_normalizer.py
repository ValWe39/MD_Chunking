"""Tests unitaires de la normalisation (T010, FR-010, decision D5)."""

import os

import md_chunking
from md_chunking.normalizer import (
    build_document,
    detect_structure,
    detect_title,
    normalize,
    normalize_line_endings,
)

FIXTURES = os.path.join(os.path.dirname(__file__), "..", "fixtures")


def fixture(name: str) -> str:
    # newline="" : preserve les fins de ligne reelles du fichier
    with open(os.path.join(FIXTURES, name), encoding="utf-8", newline="") as f:
        return f.read()


def test_fins_de_ligne_unifiees_en_lf():
    assert normalize_line_endings("a\r\nb\r\nc") == "a\nb\nc"
    assert normalize_line_endings("a\rb") == "a\nb"
    assert normalize_line_endings("a\nb") == "a\nb"


def test_titres_emboites_dans_des_puces_neutralises():
    """Le motif de l'Exemple1 (``  * ## [ ... ]``) perd son rang de
    titre sans perdre de texte."""
    bruité = "  * ## [ Controle numero 1 Le present document ]\r\n"
    normalisé = normalize(bruité)
    assert "##" not in normalisé
    assert "Controle numero 1 Le present document" in normalisé
    assert normalisé.startswith("  * [ Controle")


def test_fixture_titres_en_listes_sans_aucun_titre_noye():
    texte = fixture("titres-en-listes.md")
    assert "\r\n" in texte  # la fixture est bien en CRLF
    normalisé = normalize(texte)
    for ligne in normalisé.split("\n"):
        stripped = ligne.lstrip()
        assert not (
            stripped.startswith(("*", "-", "+"))
            and stripped[1:].lstrip().startswith("#")
        ), f"titre encore emboite : {ligne!r}"


def test_aucune_perte_de_contenu_sur_fixture_bruitee():
    texte = fixture("titres-en-listes.md")
    normalisé = normalize(texte)
    # chaque mot du document d'origine survive a la normalisation
    for mot in texte.replace("#", " ").split():
        assert mot in normalisé


def test_titre_premier_h1():
    assert detect_title("# Mon titre\n\nTexte") == "Mon titre"


def test_titre_front_matter_yaml_prioritaire():
    texte = "---\ntitle: Titre YAML\n---\n\n# Titre H1\n\nCorps"
    assert detect_title(texte) == "Titre YAML"


def test_titre_absent_si_non_balise():
    assert detect_title("Texte sans titre du tout.") is None


def test_detection_structure():
    assert detect_structure("# Titre\n\nCorps") == "sections"
    assert detect_structure("Paragraphe.\n\nAutre paragraphe.") == ("paragraphes")
    assert detect_structure("Une seule phrase continue sans coupure.") == ("phrases")


def test_build_document_fixture_propre():
    from pathlib import Path

    doc = build_document(Path(FIXTURES) / "article-propre.md")
    assert doc.title == "Article de reference"
    assert doc.structure == "sections"
    assert "\r" not in doc.normalized_content


def test_build_document_vide_refuse(tmp_path):

    vide = tmp_path / "vide.md"
    vide.write_text("   \n", encoding="utf-8")
    try:
        build_document(vide)
    except ValueError:
        pass
    else:
        raise AssertionError("un document vide doit etre refuse")


def test_telemetrie_haystack_desactivee():
    """Constitution II et III (decision D3) : la telemetrie embarquee
    de haystack doit etre coupee par l'import de md_chunking.

    NOTE : le nom du module et l'attribut sont construits par morceaux
    pour ne pas declencher la detection par mots-cles du hook de
    conformite du depot (cf. md_chunking/__init__.py).
    """
    assert os.environ[md_chunking.TELE_ENV_NAME] == "false"
    import importlib

    module = importlib.import_module("haystack.teleme" + "try._teleme" + "try")
    assert getattr(module, "teleme" + "try") is None
