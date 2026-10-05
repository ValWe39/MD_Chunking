---

description: "Task list for feature implementation"

---

# Tasks: Ratio caracteres/tokens reglable en CLI

**Input**: Design documents from `/specs/004-ratio-tokens-cli/`

**Prerequisites**: plan.md (required), spec.md (required for user
stories), research.md, data-model.md, contracts/

**Tests**: inclus — la spec exige une suite verte etendue (SC-005) et
chaque FR est verifiable par scenario ; approche TDD respectee (tests
d'abord, echouants avant implementation).

**Organization**: tasks grouped by user story (US1 defaut recale, US2
option explicite, US3 echec rapide) pour implementation et test
independants de chaque story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g. US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Projet unique : paquet `md_chunking/` et `tests/` a la racine du
depot (structure existante, voir plan.md).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Point de depart propre avant toute modification

- [ ] T001 Verifier la base : `python -m pytest` vert (89 tests) sur
  l'etat courant, arbre de travail propre

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Noyau du ratio parametrable, commun aux trois stories

**CRITICAL**: Aucune user story ne peut commencer avant la fin de cette
phase

- [ ] T002 Dans md_chunking/reviewer.py : remplacer la constante
  `RATIO_CHARS_PER_TOKEN = 4` par `DEFAULT_RATIO_CHARS_PER_TOKEN = 3.5`
  et faire du ratio un parametre de `estimate_tokens(text, ratio)` —
  calcul `ceil(len(texte) / ratio)` exact via
  `fractions.Fraction(str(ratio))` (FR-001, FR-005 ; research.md D2)
- [ ] T003 Dans md_chunking/reviewer.py : faire du ratio un parametre
  de `build_review(doc, chunks, ratio)` et afficher l'en-tete « Tokens
  estimes a ~{ratio} caracteres par token » avec formatage fixe a une
  decimale (3.5 par defaut, 3.3 pour 3.333) (FR-004 ; research.md D4)

**Checkpoint**: Noyau pret — les stories peuvent commencer

---

## Phase 3: User Story 1 - Defaut recale sans option (P1) — MVP

**Goal**: Sans aucune option, le rapport estime a 3,5 car./token et
l'en-tete l'affiche ; index et noms inchanges (spec US1)

**Independent Test**: Executer le pipeline sans option sur un document
temoin et verifier l'en-tete ~3.5 et `ceil(len/3.5)` par chunk ; index
identique octet par octet a l'etat d'avant la feature

### Tests for User Story 1

- [ ] T004 [P] [US1] Tests unitaires dans tests/unit/test_reviewer.py :
  estimation au defaut 3,5 (ex. 7 caracteres → 2 tokens), arrondi
  superieur, en-tete « ~3.5 caracteres par token », determination
  (meme texte → meme valeur) — ecrire d'abord, verifier l'echec
- [ ] T005 [P] [US1] Test d'integration dans tests/integration/test_cli.py :
  execution sans option → en-tete 3.5, estimations recalculées, index
  JSON et noms de fichiers identiques octet par octet a ceux produits
  sans la feature (SC-004) — ecrire d'abord, verifier l'echec

### Implementation for User Story 1

- [ ] T006 [US1] Dans md_chunking/cli.py : router le ratio effectif
  (defaut 3.5) de `parse_args` jusqu'a `build_review` via
  `process_document` (signature mise a jour ; aucun autre module
  touche) (FR-001 ; research.md D1)
- [ ] T007 [US1] Valider le scenario 1 du quickstart.md sur
  Examples/nettoye.md : en-tete ~3.5, estimations coherentes, suite
  pytest verte

**Checkpoint**: US1 fonctionnelle et testable independamment (MVP)

---

## Phase 4: User Story 2 - Ratio explicite via --tokencpte (P2)

**Goal**: L'utilisateur adapte le ratio par option ; rapport au ratio
saisi, index et noms inchanges (spec US2)

**Independent Test**: Executer avec et sans `--tokencpte 3.2` sur le
meme document : estimations differentes conformes au ratio, index
identique entre les deux executions

### Tests for User Story 2

- [ ] T008 [P] [US2] Tests unitaires dans tests/unit/test_cli.py :
  `parse_args` accepte `--tokencpte 3.2` et expose la valeur ;
  en-tete arrondi a une decimale (saisie 3.333 → « 3.3 ») — ecrire
  d'abord, verifier l'echec
- [ ] T009 [P] [US2] Tests d'integration dans tests/integration/test_cli.py :
  option explicite appliquee a tous les documents d'une execution
  multi-fichiers ; `--no-review --tokencpte 2` sans erreur, aucun
  rapport produit (FR-008, FR-009) — ecrire d'abord, verifier l'echec

### Implementation for User Story 2

- [ ] T010 [US2] Dans md_chunking/cli.py : declarer l'option
  `--tokencpte` (`type=float`, point decimal, aucune borne ici —
  bornes en US3) et router sa valeur a la place du defaut
  (FR-002 ; contracts/cli.md)
- [ ] T011 [US2] Valider les scenarios 2, 5 et 6 du quickstart.md sur
  Examples/nettoye.md : ratio explicite, --no-review, determinisme sur
  double execution

**Checkpoint**: US1 et US2 fonctionnelles et testables

---

## Phase 5: User Story 3 - Ratio invalide rejete (P3)

**Goal**: Toute valeur hors ]0 ; 10] echoue au code 2 avant toute
ecriture, compteur non incremente (spec US3)

