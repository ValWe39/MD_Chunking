"""Tests unitaires de la resolution d'entree (feature 005, D1-D7)."""

from pathlib import Path

import pytest

from md_chunking.inputs import InputError, resolve_inputs


def _ecrire(chemin: Path, contenu: str = "# Titre\n\nTexte.\n") -> Path:
    chemin.write_text(contenu, encoding="utf-8")
    return chemin


def test_dossier_trie_casse_neutre(tmp_path):
    """FR-003, D3 : tri (name.lower(), name) — a2 < B < c."""
    dossier = tmp_path / "corpus"
    dossier.mkdir()
    for nom in ("c.md", "B.md", "a2.md"):
        _ecrire(dossier / nom)
    fichiers, avertissements = resolve_inputs([dossier])
    assert [p.name for p in fichiers] == ["a2.md", "B.md", "c.md"]
    assert avertissements == []


def test_filtre_md_insensible_a_la_casse(tmp_path):
    """FR-002, D2 : .MD accepte ; .markdown, .txt, sans extension
    ignores sans avertissement."""
    dossier = tmp_path / "corpus"
    dossier.mkdir()
    _ecrire(dossier / "ok.md")
    _ecrire(dossier / "MAJUSCULE.MD")
    _ecrire(dossier / "refuse.markdown")
    _ecrire(dossier / "notes.txt")
    _ecrire(dossier / "sansextension")
    fichiers, avertissements = resolve_inputs([dossier])
    assert [p.name for p in fichiers] == ["MAJUSCULE.MD", "ok.md"]
    assert avertissements == []


def test_sous_dossier_ignore(tmp_path):
    """FR-008, D7 : surface seule, meme un sous-dossier nomme .md."""
    dossier = tmp_path / "corpus"
    dossier.mkdir()
    _ecrire(dossier / "visible.md")
    sous = dossier / "sub.md"
    sous.mkdir()
    _ecrire(sous / "cache.md")
    fichiers, _ = resolve_inputs([dossier])
    assert [p.name for p in fichiers] == ["visible.md"]


def test_dossier_vide_et_sans_md_avertissent(tmp_path):
    """FR-005b, D4 : avertissement par dossier, aucune erreur."""
    vide = tmp_path / "vide"
    vide.mkdir()
    sans_md = tmp_path / "sans-md"
    sans_md.mkdir()
    _ecrire(sans_md / "x.txt")
    fichiers, avertissements = resolve_inputs([vide, sans_md])
    assert fichiers == []
    assert avertissements == [
        f"Dossier sans fichier .md : {vide}",
        f"Dossier sans fichier .md : {sans_md}",
    ]


def test_introuvable_leve_input_error(tmp_path):
    """FR-005, D5 : echec rapide, message existant repris."""
    absent = tmp_path / "absent.md"
    with pytest.raises(InputError, match="fichier d'entree introuvable"):
        resolve_inputs([absent])


def test_doublons_conserves_sans_deduplication(tmp_path):
    """FR-001, D6 : dossier + fichier individuel -> chaque
    occurrence est conservee, aucune deduplication."""
    dossier = tmp_path / "corpus"
    dossier.mkdir()
    _ecrire(dossier / "a.md")
    _ecrire(dossier / "b.md")
    fichiers, _ = resolve_inputs([dossier, dossier / "a.md"])
    assert [p.name for p in fichiers] == ["a.md", "b.md", "a.md"]


def test_ordre_des_arguments_preserve(tmp_path):
    """FR-004 : dossier developpe a sa position, ordre des
    arguments respecte dans les deux sens."""
    dossier = tmp_path / "corpus"
    dossier.mkdir()
    _ecrire(dossier / "a.md")
    isole = _ecrire(tmp_path / "z.md")
    avant, _ = resolve_inputs([isole, dossier])
    apres, _ = resolve_inputs([dossier, isole])
    assert [p.name for p in avant] == ["z.md", "a.md"]
    assert [p.name for p in apres] == ["a.md", "z.md"]


def test_fichier_individuel_conserve_telle_quelle(tmp_path):
    """Un fichier hors dossier passe tel quel, quelle que soit son
    extension (contrat 001 inchange pour les fichiers)."""
    fichier = _ecrire(tmp_path / "isole.markdown")
    fichiers, avertissements = resolve_inputs([fichier])
    assert fichiers == [fichier]
    assert avertissements == []
