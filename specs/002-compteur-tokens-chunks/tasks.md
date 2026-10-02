# Tasks: Compteur de tokens dans le rapport de relecture

**Input**: Design documents from `/specs/002-compteur-tokens-chunks/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/review-render.md, quickstart.md

**Tests**: inclus — la spécification définit des scénarios
d'acceptation par exigence et la décision D5 de research.md fixe la
stratégie de test (tests unitaires dans test_reviewer.py, intégration
dans test_cli.py).

**Organization**: tâches groupées par user story ; chaque story est
implémentable et testable indépendamment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: exécutable en parallèle (fichiers différents, pas de
  dépendance sur une tâche incomplète)
- **[Story]**: user story de la tâche (US1, US2) — uniquement pour
  les phases de story
- Chemins exacts dans chaque description

## Path Conventions

Projet CLI Python unique : package `md_chunking/` et tests
`tests/unit/`, `tests/integration/` à la racine du dépôt (cf.
plan.md, Project Structure).

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: garantir une base saine avant toute modification

- [ ] T001 Vérifier la base : venv actif et suite `pytest` verte sur
  la branche 005-specify-token-compte avant tout changement
  (`.venv\Scripts\python.exe -m pytest`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: socle partagé par les deux user stories

**CRITICAL**: pas de travail de story avant la fin de cette phase

- [ ] T002 Ajouter dans `md_chunking/reviewer.py` la constante
  `RATIO_CHARS_PER_TOKEN = 4` — contrainte data-model : « entière,
  strictement positive ; modifiable dans le code uniquement, sans
  paramètre d'interface en v1 » — et la fonction pure
  `estimate_tokens(text)` : `ceil(len(text) / 4)`, entier
  supérieur ou égal à 1 pour tout chunk (texte jamais vide),
  aucune dépendance nouvelle ni réseau (FR-T02, research.md D1/D2)

**Checkpoint**: socle prêt — les stories peuvent commencer

---

## Phase 3: User Story 1 - Estimation par chunk (Priority: P1) - MVP

**Goal**: chaque chunk du rapport de relecture porte une ligne
`- tokens (estimation) : ≈ N` en complément de ses métadonnées

**Independent Test**: découper un exemple réel ; `review.md`
contient une estimation marquée « ≈ » par chunk ; l'en-tête
`## Chunk <ref> — <N> car.` est intact ; `index.json` ne contient
aucun champ `tokens` (FR-T01, FR-T04, FR-T07, SC-T01)

### Tests for User Story 1

> **NOTE**: écrire ces tests d'abord, s'assurer qu'ils ÉCHOUENT
> avant l'implémentation de T005

- [ ] T003 [US1] Tests unitaires de `estimate_tokens` dans
  `tests/unit/test_reviewer.py` : multiples exacts de 4,
  arrondi supérieur (ex. 5 caractères → 2), texte minimal ;
  déterminisme (même texte → même valeur, FR-T06)
- [ ] T004 [US1] Tests unitaires de rendu dans
  `tests/unit/test_reviewer.py` : ligne
  `- tokens (estimation) : ≈ N` présente pour chaque chunk,
  en-tête `## Chunk <ref> — <N> car.` inchangé (FR-T04),
  rendu identique sur deux appels (SC-T04)

### Implementation for User Story 1

- [ ] T005 [US1] Implémenter la ligne de métadonnées dans
  `build_review` (`md_chunking/reviewer.py`) : après les métadonnées
  existantes, `- tokens (estimation) : ≈ {estimate_tokens(text)}`
  — forme exacte et règles dans
  `specs/002-compteur-tokens-chunks/contracts/review-render.md`
  (dépend de T002, T003, T004)
- [ ] T006 [US1] Test d'intégration dans
  `tests/integration/test_cli.py` : exécution CLI complète sur un
  exemple réel ; `review.md` contient une estimation par chunk ;
  `index.json` ne contient aucun champ `tokens` à aucun niveau
  (verrou FR-T07, research.md D5) (dépend de T005)

**Checkpoint**: User Story 1 fonctionnelle et testable seule —
c'est le MVP (SC-T01 atteint)

---

