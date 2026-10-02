# Tasks: Chunking de Markdown avec sortie JSON

**Input**: Design documents from `/specs/001-md-chunking/`

**Prerequisites**: plan.md (required), spec.md (required for user
stories), research.md, data-model.md, contracts/

**Tests**: inclus — plan.md impose pytest et quickstart.md
consacre son scénario 7 aux tests automatisés.

**Organization**: tâches groupées par user story (US1–US4 de la
spec) pour permettre implémentation et test indépendants.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: exécutable en parallèle (fichiers différents, pas de
  dépendance sur une tâche incomplète)
- **[Story]**: user story rattachée (US1, US2, US3, US4)
- Chemins exacts dans chaque description

## Path Conventions

Projet unique : package `md_chunking/` et dossier `tests/` à la
racine du dépôt (cf. plan.md, Structure Decision).

---

## Phase 1: Setup (infrastructure partagée)

**Purpose**: initialisation du projet et structure de base

- [x] T001 Créer la structure du projet selon plan.md : package
      md_chunking/ (vide, avec `__init__.py`) et dossiers
      tests/unit, tests/integration, tests/fixtures
- [x] T002 Initialiser le projet Python dans pyproject.toml :
      dépendances haystack-ai épinglé en 2.x stable et markdown-it-py
      ( licences Apache-2.0 et MIT), point d'entrée
      `md_chunking = md_chunking.cli:main`
- [x] T003 [P] Configurer pytest dans pyproject.toml (section
      [tool.pytest.ini_options], dossier tests/)
- [x] T004 [P] Créer les mini-fixtures committées dans
      tests/fixtures/ (décision D7 de research.md) :
      article-propre.md (sections régulières, CRLF),
      titres-en-listes.md (motif `* ## [`, CRLF),
      prose-longue.md (LF, sections > 700 mots),
      sans-structure.md (prose sans titres)
- [x] T005 Vérifier l'absence de télémétrie dans haystack-ai au
      premier build (décision D3 de research.md) et consigner le
      résultat dans README.md ; le cas échéant, documenter la
      variable de désactivation dans README.md

---

## Phase 2: Foundational (prérequis bloquants)

**Purpose**: socle requis avant TOUTE user story

**CRITICAL**: aucune user story ne peut commencer avant la fin de
cette phase

- [x] T006 Créer les entités DocumentSource et Chunk dans
      md_chunking/models.py conformément à data-model.md, avec les
      contraintes verbatim : `length = len(text)` en caractères,
      `ref` séquentiel unique, `text` jamais vide, `atomic` bool
      (écart de fourchette signalé)
- [x] T007 Implémenter la validation de configuration dans
      md_chunking/cli.py (FR-012) : --min < --max, --overlap dans
      0–20, --typologie parmi les 5, --naming parmi
      numbered/title, chemin d'entrée présent ; échec rapide avec
      code de sortie 2 et message clair, aucun fichier écrit
