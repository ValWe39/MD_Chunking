# Implementation Plan: Ratio caracteres/tokens reglable en CLI

**Branch**: `010-fix-token-cpte` | **Date**: 2026-10-05 |
**Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/004-ratio-tokens-cli/spec.md`

## Summary

Rendre le ratio caracteres→tokens de l'estimation du rapport de relecture
parametrable via une option CLI dediee `--tokencpte` (decimal, bornes
]0 ; 10]), avec un defaut recale de 4 a 3,5 caracteres par token pour le
corpus francais. L'estimation reste locale, deterministe et
modele-agnostique ; le decoupage, l'index JSON, le nommage des sorties et
le compteur d'occurrence ne changent pas. Les artefacts de la feature 002
(FR-T02 « sans parametre d'interface ») sont amendes par la presente
feature, reouverture assumee et validee par l'assessment
tokencpte-flottant (verdict GO).

## Technical Context

**Language/Version**: Python 3.11+ (pyproject : requires-python >=3.11) ;
le module standard `fractions` est disponible sans dependance.

**Primary Dependencies**: inchangees — haystack-ai 2.x, markdown-it-py 3.x.
Aucune dependance nouvelle : la feature n'ajoute ni tokenizer, ni
bibliotheque de calcul (constitution III).

**Storage**: aucun — le ratio est un parametre d'execution transitoire,
jamais persiste ; `counter.txt` (compteur d'occurrence) reste le seul etat
local de l'outil, non concerne.

**Testing**: pytest (dev), suite existante de 89 tests ; tests unitaires
dans tests/unit/test_reviewer.py et tests d'integration dans
tests/integration/test_cli.py, etendus aux nouveaux comportements.

**Target Platform**: CLI locale, hors-ligne (constitution II).

**Project Type**: cli.

**Performance Goals**: negligeables — une division entiere par chunk au
rendu ; aucun impact sur le decoupage.

**Constraints**: determinisme strict (meme texte + meme ratio → meme
estimation, quel que soit le ratio saisi) ; aucune ecriture en cas
d'echec de configuration ; arithmetique insensible aux artefacts binaires
du flottant (ex. 3,3).

**Scale/Scope**: corpus personnel, quelques documents par execution ; 7
fichiers touches au maximum (2 sources, 2 tests, 3 documentations).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principe | Verdict |
| -------- | ------- |
| I. Isolation des secrets | PASS |
| II. Local-first & confidentialite | PASS |
| III. Open-source & sans trackers | PASS |
| IV. Simplicité (YAGNI) | PASS |
| V. Governance (amendements documentes) | PASS |

Justifications :

- **I — PASS** : aucun secret, aucun identifiant ; rien de nouveau.
- **II — PASS** : calcul purement local ; aucun reseau, aucun
  tokenizer importe ; la mesure optionnelle SC-001 reste hors
  pipeline et hors dependances du projet.
- **III — PASS** : aucune dependance nouvelle ; `fractions` fait
  partie de la bibliotheque standard.
- **IV — PASS** : une option CLI de plus, justifiee par le verdict GO
  de l'assessment et le but d'adaptabilite ; pas de module nouveau,
  pas de config, pas de ratio par typologie.
- **V — PASS** : la reouverture de FR-T02 (feature 002) est tracee :
  assessment complet + spec 004 + note d'amendement ajoutee a la
  feature 002.

Aucune violation : pas de tableau de suivi de complexite requis.

## Project Structure

### Documentation (this feature)

```text
specs/004-ratio-tokens-cli/
├── plan.md              # Ce fichier
├── research.md          # Phase 0 : decisions D1-D7
├── data-model.md        # Phase 1 : entites et garde-fous
├── quickstart.md        # Phase 1 : scenarios de validation
├── contracts/
│   ├── cli.md           # Surface CLI amendee (supersede 003)
│   └── review-render.md # Rendu amendé (supersede 002)
└── tasks.md             # Phase 2 (/speckit-tasks — non cree ici)
```

### Source Code (repository root)

```text
md_chunking/
├── reviewer.py          # Ratio parametrable, estimation, en-tete
├── cli.py               # Option --tokencpte, validation, routage
├── models.py            # Inchange (garde-fou)
├── indexer.py           # Inchange (garde-fou)
├── naming.py            # Inchange (garde-fou)
├── counter.py           # Inchange (garde-fou)
└── presets.py           # Inchange (le ratio n'entre pas dans les presets)

tests/
├── unit/
│   ├── test_reviewer.py # Extension : ratio, arrondi, en-tete, Fraction
│   └── test_cli.py      # Extension : validation des bornes (parse_args)
└── integration/
    └── test_cli.py      # Extension : option, exit 2, --no-review, non regression

README.md                # Documentation de l'option (FR-010)
```

**Structure Decision**: structure existante du depot conservee ; la
feature touche deux modules existants (reviewer, cli) et aucun module
nouveau — le module dedie `tokens.py` avait deja ete ecarte en feature
002 (YAGNI) et ne se justifie toujours pas pour une constante, une
division et un parametre.
