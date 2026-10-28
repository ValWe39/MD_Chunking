# Feature Specification: Appariement robuste .md/.json sur préfixes longs

**Feature Branch**: `[013-fix-lien]`

**Created**: 2026-10-28

**Status**: Draft

**Input**: Handoff de l'assessment `robust-pairing` (verdict GO,
Option A — extension progressive par paliers) : « Extension
progressive de la clé d'appariement dans `apparie_niveau()` :
au lieu d'une troncature fixe à 8 caractères, essayer les
paliers 8, 12, 16, 20, … jusqu'à unicité ou longueur maximale.
`cle_normale()` retourne la chaîne normalisée complète.
Préserver les appariements existants (`Examples/Extension/`),
résoudre les cas à préfixe long (`Examples/Pairing/`), zéro
faux positif. Hors scope : format `.json`, branche couple,
comportement sans `--add-context`, nommage, flag opt-in. »

## Clarifications

### Session 2026-10-28

- Q: Quand l'appariement par paliers atteint un niveau où
  certains `.md` sont appariés sans ambiguïté mais d'autres
  n'ont aucun candidat à ce palier, faut-il continuer aux
  paliers supérieurs pour les `.md` restants, ou arrêter
  pour tout le niveau ? → A: Option A — continuer palier par
  palier pour tous les `.md` non résolus ; chaque `.md`
  avance indépendamment jusqu'à résolution ou longueur
  maximale (FR-004).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Traiter un corpus mélangé à préfixes longs (Priority: P1)

Un utilisateur prépare un dossier contenant plusieurs paires
`.md`/`.json` dont les noms partagent un préfixe commun long
(ex. `fipeco.fr-000033-nettoye.md` et
`fipeco.fr-000033-net-0063.json`). Il lance la commande avec
`--add-context` : chaque paire est appariée automatiquement,
sans renommage manuel, et chaque sortie JSON embarque les
sept champs du contexte.

**Why this priority**: C'est le problème observé qui motive
cette feature — sans résolution, l'utilisateur doit
systématiquement contourner manuellement (renommage ou
déplacement en sous-dossiers). C'est le MVP de la feature.

**Independent Test**: Utiliser le dossier `Examples/Pairing/`
(3 paires Fipeco) avec `--add-context` : trois sorties,
chacune avec les sept champs du contexte correspondant,
aucun avertissement « Appariement ambigu ».

**Acceptance Scenarios**:

1. **Given** un dossier contenant 3 paires `.md`/`.json`
   partageant le préfixe `fipeco.fr-00003`, **When**
   l'utilisateur invoque l'outil avec `--add-context`,
   **Then** les 3 paires sont appariées, chaque sortie
   embarque le contexte de sa paire, et aucun avertissement
   « Appariement ambigu » n'est émis.
2. **Given** le même dossier, **When** l'utilisateur
   invoque l'outil sans `--add-context`, **Then** le
   comportement est inchangé (aucun appariement tenté).
3. **Given** un dossier avec une paire dont le `.json` est
   invalide (clés manquantes), **When** l'utilisateur
   invoque l'outil avec `--add-context`, **Then** un
   avertissement nomme le `.json` invalide, le document
   correspondant est traité sans contexte, et le lot se
   poursuit.

---

### User Story 2 - Préserver les appariements existants (Priority: P2)

Un utilisateur dispose d'un corpus organisé avec des couples
à préfixe court (ex. `premiere-0034.json` et
`premiere-seance-du-v-nettoye.md`). Il lance la commande
avec `--add-context` : les appariements continuent de
fonctionner exactement comme avant, sans changement de
comportement ni de sortie.

**Why this priority**: La compatibilité ascendante est un
goal explicite du problème — casser ce qui fonctionne
actuellement serait une régression inacceptable.

**Independent Test**: Utiliser les dossiers `Examples/Extension/`
(Couple, Multi-couples, Multi-coupes mix, Sous-dossiers) avec
`--add-context` : les appariements sont identiques à ceux de
la feature 006, aucune régression détectée.

**Acceptance Scenarios**:

