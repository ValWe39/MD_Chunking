"""Contexte utilisateur embarque dans la sortie (feature 006).

Contrats specs/006-add-context/contracts/cli.md et
contracts/chunk-json.md ; decisions D1 a D9 de research.md.
Fonctions pures : la resolution ne lit que les entrees utilisateur
et ne modifie jamais le .json de contexte (FR-010).
"""

import json
import unicodedata
from pathlib import Path

from .inputs import InputError

CHAMPS_CONTEXTE = (
    "Typologie",
    "Auteur(s)",
    "Titre",
    "Editeur",
    "Date",
    "Référence",
    "Citation",
)

_AUTORISES = set("abcdefghijklmnopqrstuvwxyz0123456789_")


def cle_normale(nom: str) -> str:
    """Cle d'appariement (D3) : NFKD puis suppression des
    diacritiques, minuscules, espaces convertis en ``_``, seuls
    ``a-z 0-9 _`` conserves, tronquee a 8 caracteres."""
    if not nom:
        return ""
    ascii_part = unicodedata.normalize("NFKD", nom)
    ascii_part = ascii_part.encode("ascii", "ignore").decode("ascii")
    base = ascii_part.lower().replace(" ", "_")
    return "".join(caractere for caractere in base if caractere in _AUTORISES)[:8]


def charge_contexte(chemin: Path) -> dict | None:
    """Charge et valide un ``.json`` de contexte (D4) : exactement
    les sept cles attendues, ni manquante, ni supplementaire ;
    ``None`` si invalide (illisible, non-objet, cles en trop ou
    manquantes). Les valeurs ne sont jamais transformees (FR-004)."""
    try:
        donnees = json.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError):
        return None
    if not isinstance(donnees, dict):
        return None
    if set(donnees) != set(CHAMPS_CONTEXTE):
        return None
    return donnees


def apparie_niveau(
    mds: list[Path],
    jsons: list[Path],
) -> tuple[dict[Path, dict], list[str]]:
    """Apparie les ``.md`` et ``.json`` d'un meme niveau (D5).

    Branche couple (exactement 1 ``.md`` et 1 ``.json``) : le
    ``.json`` est le contexte du ``.md``, quel que soit son nom,
    apres validation (FR-002). Branche melee : un ``.md`` est
    apparie a un ``.json`` si leurs cles normalisees coincident et
    que la correspondance est unique des deux cotes (FR-005).
    Retourne (contextes par ``.md``, avertissements) ; tout etat
    degrade est un avertissement, jamais un echec (FR-008).
    """
    contextes: dict[Path, dict] = {}
    avertissements: list[str] = []
    if len(mds) == 1 and len(jsons) == 1:
        contexte = charge_contexte(jsons[0])
        if contexte is None:
            avertissements.append(f".json de contexte invalide : {jsons[0]}")
        else:
            contextes[mds[0]] = contexte
        return contextes, avertissements
    cles_md = {md: cle_normale(md.stem) for md in mds}
    cles_json = {js: cle_normale(js.stem) for js in jsons}
    cles_utilisees = set(cles_md.values())
    for md, cle in cles_md.items():
        candidats = [js for js in jsons if cles_json[js] == cle]
        if len(candidats) > 1:
            avertissements.append(f"Appariement ambigu pour {md}")
            continue
        if not candidats:
            continue
        concurrents = [m for m in mds if m != md and cles_md[m] == cle]
        if concurrents:
            avertissements.append(f"Appariement ambigu pour {md}")
            continue
        contexte = charge_contexte(candidats[0])
        if contexte is None:
            avertissements.append(f".json de contexte invalide : {candidats[0]}")
        else:
            contextes[md] = contexte
    for js, cle in cles_json.items():
        if cle not in cles_utilisees:
            avertissements.append(f".json de contexte orphelin : {js}")
    return contextes, avertissements


def _cle_de_tri(chemin: Path) -> tuple[str, str]:
    """Cle de tri casse neutre, tie-break sur le nom brut (D2,
    meme regle que la feature 005)."""
    return (chemin.name.lower(), chemin.name)


def _contenus_du_niveau(
    dossier: Path,
) -> tuple[list[Path], list[Path], list[Path]]:
    """Fichiers directement presents du niveau : ``.md`` et
    ``.json`` tries casse neutre, sous-dossiers tries casse neutre
    ; le contenu d'un sous-dossier ne compte jamais dans le niveau
    parent (D2, FR-003)."""
    mds: list[Path] = []
    jsons: list[Path] = []
    sous_dossiers: list[Path] = []
    for chemin in dossier.iterdir():
        if chemin.is_file():
            if chemin.suffix.lower() == ".md":
                mds.append(chemin)
            elif chemin.suffix.lower() == ".json":
                jsons.append(chemin)
        elif chemin.is_dir():
            sous_dossiers.append(chemin)
    return (
        sorted(mds, key=_cle_de_tri),
        sorted(jsons, key=_cle_de_tri),
        sorted(sous_dossiers, key=_cle_de_tri),
    )


def _niveau(dossier: Path) -> tuple[list[tuple[Path, dict | None]], list[str]]:
    """Traite un niveau : ``.md`` du niveau d'abord, puis descente
    profondeur d'abord dans les sous-dossiers (D2, FR-003) ; un
    niveau sans ``.md`` produit l'avertissement existant et la
    descente se poursuit."""
    documents: list[tuple[Path, dict | None]] = []
    avertissements: list[str] = []
    mds, jsons, sous_dossiers = _contenus_du_niveau(dossier)
    if not mds:
        avertissements.append(f"Dossier sans fichier .md : {dossier}")
    contextes, warns = apparie_niveau(mds, jsons)
    avertissements.extend(warns)
    documents.extend((md, contextes.get(md)) for md in mds)
    for sous_dossier in sous_dossiers:
        docs, warns = _niveau(sous_dossier)
        documents.extend(docs)
        avertissements.extend(warns)
    return documents, avertissements


def resolve_avec_contextes(
    chemins: list[Path],
) -> tuple[list[tuple[Path, dict | None]], list[str]]:
    """Developpe chaque argument en documents accompagnes de leur
    contexte (D1, FR-003).

    Un fichier individuel est conserve tel quel, jamais apparie
    (D8) ; un dossier est parcouru recursivement a toute profondeur
    (D2) ; un chemin introuvable ou ni-fichier-ni-dossier leve
    ``InputError`` (echec rapide code 2, FR-005 de la feature 005).
    Retourne (documents avec contexte, avertissements).
    """
    documents: list[tuple[Path, dict | None]] = []
    avertissements: list[str] = []
    for chemin in chemins:
        if chemin.is_file():
            documents.append((chemin, None))
        elif chemin.is_dir():
            docs, warns = _niveau(chemin)
            documents.extend(docs)
            avertissements.extend(warns)
        else:
            raise InputError(f"fichier d'entree introuvable : {chemin}")
    return documents, avertissements