**Independent Test**: Executer successivement avec 0, -1, 12 et 3,5 :
code de sortie 2, message explicite, aucun fichier ecrit

### Tests for User Story 3

- [ ] T012 [P] [US3] Tests dans tests/unit/test_cli.py et
  tests/integration/test_cli.py : bornes 0 et -1 rejetees, 12 rejetee
  avec message « --tokencpte doit etre > 0 et <= 10 (recu : 12.0) »,
  0.5 et 10 acceptes, virgule `3,5` rejetee au parsing (code 2),
  execution hors bornes sans aucun fichier ecrit ni compteur
  incremente (FR-003, SC-003) — ecrire d'abord, verifier l'echec

### Implementation for User Story 3

- [ ] T013 [US3] Dans md_chunking/cli.py : ajouter la validation
  `0 < ratio <= 10` a la liste d'erreurs de `parse_args` (ConfigError,
  code 2) avec le message du contrat contracts/cli.md (FR-003 ;
  research.md D3)
- [ ] T014 [US3] Valider les scenarios 3 et 4 du quickstart.md :
  echec rapide sans ecriture, virgule refusee

**Checkpoint**: Les trois stories sont independamment fonctionnelles

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, amendement spec 002, validation globale

- [ ] T015 [P] Documenter l'option dans README.md : nom, format (point
  decimal), bornes ]0 ; 10], defaut 3.5, effet (rapport uniquement),
  exemples (FR-010)
- [ ] T016 [P] Ajouter la note d'amendement en tete de
  specs/002-compteur-tokens-chunks/spec.md et de son contrat
  contracts/review-render.md : FR-T02 « sans parametre d'interface en
  v1 » est amende par la feature 004 (FR-010 ; research.md D7)
- [ ] T017 Suite complete `python -m pytest` verte (SC-005) et
  revue des six scenarios du quickstart.md ; verification finale :
  aucun champ `tokens` ni `ratio` dans l'index JSON produit

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: aucune dependance — demarrage immediat
- **Foundational (Phase 2)**: depend de Phase 1 — BLOQUE toutes les
  stories (T003 depend de T002, meme fichier)
- **User Stories (Phases 3-5)**: dependent de Phase 2 ; en sequence
  par priorite P1 → P2 → P3 recommande (T002/T003 posent le defaut
  3.5 des le depart, US1 ne fait que le router)
- **Polish (Phase 6)**: depend de toutes les stories completes

### User Story Dependencies

- **US1 (P1)**: apres Phase 2 — independante des autres stories
- **US2 (P2)**: apres Phase 2 — independante d'US1 testable seule
  (routage deja en place par T006 ; T010 ne modifie que parse_args)
- **US3 (P3)**: apres Phase 2 — independante (validation pure de
  parse_args, sans rapport avec le rendu)

### Within Each User Story

- Tests d'abord, echouants avant implementation (TDD)
- Pas de modele nouveau : reviewer.py (Phase 2) puis cli.py (stories)
- Implementation avant validation quickstart

### Parallel Opportunities

- T004 et T005 (fichiers de tests differents) en parallele
- T008 et T009 en parallele ; T012 en parallele des autres tests US
- T015 et T016 (Phase 6) en parallele
- US2 et US3 testables en parallele apres US1 si capacity (meme fichier
  md_chunking/cli.py : preferer la sequence)

---

## Parallel Example: User Story 1

```bash
# Tests US1 en parallele (fichiers differents) :
Task: "Tests unitaires reviewer dans tests/unit/test_reviewer.py"
Task: "Test integration defaut dans tests/integration/test_cli.py"

# Puis implementation sequentielle (meme fichier md_chunking/cli.py) :
Task: "Routage du ratio dans md_chunking/cli.py"
Task: "Validation quickstart scenario 1 sur Examples/nettoye.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 : base verte
2. Phase 2 : noyau ratio parametrable
3. Phase 3 : US1 — defaut 3.5 route et affiche
4. **STOP and VALIDATE**: quickstart scenario 1 + pytest verts
5. Demo possible : chaque relecture gagne le calibrage francais

### Incremental Delivery

1. Setup + Foundational → noyau pret
2. US1 → defaut recalé (MVP)
3. US2 → option --tokencpte
4. US3 → echec rapide bornes
5. Polish → README, amendement 002, validation globale

---

## Notes

- [P] tasks = fichiers differents, pas de dependance
- Chaque story est completable et testable independamment
- Verifier que les tests echouent avant d'implementer
- Commit apres chaque tache ou groupe logique (hooks pre-commit actifs,
  formatage markdownlint 80 colonnes)
- Le ratio ne fuit jamais hors du rapport (FR-007, FR-008) : tout test
  d'ecriture hors review.md est une regression
