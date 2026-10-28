# Tasks: Appariement robuste .md/.json sur préfixes longs

**Input**: Design documents from `/specs/007-robust-pairing/`

**Prerequisites**: plan.md (required), spec.md (required for
user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable
independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no
  dependencies)
- **[Story]**: Which user story this task belongs to
  (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Source code: `md_chunking/` at repository root
- Tests: `tests/unit/`, `tests/integration/`
- Specs: `specs/006-add-context/` (amendement),
  `specs/007-robust-pairing/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Vérifier l'état du dépôt et préparer les
fixtures de test.

- [ ] T001 Vérifier la branche `013-fix-lien` et l'état
  propre du dépôt (`git status`)
- [ ] T002 [P] Copier `Examples/Pairing/` en fixture de
  test temporaire pour les tests d'intégration
  (`tests/integration/test_cli.py`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Modification de `cle_normale()` — prérequis
bloquant pour toutes les user stories.

**CRITICAL**: No user story work can begin until this
phase is complete.

- [ ] T003 Modifier `cle_normale()` dans
  `md_chunking/contexts.py` pour supprimer la troncature
  `[:8]` et retourner la chaîne normalisée complète
  (FR-001, D3)
- [ ] T004 [P] Mettre à jour les tests unitaires de
  `cle_normale` dans `tests/unit/test_contexts.py` :
  supprimer les assertions `== "premiere"` etc., les
  remplacer par les chaînes complètes (`premiere0034`,
  `an_rappo`, etc.) (FR-001)

**Checkpoint**: `cle_normale()` retourne la chaîne complète
sans troncature — foundation ready.

---

## Phase 3: User Story 1 — Corpus à préfixes longs (P1) MVP

**Goal**: Les 3 paires Fipeco de `Examples/Pairing/` sont
appariées automatiquement par extension progressive, sans
avertissement « Appariement ambigu ».

**Independent Test**: Exécuter `--add-context` sur
`Examples/Pairing/` : 3/3 appariées, 0 avertissement
« Appariement ambigu », chaque sortie embarque les 7
champs du contexte (SC-001).

### Implementation for User Story 1

- [ ] T005 [US-1] Implémenter la boucle par paliers dans
  `apparie_niveau()` dans `md_chunking/contexts.py` :
  itérer sur les paliers 8, 12, 16, 20, 24, … jusqu'à la
  longueur maximale ; chaque `.md` non résolu avance
  indépendamment ; unicité des deux côtés requise
  (FR-002, FR-003, FR-004, FR-005, D1, D2)
- [ ] T006 [P] [US-1] Ajouter le test unitaire du cas
  Fipeco dans `tests/unit/test_contexts.py` : 3 paires
  `fipeco.fr-00003x`, résolution au palier 16, clés
  complètes `fipecofr000033nettoye` /
  `fipecofr000033net0063` (SC-001)
- [ ] T007 [P] [US-1] Ajouter le test d'intégration CLI
  sur `Examples/Pairing/` copié en `tmp_path` dans
  `tests/integration/test_cli.py` : vérifier les 3
  sorties avec `document.context`, aucun avertissement
  « Appariement ambigu » (SC-001)
- [ ] T008 [US-1] Vérifier SC-001 : exécuter le test
  d'intégration et confirmer 3/3 appariées, 0
  avertissement

**Checkpoint**: User Story 1 fully functional — les 3
paires Fipeco sont appariées automatiquement.

---

## Phase 4: User Story 2 — Compatibilité ascendante (P2)

**Goal**: Les 3 couples de `Examples/Extension/` continuent
de s'apparier au palier 8, sans régression.

**Independent Test**: Exécuter `--add-context` sur
`Examples/Extension/Multi-couples` : 3/3 appariées,
identique au comportement de la feature 006 (SC-002).

### Implementation for User Story 2

- [ ] T009 [US-2] Adapter
  `test_melee_ambiguite_deux_json_meme_prefixe` dans
  `tests/unit/test_contexts.py` : les fichiers
  `premiere-0034.json` et `premiere-0035.json` ont des
  clés complètes différentes → résolus au palier 12 ;
  vérifier l'appariement correct au lieu de
  l'avertissement (D4, FR-010)
- [ ] T010 [US-2] Adapter
  `test_melee_ambiguite_json_partage_par_deux_md` dans
  `tests/unit/test_contexts.py` : les fichiers
  `an_rappo-1.md` et `an_rappo-2.md` ont des clés
  complètes différentes → le `.json` `an_rappo-0032`
  reste orphelin ; vérifier l'avertissement orphelin
  (D4, FR-010)
- [ ] T011 [P] [US-2] Ajouter le test d'intégration CLI
  sur `Examples/Extension/Multi-couples` copié en
  `tmp_path` dans `tests/integration/test_cli.py` :
  vérifier les 3 sorties avec `document.context`,
  appariements identiques à la feature 006 (SC-002)
- [ ] T012 [US-2] Vérifier SC-002 : exécuter les tests
  d'intégration sur `Examples/Extension/` et confirmer
  3/3 appariées, pas de régression

**Checkpoint**: User Stories 1 AND 2 both work
independently — compatibilité ascendante préservée.

---

## Phase 5: User Story 3 — Vraies ambiguïtés (P3)

**Goal**: Deux fichiers de même stem normalisé complet
émettent « Appariement ambigu », aucun faux positif.

**Independent Test**: Créer un dossier avec deux `.md` de
même stem normalisé complet : avertissement « Appariement
ambigu » pour chaque, aucun contexte embarqué (SC-003).

### Implementation for User Story 3

- [ ] T013 [US-3] Ajouter le test de vraie ambiguïté dans
  `tests/unit/test_contexts.py` : deux `.md` de même
  stem normalisé complet → avertissement
  « Appariement ambigu » à la longueur maximale
  (FR-005, FR-009)
- [ ] T014 [P] [US-3] Ajouter le test de faux positif
  exclu dans `tests/unit/test_contexts.py` : deux
  paires avec préfixe long identique mais clés complètes
  différentes → appariement correct, pas d'erreur
  (FR-009, SC-003)
- [ ] T015 [US-3] Vérifier SC-003 : exécuter les tests
  et confirmer 0 faux positif

**Checkpoint**: All user stories independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Amendements documentaires et validation
finale.

- [ ] T016 [P] Amender le contrat CLI
  `specs/006-add-context/contracts/cli.md` : section
  « Niveau mélangé » → extension progressive par paliers
  (D5)
- [ ] T017 [P] Amender le data-model
  `specs/006-add-context/data-model.md` : table « Clé
  d'appariement normalisée » → sans troncature, paliers
  dans `apparie_niveau()` (D5)
- [ ] T018 [P] Amender le research
  `specs/006-add-context/research.md` : D3 → extension
  progressive par paliers (D5)
- [ ] T019 Exécuter la suite complète de tests
  (`.venv/Scripts/python.exe -m pytest`) et vérifier
  SC-004 (tous les tests passent) et SC-005 (2 tests
  d'ambiguïté adaptés passent)
- [ ] T20 Valider le `quickstart.md` : exécuter les 4
  scénarios (Fipeco, compatibilité, sans option, vraie
  ambiguïté) et confirmer les résultats attendus

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start
  immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS
  all user stories
- **User Stories (Phase 3+)**: All depend on Foundational
  phase completion
  - US1 (P1) → US2 (P2) → US3 (P3) recommended order
  - US2 and US3 can run in parallel after US1 if staffed
- **Polish (Phase 6)**: Depends on all desired user
  stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational
  (Phase 2) — no dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational
  (Phase 2) — independent of US1
- **User Story 3 (P3)**: Can start after Foundational
  (Phase 2) — independent of US1/US2

### Within Each User Story

- Models before services (N/A here, fonctions pures)
- Core implementation before integration tests
- Story complete before moving to next priority

### Parallel Opportunities

- T002, T004 can run in parallel (different files)
- T006, T007 can run in parallel (different test files)
- T009, T010 can run in parallel (same file but
  different test functions — coordinate)
- T013, T014 can run in parallel (same file, different
  test functions — coordinate)
- T016, T017, T018 can run in parallel (different
  spec files)
- US2 and US3 can be worked on in parallel after US1

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1
   independently (`Examples/Pairing/` → 3/3 appariées)
5. Commit and push if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Commit
   (MVP!)
3. Add User Story 2 → Test independently → Commit
4. Add User Story 3 → Test independently → Commit
5. Polish (Phase 6) → Amendements doc → Final
   validation

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (P1)
   - Developer B: User Story 2 (P2)
   - Developer C: User Story 3 (P3)
3. Stories complete and integrate independently
4. Team converges on Polish (Phase 6)

---

## Notes

- [P] tasks = different files or independent test
  functions, no dependencies
- [Story] label maps task to specific user story for
  traceability
- Each user story should be independently completable
  and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- The spec 006 is amended in-place (D3, contrat CLI,
  data-model) — no spec 007 dédiée pour le code, seulement
  pour la documentation de la feature