- [x] T008 Implémenter la normalisation des entrées dans
      md_chunking/normalizer.py (FR-010, décision D5) : fins de
      ligne CRLF/LF unifiées en LF, neutralisation des titres
      emboîtés dans des puces (motif `* ## [` d'Exemple1) sans
      perte de contenu, détection du titre (H1 ou front-matter
      YAML, sinon champ absent)
- [x] T009 Implémenter les presets dans md_chunking/presets.py
      avec les valeurs exactes de data-model.md : documentation
      min 100 max 1000 overlap 15 (défaut), articles 150/1500/13,
      conversations 50/500/10, code 200/2000/15, livre 150/1200/15

**Checkpoint**: socle prêt — les user stories peuvent démarrer

---

## Phase 3: User Story 1 - Découpage conforme (Priority: P1) — MVP

**Goal**: découper un document Markdown en chunks dans la
fourchette min/max en respectant sections, puis paragraphes, puis
phrases, avec overlap structurel (FR-002 à FR-005, FR-010)

**Independent Test**: traiter tests/fixtures/article-propre.md
avec les défauts, vérifier que chaque chunk est entre 100 et 1000
caractères et qu'aucune frontière n'est coupée sans nécessité

### Tests for User Story 1

- [x] T010 [P] [US1] Tests unitaires de normalisation dans
      tests/unit/test_normalizer.py : CRLF→LF, neutralisation des
      titres en listes sur tests/fixtures/titres-en-listes.md,
      détection de titre
- [x] T011 [P] [US1] Tests d'intégration de découpage dans
      tests/integration/test_split.py : bornes respectées sur les
      4 fixtures, bascule de niveaux sur prose-longue.md et
      sans-structure.md, blocs code/tableaux atomiques

### Implementation for User Story 1

- [x] T012 [US1] Implémenter le découpage par sections dans
      md_chunking/splitter.py : MarkdownToDocument puis
      MarkdownHeaderSplitter (hiérarchie préservée en métadonnées,
      décision D1), construction des Chunk
- [x] T013 [US1] Implémenter la bascule de niveaux dans
      md_chunking/splitter.py (FR-003) : sections → paragraphes →
      phrases en dernier recours ; entités atomiques (blocs
      code/tableaux) jamais coupées, écart signalé via atomic
- [x] T014 [US1] Implémenter l'heuristique gloutonne d'occupation
      maximale dans md_chunking/splitter.py (FR-004) : fusion des
      unités voisines tant que chunk_max n'est pas atteint et que
      les frontières tiennent ; jamais sous chunk_min sauf section
      entière plus courte (edge case spec)
- [x] T015 [US1] Implémenter l'overlap structurel dans
      md_chunking/overlap.py (FR-005, décision D6) : 0–20% du
      chunk découpé aux mêmes frontières, filtrage des fenêtres
      entièrement couvertes (contournement du bug Haystack
      référencé #12686, décision D2)
- [x] T016 [US1] Câbler le traitement de fichiers dans
      md_chunking/cli.py : lecture UTF-8, pipeline
      normalise→découpe→overlap, échec d'un document sans arrêter
      le lot (code 1, message nommant le fichier)

**Checkpoint**: US1 fonctionnelle et testable seule — MVP avec US2

---

## Phase 4: User Story 2 - Index de traçabilité JSON (Priority: P1)

**Goal**: exporter chunks.json conforme au contrat
contracts/chunk-json.md (schema_version 1.0, champs obligatoires
et conditionnels, invariants SC-001/SC-002)

**Independent Test**: produire chunks.json pour
tests/fixtures/article-propre.md et vérifier chaque règle de
champs du contrat, y compris l'absence des champs non balisés

### Tests for User Story 2

- [x] T017 [P] [US2] Tests unitaires de l'indexeur dans
      tests/unit/test_indexer.py : schéma complet, ref séquentiels
      uniques, champs conditionnels présents si et seulement si
      balisés, params reflétant la configuration effective

### Implementation for User Story 2

- [x] T018 [US2] Implémenter l'export JSON dans
      md_chunking/indexer.py selon contracts/chunk-json.md :
      schema_version, document (path/title/structure/typologie),
      params (unit chars), chunks[] avec ref/text/length/boundary/
      part/page/position_in_part/atomic
- [x] T019 [US2] Brancher l'écriture de chunks.json dans
      md_chunking/cli.py : un fichier JSON par document traité,
      valeurs de sortie non horodatées (déterminisme SC-005)

**Checkpoint**: US1 + US2 forment le MVP complet du pipeline

---

## Phase 5: User Story 3 - Contrôle avant embedding (Priority: P2)

**Goal**: produire review.md, rendu Markdown annoté lisible par
un humain (FR-008, réponse utilisateur Q2)

**Independent Test**: ouvrir review.md produit pour un fixture
d'environ 50 chunks et repérer frontières et métadonnées sans
outil supplémentaire

### Tests for User Story 3

- [x] T020 [P] [US3] Tests unitaires du rendu dans
      tests/unit/test_reviewer.py : un titre par chunk, métadonnées
      en liste, texte intégral, option --no-review respectée

### Implementation for User Story 3

- [x] T021 [US3] Implémenter le rendu de relecture dans
      md_chunking/reviewer.py : `## Chunk N — [partie] — X car.`,
      métadonnées du chunk en liste, texte intégral dans un bloc ;
      déterminisme (aucun horodatage)
- [x] T022 [US3] Brancher --no-review dans md_chunking/cli.py et
      vérifier le scénario SC-004 sur le corpus Examples/ (moins
      de 10 minutes de relecture pour environ 50 chunks)

**Checkpoint**: US3 fonctionnelle — relecture humaine possible

---

## Phase 6: User Story 4 - Presets et sorties (Priority: P3)

**Goal**: presets par typologie applicables et surchargeables,
organisation des sorties en sous-dossiers dédiés (FR-006, FR-009)

**Independent Test**: traiter 2 fixtures avec la typologie
documentation sans paramètres : bornes du preset appliquées et
un sous-dossier créé par document

### Tests for User Story 4

- [x] T023 [P] [US4] Tests unitaires des presets dans
      tests/unit/test_presets.py : valeurs exactes de T009
      citées verbatim, surcharge par --min/--max/--overlap

### Implementation for User Story 4

- [x] T024 [US4] Implémenter l'organisation des sorties dans
      md_chunking/cli.py : sous-dossier numéroté `0001` par défaut
      ou slug du titre limité à 30 caractères si --naming title
      et titre disponible, repli sur la numérotation sinon,
      création du dossier --output (défaut relatif output/)
- [x] T025 [US4] Brancher --typologie dans md_chunking/cli.py :
      preset appliqué par défaut, surcharge par options explicites
      (US4, scénario 3 de la spec)

**Checkpoint**: US4 fonctionnelle — toutes les stories livrées

---

## Phase 7: Polish &amp; transversal

**Purpose**: améliorations touchant plusieurs stories

- [x] T026 [P] Documenter l'installation et l'usage dans README.md
      (prérequis, exemples de commandes, résultat attendu,
      conclusion de la vérification de télémétrie de T005)
- [x] T027 Valider le déterminisme (SC-005) : deux exécutions
      identiques sur tests/fixtures/article-propre.md, diff des
      sorties sans différence
- [x] T028 Exécuter les scénarios 1 à 7 de quickstart.md sur le
      corpus Examples/ et consigner les résultats
- [x] T029 [P] Vérification de performance (plan.md) : les 4
      documents de Examples/ traités en quelques secondes au total
- [x] T030 Nettoyage final : suppression des TODO résiduels,
      passage complet de pytest, revue des messages d'erreur en
      français

---

## Dependencies &amp; Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sans dépendance — démarrage immédiat
- **Foundational (Phase 2)**: dépend de la Phase 1 — BLOQUE toutes
  les user stories
- **User Stories (Phases 3–6)**: dépendent de la Phase 2
  - en séquence de priorité : US1, US2 (P1) puis US3 (P2) puis
    US4 (P3)
  - en parallèle possible : US3 et US4 après US1+US2
- **Polish (Phase 7)**: dépend des user stories livrées

### User Story Dependencies

- **US1 (P1)**: démarre après la Phase 2, sans dépendance vers
  une autre story
- **US2 (P1)**: démarre après la Phase 2 ; consomme les Chunk de
  US1 mais reste testable sur des chunks construits à la main
- **US3 (P2)**: après la Phase 2 ; lit les chunks en mémoire,
  indépendante de l'indexeur
- **US4 (P3)**: après la Phase 2 ; s'appuie sur presets.py
  (Phase 2) et sur le câblage CLI des stories précédentes

### Within Each User Story

- Tests d'abord, en échec avant implémentation
- Entités avant services, services avant câblage CLI
- Story complète avant la priorité suivante

### Parallel Opportunities

- T003, T004 en Phase 1 ; T010, T011 en US1 ; T017 en US2 ;
  T020 en US3 ; T023 en US4 ; T26, T29 en Phase 7
- Après la Phase 2, US3 et US4 peuvent être menées en parallèle
  par des personnes différentes (fichiers distincts)

---

## Parallel Example: User Story 1

```bash
# Tests US1 en parallèle (fichiers distincts) :
Task: "Tests unitaires de normalisation dans tests/unit/test_normalizer.py"
Task: "Tests d'intégration de découpage dans tests/integration/test_split.py"

# Puis implémentation séquentielle (même fichier md_chunking/splitter.py
# pour T012-T014, md_chunking/overlap.py indépendant) :
Task: "Overlap structurel dans md_chunking/overlap.py"   # parallélisable
```

---

## Implementation Strategy

### MVP First (US1 + US2)

1. Compléter la Phase 1 (Setup) puis la Phase 2 (Foundational)
2. Compléter la Phase 3 (US1) et la Phase 4 (US2)
3. **STOP et VALIDER** : pipeline minimal — document en entrée,
   chunks.json conforme en sortie
4. Démo possible avec tests/fixtures/ et Examples/

### Incremental Delivery

1. Setup + Foundational → socle prêt
2. US1 : découpage conforme → valider → démo
3. US2 : JSON de traçabilité → valider → démo (MVP complet)
4. US3 : relecture humaine → valider → démo
5. US4 : presets et sorties organisées → valider → démo
6. Polish → validation quickstart complète

---

## Notes

- [P] = fichiers différents, pas de dépendance
- Chaque story est livrable et testable indépendamment
- Committer après chaque tâche ou groupe logique (hooks actifs)
- Les tests doivent échouer avant l'implémentation
- Corpus Examples/ = validation finale (Phase 7), fixtures
  committées = tests reproductibles (décision D7)
