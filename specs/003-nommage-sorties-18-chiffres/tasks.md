---
description: "Task list for feature implementation"
---

# Tasks: Nommage des sorties (18 chiffres)

**Input**: Design documents from
`/specs/003-nommage-sorties-18-chiffres/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/output-naming.md, contracts/cli.md, quickstart.md

**Tests**: inclus — la stratégie de test D6 de research.md fait partie
des critères de succès SC-001 à SC-005 de la spécification.

**Organization**: tâches groupées par user story ; chaque story est
implémentable et testable indépendamment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: exécutable en parallèle (fichiers différents, pas de
  dépendance sur une tâche incomplète)
- **[Story]**: user story de rattachement (US1, US2, US3)
- Chemins de fichiers exacts dans chaque description

---

## Phase 1: Setup (infrastructure partagée)

**Purpose**: préparer le dépôt à accueillir l'état local du compteur

- [ ] T001 Ajouter l'entrée `counter.txt` au fichier `.gitignore`
  racine (FR-014, research.md D1) — le fichier d'état ne doit jamais
  être commité

---

## Phase 2: Foundational (prérequis bloquants)

**Purpose**: les deux modules purs dont toutes les user stories
dépendent ; aucune story ne peut commencer avant

**CRITICAL**: aucune user story ne peut commencer avant la fin de
cette phase

- [ ] T002 [P] Créer le module `md_chunking/naming.py` : extraction des
  lettres (NFKD, marques combinantes retirées, hors `a`–`z` ignoré,
  casse neutre — research.md D2), encodage et décodage bijectif base 26
  (A=1 … Z=26, FR-003), construction du nom
  `build_output_name(stem, title, occurrence)` en blocs 8/6/4 zéro-
  paddés à gauche (FR-002, FR-004 ; bornes : 5 lettres ≤ 12 356 630,
  4 lettres ≤ 475 254, bloc vide = `00000000`/`000000`)
- [ ] T003 [P] Créer le module `md_chunking/counter.py` :
  `COUNTER_PATH` résolu en `Path(__file__).resolve().parent.parent /
  "counter.txt"` (research.md D1), lecture au démarrage (absent →
  0001 ; contenu « NNNN\n » hors 0–9999 → erreur — FR-009),
  incrément modulo 10000 (9999 → 0000, FR-008), persistance après
  chaque document via fichier temporaire + `os.replace` atomique
  (FR-007, research.md D4)

**Checkpoint**: les deux modules existent et sont appelables — les
user stories peuvent démarrer

---

## Phase 3: User Story 1 - Sortie plate au nom unique (Priority: P1) - MVP

**Goal**: chaque document traité écrit `<18 chiffres>.json` et
`<18 chiffres>_review.md` directement dans `--output`, sans
sous-dossier ; les `--naming` sont rejetées

**Independent Test**: `python -m md_chunking doc.md --output
/tmp/v` produit exactement deux fichiers à 18 chiffres sans
sous-dossier ; `--naming title` échoue (code 2)

### Tests for User Story 1

> **NOTE**: écrire ces tests AVANT l'implémentation, vérifier leur
> ÉCHEC d'abord

- [ ] T004 [US1] Adapter `tests/integration/test_cli.py` : remplacer
  les 7 assertions verrouillant `output/NNNN/chunks.json` par la
  sortie plate, ajouter les tests « deux fichiers par document, aucun
  sous-dossier » (FR-001), « trois documents → six noms tous
  différents » (FR-006) et « --naming rejetée, code de sortie 2 »
  (FR-012)

### Implementation for User Story 1

- [ ] T005 [US1] Supprimer dans `md_chunking/cli.py` l'option
  `--naming` et les fonctions `_slugify`, `TITLE_SLUG_MAX`,
  `_subdir_name`, `_resolve_subdir` (FR-012, research.md D5) ;
  vérifier qu'aucun appel résiduel ne subsiste
- [ ] T006 [US1] Câbler le nommage dans `md_chunking/cli.py`
  (`main`, `process_document`) : lecture du compteur au démarrage —
  illisible → erreur de configuration, code 2, aucun fichier écrit
  (FR-009) ; par document produit, construction du nom 18 chiffres
  (FR-002), écriture de `<nom>.json` et `<nom>_review.md` à plat dans
  `--output` (FR-001), incrément + persistance du compteur (FR-006,
  FR-007) ; message console
  « {fichier} : {n} chunks -> {output}/{nom}.json » (contracts/cli.md)

**Checkpoint**: User Story 1 fonctionnelle et testable seule — MVP

---

## Phase 4: User Story 2 - Nom décodable sans perte (Priority: P2)

**Goal**: chaque bloc du nom redonne exactement ses lettres
d'origine ; casse et accents neutralisés

**Independent Test**: les tests unitaires de
`tests/unit/test_naming.py` passent, y compris l'aller-retour sur le
corpus réel (« CONTEXTE », « À LA DÉMOCRATIE »)

### Tests for User Story 2

- [ ] T007 [P] [US2] Créer `tests/unit/test_naming.py` : aller-retour
  encodage/décodage (FR-003), bornes (`zzzzz` → 12356630, `wxyz` →
  475254), padding gauche (`abc` → `00000731`, FR-004), casse
  (« CONTEXTE » = « contexte », FR-005), accents (« DÉMOCRATIE » =
  « DEMOCRATIE », FR-011), blocs vides (`00000000`, `000000`),
  noms plus longs que 5 lettres (tronqués aux 5 premières)

### Implementation for User Story 2

- [ ] T008 [US2] Corriger `md_chunking/naming.py` sur tout écart
  révélé par T007 ; la conformité au contrat
  `specs/003-nommage-sorties-18-chiffres/contracts/output-naming.md`
  fait foi (FR-003, FR-004, FR-005, FR-011)

**Checkpoint**: User Stories 1 et 2 fonctionnelles indépendamment

---

## Phase 5: User Story 3 - Compteur persistant et robuste (Priority: P3)

**Goal**: le numéro d'occurrence avance entre les exécutions, survit
aux interruptions, et échoue proprement si corrompu

**Independent Test**: deux exécutions successives produisent des
numéros strictement croissants ; `counter.txt` corrompu → code 2
sans écriture

### Tests for User Story 3

- [ ] T009 [P] [US3] Créer `tests/unit/test_counter.py` en isolation
  `tmp_path` (jamais le `counter.txt` réel du dépôt — research.md D6) :
  fichier absent → 0001 (FR-009), contenu non numérique ou hors
  0–9999 → erreur (FR-009), cycle 9999 → 0000 (FR-008), persistance
  après chaque document (FR-007), aucun fichier temporaire résiduel
  après `os.replace` (research.md D4)
- [ ] T010 [P] [US3] Ajouter dans `tests/integration/test_cli.py` :
  deux exécutions successives → numéros d'occurrence strictement
  croissants (SC-005) et contenu du JSON identique octet par octet
  entre exécutions du même document (SC-003)

### Implementation for User Story 3

- [ ] T011 [US3] Corriger `md_chunking/counter.py` sur tout écart
  révélé par T009/T010 ; vérifier que la persistance a bien lieu après
  chaque document (un numéro consommé n'est jamais réutilisé,
  FR-007)

**Checkpoint**: les trois user stories sont fonctionnelles
indépendamment

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: documentation et validation transverses

- [ ] T012 [P] Mettre à jour `README.md` : nommage 18 chiffres,
  format décodable (référence au contrat), `counter.txt` et sa
  régénération, disparition des sous-dossiers et de `--naming`
- [ ] T013 Exécuter les 6 scénarios de
  `specs/003-nommage-sorties-18-chiffres/quickstart.md` sur le corpus
  réel (`Examples/`), puis la suite complète `python -m pytest` :
  tout doit être vert (SC-001, SC-002, SC-004)
- [ ] T014 Vérifier `git check-ignore counter.txt` (T001 effectif),
  puis marquer les tâches accomplies dans ce fichier

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: aucune dépendance — démarrage immédiat
- **Foundational (Phase 2)**: après Phase 1 — BLOQUE toutes les
  user stories (T002, T003 requises par US1, US2, US3)
- **User Stories (Phases 3–5)**: dépendent de Phase 2 uniquement
- **Polish (Phase 6)**: dépend de la complétude des stories retenues

### User Story Dependencies

- **US1 (P1)**: après Phase 2 — câble les deux modules dans la CLI ;
  aucune dépendance aux autres stories
- **US2 (P2)**: après Phase 2 — ne dépend que de `naming.py` ;
  parallélisable avec US1 sur des fichiers différents
- **US3 (P3)**: après Phase 2 — ne dépend que de `counter.py` ;
  parallélisable avec US1 et US2

### Within Each User Story

- Tests d'abord, échec vérifié, puis implémentation, puis correction
- Modules (Phase 2) avant câblage (US1)
- US1 avant US3 côté intégration : T010 suppose la sortie plate de
  US1 en place

### Parallel Opportunities

- T002 et T003 (Phase 2) : fichiers différents — parallélisables
- T007, T009, T010 : fichiers de tests différents —
  parallélisables une fois la Phase 2 faite
- T012 : indépendant des autres fichiers de code

---

## Parallel Example: User Story 2 + 3

```bash
# Une fois la Phase 2 terminée, en parallèle (fichiers distincts) :
Task: "T007 [P] [US2] Créer tests/unit/test_naming.py"
Task: "T009 [P] [US3] Créer tests/unit/test_counter.py"
Task: "T010 [P] [US3] Ajouter tests compteur dans tests/integration/test_cli.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 + Phase 2 (T001–T003)
2. Phase 3 (T004–T006)
3. **STOP et VALIDER**: sortie plate unique, `--naming` rejetée
4. Le MVP est livrable : chaque exécution produit des fichiers
   identifiés

### Incremental Delivery

1. Setup + Foundational → fondations prêtes
2. puis US1 → test isolé → MVP
3. puis US2 → décodabilité vérifiée (SC-002)
4. puis US3 → compteur robuste (SC-003, SC-005)
5. Phase 6 → documentation et validation bout-en-bout

---

## Notes

- [P] = fichiers différents, aucune dépendance sur tâche incomplète
- Les tests ne touchent jamais le `counter.txt` réel du dépôt
  (isolation `tmp_path`, research.md D6)
- Le contenu du JSON et du rendu de relecture ne doit changer en
  rien (FR-010) — régression impossible par construction : ni
  `indexer.py` ni `reviewer.py` ne sont modifiés
- Committer après chaque tâche ou groupe logique ; valider à chaque
  checkpoint
