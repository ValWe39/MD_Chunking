"""Tests d'integration du CLI (T016, T019, T022, T024, T025)."""

import json
from pathlib import Path

from md_chunking.cli import main

FIXTURES = Path(__file__).parents[1] / "fixtures"
PROPRE = FIXTURES / "article-propre.md"
BRUITEE = FIXTURES / "titres-en-listes.md"


def test_succes_produit_json_et_review(tmp_path):
    sortie = tmp_path / "out"
    code = main([str(PROPRE), "--output", str(sortie)])
    assert code == 0
    sous_dossiers = [d for d in sortie.iterdir() if d.is_dir()]
    assert len(sous_dossiers) == 1
    assert (sous_dossiers[0] / "chunks.json").is_file()
    assert (sous_dossiers[0] / "review.md").is_file()
    index = json.loads((sous_dossiers[0] / "chunks.json").read_text(encoding="utf-8"))
    assert index["schema_version"] == "1.0"
    assert index["params"]["unit"] == "chars"


def test_no_review_ne_produit_pas_le_rendu(tmp_path):
    sortie = tmp_path / "out"
    code = main([str(PROPRE), "--output", str(sortie), "--no-review"])
    assert code == 0
    sous_dossier = next(sortie.iterdir())
    assert (sous_dossier / "chunks.json").is_file()
    assert not (sous_dossier / "review.md").exists()


def test_naming_title_utilise_le_slug_du_titre(tmp_path):
    sortie = tmp_path / "out"
    code = main(
        [
            str(PROPRE),
            "--output",
            str(sortie),
            "--naming",
            "title",
        ]
    )
    assert code == 0
    assert (sortie / "article-de-reference").is_dir()


def test_lot_continue_apres_echec_d_un_document(tmp_path):
    """Edge case spec : un document en echec n'arrete pas le lot ;
    code de sortie 1, message nommant le fichier."""
    sortie = tmp_path / "out"
    code = main(
        [
            str(BRUITEE),
            str(PROPRE),
            "--output",
            str(sortie),
        ]
    )
    assert code == 0  # la fixture bruitee doit reussir apres normalisation

    # cas reel d'echec : fichier illisible en position intermediaire
    invalide = tmp_path / "invalide.md"
    invalide.write_bytes(b"\xff\xfe\x00invalide")
    code2 = main(
        [
            str(invalide),
            str(PROPRE),
            "--output",
            str(sortie / "out2"),
        ]
    )
    assert code2 == 1
    assert (sortie / "out2" / "0002" / "chunks.json").is_file()


def test_configuration_invalide_code_2_rien_n_est_ecrit(tmp_path):
    sortie = tmp_path / "out"
    code = main(
        [
            str(PROPRE),
            "--output",
            str(sortie),
            "--min",
            "500",
            "--max",
            "100",
        ]
    )
    assert code == 2
    assert not sortie.exists()


def test_typologie_livre_applique_ses_bornes(tmp_path):
    sortie = tmp_path / "out"
    code = main(
        [
            str(FIXTURES / "prose-longue.md"),
            "--output",
            str(sortie),
            "--typologie",
            "livre",
        ]
    )
    assert code == 0
    sous_dossier = next(sortie.iterdir())
    index = json.loads((sous_dossier / "chunks.json").read_text(encoding="utf-8"))
    assert index["document"]["typologie"] == "livre"
    assert index["params"]["chunk_max"] == 1200


def test_determinisme_deux_executions_identiques(tmp_path):
    """SC-005 : memes entrees et memes options, sorties identiques."""
    sortie_a = tmp_path / "a"
    sortie_b = tmp_path / "b"
    assert main([str(PROPRE), "--output", str(sortie_a)]) == 0
    assert main([str(PROPRE), "--output", str(sortie_b)]) == 0
    json_a = (sortie_a / "0001" / "chunks.json").read_text(encoding="utf-8")
    json_b = (sortie_b / "0001" / "chunks.json").read_text(encoding="utf-8")
    assert json_a == json_b
