"""Tests unitaires du contexte utilisateur (feature 006, T007,
T010, T013 : normalisation, validation, cascade, resolution)."""

import json
from pathlib import Path

import pytest

from md_chunking.contexts import (
    CHAMPS_CONTEXTE,
    apparie_niveau,
    charge_contexte,
    cle_normale,
    resolve_avec_contextes,
)
from md_chunking.inputs import InputError

CONTEXTE_VALIDE = {
    "Typologie": "Compte-rendu",
    "Auteur(s)": ["Assemblée nationale"],
    "Titre": "Compte rendu de la première séance",
    "Editeur": "Assemblée nationale",
    "Date": "09 octobre 2026",
    "Référence": "",
    "Citation": "Assemblée nationale, 09 octobre 2026",
}


def _ecrire_md(dossier: Path, nom: str) -> Path:
    chemin = dossier / nom
    chemin.write_text("# Titre\n\nTexte du document.\n", encoding="utf-8")
    return chemin


def _ecrire_contexte(dossier: Path, nom: str, donnees: dict | None = None) -> Path:
    chemin = dossier / nom
    chemin.write_text(
        json.dumps(
            donnees if donnees is not None else CONTEXTE_VALIDE, ensure_ascii=False
        ),
        encoding="utf-8",
    )
    return chemin


def test_champs_contexte_exacts():
    """FR-004 : exactement les sept cles attendues."""
    assert CHAMPS_CONTEXTE == (
        "Typologie",
        "Auteur(s)",
        "Titre",
        "Editeur",
        "Date",
        "Référence",
        "Citation",
    )


# --- cle_normale (D3) ---


def test_cle_normale_exemples_reels():
    """Les trois couples d'Examples/Extension coincident (D3,
    valide sur le corpus fourni par l'utilisateur)."""
    assert cle_normale("premiere-0034") == "premiere"
    assert cle_normale("premiere-seance-du-v-nettoye") == "premiere"
    assert cle_normale("AN_Rappo-0032") == "an_rappo"
    assert cle_normale("AN_Rapport") == "an_rappo"
    assert cle_normale("Ecalle_o-0040") == "ecalle_o"
    assert cle_normale("Ecalle_ouvrage") == "ecalle_o"


def test_cle_normale_accents_et_espaces():
    """Le .md peut porter accents et espaces que le .json convertit
    en _ ou simplifie (clarification du 2026-10-14)."""
    assert cle_normale("Mécomptes publics") == "mecompte"
    assert cle_normale("Rapport d'information") == "rapport_"
    assert cle_normale("") == ""


# --- charge_contexte (D4) ---


def test_charge_contexte_valide(tmp_path):
    chemin = _ecrire_contexte(tmp_path, "contexte.json")
    assert charge_contexte(chemin) == CONTEXTE_VALIDE
    assert charge_contexte(chemin)["Référence"] == ""


def test_charge_contexte_cle_en_trop_rejete(tmp_path):
    donnees = dict(CONTEXTE_VALIDE, Extra="refuse")
    chemin = _ecrire_contexte(tmp_path, "contexte.json", donnees)
    assert charge_contexte(chemin) is None


def test_charge_contexte_cle_manquante_rejetee(tmp_path):
    donnees = {c: v for c, v in CONTEXTE_VALIDE.items() if c != "Editeur"}
    chemin = _ecrire_contexte(tmp_path, "contexte.json", donnees)
    assert charge_contexte(chemin) is None


def test_charge_contexte_illisible_rejete(tmp_path):
    chemin = tmp_path / "contexte.json"
    chemin.write_bytes(b"\xff\xfe pas du json")
    assert charge_contexte(chemin) is None


def test_charge_contexte_non_objet_rejete(tmp_path):
    chemin = tmp_path / "contexte.json"
    chemin.write_text('["liste"]', encoding="utf-8")
    assert charge_contexte(chemin) is None


