# Feature Specification: Contexte et auto-identification dans la sortie JSON

**Feature Branch**: `[006-add-context]`

**Created**: 2026-10-14

**Status**: Draft

**Input**: Handoff de l'assessment `contexte-chunkingid` (verdict GO,
Option A cascade) : « Option CLI `--add-context` avec appariement en
cascade — (1) dossier contenant exactement 1 .md + 1 .json →
appariement par co-localisation, validation du format attendu quel que
soit le nom ; (2) dossier de sous-dossiers → même règle par
sous-dossier, récursivité circonscrite au mode actif ; (3) dossier
mélangé → préfixe 8 caractères des noms normalisés (cas border).
Sortie : `document.chunkingid` (stem numérique du fichier de sortie,
sans `.json`) + `document.context` (7 champs verbatim, vides compris).
Sans couple : avertissement et processus classique inchangé. »

## Clarifications

### Session 2026-10-14

- Q: Avec `--add-context`, comment la cascade d'appariement
  doit-elle se comporter dans une arborescence à plusieurs
  niveaux de sous-dossiers ? → A: Cascade à chaque niveau,
  comptage par niveau : chaque niveau est évalué sur ses seuls
  fichiers directs, la reconnaissance couple (FR-002) ou
  mélangée (FR-005) s'applique à chaque niveau, et la descente se
  poursuit même à travers un niveau intermédiaire sans .md.
- Q: Sous quels noms exacts les deux nouveaux champs doivent-ils
  apparaître dans le bloc documentaire du JSON de sortie ? → A:
  `document.chunkingid` et `document.context`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Découper un dossier couple avec son contexte (Priority: P1)

Un utilisateur prépare, dans un dossier, un document Markdown et un
fichier JSON de contexte le décrivant (typologie, auteurs, titre,
éditeur, date, référence, citation). Il lance la commande habituelle
en ajoutant l'option `--add-context` : le JSON de sortie du document
embarque, dans son bloc documentaire, l'identifiant numérique de son
propre fichier de sortie et les sept champs du contexte, copiés tels
quels — y compris les champs laissés vides par ses soins.

**Why this priority**: C'est le cœur de la demande et le plus petit
chemin vers la valeur : aujourd'hui aucune métadonnée descriptive ne
peut entrer dans la sortie et l'utilisateur réassocie tout à la main.
Cette story seule constitue le MVP.

**Independent Test**: Utiliser le dossier d'exemple `Couple` (1 .md +
1 .json) avec `--add-context` : la sortie contient les sept champs du
contexte à l'identique (champ vide compris) et un identifiant égal au
nom du fichier de sortie sans extension.

**Acceptance Scenarios**:

1. **Given** un dossier contenant exactement `un-doc.md` et
   `contexte-2026.json` (nom quelconque), **When** l'utilisateur
   invoque l'outil sur ce dossier avec `--add-context`, **Then** le
   JSON de sortie du document embarque les sept champs du contexte
   verbatim, et l'identifiant de sortie vaut le nom du fichier JSON
   produit sans extension.
2. **Given** le même dossier, **When** l'utilisateur invoque l'outil
   sans `--add-context`, **Then** aucun champ de contexte n'est
   embarqué ; la sortie ne diffère du comportement actuel que par
   l'identifiant de sortie, émis dans tous les cas (FR-007).
3. **Given** un dossier contenant exactement 1 .md et 1 .json dont les
   champs ne respectent pas le format attendu, **When** l'utilisateur
   invoque l'outil avec `--add-context`, **Then** un avertissement
   nomme le .json en cause, le document est traité par le processus
   classique, et le lot se poursuit.

---

### User Story 2 - Traiter un corpus organisé en sous-dossiers (Priority: P2)

Un utilisateur organise son corpus — son usage principal durable — en
sous-dossiers, chacun contenant un document et son contexte. Il lance
une seule commande avec `--add-context` sur le dossier racine :
chaque sous-dossier est parcouru, chaque couple est reconnu par
co-localisation (un .md + un .json, quels que soient leurs noms), et
chaque sortie embarque son contexte.

**Why this priority**: Usage principal déclaré par l'utilisateur pour
la suite ; c'est la disposition la plus robuste car l'appariement ne
dépend d'aucun nom de fichier. Elle nécessite le parcours des
sous-dossiers, aujourd'hui exclu.

