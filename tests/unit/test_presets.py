"""Tests unitaires des presets et de la validation CLI (T023, FR-006,
FR-012, US-4)."""

import pytest

from md_chunking.cli import ConfigError, _preset_effectif, parse_args
from md_chunking.presets import PRESETS, get_preset

FIXTURE = "tests/fixtures/article-propre.md"


def test_valeurs_exactes_des_presets():
    """Valeurs verbatim de data-model.md (T009)."""
    assert PRESETS["documentation"].chunk_min == 100
    assert PRESETS["documentation"].chunk_max == 1000
    assert PRESETS["documentation"].overlap_pct == 15
    assert PRESETS["articles"].chunk_min == 150
    assert PRESETS["articles"].chunk_max == 1500
    assert PRESETS["articles"].overlap_pct == 13
    assert PRESETS["conversations"].chunk_min == 50
    assert PRESETS["conversations"].chunk_max == 500
    assert PRESETS["conversations"].overlap_pct == 10
    assert PRESETS["code"].chunk_min == 200
    assert PRESETS["code"].chunk_max == 2000
    assert PRESETS["code"].overlap_pct == 15
    assert PRESETS["livre"].chunk_min == 150
    assert PRESETS["livre"].chunk_max == 1200
    assert PRESETS["livre"].overlap_pct == 15


def test_typologie_inconnue_refusee():
    with pytest.raises(KeyError):
        PRESETS["inconnue"]
    with pytest.raises(ValueError, match="typologie inconnue"):
        get_preset("inconnue")


def test_surcharge_explicite_des_bornes():
    args = parse_args([FIXTURE, "--min", "200", "--max", "1800", "--overlap", "20"])
    preset, _ = _preset_effectif(args)
    assert (preset.chunk_min, preset.chunk_max, preset.overlap_pct) == (
        200,
        1800,
        20,
    )


def test_defauts_du_preset_appliques():
    args = parse_args([FIXTURE])
    preset, nom = _preset_effectif(args)
    assert nom == "documentation"
    assert (preset.chunk_min, preset.chunk_max) == (100, 1000)


def test_guillemets_actifs_par_defaut():
    """Bug chunking-quotes-words : regle 1 activee sans option."""
    assert PRESETS["documentation"].guillemets is True
    args = parse_args([FIXTURE])
    assert args.guillemets is True
    preset, _ = _preset_effectif(args)
    assert preset.guillemets is True


def test_option_no_guillemets_desactive():
    args = parse_args([FIXTURE, "--no-guillemets"])
    preset, _ = _preset_effectif(args)
    assert preset.guillemets is False


def test_min_superieur_ou_egal_max_refuse():
    with pytest.raises(ConfigError, match="--min"):
        parse_args([FIXTURE, "--min", "1000", "--max", "100"])


def test_overlap_hors_plage_refuse():
    with pytest.raises(ConfigError, match="--overlap"):
        parse_args([FIXTURE, "--overlap", "21"])
    with pytest.raises(ConfigError, match="--overlap"):
        parse_args([FIXTURE, "--overlap", "-1"])


def test_min_negatif_refuse():
    with pytest.raises(ConfigError, match="--min"):
        parse_args([FIXTURE, "--min", "-5"])


def test_fichier_introuvable_valide_par_la_resolution():
    """Feature 005 : parse_args ne valide plus l'existence des
    entrees ; c'est resolve_inputs qui tranche (InputError,
    couvert par tests/unit/test_inputs.py et l'integration)."""
    args = parse_args(["inexistant.md"])
    assert [str(p) for p in args.fichiers] == ["inexistant.md"]
