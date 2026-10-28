# Implementation Plan: Appariement robuste .md/.json sur préfixes longs

**Branch**: `013-fix-lien` | **Date**: 2026-10-28 |
**Spec**: [spec.md](spec.md)

**Input**: Feature specification from
`/specs/007-robust-pairing/spec.md`

## Summary

Remplacer la troncature fixe à 8 caractères de la clé normalisée
par une extension progressive par paliers (8, 12, 16, 20, 24, …)
dans `apparie_niveau()` : chaque `.md` non résolu avance
indépendamment jusqu'à unicité ou longueur maximale. Cela
résout les collisions sur préfixes longs (cas Fipeco,
`Examples/Pairing/`) sans casser les appariements existants
(`Examples/Extension/`). `cle_normale()` retourne la chaîne
normalisée complète sans troncature. La branche « couple »
(1 `.md` + 1 `.json`), le comportement sans `--add-context`,
les messages d'avertissement et le nommage restent inchangés.

## Technical Context

**Language/Version**: Python 3.11+ (pyproject : `>=3.11`)

**Primary Dependencies**: aucune nouvelle — bibliothèque
standard uniquement (`unicodedata`, `pathlib`) ; `json`,
haystack-ai et markdown-it-py inchangés

**Storage**: aucun nouvel état — `counter.txt` (feature 003)
inchangé ; les fichiers `.md` et `.json` ne sont jamais modifiés

**Testing**: pytest 8.x — modification de
`tests/unit/test_contexts.py` (2 tests d'ambiguïté adaptés,
nouveaux tests pour les paliers et le cas Fipeco), extension de
`tests/integration/test_cli.py` sur `Examples/Pairing/` copié
en `tmp_path`, compteur isolé en `tmp_path`

**Target Platform**: CLI, machine locale (Windows/PowerShell
documenté au README, Linux équivalent)

**Project Type**: cli

**Performance Goals**: négligeable — boucle sur paliers
O(p × n²) où p = nombre de paliers (~6 max) et n = nombre de
fichiers par niveau ; pour un usage local mono-utilisateur
(quelques dizaines de fichiers), temps imperceptible

**Constraints**: hors-ligne total (constitution II) ; aucune
écriture hors `--output` ; sans `--add-context`, comportement
identique (FR-007) ; ordre de traitement déterministe (D2 de la
spec 006) ; valeurs de contexte jamais transformées ; zéro faux
positif (FR-009)

**Scale/Scope**: 1 module modifié (`md_chunking/contexts.py`,
2 fonctions modifiées : `cle_normale` et `apparie_niveau`),
1 suite unitaire adaptée, ~5 nouveaux tests, 1 contrat CLI
amendé, 1 data-model amendé

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after
Phase 1 design.*

| Principe | Statut | Détail |
| -------- | ------ | ------ |
| I. Secrets | PASS | aucun identifiant, aucun réseau |
| II. Local-first | PASS | lecture de fichiers locaux uniquement |
| III. Sans trackers | PASS | zéro dépendance nouvelle |
| IV. Simplicité | PASS | 1 module modifié, 2 fonctions modifiées |
| Path isolation | PASS | seules les entrées utilisateur sont listées |
| Data retention | PASS | aucun fichier d'état nouveau |
| Config validation | PASS | introuvable -> échec rapide code 2 inchangé |

Note IV : l'extension progressive remplace un comportement
existant (troncature fixe) sans ajouter de surface CLI ni de
nouvelle option ; la complexité ajoutée est confinée à la
boucle d'appariement dans `apparie_niveau()`. Aucune
violation : la section de suivi de complexité est supprimée.

Re-check après Phase 1 : PASS — les décisions D1-D6 de
research.md respectent les principes I à IV ; le contrat CLI
amendé ne change que la section « Niveau mélangé » ; le data
model ne modifie que la définition de la clé d'appariement.

## Project Structure

### Documentation (this feature)

```text
specs/007-robust-pairing/
├── checklists/requirements.md  # Qualité (specify, clarify)
├── spec.md                # Spécification (specify, clarify)
├── plan.md                # Ce fichier (/speckit-plan)
├── research.md            # Phase 0 (/speckit-plan)
├── data-model.md          # Phase 1 (/speckit-plan)
├── quickstart.md          # Phase 1 (/speckit-plan)
├── contracts/
│   └── cli.md             # Phase 1 : amendement du contrat CLI
└── tasks.md               # Phase 2 (/speckit-tasks - pas encore créé)
```

### Source Code (repository root)

```text
md_chunking/
├── contexts.py            # MODIFIÉ : cle_normale sans troncature,
│                          #   apparie_niveau avec boucle par paliers
└── ...                    # INCHANGÉ : cli.py, indexer.py, inputs.py,
                           #   counter.py, naming.py, models.py,
                           #   normalizer.py, overlap.py, presets.py,
                           #   reviewer.py, splitter.py

tests/
├── unit/
│   └── test_contexts.py   # MODIFIÉ : 2 tests d'ambiguïté adaptés,
│                          #   nouveaux tests paliers + cas Fipeco
└── integration/
    └── test_cli.py        # ÉTENDU : --add-context sur Examples/Pairing/
                           #   copié en tmp_path
```

**Structure Decision**: modification confinée à
`md_chunking/contexts.py` (2 fonctions) et aux tests associés ;
`cli.py` et `indexer.py` ne sont pas touchés (l'interface
`resolve_avec_contextes` et le bloc `document` de sortie sont
inchangés). Le contrat CLI est amendé (section « Niveau
mélangé »), le contrat chunk-json.md est inchangé.