## Phase 4: User Story 2 - Valeur de l'estimation (Priority: P2)

**Goal**: l'en-tête du rapport mentionne le caractère approximatif
et modèle-agnostique de l'estimation, avec le ratio, sans nom de
modèle

**Independent Test**: ouvrir `review.md` ; la mention d'en-tête est
lisible sans documentation externe (FR-T05, SC-T02)

### Tests for User Story 2

> **NOTE**: écrire le test d'abord, s'assurer qu'il ÉCHOUE avant
> l'implémentation de T008

- [ ] T007 [US2] Test unitaire dans `tests/unit/test_reviewer.py` :
  mention d'en-tête présente sous le titre, contient « ~4
  caractères par token », aucun nom de modèle (FR-T05, FR-T09)

### Implementation for User Story 2

- [ ] T008 [US2] Implémenter la mention d'en-tête dans
  `build_review` (`md_chunking/reviewer.py`) : ligne sous le titre
  « Tokens estimes a ~4 caracteres par token : approximation
  locale, independante de tout modele d'embedding. » — libellé et
  règles dans contracts/review-render.md (dépend de T007)

**Checkpoint**: User Stories 1 et 2 fonctionnelles et testables
indépendamment

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: documentation et validation transversales

- [ ] T009 [P] Mettre à jour `README.md` : mentionner la ligne
  d'estimation de tokens dans la description de `review.md`
  (section sorties, ligne 74)
- [ ] T010 Exécuter les six scénarios de
  `specs/002-compteur-tokens-chunks/quickstart.md` et consigner les
  résultats (couvre SC-T01 à SC-T05)
- [ ] T011 Relancer la suite complète
  (`.venv\Scripts\python.exe -m pytest`) et vérifier les
  non-régressions de la feature 001 : SC-005 (déterminisme),
  SC-006 (zéro réseau), fourchette en caractères intacte (D4)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: aucune dépendance — démarrage immédiat
- **Foundational (Phase 2)**: dépend du Setup — BLOQUE les stories
- **User Stories (Phases 3–4)**: dépendent de la Phase 2 ; US2
  touche le même fichier que US1 (`reviewer.py`) — exécution
  séquentielle recommandée : US1 puis US2
- **Polish (Phase 5)**: dépend de la complétion des stories visées

### User Story Dependencies

- **US1 (P1)**: démarre après la Phase 2 — aucune dépendance sur
  une autre story
- **US2 (P2)**: démarre après la Phase 2 — indépendante
  fonctionnellement (mention d'en-tête), mais séquentielle avec US1
  en pratique (même fichier)

### Within Each User Story

- Tests d'abord (échec prouvé), puis implémentation, puis
  intégration
- T003 et T004 touchent le même fichier de test : séquentielles
- T009 (README) est le seul [P] réel : fichier distinct, aucune
  dépendance de code

### Parallel Opportunities

- T009 peut s'exécuter en parallèle de toute tâche de story
  (fichier différent)

---

## Parallel Example: User Story 1

```bash
# Après la Phase 2, en séquentiel (mêmes fichiers) :
Task: "T003 Tests unitaires estimate_tokens"
Task: "T004 Tests unitaires rendu"
Task: "T005 Ligne de métadonnées dans build_review"
Task: "T006 Test d'intégration CLI"

# En parallèle (fichier différent) :
Task: "T009 Mise à jour du README"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. T001 : base verte
2. T002 : constante + fonction pure
3. T003–T005 : tests puis ligne de métadonnée
4. **STOP et VALIDER** : SC-T01 vérifié sur un exemple réel
   (quickstart scénario 1)

### Incremental Delivery

1. Setup + Foundational → socle prêt
2. US1 → testée seule → MVP (l'estimation est lisible par chunk)
3. US2 → testée seule → le rapport est auto-documenté
4. Polish → README, quickstart complet, non-régressions

---

## Notes

- [P] = fichiers différents, aucune dépendance
- [Story] = traçabilité vers spec.md ; Setup/Foundational/Polish
  sans label
- Vérifier que les tests échouent avant l'implémentation (TDD)
- Committer après chaque tâche ou groupe logique
- S'arrêter aux checkpoints pour valider chaque story
  indépendamment