# --- apparie_niveau : branche couple (D5, FR-002) ---


def test_couple_unique_peu_importe_le_nom(tmp_path):
    md = _ecrire_md(tmp_path, "un-doc.md")
    js = _ecrire_contexte(tmp_path, "contexte-2026.json")
    contextes, avertissements = apparie_niveau([md], [js])
    assert contextes == {md: CONTEXTE_VALIDE}
    assert avertissements == []


def test_couple_invalide_avertit_pas_de_contexte(tmp_path):
    md = _ecrire_md(tmp_path, "un-doc.md")
    js = _ecrire_contexte(tmp_path, "c.json", {"Typologie": "x"})
    contextes, avertissements = apparie_niveau([md], [js])
    assert contextes == {}
    assert avertissements == [f".json de contexte invalide : {js}"]


# --- apparie_niveau : branche melee (D5, FR-005) ---


def test_melee_appariement_unique_par_prefixe(tmp_path):
    md_a = _ecrire_md(tmp_path, "premiere-seance-du-v.md")
    md_b = _ecrire_md(tmp_path, "autre.md")
    js_a = _ecrire_contexte(tmp_path, "premiere-0034.json")
    js_orphelin = _ecrire_contexte(tmp_path, "zzz-0099.json")
    contextes, avertissements = apparie_niveau([md_a, md_b], [js_a, js_orphelin])
    assert contextes == {md_a: CONTEXTE_VALIDE}
    assert avertissements == [f".json de contexte orphelin : {js_orphelin}"]


def test_melee_ambiguite_deux_json_meme_prefixe(tmp_path):
    md = _ecrire_md(tmp_path, "premiere-seance.md")
    _ecrire_contexte(tmp_path, "premiere-0034.json")
    _ecrire_contexte(tmp_path, "premiere-0035.json")
    jsons = sorted(tmp_path.glob("premiere-003*.json"))
    contextes, avertissements = apparie_niveau([md], jsons)
    assert contextes == {}
    assert avertissements == [f"Appariement ambigu pour {md}"]


def test_melee_ambiguite_json_partage_par_deux_md(tmp_path):
    md_1 = _ecrire_md(tmp_path, "an_rappo-1.md")
    md_2 = _ecrire_md(tmp_path, "an_rappo-2.md")
    js = _ecrire_contexte(tmp_path, "an_rappo-0032.json")
    contextes, avertissements = apparie_niveau([md_1, md_2], [js])
    assert contextes == {}
    assert sorted(avertissements) == sorted(
        [f"Appariement ambigu pour {md_1}", f"Appariement ambigu pour {md_2}"]
    )


def test_melee_json_invalide_apparie_avertit(tmp_path):
    md = _ecrire_md(tmp_path, "an_rapport.md")
    js = _ecrire_contexte(tmp_path, "an_rappo-0032.json", {"pas": "bon"})
    contextes, avertissements = apparie_niveau([md], [js])
    assert contextes == {}
    assert avertissements == [f".json de contexte invalide : {js}"]


def test_melee_md_sans_candidat_silencieux(tmp_path):
    """US-3 : un .md sans partenaire part en classique, sans
    avertissement (seuls les .json orphelins sont signales)."""
    md = _ecrire_md(tmp_path, "isole.md")
    contextes, avertissements = apparie_niveau([md], [])
    assert contextes == {}
    assert avertissements == []


# --- resolve_avec_contextes (D1, D2, D8) ---


def test_fichier_individuel_jamais_apparie(tmp_path):
    """D8 : un .md passe en direct n'est jamais apparie, meme avec
    un .json voisin."""
    md = _ecrire_md(tmp_path, "un-doc.md")
    _ecrire_contexte(tmp_path, "un-doc.json")
    documents, avertissements = resolve_avec_contextes([md])
    assert documents == [(md, None)]
    assert avertissements == []


def test_introuvable_leve_inputerror(tmp_path):
    absent = tmp_path / "absent.md"
    with pytest.raises(InputError):
        resolve_avec_contextes([absent])


