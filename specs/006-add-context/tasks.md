---
description: "Task list template for feature implementation"
---

# Tasks: Contexte utilisateur et auto-identification dans la sortie JSON

**Input**: Design documents from `/specs/006-add-context/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/cli.md, contracts/chunk-json.md, quickstart.md

**Tests**: inclus — la spec l'exige (Assumptions : copies
temporaires des dossiers `Examples/Extension/`, jamais les
originaux ; compteur isolé en `tmp_path`).

**Organization**: tâches groupées par user story (spec.md, P1-P3).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: exécutable en parallèle (fichiers différents)
- **[Story]**: story cible (US-1, US-2, US-3)
- Chemins exacts dans chaque description

## Path Conventions

Projet monolithe : `md_chunking/` (paquet) et `tests/` à la racine
du dépôt (structure du plan.md).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: s'assurer de partir d'une base verte avant tout.

- [x] T001 Vérifier la baseline : `.venv/Scripts/python -m pytest`
      passe sur la suite existante (suite verte attendue)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: le socle partagé par toutes les stories — champ
`chunkingid` (inconditionnel), validation de format, normalisation
de clé, option CLI. Aucune story ne peut commencer avant la fin de
cette phase.

- [x] T002 [P] Modifier `md_chunking/indexer.py` : `build_index`
      gagne les paramètres `nom: str` et `contexte: dict | None` ;
      le bloc `document` émet `chunkingid` (valeur de `nom`, sans
      extension, pour chaque document, FR-007) et `context`
      (l'objet verbatim, uniquement si `contexte` n'est pas
      `None`, FR-006) ; `schema_version` reste `"1.0"` (D7) ;
      conformité exacte à `specs/006-add-context/contracts/
      chunk-json.md`
- [x] T003 [P] Créer `md_chunking/contexts.py` : constante
      `CHAMPS_CONTEXTE` (exactement `Typologie`, `Auteur(s)`,
      `Titre`, `Editeur`, `Date`, `Référence`, `Citation` — ni
      manquante, ni supplémentaire, FR-004), fonction pure
      `charge_contexte(chemin) -> dict | None` (objet JSON lisible,
      clés exactes, valeurs jamais transformées, D4), fonction
      pure `cle_normale(nom) -> str` (NFKD sans diacritiques,
      minuscules, espaces convertis en `_`, seuls `a-z 0-9 _`
      conservés, tronqué à 8 caractères, D3)
- [x] T004 Modifier `md_chunking/cli.py` : option `--add-context`
      (désactivée par défaut, FR-001) ; `process_document` passe
      `nom` et le contexte éventuel à `build_index` ; sans
      l'option, résolution de la feature 005 inchangée et
      contextes tous `None` (D1, D8) — les sorties ne diffèrent
      de l'existant que par `chunkingid` (SC-002)

---

## Phase 3: User Story 1 - Dossier couple avec son contexte (P1) — MVP

**Goal**: un dossier contenant exactement 1 .md et 1 .json, traité
avec `--add-context`, produit une sortie embarquant le contexte
verbatim et son identifiant (FR-002, FR-004, FR-006, FR-007).

**Independent Test**: copie de `Examples/Extension/Couple` avec
`--add-context` : `document.context` contient les sept champs à
l'identique (`Référence` vide comprise) et `document.chunkingid`
égal au nom du fichier de sortie sans extension (quickstart
scénario 1).

### Implementation for User Story 1

- [x] T005 [US-1] Étendre `md_chunking/contexts.py` : fonction
      `apparie_niveau(mds, jsons) -> (couples, avertissements)` —
      branche couple : exactement 1 `.md` et 1 `.json` directs,
      quel que soit le nom, le `.json` apparié après validation
      (D5) ; format invalide → avertissement « .json de contexte
      invalide : {chemin} » et aucun contexte (D4, D6) ; fonction
      `resolve_avec_contextes(chemins) -> (documents avec
      contexte, avertissements)` : arguments dans l'ordre, fichier
      individuel jamais apparié (D8), `InputError` existante pour
      introuvable (D1)
- [x] T006 [US-1] Brancher dans `md_chunking/cli.py` : avec
      `--add-context`, appeler `resolve_avec_contextes`, imprimer
      les avertissements sur stderr, transmettre le contexte de
      chaque document à `process_document` (FR-008, D1)
- [x] T007 [P] [US-1] Créer `tests/unit/test_contexts.py` :
      `charge_contexte` (7 clés exactes, clé en trop, clé
      manquante, illisible, valeurs verbatim vides comprises),
      branche couple (1 + 1 quel que soit le nom, autres fichiers
      ignorés, json invalide → avertissement + classique), fichier
      individuel jamais apparié, avertissement exact « .json de
      contexte invalide : {chemin} » (FR-002, FR-004, FR-008)
- [x] T008 [US-1] Étendre `tests/integration/test_cli.py` : copie
      de `Examples/Extension/Couple` en `tmp_path` avec
      `--add-context` — `document.context` verbatim (`Référence`
      vide), `document.chunkingid` = stem du fichier écrit,
      compteur isolé ; sans l'option, `context` absent et sortie
      ne différant de l'existant que par `chunkingid` (SC-001,
      SC-002, quickstart scénarios 1 et 4)

**Checkpoint**: US-1 fonctionne seule — dossier couple en une
commande, sortie enrichie, comportement classique intact.

---

## Phase 4: User Story 2 - Corpus en sous-dossiers (P2)

**Goal**: le parcours récursif à toute profondeur, comptage par
niveau, ordre déterministe (FR-003, D2).

**Independent Test**: copie de `Examples/Extension/Sous-dossiers`
avec `--add-context` : trois sorties, chacune avec le contexte de
son propre sous-dossier (quickstart scénario 2).

### Implementation for User Story 2

- [x] T009 [US-2] Étendre `md_chunking/contexts.py` : récursivité
      dans `resolve_avec_contextes` — à chaque niveau, seuls les
      fichiers directs comptent (le contenu d'un sous-dossier ne
      compte jamais dans le niveau parent), `.md` du niveau triés
      casse neutre d'abord, puis descente dans les sous-dossiers
      triés casse neutre, profondeur d'abord (D2) ; niveau sans
      `.md` → avertissement « Dossier sans fichier .md :
      {dossier} » puis poursuite de la descente (FR-003, D6) ;
      un dossier argument sans aucun `.md` à l'issue du parcours
      reste code 0 avec avertissement (contrat cli.md)
- [x] T010 [US-2] Étendre `tests/unit/test_contexts.py` : niveau
      intermédiaire sans `.md` dont les sous-dossiers contiennent
      des couples (avertissement + descente), ordre déterministe
      (md du niveau puis sous-dossiers triés, reproductibilité des
      occurrences), imbrication à trois niveaux (FR-003, D2)
- [x] T011 [US-2] Étendre `tests/integration/test_cli.py` : copie
      de `Examples/Extension/Sous-dossiers` avec `--add-context`
      — trois sorties avec le contexte de leur sous-dossier,
      occurrences reproductibles ; sans l'option, avertissement
      « Dossier sans fichier .md » et code 0, comportement 005
      inchangé (quickstart scénario 2)

**Checkpoint**: US-1 et US-2 fonctionnent indépendamment — le
corpus organisé en sous-dossiers se traite en une commande.

---

## Phase 5: User Story 3 - Lot mélangé : couples et orphelins (P3)

**Goal**: la branche mélangée du cas border — appariement par
préfixe normalisé unique, orphelins et ambiguïtés en classique
(FR-005, FR-008, D3).

**Independent Test**: copie de `Examples/Extension/Multi-coupes
mix` avec `--add-context` : trois sorties avec contexte
(`premiere`, `an_rappo`, `ecalle_o`), deux sorties classiques,
aucun couple mal apparié (quickstart scénario 3).

### Implementation for User Story 3

- [x] T012 [US-3] Étendre `md_chunking/contexts.py` :
      `apparie_niveau` branche mélangée — un `.md` est apparié à
      un `.json` si `cle_normale` coïncide et que la
      correspondance est unique des deux côtés (D5) ; json apparié
      validé par `charge_contexte` (D4) ; `.json` non apparié →
      avertissement « .json de contexte orphelin : {chemin} » ;
      ambiguïté → avertissement « Appariement ambigu pour {md} »
      et classique (D6)
- [x] T013 [P] [US-3] Étendre `tests/unit/test_contexts.py` :
      `cle_normale` sur les trois couples réels d'exemples
      (`premiere-0034`/`premiere-seance-du-v-nettoye` →
      `premiere`, `AN_Rappo-0032`/`AN_Rapport` → `an_rappo`,
      `Ecalle_o-0040`/`Ecalle_ouvrage` → `ecalle_o`), accents et
      espaces (`Mécomptes publics` → `mecompte`... au sens de
      D3), ambiguïté (deux `.json` même préfixe, deux `.md` même
      préfixe), orphelin, unicité des deux côtés (FR-005, D3)
- [x] T014 [US-3] Étendre `tests/integration/test_cli.py` : copies
      de `Examples/Extension/Multi-couples` et `Multi-coupes mix`
      avec `--add-context` — 3 couples appariés par préfixe,
      orphelins en classique sans avertissement d'échec ; json
      renommé en orphelin → avertissement ; json dupliqué →
      ambiguïté + classique ; json à clé modifiée → invalide +
      classique (quickstart scénarios 3, 5, 6)

**Checkpoint**: les trois stories fonctionnent ; la cascade
complète est opérationnelle sur les quatre dossiers d'exemples.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: documentation et validation transverses.

- [x] T015 [P] Documenter `--add-context` dans `README.md` :
      option, reconnaissance des couples (co-localisation puis
      préfixe), limitation aux entrées dossier (SC-005)
- [x] T016 Exécuter `specs/006-add-context/quickstart.md` en
      entier (6 scénarios sur copies des exemples) et vérifier
      SC-001 à SC-004 : appariements exacts, verbatim vides
      compris, `chunkingid` = stem, orphelins identiques au
      classique
- [x] T017 Suite complète `.venv/Scripts/python -m pytest` verte
      + hooks pre-commit verts ; vérifier qu'aucune sortie sans
      `--add-context` ne diffère de l'existant au-delà du seul
      champ `chunkingid` (SC-002)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: aucun prérequis — démarrage immédiat
- **Foundational (Phase 2)**: dépend de Phase 1 — BLOQUE toutes
  les stories (T002/T003 en parallèle, T004 après T002)
- **US-1 (Phase 3)**: dépend de Phase 2 ; T005 puis T006, tests
  T007/T008 après implémentation
- **US-2 (Phase 4)**: dépend de Phase 2 et de T005 (résolution par
  niveau) — étend la même fonction vers la récursivité
- **US-3 (Phase 5)**: dépend de Phase 2 et de T005/T012 (branche
  mélangée de `apparie_niveau`, `cle_normale` de T003)
- **Polish (Phase 6)**: dépend de toutes les stories retenues

### User Story Dependencies

- **US-1 (P1)**: démarrable après Phase 2 — MVP autonome
- **US-2 (P2)**: étend US-1 (même fonction de résolution) mais
  reste testable indépendamment sur `Sous-dossiers`
- **US-3 (P3)**: étend `apparie_niveau` (US-1) avec `cle_normale`
  (T003) ; testable indépendamment sur `Multi-couples`

### Within Each User Story

- Module (`contexts.py`) avant branchement (`cli.py`)
- Tests unitaires avant tests d'intégration
- Une story complète avant la priorité suivante

### Parallel Opportunities

- T002 et T003 (fichiers différents, aucun interdépendance)
- T007, T010, T013 peuvent s'écrire en parallèle une fois les
  fonctions cibles en place
- T015 (README) est indépendant de toute story

---

## Parallel Example: User Story 1

```text
# Après Phase 2, lancer en parallèle :
Task: "T005 [US-1] contexts.py : apparie_niveau, branche couple,
       resolve_avec_contextes"
