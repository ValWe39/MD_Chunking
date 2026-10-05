"""Resolution des entrees CLI (feature 005) : fichiers individuels
et dossiers developpes en listes de ``.md`` triees.

Decisions D1 a D7 de research.md ; contrat
specs/005-dossier-entree-cli/contracts/cli.md.
"""

from pathlib import Path


class InputError(Exception):
    """Entree introuvable ou ni fichier ni dossier : echec rapide,
    code de sortie 2, aucun fichier ecrit (FR-005)."""


def _cle_de_tri(chemin: Path) -> tuple[str, str]:
    """Cle de tri : casse neutre d'abord, tie-break sur le nom brut
    pour stabiliser les differences de casse (FR-003, D3)."""
    return (chemin.name.lower(), chemin.name)


def _md_du_dossier(dossier: Path) -> list[Path]:
    """Fichiers ``.md`` de la surface du dossier (FR-002, FR-008),
    tries par la cle casse neutre (FR-003, D3)."""
    fichiers = [
        p for p in dossier.iterdir() if p.is_file() and p.suffix.lower() == ".md"
    ]
    return sorted(fichiers, key=_cle_de_tri)


def resolve_inputs(
    chemins: list[Path],
) -> tuple[list[Path], list[str]]:
    """Developpe chaque argument d'entree en documents a traiter.

    Un fichier est conserve tel quel (contrat 001 inchange) ; un
    dossier est remplace par les ``.md`` de sa surface, tries,
    insere a sa position (FR-001, FR-004) ; aucune deduplication
    (D6). Retourne (documents, avertissements) ; un dossier vide ou
    sans ``.md`` produit un avertissement et aucun document
    (FR-005b, D4). Leve ``InputError`` pour un chemin introuvable
    ou ni fichier ni dossier (FR-005, D5).
    """
    documents: list[Path] = []
    avertissements: list[str] = []
    for chemin in chemins:
        if chemin.is_file():
            documents.append(chemin)
        elif chemin.is_dir():
            md_du_dossier = _md_du_dossier(chemin)
            if not md_du_dossier:
                avertissements.append(f"Dossier sans fichier .md : {chemin}")
            documents.extend(md_du_dossier)
        else:
            raise InputError(f"fichier d'entree introuvable : {chemin}")
    return documents, avertissements