def test_dossier_couple_en_un_niveau(tmp_path):
    """US-1 : 1 .md + 1 .json quelconque + autres fichiers ignores
    (FR-002)."""
    dossier = tmp_path / "couple"
    dossier.mkdir()
    md = _ecrire_md(dossier, "un-doc.md")
    _ecrire_contexte(dossier, "contexte-2026.json")
    (dossier / "notes.txt").write_text("ignore", encoding="utf-8")
    documents, avertissements = resolve_avec_contextes([dossier])
    assert documents == [(md, CONTEXTE_VALIDE)]
    assert avertissements == []


def test_recursion_profondeur_d_abord(tmp_path):
    """US-2 (FR-003, D2) : .md du niveau puis sous-dossiers tries
    casse neutre ; chaque couple reconnu dans son sous-dossier."""
    racine = tmp_path / "racine"
    racine.mkdir()
    md_racine = _ecrire_md(racine, "a-racine.md")
    sous_1 = racine / "b-sous"
    sous_1.mkdir()
    md_1 = _ecrire_md(sous_1, "doc-1.md")
    _ecrire_contexte(sous_1, "contexte-1.json")
    sous_2 = racine / "a-sous"
    sous_2.mkdir()
    md_2 = _ecrire_md(sous_2, "doc-2.md")
    documents, avertissements = resolve_avec_contextes([racine])
    assert [chemin for chemin, _ in documents] == [
        md_racine,
        md_2,
        md_1,
    ]
    contextes = dict(documents)
    assert contextes[md_racine] is None
    assert contextes[md_2] is None
    assert contextes[md_1] == CONTEXTE_VALIDE
    assert avertissements == []


def test_niveau_intermediaire_sans_md_avertit_et_descend(tmp_path):
    """FR-003 : avertissement pour le niveau, descente poursuivie,
    couples des sous-niveaux traites."""
    racine = tmp_path / "racine"
    racine.mkdir()
    sous = racine / "couple"
    sous.mkdir()
    md = _ecrire_md(sous, "un-doc.md")
    _ecrire_contexte(sous, "ctx.json")
    documents, avertissements = resolve_avec_contextes([racine])
    assert documents == [(md, CONTEXTE_VALIDE)]
    assert avertissements == [f"Dossier sans fichier .md : {racine}"]


def test_imbrication_trois_niveaux(tmp_path):
    """D2 : la descente va a toute profondeur."""
    racine = tmp_path / "n1"
    racine.mkdir()
    n2 = racine / "n2"
    n2.mkdir()
    n3 = n2 / "n3"
    n3.mkdir()
    md = _ecrire_md(n3, "profond.md")
    _ecrire_contexte(n3, "profond-0099.json")
    documents, avertissements = resolve_avec_contextes([racine])
    assert documents == [(md, CONTEXTE_VALIDE)]
    assert avertissements == [
        f"Dossier sans fichier .md : {racine}",
        f"Dossier sans fichier .md : {n2}",
    ]


def test_dossier_vide_sans_documents(tmp_path):
    vide = tmp_path / "vide"
    vide.mkdir()
    documents, avertissements = resolve_avec_contextes([vide])
    assert documents == []
    assert avertissements == [f"Dossier sans fichier .md : {vide}"]


def test_ordre_arguments_preserve(tmp_path):
    """D1 : fichiers et dossiers dans l'ordre de la ligne de
    commande, jamais dedupliques."""
    dossier = tmp_path / "couple"
    dossier.mkdir()
    md_dossier = _ecrire_md(dossier, "un-doc.md")
    _ecrire_contexte(dossier, "ctx.json")
    md_isole = _ecrire_md(tmp_path, "z-isole.md")
    documents, _ = resolve_avec_contextes([md_isole, dossier])
    assert [chemin for chemin, _ in documents] == [md_isole, md_dossier]
