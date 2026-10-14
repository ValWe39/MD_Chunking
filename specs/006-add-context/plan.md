# Implementation Plan: Contexte et auto-identification dans la sortie JSON

**Branch**: `012-context-chunkingid` | **Date**: 2026-10-14 |
**Spec**: [spec.md](spec.md)

**Input**: Feature specification from
`/specs/006-add-context/spec.md`

## Summary

Ajouter l'option CLI `--add-context` : chaque dossier d'entrée est
alors parcouru récursivement (à toute profondeur, comptage par
niveau) pour apparier chaque `.md` à un `.json` de contexte — par
co-localisation (1 .md + 1 .json au même niveau, quel que soit le
nom, après validation du format à 7 clés exactes) ou, pour les
niveaux mélangés, par préfixe de 8 caractères normalisés ; tout
état dégradé (invalide, ambigu, orphelin, niveau sans .md) produit
un avertissement et le traitement classique, jamais d'échec du lot.
Chaque JSON de sortie embarque `document.chunkingid` (nom du
fichier de sortie sans extension, inconditionnel) et, pour chaque
document apparié, `document.context` (7 champs verbatim, vides
compris). Sans l'option, la résolution de la feature 005 reste
inchangée et la seule différence de sortie est `chunkingid`.
Découpage, compteur et nommage restent strictement inchangés
(FR-009, verdict GO de l'assessment contexte-chunkingid).

## Technical Context

**Language/Version**: Python 3.11+ (pyproject : `>=3.11`)

**Primary Dependencies**: aucune nouvelle — bibliothèque standard
uniquement (`json.loads`, `unicodedata.normalize`, `pathlib`) ;
argparse, haystack-ai et markdown-it-py inchangés

**Storage**: aucun nouvel état — `counter.txt` (feature 003)
inchangé ; le `.json` de contexte est lu et embarqué, jamais
copié, renommé ni déplacé (FR-010)

**Testing**: pytest 8.x — nouvelle suite unitaire pour
l'appariement (`tests/unit/test_contexts.py`), suite d'intégration
CLI étendue (`tests/integration/test_cli.py`) sur des copies
temporaires des dossiers d'exemples `Examples/Extension/`,
`tests/unit/test_indexer.py` mis à jour pour `chunkingid`/`context`,
compteur isolé en `tmp_path` comme dans les tests actuels

**Target Platform**: CLI, machine locale (Windows/PowerShell
documenté au README, Linux équivalent)

**Project Type**: cli

**Performance Goals**: négligeable — un listing par niveau de
dossier, tri O(n log n) par niveau, une lecture de `.json` par
candidat contexte

**Constraints**: hors-ligne total (constitution II) ; aucune
écriture hors `--output` ; sans `--add-context`, sorties identiques
au comportement actuel au champ `chunkingid` près (SC-002) ; ordre
de traitement déterministe pour la reproductibilité des occurrences
(SC-002, FR-009) ; valeurs de contexte jamais transformées (FR-004)

**Scale/Scope**: 1 module mince nouveau (`md_chunking/contexts.py`,
quatre fonctions publiques au plus), 2 modules retouchés
(`cli.py` : option et résolveur ; `indexer.py` : deux champs),
1 suite unitaire nouvelle, ~15 nouveaux tests

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1
design.*

| Principe | Statut | Détail |
| -------- | ------ | ------ |
| I. Secrets | PASS | aucun identifiant, aucun réseau |
| II. Local-first | PASS | lecture de fichiers locaux uniquement |
| III. Sans trackers | PASS | zéro dépendance nouvelle |
| IV. Simplicité | PASS* | 1 module mince, 1 option CLI justifiée |
| Path isolation | PASS | seules les entrées utilisateur sont listées |
| Data retention | PASS | aucun fichier d'état nouveau, contexte embarqué |
| Config validation | PASS | introuvable -> echec rapide code 2 inchange |

Note IV : l'option `--add-context` est la seule nouvelle surface
CLI, exigée par la spec (FR-001) ; l'appariement est une fonction
pure dans un module dédié, sur le modèle de `naming.py` et
`inputs.py`. La récursivité est circonscrite au mode actif
(amendement FR-008 de la spec 005, assumé en spec FR-003). Aucune
violation : la section de suivi de complexité est supprimée.

Re-check après Phase 1 : PASS — les décisions D1-D9 de research.md
respectent les principes I à IV ; les contrats `cli.md` et
`chunk-json.md` n'ajoutent qu'une option, des règles de résolution
conditionnelles et deux champs de sortie ; le data model
n'introduit aucune entité persistante nouvelle et ne copie jamais
le contexte sur disque.

## Project Structure

### Documentation (this feature)

```text
specs/006-add-context/
├── checklists/requirements.md  # Qualite (/speckit-specify, revalidee par /speckit-clarify)
├── spec.md                # Specification (/speckit-specify, /speckit-clarify)
├── plan.md                # Ce fichier (/speckit-plan)
├── research.md            # Phase 0 (/speckit-plan)
├── data-model.md          # Phase 1 (/speckit-plan)
├── quickstart.md          # Phase 1 (/speckit-plan)
├── contracts/
│   ├── cli.md             # Phase 1 : evolution du contrat CLI
│   └── chunk-json.md      # Phase 1 : evolution du contrat JSON de sortie
└── tasks.md               # Phase 2 (/speckit-tasks - pas encore cree)
```

### Source Code (repository root)

```text
md_chunking/
├── contexts.py            # NOUVEAU : normalisation, validation,
│                          #   cascade d'appariement, resolution recursive
├── cli.py                 # MODIFIE : option --add-context, choix du
│                          #   resolveur, passage nom + contexte a l'index
├── indexer.py             # MODIFIE : build_index emet document.chunkingid
│                          #   (toujours) et document.context (si apparie)
└── ...                    # INCHANGE : inputs.py, counter.py, naming.py,
                           #   models.py, normalizer.py, overlap.py,
                           #   presets.py, reviewer.py, splitter.py

tests/
├── unit/
│   ├── test_contexts.py   # NOUVEAU : normalisation, validation format,
│   │                      #   cascade, etats limites, exemples copies
│   └── test_indexer.py    # MIS A JOUR : chunkingid, context verbatim
└── integration/
    └── test_cli.py        # ETENDU : --add-context sur copies des exemples,
                           #   avertissements, sorties classiques intactes
```

**Structure Decision**: un module dédié `md_chunking/contexts.py`
pour la normalisation, la validation de format, la cascade et la
résolution récursive (fonctions pures), sur le modèle des modules
minces `inputs.py` et `naming.py` ; `cli.py` choisit le résolveur
selon l'option (résolution de surface de la feature 005 sans
`--add-context`, récursive avec) et `indexer.py` reçoit le nom de
sortie et l'éventuel contexte — la boucle de traitement, le
compteur et le nommage restent inchangés.
