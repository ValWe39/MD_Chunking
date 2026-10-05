# Implementation Plan: Entrée dossier pour la CLI

**Branch**: `011-folder-in-input` | **Date**: 2026-10-05 |
**Spec**: [spec.md](spec.md)

**Input**: Feature specification from
`/specs/005-dossier-entree-cli/spec.md`

## Summary

Étendre l'argument positionnel de la CLI pour accepter, à côté des
fichiers actuels, un chemin de dossier : lors de la validation de
configuration, chaque dossier est résolu en la liste triée (casse
neutre) des fichiers `.md` de sa surface, insérée à sa position dans
l'ordre des arguments, sans déduplication ni récursivité. Un dossier
vide ou sans `.md` aboutit au code 0 avec un avertissement, sans
aucune écriture ; un chemin introuvable échoue au code 2. La boucle de
traitement, le compteur d'occurrence et le nommage des sorties
restent strictement inchangés (exigence « sans modifier
substantiellement », verdict GO de l'assessment dossier-entree-md).

## Technical Context

**Language/Version**: Python 3.11+ (pyproject : `>=3.11`)

**Primary Dependencies**: aucune nouvelle — bibliothèque standard
uniquement (`pathlib.Path.iterdir`, comparaison de suffixe) ;
argparse, haystack-ai et markdown-it-py inchangés

**Storage**: aucun nouvel état — `counter.txt` (feature 003) reste
l'unique fichier d'état local, non consulté si la résolution ne
produit aucun document

**Testing**: pytest 8.x — nouvelle suite unitaire pour la résolution
d'entrée (`tests/unit/test_inputs.py`), suite d'intégration CLI
existante étendue (`tests/integration/test_cli.py`), compteur isolé
en `tmp_path` comme dans les tests actuels

**Target Platform**: CLI, machine locale (Windows/PowerShell
documenté au README, Linux équivalent)

**Project Type**: cli

**Performance Goals**: négligeable — un listing de dossier par
argument dossier, résolution en O(n log n) sur les noms

**Constraints**: hors-ligne total (constitution II) ; aucune
écriture hors `--output` ; contenu des sorties inchangé (FR-007) ;
aucune récursivité ni motif joker (FR-008) ; ordre déterministe pour
SC-002 (FR-003)

**Scale/Scope**: 1 nouveau module mince (`md_chunking/inputs.py`,
une fonction publique), 1 module retouché (`cli.py` : boucle de
validation remplacée par un appel, boucle de traitement inchangée),
2 suites de tests, ~10 nouveaux tests

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1
design.*

| Principe | Statut | Détail |
| -------- | ------ | ------ |
| I. Secrets | PASS | aucun identifiant, aucun réseau |
| II. Local-first | PASS | listing de dossier local, aucun accès distant |
| III. Sans trackers | PASS | zéro dépendance nouvelle |
| IV. Simplicité | PASS | 1 module mince, 0 nouvelle option CLI |
| Path isolation | PASS | seules les entrées utilisateur sont listées |
| Data retention | PASS | aucun fichier d'état nouveau |
| Config validation | PASS | introuvable -> echec rapide code 2 |

Note IV : la résolution d'entrée n'ajoute aucune option, aucune
récursivité ni aucun motif ; le périmètre borné de la spec
(FR-001 à FR-009) est couvert par une fonction unique. Aucune
violation : la section de suivi de complexité est supprimée.

Re-check après Phase 1 : PASS — les décisions D1-D7 de research.md
respectent les principes I à IV ; le contrat CLI n'ajoute que des
règles de résolution d'entrée et un message d'avertissement ; le
data model n'introduit aucune entité persistante nouvelle.

## Project Structure

### Documentation (this feature)

```text
specs/005-dossier-entree-cli/
├── checklists/requirements.md  # Qualite (/speckit-specify, revalidee par /speckit-clarify)
├── spec.md                # Specification (/speckit-specify, /speckit-clarify)
├── plan.md                # Ce fichier (/speckit-plan)
├── research.md            # Phase 0 (/speckit-plan)
├── data-model.md          # Phase 1 (/speckit-plan)
├── quickstart.md          # Phase 1 (/speckit-plan)
├── contracts/
│   └── cli.md             # Phase 1 : evolution du contrat CLI
└── tasks.md               # Phase 2 (/speckit-tasks - pas encore cree)
```

### Source Code (repository root)

```text
md_chunking/
├── inputs.py             # NOUVEAU : resolution dossier -> liste .md triee
├── cli.py                 # MODIFIE : validation via inputs.py, boucle inchangee
└── ...                    # INCHANGE : counter.py, naming.py, normalizer.py,
                           #   indexer.py, models.py, overlap.py, presets.py,
                           #   reviewer.py, splitter.py

tests/
├── unit/
│   └── test_inputs.py     # NOUVEAU : tri, filtre .md, casse, cas limites
└── integration/
    └── test_cli.py       # ETENDU : dossier, melange, vide, doublons
```

**Structure Decision**: un module dédié `md_chunking/inputs.py` pour
la résolution (une fonction publique), sur le modèle des modules
minces `naming.py` et `counter.py` de la feature 003 ; `cli.py`
remplace uniquement sa boucle de validation d'entrée par l'appel à
cette fonction — la boucle de traitement de `main` et tout le
pipeline aval restent inchangés.
