"""Tests d'integration du CLI (feature 003 : sortie plate, nom 18)."""

import json
import re
from pathlib import Path

import pytest

from md_chunking import counter
from md_chunking.cli import main

FIXTURES = Path(__file__).parents[1] / "fixtures"
PROPRE = FIXTURES / "article-propre.md"
BRUITEE = FIXTURES / "titres-en-listes.md"
PROSE = FIXTURES / "prose-longue.md"

NOM_18 = re.compile(r"^\d{18}$")


@pytest.fixture
def compteur(tmp_path, monkeypatch):
    """Isole le compteur : jamais le counter.txt reel du depot
    (research.md D6)."""
    chemin = tmp_path / "counter.txt"
    monkeypatch.setattr(counter, "COUNTER_PATH", chemin)
    return chemin


def _jsons(sortie: Path) -> list[Path]:
    return sorted(p for p in sortie.iterdir() if p.suffix == ".json")


def test_succes_produit_json_et_review(tmp_path, compteur):
    """FR-001 : deux fichiers a plat, sans sous-dossier ; SC-001 :
    nom a 18 chiffres conforme (contrat contracts/output-naming.md :
    'article-propre' -> 00787101, 'Article de reference' ->
    030273, premier document -> 0001)."""
    sortie = tmp_path / "out"
    code = main([str(PROPRE), "--output", str(sortie)])
    assert code == 0
    assert not any(d.is_dir() for d in sortie.iterdir())
    fichiers = sorted(p.name for p in sortie.iterdir())
    assert fichiers == [
        "007871010302730001.json",
        "007871010302730001_review.md",
    ]
    index = json.loads((sortie / "007871010302730001.json").read_text(encoding="utf-8"))
    assert index["schema_version"] == "1.0"
    assert index["params"]["unit"] == "chars"


def test_no_review_ne_produit_pas_le_rendu(tmp_path, compteur):
    sortie = tmp_path / "out"
    code = main([str(PROPRE), "--output", str(sortie), "--no-review"])
    assert code == 0
    assert len(_jsons(sortie)) == 1
    assert not list(sortie.glob("*_review.md"))


def test_naming_option_rejetee(tmp_path, compteur):
    """FR-012 : --naming supprimee, message argparse standard,
    code de sortie 2."""
    sortie = tmp_path / "out"
    with pytest.raises(SystemExit) as exc:
        main([str(PROPRE), "--output", str(sortie), "--naming", "title"])
    assert exc.value.code == 2
    assert not sortie.exists()


def test_no_guillemets_visible_dans_les_params(tmp_path, compteur):
    """Bug chunking-quotes-words : --no-guillemets desactive la regle
    et le parametre est trace dans le JSON (defaut : actif)."""
    sortie = tmp_path / "out"
    code = main([str(PROPRE), "--output", str(sortie), "--no-guillemets"])
    assert code == 0
    index = json.loads(_jsons(sortie)[0].read_text(encoding="utf-8"))
    assert index["params"]["guillemets"] is False


def test_guillemets_actifs_par_defaut_dans_les_params(tmp_path, compteur):
    sortie = tmp_path / "out"
    code = main([str(PROPRE), "--output", str(sortie)])
    assert code == 0
    index = json.loads(_jsons(sortie)[0].read_text(encoding="utf-8"))
    assert index["params"]["guillemets"] is True


def test_lot_continue_apres_echec_d_un_document(tmp_path, compteur):
    """Edge case spec : un document en echec n'arrete pas le lot ;
    code de sortie 1. Le document en echec ne consomme pas de
    numero (FR-006 : numero attribue a chaque document PRODUIT)."""
    sortie = tmp_path / "out"
    invalide = tmp_path / "invalide.md"
    invalide.write_bytes(b"\xff\xfe\x00invalide")
    code = main([str(invalide), str(PROPRE), "--output", str(sortie)])
    assert code == 1
    jsons = _jsons(sortie)
    assert len(jsons) == 1
    assert NOM_18.match(jsons[0].stem)
    assert jsons[0].stem.endswith("0001")


def test_configuration_invalide_code_2_rien_n_est_ecrit(tmp_path, compteur):
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


def test_typologie_livre_applique_ses_bornes(tmp_path, compteur):
    sortie = tmp_path / "out"
    code = main(
        [
            str(PROSE),
            "--output",
            str(sortie),
            "--typologie",
            "livre",
        ]
    )
    assert code == 0
    index = json.loads(_jsons(sortie)[0].read_text(encoding="utf-8"))
    assert index["document"]["typologie"] == "livre"
    assert index["params"]["chunk_max"] == 1200


def test_trois_documents_noms_tous_differents(tmp_path, compteur):
    """FR-006 : six fichiers, six noms distincts ; occurrences
    0001 a 0003 dans l'ordre de creation."""
    sortie = tmp_path / "out"
    code = main(
        [
            str(PROPRE),
            str(BRUITEE),
            str(PROSE),
            "--output",
            str(sortie),
        ]
    )
    assert code == 0
    fichiers = sorted(p.name for p in sortie.iterdir())
    assert len(fichiers) == 6
    assert len(set(fichiers)) == 6
    occurrences = sorted(p.stem[-4:] for p in _jsons(sortie))
    assert occurrences == ["0001", "0002", "0003"]


