"""Tests unitaires du compteur d'occurrence (FR-007 a FR-009)."""

import pytest

from md_chunking.counter import (
    OCCURRENCE_MAX,
    CounterError,
    next_value,
    persist,
    read_counter,
)


def test_absent_repart_a_zero(tmp_path):
    """FR-009 : fichier absent -> 0 (premier usage vaudra 0001)."""
    chemin = tmp_path / "counter.txt"
    assert read_counter(chemin) == 0
    assert not chemin.exists()


def test_illisible_leve_une_erreur(tmp_path):
    """FR-009 : contenu non numerique -> erreur explicite."""
    chemin = tmp_path / "counter.txt"
    chemin.write_text("abcd\n", encoding="utf-8")
    with pytest.raises(CounterError, match="counter.txt illisible"):
        read_counter(chemin)


def test_hors_bornes_leve_une_erreur(tmp_path):
    chemin = tmp_path / "counter.txt"
    chemin.write_text("12345\n", encoding="utf-8")
    with pytest.raises(CounterError, match="hors bornes"):
        read_counter(chemin)


def test_cycle_modulo_10000():
    """FR-008 : retour a 0000 apres 9999."""
    assert next_value(0) == 1
    assert next_value(9998) == 9999
    assert next_value(9999) == 0


def test_next_value_hors_bornes_rejete():
    with pytest.raises(ValueError):
        next_value(-1)
    with pytest.raises(ValueError):
        next_value(OCCURRENCE_MAX + 1)


def test_persistance_apres_chaque_document(tmp_path):
    """FR-007 : dernier numero consomme memorise, format NNNN."""
    chemin = tmp_path / "counter.txt"
    persist(1, chemin)
    assert read_counter(chemin) == 1
    assert chemin.read_text(encoding="utf-8") == "0001\n"
    persist(42, chemin)
    assert read_counter(chemin) == 42
    assert chemin.read_text(encoding="utf-8") == "0042\n"


def test_persistance_atomique_sans_fichier_residuel(tmp_path):
    """research.md D4 : ecriture via fichier temporaire + os.replace."""
    chemin = tmp_path / "counter.txt"
    persist(7, chemin)
    persist(8, chemin)
    assert chemin.read_text(encoding="utf-8") == "0008\n"
    assert not (tmp_path / "counter.txt.tmp").exists()
    assert list(tmp_path.iterdir()) == [chemin]


def test_persistance_sur_chemin_inexistant(tmp_path):
    """Le répertoire parent existe déjà (racine du projet) mais le
    fichier est créé au premier usage."""
    chemin = tmp_path / "sous" / "counter.txt"
    chemin.parent.mkdir()
    persist(0, chemin)
    assert read_counter(chemin) == 0
