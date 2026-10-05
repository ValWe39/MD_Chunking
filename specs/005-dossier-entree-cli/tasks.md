---
description: "Task list template for feature implementation"
---

# Tasks: Entrée dossier pour la CLI

**Input**: Design documents from `/specs/005-dossier-entree-cli/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/cli.md, quickstart.md

**Tests**: inclus — la spec l'exige (Assumptions : dossiers
temporaires isolés, jamais `Examples/` ni le compteur du dépôt).

**Organization**: tâches groupées par user story (spec.md, P1-P3).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: exécutable en parallèle (fichiers différents)
- **[Story]**: story cible (US1, US2, US3)
- Chemins exacts dans chaque description

## Path Conventions

Projet monolithe : `md_chunking/` (paquet) et `tests/` à la racine
du dépôt (structure du plan.md).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: s'assurer de partir d'une base verte avant tout.

- [ ] T001 Vérifier la baseline : `.venv/Scripts/python -m pytest`
      passe sur la suite existante (70+ tests verts attendus)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: le socle de résolution d'entrée, utilisé par toutes les
stories. Aucune story ne peut commencer avant la fin de cette phase.

- [ ] T002 [P] Créer `md_chunking/inputs.py` : exception
      `InputError` et fonction pure `resolve_inputs(chemins) ->
      (fichiers, avertissements)` selon research.md D1-D7 : filtre
      `suffix.lower() == ".md"` (insensible à la casse, FR-002),
      listing de surface `iterdir()` filtré sur `is_file()` (aucun
      sous-dossier, FR-008), tri des `.md` d'un dossier par
      `(name.lower(), name)` (FR-003), ordre des arguments préservé
      et dossier développé à sa position (FR-004), aucune
      déduplication (FR-001), avertissement « Dossier sans fichier
      .md : {dossier} » par dossier vide ou sans `.md` (FR-005b),
      `InputError` « fichier d'entree introuvable : {chemin} » pour
      introuvable ou ni-fichier-ni-dossier (FR-005)
- [ ] T003 [P] Créer `tests/unit/test_inputs.py` : tests unitaires
      de `resolve_inputs` en `tmp_path` — dossier de 3 `.md` triés
      casse neutre (`B.md` < `c.md` < `a2.md` ordre stable), `.MD`
      accepté, `.markdown`/`.txt`/sans extension ignorés,
      sous-dossier ignoré, avertissements pour dossier vide et
      dossier sans `.md`, `InputError` pour chemin introuvable et
      pour un chemin ni fichier ni dossier, doublon conservé
      (dossier + fichier identique -> 2 occurrences), ordre des
      arguments préservé (fichier avant dossier et inversement)
- [ ] T004 Câbler `md_chunking/cli.py` : remplacer la boucle de
      validation `is_file()` par l'appel à `resolve_inputs`, traduire
      `InputError` en `ConfigError` (code 2, message existant),
      résoudre AVANT `read_counter()` (D4 : zéro document ->
      compteur non consulté), imprimer les avertissements sur stderr,
      itérer la boucle de traitement de `main` sur la liste résolue
      sans autre changement (FR-006 à FR-009 inchangés)

**Checkpoint**: la résolution est intégrée ; `python -m md_chunking
dossier/` fonctionne de bout en bout.

---

## Phase 3: User Story 1 - Dossier complet (Priority: P1) — MVP

**Goal**: un dossier de k `.md` (+ n fichiers quelconques) est
traité en une commande : 2k sorties, occurrences reproductibles.

**Independent Test**: scénario 1 et 2 du quickstart.md — invoquer
la CLI sur un dossier de 2 `.md` + 1 `.txt`, vérifier 4 sorties,
le `.txt` ignoré et les occurrences 0001-0002 dans l'ordre
alphabétique.

### Tests for User Story 1

- [ ] T005 [P] [US1] Étendre `tests/integration/test_cli.py` :
      test d'intégration « dossier complet » — dossier de 3 `.md`
      (mini-fixtures de `tests/fixtures/` copiées en `tmp_path`)
      -> code 0, 6 sorties à plat (3 JSON + 3 reviews), compteur
      avancé de 3, un `.txt` ajouté ignoré (SC-001)
- [ ] T006 [P] [US1] Étendre `tests/integration/test_cli.py` :
      test de reproductibilité — même dossier, compteur réinitialisé,
      deux exécutions -> numéros d'occurrence attribués dans le
      même ordre alphabétique (SC-002, FR-003)

### Implementation for User Story 1

- [ ] T007 [US1] Corriger tout échec des tests T005/T006 dans
      `md_chunking/inputs.py` et `md_chunking/cli.py` (les
      comportements proviennent de la Phase 2 ; ce task est la
      boucle de durcissement US1)

**Checkpoint**: US1 démontrable seul — le quickstart scénario 1
passe.

---

## Phase 4: User Story 2 - Mélanger entrées (Priority: P2)

**Goal**: dossier et fichiers isolés coexistent dans une
invocation ; l'ordre des arguments fait foi.

**Independent Test**: scénario 2 du quickstart.md — `Corpus\ z.md`
traite `B.md` puis `z.md` (occurrences 0001, 0002) ; inverser les
arguments inverse l'ordre.

### Tests for User Story 2

- [ ] T008 [P] [US2] Étendre `tests/integration/test_cli.py` :
      test « mélange » — dossier D (`b.md`, `a.md`) + fichier
      `z.md` -> ordre de traitement `a.md`, `b.md`, `z.md`,
      occurrences consécutives ; fichier avant dossier -> fichier
      traité en premier (FR-004)
- [ ] T009 [P] [US2] Étendre `tests/integration/test_cli.py` :
      test « doublons » — dossier D + `D/a.md` en individuel ->
      `a.md` traité deux fois, deux occurrences consommées, deux
      sorties au nom distinct (FR-001, clarification 2026-10-05)

### Implementation for User Story 2

- [ ] T010 [US2] Corriger tout échec des tests T008/T009 dans
      `md_chunking/inputs.py` (l'ordre et la non-déduplication
      sont portés par la résolution)

**Checkpoint**: US1 + US2 indépendamment fonctionnels.

---

## Phase 5: User Story 3 - État du lot (Priority: P3)

**Goal**: aucun document perdu ni situation ambiguë : dossier vide,
introuvable, échec isolé — comportements tous spécifiés.

**Independent Test**: scénarios 3, 4 et 6 du quickstart.md —
dossier vide -> code 0 + avertissement, aucune écriture ;
introuvable -> code 2 ; un `.md` corrompu -> code 1, lot continué.

### Tests for User Story 3

- [ ] T011 [P] [US3] Étendre `tests/integration/test_cli.py` :
      test « dossier vide/sans .md » — dossier vide et dossier ne
      contenant qu'un `.txt` -> code 0, avertissement sur stderr,
      aucune écriture, `counter.txt` non créé (FR-005b, D4)
- [ ] T012 [P] [US3] Étendre `tests/integration/test_cli.py` :
      test « entrée introuvable » — fichier absent -> code 2,
      message « fichier d'entree introuvable », aucune écriture
      (FR-005)
- [ ] T013 [P] [US3] Étendre `tests/integration/test_cli.py` :
      test « échec isolé » — dossier de 3 `.md` dont 1 illisible
      -> code 1, message nommant le fichier, 2 documents traités
      (4 sorties) (FR-006, SC-004)

### Implementation for User Story 3

- [ ] T014 [US3] Corriger tout échec des tests T011-T013 dans
      `md_chunking/inputs.py` et `md_chunking/cli.py`

**Checkpoint**: les trois stories sont indépendamment
fonctionnelles ; la suite complète est verte.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: documentation et validation de bout en bout.

- [ ] T015 [P] Mettre à jour `README.md` : documenter le passage
      d'un dossier en une étape du mode d'emploi débutant (SC-005),
      sans syntaxe d'énumération de shell ; mentionner le filtre
      `.md`, l'ordre alphabétique et le comportement dossier vide
      (contrat contracts/cli.md)
- [ ] T016 Exécuter les six scénarios de
      `specs/005-dossier-entree-cli/quickstart.md` sur le corpus
      réel en dossiers temporaires et consigner les résultats
- [ ] T017 Passer la suite complète `.venv/Scripts/python -m
      pytest` puis les hooks pre-commit ; tout doit être vert

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1** : aucune dépendance, démarrage immédiat
- **Phase 2** : après la Phase 1 — BLOQUE toutes les stories
  (T004 dépend de T002 ; T003 parallélisable avec T002)
- **Phases 3-5 (US1-US3)** : après la Phase 2 ; exécutables en
  parallèle (fichiers de test distincts, résolution commune déjà
  posée) ou séquentiellement P1 -> P2 -> P3
- **Phase 6** : après la story la plus tardive souhaitée (T015
  parallélisable dès la Phase 2 ; T016-T017 après toutes les
  stories)

### User Story Dependencies

- **US1 (P1)** : démarre après la Phase 2 ; aucune dépendance
  inter-stories
- **US2 (P2)** : démarre après la Phase 2 ; indépendamment
  testable (l'ordre/déduplication sont dans la résolution commune)
- **US3 (P3)** : démarre après la Phase 2 ; indépendamment
  testable

### Within Each User Story

- Tests d'abord (rouges), puis durcissement (verts)
- La boucle de traitement, le compteur et le nommage ne sont JAMAIS
  modifiés (garde-fou du plan.md)

### Parallel Opportunities

- T002 + T003 en parallèle (module et sa suite de tests)
- T005, T006 (US1) puis T008, T009 (US2) puis T011-T013 (US3) :
  deux à trois tests par story, tous sur des sections distinctes
  de `tests/integration/test_cli.py` — à sérialiser si le même
  fichier est retouché simultanément
- T015 (README) parallèle dès la Phase 2

---

## Parallel Example: User Story 1

```text
# Lancer les deux tests US1 ensemble (sections distinctes de
# tests/integration/test_cli.py, fichiers temporaires isolés) :
Task: "T005 [US1] dossier complet -> 6 sorties, compteur +3"
Task: "T006 [US1] reproductibilité de l'ordre des occurrences"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 (baseline verte) puis Phase 2 (résolution intégrée)
2. Phase 3 (US1) — tests T005/T006 verts via T007
3. **STOP et VALIDER** : scénarios 1-2 du quickstart.md
4. Le MVP livré : `md_chunking Corpus\` traite tout le dossier

### Incremental Delivery

1. Setup + Foundational -> socle prêt
2. US1 -> valider (MVP)
3. US2 -> valider (mélange)
4. US3 -> valider (cas limites)
5. Phase 6 -> README + quickstart + suite verte

### Parallel Team Strategy

Mono-développeur de fait (projet local) : séquentiel recommandé,
parallélisme limité aux tests d'une même story.

---

## Notes

- [P] = fichiers différents, pas de dépendance
- Chaque story est livrable et testable seule (checkpoints)
- Compteur et `Examples/` jamais touchés par les tests (`tmp_path`
  et fixture `compteur` existante de `tests/integration/test_cli.py`)
- Committer après chaque task ou groupe logique (hooks pre-commit
  actifs, cf. feature 011 : lignes <= 80 caractères)