def test_compteur_absent_repart_a_0001(tmp_path, compteur):
    """FR-009 : fichier de compteur absent -> premier document
    0001 ; le compteur memorise le dernier numero consomme."""
    sortie = tmp_path / "out"
    assert main([str(PROPRE), "--output", str(sortie)]) == 0
    assert _jsons(sortie)[0].stem.endswith("0001")
    assert compteur.read_text(encoding="utf-8") == "0001\n"


def test_compteur_croissant_entre_executions(tmp_path, compteur):
    """SC-005 : numeros strictement croissants entre executions ;
    SC-003 : contenu du JSON identique, seul le nom avance."""
    sortie_a = tmp_path / "a"
    sortie_b = tmp_path / "b"
    assert main([str(PROPRE), "--output", str(sortie_a)]) == 0
    assert main([str(PROPRE), "--output", str(sortie_b)]) == 0
    nom_a = _jsons(sortie_a)[0]
    nom_b = _jsons(sortie_b)[0]
    assert nom_a.stem.endswith("0001")
    assert nom_b.stem.endswith("0002")
    assert nom_a.read_text(encoding="utf-8") == nom_b.read_text(encoding="utf-8")


def test_compteur_corrompu_code_2_rien_n_est_ecrit(tmp_path, compteur):
    """FR-009 : compteur illisible -> echec rapide, code 2, aucun
    fichier ecrit."""
    compteur.write_text("abcd\n", encoding="utf-8")
    sortie = tmp_path / "out"
    code = main([str(PROPRE), "--output", str(sortie)])
    assert code == 2
    assert not sortie.exists()


def test_review_porte_l_estimation_index_sans_tokens(tmp_path, compteur):
    """FR-T01, FR-T07 (feature 002) : estimation marquee approximative
    dans le rendu de relecture ; aucun champ tokens dans l'index JSON."""
    sortie = tmp_path / "out"
    assert main([str(PROPRE), "--output", str(sortie)]) == 0
    review = next(sortie.glob("*_review.md")).read_text(encoding="utf-8")
    assert "- tokens (estimation) : ≈ " in review
    index = json.loads(_jsons(sortie)[0].read_text(encoding="utf-8"))
    assert "tokens" not in json.dumps(index)


def test_defaut_3_5_sans_option_index_sans_ratio(tmp_path, compteur):
    """FR-001, FR-007, SC-004 (feature 004) : sans option, l'en-tete
    du review porte le defaut 3,5 ; l'index JSON ne contient ni champ
    tokens ni champ ratio, octet pour octet."""
    sortie = tmp_path / "out"
    assert main([str(PROPRE), "--output", str(sortie)]) == 0
    review = next(sortie.glob("*_review.md")).read_text(encoding="utf-8")
    assert "~3.5 caracteres par token" in review
    brut = _jsons(sortie)[0].read_text(encoding="utf-8")
    assert "ratio" not in brut
    assert "tokens" not in brut
    index = json.loads(brut)
    assert index["params"]["unit"] == "chars"


def test_tokencpte_explicite_change_le_review_pas_l_index(tmp_path, compteur):
    """FR-002, SC-002 (feature 004) : le ratio explicite recalcule les
    estimations du review ; l'index JSON est identique octet par
    octet a celui d'une execution au defaut."""
    sortie_defaut = tmp_path / "defaut"
    sortie_ratio = tmp_path / "ratio"
    assert main([str(PROPRE), "--output", str(sortie_defaut)]) == 0
    code = main([str(PROPRE), "--output", str(sortie_ratio), "--tokencpte", "3.2"])
    assert code == 0
    review = next(sortie_ratio.glob("*_review.md")).read_text(encoding="utf-8")
    assert "~3.2 caracteres par token" in review
    index_defaut = _jsons(sortie_defaut)[0].read_text(encoding="utf-8")
    index_ratio = _jsons(sortie_ratio)[0].read_text(encoding="utf-8")
    assert index_defaut == index_ratio


def test_tokencpte_applique_a_tous_les_documents(tmp_path, compteur):
    """FR-008 : le ratio est global a l'execution, pas par document."""
    sortie = tmp_path / "out"
    code = main(
        [
            str(PROPRE),
            str(BRUITEE),
            "--output",
            str(sortie),
            "--tokencpte",
            "2",
        ]
    )
    assert code == 0
    reviews = sorted(sortie.glob("*_review.md"))
    assert len(reviews) == 2
    for review in reviews:
        assert "~2.0 caracteres par token" in review.read_text(encoding="utf-8")


def test_tokencpte_avec_no_review_sans_erreur(tmp_path, compteur):
    """FR-009 : --no-review accepte l'option sans erreur, aucune
    estimation produite."""
    sortie = tmp_path / "out"
    code = main(
        [str(PROPRE), "--output", str(sortie), "--no-review", "--tokencpte", "2"]
    )
    assert code == 0
    assert len(_jsons(sortie)) == 1
    assert not list(sortie.glob("*_review.md"))


def test_tokencpte_hors_bornes_code_2_rien_n_est_ecrit(tmp_path, compteur):
    """FR-003, SC-003 : ratio hors bornes -> echec rapide code 2,
    aucun fichier ecrit, compteur non incremente."""
    sortie = tmp_path / "out"
    code = main([str(PROPRE), "--output", str(sortie), "--tokencpte", "12"])
    assert code == 2
    assert not sortie.exists()
    assert not compteur.exists()