1. **Given** un dossier avec `premiere-0034.json` et
   `premiere-seance-du-v-nettoye.md`, **When** l'utilisateur
   invoque l'outil avec `--add-context`, **Then** le `.md`
   est apparié au `.json` (clé `premiere` au palier 8) et la
   sortie embarque le contexte.
2. **Given** un dossier avec `AN_Rapport.md` et
   `AN_Rappo-0032.json`, **When** l'utilisateur invoque
   l'outil avec `--add-context`, **Then** le `.md` est
   apparié au `.json` (clé `an_rappo` au palier 8).
3. **Given** un dossier avec `Ecalle_ouvrage.md` et
   `Ecalle_o-0040.json`, **When** l'utilisateur invoque
   l'outil avec `--add-context`, **Then** le `.md` est
   apparié au `.json` (clé `ecalle_o` au palier 8).

---

### User Story 3 - Détecter les vraies ambiguïtés (Priority: P3)

Un utilisateur a deux paires de fichiers réellement
homonymes (ex. `rapport-2024.md` + `rapport-2024.json` et
`rapport-2024-old.md` + `rapport-2024-old.json` dans des
situations où les clés normalisées complètes coïncident).
L'outil émet l'avertissement « Appariement ambigu » pour
les fichiers concernés, sans les apparier incorrectement.

**Why this priority**: Garantir l'absence de faux positifs
est un goal explicite — un appariement incorrect serait
plus nuisible qu'aucun appariement.

**Independent Test**: Créer un dossier avec deux `.md` et
deux `.json` ayant la même clé normalisée complète (même
nom de stem), invoquer avec `--add-context` : avertissement
« Appariement ambigu » pour chaque `.md`, aucun contexte
embarqué.

**Acceptance Scenarios**:

1. **Given** un dossier avec `doc-a.md`, `doc-a.json`,
   `doc-a-2.md`, `doc-a-2.json` où les clés normalisées
   complètes de `doc-a` et `doc-a-2` diffèrent mais le
   préfixe à 8 caractères est identique, **When**
   l'utilisateur invoque l'outil avec `--add-context`,
   **Then** chaque paire est appariée correctement (les
   clés complètes diffèrent).
2. **Given** un dossier avec deux `.md` de même stem
   normalisé complet, **When** l'utilisateur invoque
   l'outil avec `--add-context`, **Then** un avertissement
   « Appariement ambigu » est émis pour chaque `.md`, et
   aucun contexte n'est embarqué.

### Edge Cases

- **Préfixe long identique** : deux paires partageant le
  même préfixe normalisé complet (même stem) → avertissement
  « Appariement ambigu », aucun appariement (FR-009).
- **Longueur maximale atteinte** : si à la longueur maximale
  du stem normalisé le plus long, l'appariement reste
  ambigu → avertissement « Appariement ambigu » (FR-005).
- **`.md` sans candidat** : un `.md` sans `.json` correspondant
  à aucun palier → traitement classique, sans avertissement
  (seuls les `.json` orphelins sont signalés).
- **`.json` orphelin** : un `.json` non apparié à la fin de
  tous les paliers → avertissement « .json de contexte
  orphelin » (comportement actuel préservé).
- **Branche couple inchangée** : un niveau avec exactement
  1 `.md` et 1 `.json` → appariement inconditionnel, quel
  que soit le nom (FR-006).
- **Paliers** : 8, 12, 16, 20, 24, … de 4 en 4 jusqu'à la
  longueur maximale du stem normalisé le plus long du niveau.
- **Fichier individuel** : un `.md` passé en argument direct
  n'est jamais apparié (comportement actuel, D8 de la spec
  006).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `cle_normale()` MUST retourner la chaîne
  normalisée complète (NFKD, minuscules, espaces convertis
  en `_`, seuls `a-z`, `0-9` et `_` conservés), sans
  troncature.
- **FR-002**: `apparie_niveau()` MUST tenter l'appariement
  par paliers de préfixe croissant : 8, 12, 16, 20, 24, …
  caractères, de 4 en 4.
