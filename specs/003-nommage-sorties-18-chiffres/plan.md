# Implementation Plan: Nommage des sorties (18 chiffres)

**Branch**: `003-nommage-sorties-18-chiffres` | **Date**: 2026-10-05 |
**Spec**: [spec.md](spec.md)

**Input**: Feature specification from
`/specs/003-nommage-sorties-18-chiffres/spec.md`

## Summary

Nommer chaque sortie par un nombre à 18 chiffres unique et décodable :
8 chiffres encodant les 5 premières lettres du nom de fichier source en
numération bijective base 26, 6 chiffres encodant les 4 premières
lettres du `document.title`, 4 chiffres d'un numéro d'occurrence
persisté localement — approche A de l'assessment. Les fichiers
s'écrivent à plat dans le dossier de sortie (`<18 chiffres>.json`,
`<18 chiffres>_review.md`), les sous-dossiers et l'option `--naming`
disparaissent ; le contenu des sorties (schéma JSON 1.0, review)
reste strictement inchangé.

## Technical Context

**Language/Version**: Python 3.11+ (pyproject : `>=3.11`)

**Primary Dependencies**: aucune nouvelle — bibliothèque standard
uniquement (`unicodedata`, `pathlib`) ; haystack-ai et markdown-it-py
inchangés

**Storage**: un nouveau fichier d'état local, `counter.txt`, à la
racine du projet (parent du paquet `md_chunking`), contenant
uniquement le dernier numéro d'occurrence ; ignoré par git (FR-014)

**Testing**: pytest 8.x (suites unitaires et intégration existantes,
adaptées)

**Target Platform**: CLI, machine locale (Windows/Linux)

**Project Type**: cli

**Performance Goals**: négligeable — encodage O(longueur du titre),
une lecture + une écriture fichier par document

**Constraints**: hors-ligne total (constitution II) ; contenu des
sorties inchangé (FR-010) ; concurrence non garantie en v1 (FR-013) ;
suppression publique de `--naming` (FR-012)

**Scale/Scope**: 3 modules source touchés (`cli.py` + 2 nouveaux),
7 fichiers de tests à adapter, ~50 tests au total

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1
design.*

| Principe | Statut | Détail |
| -------- | ------ | ------ |
| I. Secrets | PASS | aucun identifiant, aucun réseau |
| II. Local-first | PASS | compteur fichier texte local |
| III. Sans trackers | PASS | zéro dépendance nouvelle |
| IV. Simplicité | PASS | 2 modules minces, 0 option |
| Path isolation | PASS | compteur résolu depuis la structure |
| Data retention | PASS | compteur supprimable par l'utilisateur |

Note IV : le compteur introduit le premier état mutable de l'outil —
justifié par la spec (FR-006 à FR-009), minimal (un entier dans un
fichier texte, pas de base de données), et documenté. Aucune
violation : la section de suivi de complexité est supprimée.

Re-check après Phase 1 : PASS — les décisions D1–D6 de research.md
respectent les principes I à IV ; le contrat de nommage et le data
model n'ajoutent aucune dépendance ni surface réseau ; le fichier
compteur est couvert par le `.gitignore` (commit hygiene).

## Project Structure

### Documentation (this feature)

```text
specs/003-nommage-sorties-18-chiffres/
├── spec.md                # Spécification (/speckit-specify)
├── checklists/
│   └── requirements.md    # Checklist qualité (16/16)
├── plan.md                # Ce fichier (/speckit-plan)
├── research.md            # Phase 0 : décisions D1–D6
├── data-model.md          # Phase 1 : entités et garde-fous
├── quickstart.md          # Phase 1 : guide de validation
├── contracts/
│   ├── output-naming.md   # Phase 1 : format du nom à 18 chiffres
│   └── cli.md             # Phase 1 : surface CLI après retrait
└── tasks.md               # /speckit-tasks (non créé ici)
```

### Source Code (repository root)

```text
md_chunking/
├── naming.py              # Encodage bijectif base 26 : extraction
│                          # des lettres (NFKD, casse neutre),
│                          # encode/decode, construction du nom
├── counter.py             # Compteur d'occurrence : lecture au
│                          # démarrage, incrément, persistance
│                          # atomique après chaque document
└── cli.py                 # Retrait de --naming, _slugify,
                           # _subdir_name, _resolve_subdir ;
                           # écriture à plat dans --output

tests/
├── unit/
│   ├── test_naming.py     # Aller-retour, bornes, padding, accents,
│   │                      # casse, blocs vides, > 5 lettres
│   ├── test_counter.py    # Absent, corrompu, cycle 9999→0000,
│   │                      # persistance, atomicité
│   └── test_reviewer.py   # Inchangé (garde-fou)
└── integration/
    └── test_cli.py        # Sortie plate, noms uniques, compteur
                           # croissant, --naming rejetée,
                           # adaptation des 7 tests verrouillés

.gitignore                # Entrée counter.txt (FR-014)
README.md                 # Nommage documenté
```

**Structure Decision**: deux nouveaux modules plutôt qu'un
enrichissement de `cli.py` — `naming.py` est une fonction pure
testable en aller-retour (FR-003) et `counter.py` isole le seul état
mutable de l'outil (constitution IV : responsabilité unique). Les
entités existantes (`models.py`, `indexer.py`, `reviewer.py`,
`normalizer.py`, `overlap.py`, `splitter.py`, `presets.py`) ne sont
pas touchées : FR-010 est garanti par construction.