Task: "T007 [P] [US-1] tests/unit/test_contexts.py : validation,
       couple, avertissements"

# Puis séquentiellement :
Task: "T006 [US-1] cli.py : résolveur, stderr, contexte"
Task: "T008 [US-1] tests/integration/test_cli.py : Couple,
       chunkingid, SC-002"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 (baseline verte) puis Phase 2 (indexer, contexts,
   option CLI)
2. Phase 3 : US-1 — dossier couple en une commande
3. **STOP et VALIDER** : quickstart scénarios 1 et 4 sur une
   copie de `Examples/Extension/Couple`
4. Le MVP délivre déjà la valeur principale (contexte + identité
   embarqués)

### Incremental Delivery

1. Setup + Foundational → socle prêt
2. Ajouter US-1 → dossier couple → validation (MVP)
3. Ajouter US-2 → sous-dossiers récursifs → validation
4. Ajouter US-3 → lot mélangé, orphelins et ambiguïtés → validation
5. Polish : README, quickstart complet, suite verte

---

## Notes

- [P] = fichiers différents, aucune dépendance
- [Story] = traçabilité vers spec.md (US-1, US-2, US-3)
- Chaque story est indépendamment testable sur son dossier
  d'exemple (`Couple`, `Sous-dossiers`, `Multi-coupes mix`)
- Les contraintes des décisions D1-D9 (research.md) sont citées
  dans les tâches — ne pas les relâcher à l'implémentation
- Compteur isolé en `tmp_path` ; copies des exemples, jamais les
  originaux ni le compteur du dépôt
- Commit après chaque tâche ou groupe logique ; valider à chaque
  checkpoint de story