**Independent Test**: Utiliser le dossier d'exemple `Sous-dossiers`
(3 sous-dossiers, chacun 1 .md + 1 .json) avec `--add-context` :
trois sorties, chacune avec le contexte de son sous-dossier et son
identifiant de sortie ; sans l'option, seuls les .md de la surface
sont traités, comme aujourd'hui.

**Acceptance Scenarios**:

1. **Given** un dossier racine contenant 3 sous-dossiers, chacun avec
   1 .md + 1 .json, **When** l'utilisateur invoque l'outil sur la
   racine avec `--add-context`, **Then** les 3 documents sont traités
   et chacun embarque le contexte de son propre sous-dossier.
2. **Given** un sous-dossier contenant 1 .md mais aucun .json,
   **When** la commande avec `--add-context` parcourt la racine,
   **Then** ce document est traité par le processus classique, sans
   avertissement.
3. **Given** un sous-dossier ne contenant aucun .md, **When** la
   commande avec `--add-context` le rencontre, **Then** un
   avertissement le signale et le lot se poursuit (comportement
   aligné sur l'existant pour un dossier sans .md).

---

### User Story 3 - Lot mélangé : couples et documents orphelins (Priority: P3)

Un utilisateur passe en une commande un dossier contenant à la fois
plusieurs .md et plusieurs .json — un cas border qu'il rencontrera
rarement. Chaque .md dont le nom, une fois normalisé, partage ses 8
premiers caractères avec un .json du même niveau est apparié à lui
seul ; les .md sans partenaire sont traités par le processus classique
et les .json orphelins sont signalés, sans jamais faire échouer le
lot.

**Why this priority**: Filet de secours pour la disposition la moins
robuste ; la valeur est réelle (les exemples `Multi-couples` et
`Multi-coupes mix` l'exigent) mais marginale par rapport aux deux
autres branches.

**Independent Test**: Utiliser le dossier d'exemple `Multi-coupes
mix` (3 couples + 2 .md orphelins) avec `--add-context` : 3 sorties
avec contexte, 2 sorties classiques, aucun couple mal apparié, code de
sortie inchangé.

**Acceptance Scenarios**:

1. **Given** un dossier contenant `Ecalle_ouvrage.md` et
   `Ecalle_o-0040.json`, **When** l'utilisateur invoque l'outil avec
   `--add-context`, **Then** le couple est reconnu (les 8 premiers
   caractères normalisés coïncident) et la sortie embarque le
   contexte.
2. **Given** un dossier contenant un .md dont aucun .json du même
   niveau ne partage le préfixe, **When** la commande est lancée,
   **Then** ce document est traité par le processus classique.
3. **Given** un dossier où deux .json partagent leur préfixe avec un
   même .md, **When** la commande est lancée, **Then** un
   avertissement signale l'ambiguïté, le document est traité par le
   processus classique, et aucun contexte n'est embarqué.

---

### Edge Cases

- `.json` de contexte illisible ou vide dans un dossier couple :
  avertissement nommant le fichier, processus classique, lot poursuivi.
- `.json` présent mais avec des champs en trop ou manquants :
  format invalide → avertissement, processus classique.
- Dossier contenant 1 .md et 2 .json, ou 2 .md et 1 .json :
  le dossier est traité comme mélangé (appariement par préfixe) ;
  si l'appariement reste ambigu, avertissement et processus classique.
- Niveau intermédiaire sans .md mais dont les sous-dossiers
  contiennent des couples : avertissement pour le niveau, descente
  poursuivie, couples des sous-niveaux traités.
- `.json` orphelin dans un dossier mélangé (aucun .md ne le
  rejoint) : avertissement, aucune sortie ne l'embarque.
- Fichiers autres que .md et .json dans un dossier couple (images,
  .txt) : ignorés, sans effet sur la reconnaissance du couple.
- `--add-context` utilisé avec uniquement des fichiers .md passés
  individuellement (aucun dossier) : l'option est sans effet
  (aucun appariement, aucun avertissement) ; l'identifiant de
  sortie reste émis (FR-007).
- `--add-context` combiné avec `--no-review` ou les options de
  taille : chaque option garde son effet indépendant.
- Document apparié dont le traitement échoue (contenu invalide) :
  sémantique de lot existante, l'échec n'interrompt pas les autres.
- Sans `--add-context`, un dossier contenant des .json : les .json
  sont ignorés comme tout fichier non .md, comportement inchangé.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: L'outil DOIT accepter une option `--add-context`,
  désactivée par défaut ; sans elle, aucun champ de contexte n'est
  jamais embarqué, et le comportement ne diffère du comportement
  actuel que par le seul champ d'identifiant de sortie (FR-007),
  toujours émis.
- **FR-002**: Avec `--add-context`, pour un dossier d'entrée dont le
  niveau considéré contient exactement un fichier `.md` et un
  fichier `.json`, l'outil DOIT apparier ce `.json` comme contexte du
  `.md`, quel que soit son nom, après validation du format attendu
  (FR-004) ; la présence d'autres fichiers de types quelconques ne
  DOIT PAS affecter cette reconnaissance.
- **FR-003**: Avec `--add-context`, l'outil DOIT parcourir
  récursivement les sous-dossiers d'un dossier d'entrée, à toute
  profondeur ; la cascade — FR-002 pour les niveaux à un couple,
  FR-005 pour les niveaux mélangés — s'évalue à chaque niveau sur
  les seuls fichiers directement présents : le contenu d'un
  sous-dossier ne compte jamais dans le niveau parent. Cette
  récursivité DOIT être circonscrite au mode `--add-context` —
  sans l'option, aucun sous-dossier n'est parcouru (comportement
  existant). Un niveau sans `.md` DOIT produire un avertissement
  et la descente se poursuit vers ses sous-dossiers ; un niveau
  dont un .md n'a pas de .json DOIT aboutir au processus
  classique, sans avertissement.
- **FR-004**: Le format attendu d'un `.json` de contexte DOIT être
  un objet contenant exactement les sept clés `Typologie`,
  `Auteur(s)`, `Titre`, `Editeur`, `Date`, `Référence`, `Citation` —
  ni clé manquante, ni clé supplémentaire ; les valeurs ne sont pas
  contraintes (chaîne ou liste, vide admis) et ne DOIVENT jamais
  être ni transformées, ni complétées, ni devinées.
- **FR-005**: Pour un niveau contenant plusieurs `.md` ou plusieurs
  `.json`, l'outil DOIT apparier un `.md` à un `.json` si et seulement
  si les huit premiers caractères de leurs noms, après normalisation
  — décomposition des accents puis suppression des diacritiques,
  minuscules, espaces convertis en `_`, seuls les caractères
  alphanumériques et `_` conservés — coïncident, et si cette
  correspondance est unique des deux côtés ; toute absence de
  candidat ou ambiguïté DOIT produire un avertissement et le
  traitement classique.
- **FR-006**: Pour chaque document apparié, le JSON de sortie DOIT
  embarquer un champ `document.context` contenant les sept champs
  du `.json` validé, copiés verbatim, y compris les champs vides.
- **FR-007**: Le JSON de sortie DOIT embarquer un champ
  `document.chunkingid` égal au nom du fichier de sortie, sans
  l'extension `.json` ; ce champ est inconditionnel : il est émis
  pour chaque document traité, avec ou sans `--add-context`
  (clarification du 2026-10-14).
- **FR-008**: Tout avertissement lié au contexte (format invalide,
  ambiguïté, .json orphelin, sous-dossier sans .md) DOIT être émis
  sur le flux d'erreur, en français, nommant le fichier en cause, et
  ne DOIT jamais faire échouer le lot ni modifier les codes de
  sortie existants.
- **FR-009**: Les numéros d'occurrence, les noms de sortie, le
  découpage, les chunks et le rendu de relecture DOIVENT rester
  inchangés, avec ou sans `--add-context`.
- **FR-010**: Le fichier `.json` de contexte DOIT être embarqué dans
  la sortie et ne DOIT jamais être recopié, renommé ni déplacé dans
  le dossier de sortie.
- **FR-011**: Le contrat du JSON de sortie DOIT être amendé pour
  documenter les deux nouveaux champs du bloc documentaire :
  `chunkingid`, inconditionnel (FR-007), et `context`,
  conditionnel à l'appariement (FR-006).

### Key Entities

- **Contexte documentaire** : ensemble de sept champs fourni par
  l'utilisateur dans un `.json` compagnon ; validé par présence
  exacte des clés, copié verbatim, jamais transformé.
- **Couple** : un document `.md` et son `.json` de contexte, reconnu
  par co-localisation (un .md + un .json au même niveau, quel que
  soit le nom) ou par préfixe de huit caractères normalisés (niveaux
  mélangés).
- **Clé d'appariement normalisée** : forme comparée d'un nom de
  fichier (accents simplifiés, minuscules, espaces convertis en
  `_`, caractères non alphanumériques hors `_` supprimés), tronquée
  à huit caractères ; n'intervient que dans le cas mélangé.
- **Identifiant de sortie** : nom numérique du fichier de sortie
  sans extension, restitué à l'intérieur même du fichier ; il
  n'introduit pas de nouveau nommage.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Les quatre dossiers d'exemples fournis (`Couple`,
  `Sous-dossiers`, `Multi-couples`, `Multi-coupes mix`) traités avec
  `--add-context` produisent exactement les appariements attendus :
  chaque couple embarque ses sept champs verbatim (champ vide
  compris), aucun couple mal apparié, les .md orphelins traités par
  le processus classique (baseline : aucun mécanisme aujourd'hui).
- **SC-002**: Pour toute invocation sans `--add-context`, chaque
  fichier de sortie ne diffère du comportement actuel que par le
  seul champ d'identifiant de sortie, présent partout (FR-007) ;
  découpage, chunks, review, nommage et absence de champ de contexte
  restent identiques octet par octet (aucune régression au-delà du
  champ prévu).
- **SC-003**: Tout état de contexte dégradé (.json invalide,
  ambigu, orphelin, sous-dossier sans .md) aboutit à un
  avertissement sur le flux d'erreur et à la poursuite du lot ;
  aucun de ces états ne change le code de sortie final.
- **SC-004**: Dans chaque sortie de document apparié, l'identifiant
  de sortie est vérifiable immédiatement : sa valeur est égale au
  nom du fichier qui la contient, sans extension.
- **SC-005**: Le README documente l'option `--add-context` et la
  reconnaissance des couples en une seule commande, sans exiger de
  préparation de fichier au-delà du dépôt du .json à côté du .md
  (baseline : aucune mention).

## Assumptions

- Format validé strict : exactement les sept clés, ni manquante ni
  supplémentaire ; types de valeurs libres (chaîne ou liste, vide
  admis). Découlant de « exactement les champs (y compris les
  vides) » ; un format invalide ne fait jamais échouer le lot.
- Dossiers intermédiaires (1 .md + 2 .json, 2 .md + 1 .json) :
  bascule dans la règle mélangé (préfixe), avec avertissement et
  classique si ambiguïté persiste.
- Table de normalisation du cas mélangé : décomposition des
  accents, suppression des diacritiques, minuscules, espaces
  convertis en `_`, seuls alphanumériques et `_` conservés, huit
  premiers caractères — validée sur les trois couples d'exemples
  (`premiere`, `AN_Rappo`, `Ecalle_o` coïncident tous).
- Appariement limité aux entrées dossier : un .md passé
  individuellement n'est jamais apparié, même avec `--add-context`
  (le dossier parent n'est pas considéré comme unité de couple).
- Portée de l'identifiant de sortie : toujours émis, avec ou sans
  `--add-context` — tranché par l'utilisateur en clarification du
  2026-10-14 (choix A) ; les tests existants verrouillant le contenu
  du JSON devront intégrer ce champ.
- Le champ `Typologie` du contexte vit dans le champ de contexte
  (sous-ensemble verbatim) et n'entre pas en collision avec le champ
  de typologie existant du bloc documentaire (nom du preset),
  inchangé.
- Ajouter des champs au bloc documentaire (dont un inconditionnel)
  est un changement compatible : la version du schéma de sortie
  n'est pas incrémentée, le contrat est amendé. À confirmer en
  revue de plan.
- Usage principal Windows/PowerShell ; comportement identique sur
  tout shell.
- Les tests valideront via des dossiers temporaires isolés et des
  copies des exemples, jamais les originaux de `Examples/Extension`
  ni l'état du compteur du dépôt.
