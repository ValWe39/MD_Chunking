"""Tests unitaires de validation du CLI (feature 004 : --tokencpte)."""

from pathlib import Path

import pytest

from md_chunking.cli import ConfigError, parse_args

FIXTURES = Path(__file__).parents[1] / "fixtures"
PROPRE = FIXTURES / "article-propre.md"


def test_tokencpte_absent_prend_le_defaut():
    """FR-001 : sans option, le ratio effectif est le defaut 3,5."""
    args = parse_args([str(PROPRE)])
    assert args.tokencpte == 3.5


def test_tokencpte_explicite_accepte():
    """FR-002 : toute valeur decimale valide remplace le defaut."""
    args = parse_args([str(PROPRE), "--tokencpte", "3.2"])
    assert args.tokencpte == 3.2


def test_tokencpte_bornes_acceptees():
    """FR-003 : 0,5 et 10 (bornes incluses) sont valides."""
    assert parse_args([str(PROPRE), "--tokencpte", "0.5"]).tokencpte == 0.5
    assert parse_args([str(PROPRE), "--tokencpte", "10"]).tokencpte == 10.0


def test_tokencpte_hors_bornes_rejete():
    """FR-003 : 0, negatif et > 10 echouent au parsing (ConfigError)."""
    for valeur in ("0", "-1", "10.001", "12"):
        with pytest.raises(ConfigError):
            parse_args([str(PROPRE), "--tokencpte", valeur])


def test_tokencpte_message_explicite_les_bornes():
    """FR-003 : le message d'erreur donne les bornes (contrat
    contracts/cli.md)."""
    with pytest.raises(ConfigError) as err:
        parse_args([str(PROPRE), "--tokencpte", "12"])
    assert "--tokencpte doit etre > 0 et <= 10 (recu : 12.0)" in str(err.value)


def test_tokencpte_virgule_refusee_au_parsing():
    """FR-003 : separateur virgule mal forme -> erreur argparse
    standard, code de sortie 2 (comme --min abc)."""
    with pytest.raises(SystemExit) as exc:
        parse_args([str(PROPRE), "--tokencpte", "3,5"])
    assert exc.value.code == 2
