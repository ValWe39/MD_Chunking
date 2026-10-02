# Implementation Plan: Chunking de Markdown avec sortie JSON

**Branch**: `002-assessment` | **Date**: 2026-10-02 |
**Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-md-chunking/spec.md`

Handoff GO de l'assessment md-chunking-json-output.

## Summary

Découper des documents Markdown en chunks de 100–1000 caractères
par défaut (fourchette paramétrable), en respectant la structure
(sections, puis paragraphes, puis phrases), avec overlap
structurel, puis exporter par document un JSON de traçabilité et
un rendu Markdown annoté pour relecture humaine, le tout en local.
Approche technique retenue : socle Haystack (deepset) —
`MarkdownToDocument` + `MarkdownHeaderSplitter` — étendu par des
composants maison ciblés (normalisation des entrées irrégulières,
overlap structurel, export JSON, rendu de relecture). C'est
l'option B de l'assessment, arbitrée contre une solution 100% maison
(option A, réinvention) et Haystack tel quel (option C, incomplet).

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: haystack-ai (Apache-2.0, deepset — Berlin)
pour le socle de parsing et de découpage ; markdown-it-py (MIT)
pour la normalisation des entrées irrégulières si nécessaire ;
stdlib uniquement pour le reste (json, argparse, pathlib).

**Storage**: fichiers uniquement — JSON de chunks et rendus
Markdown annotés écrits dans le dossier de sortie ; aucune base de
données.

**Testing**: pytest ; corpus de validation = les 4 documents réels
du dossier `Examples/` (voir [research.md](research.md), décision
D7 : ces fichiers sont locaux/gitignorés, donc complétés par des
mini-fixtures committées).

**Target Platform**: ligne de commande, machine locale (Windows en
pratique, code portable).

**Project Type**: cli

**Performance Goals**: quelques dizaines de documents de 44–110 KB
traités en quelques secondes au total ; pas d'exigence de latence
stricte au-delà de l'expérience utilisateur.

**Constraints**: 100% hors ligne (constitution II), aucune
télémétrie/tracker (constitution III — vérification Haystack en
décision D3), aucun secret (constitution I), chemins résolus en
relatif ou via arguments (path isolation).

**Scale/Scope**: utilisateur unique ; ~50–150 chunks par document ;
4 typologies de preset + livre/littérature.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1
design.*

| Principe | Statut | Détail |
| ---------- | -------- | -------- |
| I. Secrets | PASS | aucun identifiant, aucun réseau |
| II. Local-first | PASS | fichiers locaux, hors ligne total |
| III. Sans trackers | PASS* | haystack-ai Apache-2.0 ; voir note |
| IV. Simplicité | PASS | CLI unique, deux dépendances (YAGNI) |
| Path isolation | PASS | sortie relative `output/`, surchargeable |
| Souveraineté | PASS | deepset (Berlin), Apache-2.0 |

Note * : la conformité III se prouve au premier build — vérifier
l'absence de télémétrie Haystack et consigner le résultat
(décision D3 de [research.md](research.md)).

Aucune violation : la section de suivi de complexité est supprimée.

## Project Structure

### Documentation (this feature)

```text
specs/001-md-chunking/
├── plan.md              # Ce fichier (/speckit-plan)
├── research.md          # Phase 0 : décisions techniques
├── data-model.md        # Phase 1 : entités et schéma JSON
├── quickstart.md        # Phase 1 : guide de validation
├── contracts/           # Phase 1 : contrats CLI et JSON
│   ├── cli.md           # Schéma de commande
│   └── chunk-json.md    # Schéma JSON de sortie
└── tasks.md             # /speckit-tasks (non créé ici)
```

### Source Code (repository root)

```text
md_chunking/
├── __init__.py
├── cli.py          # Point d'entrée (argparse), validation config
├── presets.py      # Typologies : documentation/articles/…
├── normalizer.py   # Fins de ligne, titres malformés (Exemple1)
├── splitter.py     # Orchestration Haystack + bascule de niveaux
├── overlap.py      # Overlap structurel (parties/paragraphes)
├── indexer.py      # Export JSON de traçabilité
└── reviewer.py     # Rendu Markdown annoté

tests/
├── unit/           # Normalisation, overlap, presets, index
├── integration/    # Bout-en-bout sur corpus
└── fixtures/       # Mini-documents committés (dérivés des
                    # 4 exemples, anonymisés/reduits)
```

**Structure Decision**: projet unique (option par défaut), package
`md_chunking/` à la racine du dépôt avec modules à responsabilité
unique, sans couche de service inutile (YAGNI). Les tests
d'intégreation pointent aussi `Examples/` lorsqu'il est présent
(corpus réel local, non committé).

## Post-Phase-1 Constitution Re-check

Après génération de research.md, data-model.md, contracts/ et
quickstart.md : aucun changement de dépendance, aucun stockage
distant, aucune interface réseau — les six gates restent PASS.
Le point ouvert unique (télémétrie Haystack, D3) est tracé comme
vérification du premier build dans quickstart.md et research.md.
