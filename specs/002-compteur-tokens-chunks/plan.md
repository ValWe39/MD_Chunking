# Implementation Plan: Compteur de tokens dans le rapport de relecture

**Branch**: `005-specify-token-compte` | **Date**: 2026-10-02 |
**Spec**: [spec.md](spec.md)

**Input**: Feature specification from
`/specs/002-compteur-tokens-chunks/spec.md`

## Summary

Afficher, pour chaque chunk du rapport de relecture (review.md), une
estimation approximative de son nombre de tokens — approche A de
l'assessment : heuristique locale zéro-dépendance, calculée au rendu
par division de la longueur du chunk par un ratio constant de
4 caractères par token, arrondi supérieur. Le découpage, l'index JSON
et l'interface CLI restent inchangés ; une mention d'en-tête
documente le caractère approximatif et modèle-agnostique de
l'estimation.

## Technical Context

**Language/Version**: Python 3.11+ (venv de développement en 3.14)

**Primary Dependencies**: haystack-ai 2.x, markdown-it-py 3.x —
aucune nouvelle dépendance (constitution III, FR-T02)

**Storage**: fichiers locaux uniquement ; aucune nouvelle donnée
persistée (l'estimation est calculée au rendu, jamais stockée)

**Testing**: pytest 8.x (suites unitaires et intégration existantes)

**Target Platform**: CLI, machine locale (Windows/Linux)

**Project Type**: cli

**Performance Goals**: négligeable — une division entière et un
arrondi par chunk ; sur le corpus Examples/ (415 chunks), surcoût
inférieur à la milliseconde

**Constraints**: hors-ligne total (constitution II, SC-T05) ;
déterminisme bit-à-bit (SC-005 de la feature 001, SC-T04) ; index
JSON inchangé (FR-T07)

**Scale/Scope**: ~50–150 chunks par document ; 415 chunks sur le
corpus Examples/ ; un seul module source touché (reviewer.py)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1
design.*

| Principe | Statut | Détail |
| -------- | ------ | ------ |
| I. Secrets | PASS | aucun identifiant, aucun réseau |
| II. Local-first | PASS | arithmétique locale, zéro réseau |
| III. Sans trackers | PASS | zéro dépendance nouvelle |
| IV. Simplicité | PASS | une constante, une fonction, un module |
| Path isolation | PASS | sorties existantes inchangées |
| Souveraineté | PASS | rien de nouveau à évaluer |

Aucune violation : la section de suivi de complexité est supprimée.

Re-check après Phase 1 : PASS — aucun changement de dépendance ni de
surface réseau ; toutes les décisions D1–D5 de research.md
respectent les principes I à IV.

## Project Structure

### Documentation (this feature)

```text
specs/002-compteur-tokens-chunks/
├── spec.md                # Spécification (/speckit-specify)
├── checklists/
│   └── requirements.md    # Checklist qualité (16/16)
├── plan.md                # Ce fichier (/speckit-plan)
├── research.md            # Phase 0 : décisions D1–D5
├── data-model.md          # Phase 1 : entités et garde-fous
├── quickstart.md          # Phase 1 : guide de validation
├── contracts/
│   └── review-render.md   # Phase 1 : contrat du rendu de relecture
└── tasks.md               # /speckit-tasks (non créé ici)
```

### Source Code (repository root)

```text
md_chunking/
└── reviewer.py            # Constante RATIO_CHARS_PER_TOKEN,
                           # estimate_tokens(), ligne de métadonnée
                           # par chunk, mention d'en-tête

tests/
├── unit/
│   └── test_reviewer.py    # Arrondi supérieur, chunk minimal,
                           # mention d'en-tête, « X car. » conservé,
                           # déterminisme du rendu
└── integration/
    └── test_cli.py         # Bout-en-bout : estimation présente dans
                            # review.md, aucun champ tokens dans
                            # l'index JSON
```

**Structure Decision**: aucun nouveau module — l'heuristique tient
en une constante et une fonction pure dans `reviewer.py`, son seul
consommateur (constitution IV). FR-T07 est garanti par
construction : l'estimation ne transite ni par `Chunk`
(`models.py`) ni par `indexer.py`.