- **FR-003**: À chaque palier, un `.md` MUST être apparié à
  un `.json` si leurs clés normalisées tronquées à ce palier
  coïncident et que la correspondance est unique des deux
  côtés.
- **FR-004**: L'appariement MUST continuer palier par palier
  pour tous les `.md` non résolus ; chaque `.md` avance
  indépendamment jusqu'à résolution sans ambiguïté ou
  jusqu'à la longueur maximale. Les `.md` non résolus à la
  longueur maximale passent en traitement classique.
- **FR-005**: Si la longueur maximale (stem normalisé le plus
  long du niveau) est atteinte sans que l'appariement soit
  unique, l'avertissement « Appariement ambigu pour {md} »
  MUST être émis pour chaque `.md` concerné (comportement
  actuel préservé).
- **FR-006**: La branche « couple » (exactement 1 `.md` et
  1 `.json` au même niveau) MUST rester inchangée :
  appariement inconditionnel après validation du format.
- **FR-007**: Le comportement sans l'option `--add-context`
  MUST rester inchangé.
- **FR-008**: Les messages d'avertissement existants
  (« .json de contexte invalide », « .json de contexte
  orphelin », « Appariement ambigu pour {md} », « Dossier
  sans fichier .md ») MUST être conservés tels quels.
- **FR-009**: Aucun appariement incorrect (faux positif)
  MUST être produit : deux fichiers dont les clés normalisées
  complètes diffèrent ne sont jamais appariés, même si un
  palier intermédiaire les rend ambigus.
- **FR-010**: Les tests existants qui dépendent du
  comportement d'ambiguïté à 8 caractères MUST être adaptés
  pour refléter le nouveau comportement (résolution à un
  palier supérieur quand les clés complètes diffèrent).

### Key Entities *(include if feature involves data)*

- **Clé d'appariement normalisée (éphémère)** : chaîne
  normalisée complète d'un nom de fichier (NFKD, minuscules,
  espaces → `_`, `a-z 0-9 _` conservés), sans troncature.
  Attributs : valeur (chaîne), longueur (nombre de
  caractères).
- **Palier de préfixe (éphémère)** : longueur de troncature
  appliquée à la clé normalisée lors d'une tentative
  d'appariement. Valeurs : 8, 12, 16, 20, 24, … jusqu'à la
  longueur maximale du niveau.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Sur `Examples/Pairing/` (3 paires Fipeco),
  3/3 paires sont appariées et 0 avertissement
  « Appariement ambigu » est émis (baseline : 0/3, 3
  avertissements).
- **SC-002**: Sur `Examples/Extension/` (3 couples existants
  : Couple, Multi-couples, Multi-coupes mix), 3/3 paires
  sont appariées, identique au comportement de la feature
  006 (baseline : 3/3, cible : 3/3 — pas de régression).
- **SC-003**: 0 faux positif détecté sur les tests dédiés
  (deux paires à préfixe long identique non appariées).
- **SC-004**: La suite de tests complète passe (tous les
  tests existants, adaptés si nécessaire, plus les nouveaux
  tests de la feature).
- **SC-005**: Les 2 tests d'ambiguïté existants
  (`test_melee_ambiguite_deux_json_meme_prefixe`,
  `test_melee_ambiguite_json_partage_par_deux_md`) sont
  adaptés et passent avec le nouveau comportement.

## Assumptions

- Les paliers de 4 en 4 (8, 12, 16, 20, 24, …) sont
  suffisants pour différencier les cas réels observés ;
  aucun palier intermédiaire (9, 10, 11, …) n'est
  nécessaire.
- La longueur maximale est celle du stem normalisé le plus
  long du niveau ; au-delà, l'appariement est déclaré
  ambigu.
- Aucun seuil de confiance configurable n'est nécessaire ;
  l'unicité à un palier est le seul critère d'acceptation.
- Le nouveau comportement remplace directement l'ancien,
  sans flag opt-in.
- Le dossier `Examples/Pairing/` est copié en `tmp_path`
  pour les tests d'intégration, comme les autres exemples.
- La spec 006 est amendée (D3) ou une spec 007 dédiée est
  créée ; le choix est tranché en planification.
