# Feature Specification: Entrée dossier pour la CLI

**Feature Branch**: `[005-dossier-entree-cli]`

**Created**: 2026-10-05

**Status**: Draft

**Input**: User description: "La CLI accepte un chemin de dossier à côté
des fichiers actuels ; les fichiers `.md` de sa surface (sans
récursivité) sont traités en tri alphabétique, comme s'ils avaient été
passés un par un." (handoff de l'assessment dossier-entree-md, verdict
GO, Option B)

## Clarifications

### Session 2026-10-05

- Q: Un dossier existant mais vide (ou sans aucun fichier `.md`)
  doit-il faire échouer la commande avec le code 2 ? → A: Non —
  succès au code 0 avec un message d'avertissement signalant
  qu'aucun `.md` n'a été trouvé ; aucune écriture.
- Q: Le même fichier présent deux fois dans une invocation
  (dossier + fichier individuel, ou dossier répété) doit-il être
  traité deux fois ? → A: Oui — traité à chaque occurrence, sans
  déduplication, conformément au principe « comme s'il avait été
  passé individuellement ».

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Découper tout un dossier en une commande (Priority: P1)

Un utilisateur (débutant sous PowerShell, public cible du README) veut
découper tous les documents Markdown d'un dossier — typiquement son
corpus de notes — sans les énumérer un par un. Il saisit la commande
documentée avec le chemin du dossier ; l'outil traite chaque fichier
`.md` du dossier, dans un ordre prévisible, et écrit pour chacun ses
deux fichiers de sortie au nom à 18 chiffres, exactement comme si les
fichiers avaient été passés individuellement.

**Why this priority**: C'est le cœur de la demande : aujourd'hui un
dossier échoue au code 2 et le shell Windows n'étend pas les jokers,
donc le public cible n'a aucun chemin simple vers le traitement par
corpus. Cette story seule constitue le MVP.

**Independent Test**: Créer un dossier avec k fichiers `.md` et n
fichiers d'autres types, invoquer l'outil avec le chemin du dossier :
2k fichiers de sortie apparaissent (k JSON + k reviews), les n autres
fichiers sont ignorés, et le compteur d'occurrence a avancé de k.

**Acceptance Scenarios**:

1. **Given** un dossier contenant 3 fichiers `.md`, **When**
   l'utilisateur invoque l'outil avec le seul chemin du dossier,
   **Then** les 3 documents sont traités et 6 fichiers de sortie sont
   écrits dans le dossier de sortie.
2. **Given** un dossier contenant 2 `.md` et 1 `.txt`, **When**
   l'utilisateur invoque l'outil avec le chemin du dossier, **Then**
   seuls les 2 `.md` sont traités (4 sorties), sans erreur ni
   avertissement pour le `.txt`.
3. **Given** un même dossier avec les mêmes 3 `.md` sur deux
   exécutions successives avec compteur réinitialisé, **When**
   l'utilisateur relance la même commande, **Then** les numéros
   d'occurrence attribués suivent le même ordre d'un run à l'autre.

---

### User Story 2 - Mélanger dossier et fichiers individuels (Priority: P2)

Un utilisateur veut compléter un dossier avec un fichier isolé
situé ailleurs : il passe le dossier et le fichier dans la même
invocation. Chaque argument est traité dans l'ordre de la ligne de
commande ; un dossier est développé à sa place, ses fichiers dans
l'ordre alphabétique du dossier.

**Why this priority**: Confort au-delà du MVP ; l'usage réel (`Examples/`
plus un fichier de travail) gagne en fluidité, mais la valeur est
inférieure au cas corpus pur.

**Independent Test**: Passer un dossier de 2 `.md` puis un fichier
individuel dans une invocation : 3 documents traités, les 2 du dossier
dans l'ordre alphabétique, puis le fichier isolé, occurrences
consécutives.

**Acceptance Scenarios**:

1. **Given** un dossier D contenant `b.md` et `a.md`, et un fichier
   `z.md` hors du dossier, **When** l'utilisateur invoque l'outil avec
   `D z.md`, **Then** les documents sont traités dans l'ordre `a.md`,
   `b.md`, `z.md` (occurrences 0001, 0002, 0003).
2. **Given** un fichier individuel puis un dossier dans cet ordre,
   **When** l'invocation est lancée, **Then** le fichier individuel est
   traité avant les fichiers du dossier.

---

### User Story 3 - État du lot après traitement (Priority: P3)

Un utilisateur lance l'outil sur un dossier contenant un fichier
corrompu ou illisible parmi des documents sains. Il doit savoir
précisément ce qui a été traité et ce qui a échoué : le comportement de
lot existant (un échec n'interrompt pas les autres documents, message
nommant le fichier en cause, code de sortie 1) s'étend naturellement
aux documents issus d'un dossier.

**Why this priority**: Sémantique de robustesse déjà garantie pour les
fichiers individuels ; il s'agit de s'assurer qu'elle est préservée à
l'identique, pas d'une nouvelle capacité.

**Independent Test**: Un dossier de 3 `.md` dont 1 illisible : les 2
valides sont traités, le message d'échec nomme le fichier en cause,
code de sortie 1.

**Acceptance Scenarios**:

1. **Given** un dossier de 3 `.md` dont 1 illisible, **When**
   l'invocation est lancée, **Then** 2 documents sont traités (4
   sorties), un message d'échec nomme le fichier en cause, et le code
   de sortie est 1.
2. **Given** un dossier dont le traitement réussit intégralement,
   **When** l'invocation se termine, **Then** le code de sortie est 0
   et chaque document a produit sa ligne de succès console.

---

### Edge Cases

- Dossier inexistant ou chemin qui n'est ni fichier ni dossier : échec
  rapide au code 2, message en français nommant le chemin en cause,
  aucun fichier écrit.
- Dossier existant mais vide, ou sans aucun `.md` : succès au code 0,
  message d'avertissement nommant le dossier, aucun fichier écrit
  (FR-005b).
- Fichier `.MD` (casse majuscule) sous Windows : traité comme un
  document Markdown.
- Fichier `.markdown` ou sans extension : ignoré, comme tout fichier
  non `.md`.
- Sous-dossier d'un dossier passé en argument : jamais parcouru, ni
  signalé.
- Dossier passé avec `--no-review` : chaque document ne produit que son
  JSON (comportement existant, inchangé).
- Fichier `.md` d'un dossier caché ou système (Windows) : traité
  comme tout `.md` du dossier.
- Même fichier présent deux fois dans une invocation (fichier
  individuel déjà couvert par un dossier passé, ou dossier passé deux
  fois) : traité à chaque occurrence, deux numéros d'occurrence
  consommés, deux sorties au nom distinct (FR-001).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: L'outil DOIT accepter, en argument d'entrée, un chemin
  de dossier à côté de chemins de fichiers, et traiter chaque fichier
  `.md` contenu directement dans ce dossier comme s'il avait été
  passé individuellement ; un même fichier apparaissant plusieurs
  fois dans la résolution des arguments DOIT être traité à chaque
  occurrence, sans déduplication.
- **FR-002**: L'outil DOIT ignorer, dans un dossier passé en
  argument, tout fichier dont l'extension n'est pas `.md` (comparaison
  insensible à la casse), sans erreur ni avertissement.
- **FR-003**: L'outil DOIT traiter les fichiers `.md` d'un dossier
  dans l'ordre alphabétique de leur nom de fichier, afin que les
  numéros d'occurrence attribués soient reproductibles pour un même
  contenu de dossier.
- **FR-004**: L'outil DOIT préserver l'ordre des arguments de la
  ligne de commande : chaque dossier est développé à sa position, ses
  fichiers dans l'ordre défini par FR-003.
- **FR-005**: L'outil DOIT échouer rapidement au code de sortie 2,
  sans écrire aucun fichier, si un argument d'entrée est introuvable
  ou n'est ni un fichier ni un dossier ; le message DOIT nommer le
  chemin en cause, en français.
- **FR-005b**: Un dossier existant mais vide, ou ne contenant aucun
  fichier `.md`, DOIT aboutir au code de sortie 0, sans écriture
  d'aucun fichier, avec un message d'avertissement en français nommant
  le dossier et signalant qu'aucun `.md` n'y a été trouvé.
- **FR-006**: L'outil DOIT conserver la sémantique de lot existante
  pour les documents issus d'un dossier : l'échec d'un document
  (illisible, contenu invalide) n'interrompt pas les autres, le
  message nomme le fichier en cause, et le code de sortie est 1 s'il
  y a au moins un échec.
- **FR-007**: L'outil DOIT attribuer les numéros d'occurrence et les
  noms de sortie aux documents issus d'un dossier selon les règles
  existantes (incrémentation par document, persistance, format 18
  chiffres), sans aucune adaptation.
- **FR-008**: L'outil NE DOIT PAS parcourir les sous-dossiers d'un
  dossier passé en argument, ni accepter de motifs jokers en entrée.
- **FR-009**: L'outil DOIT produire une ligne de message de succès
  console par document traité, identique au comportement existant.

### Key Entities

- **Dossier d'entrée** : chemin fourni par l'utilisateur sur la ligne
  de commande ; résolu, au moment de la validation de la
  configuration, en la liste ordonnée (FR-003) des fichiers `.md` de
  sa surface ; cette liste rejoint la liste des documents du lot sans
  distinction avec les fichiers passés individuellement. Aucune
  autre entité n'est introduite : compteur d'occurrence, nom de
  sortie, document et chunk restent inchangés.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un dossier de k fichiers `.md` (plus n fichiers
  quelconques) est traité en une seule commande et produit exactement
  2k fichiers de sortie (k JSON + k reviews, sauf `--no-review`),
  les n autres fichiers étant ignorés (baseline : impossible
  aujourd'hui, un dossier échoue au code 2).
- **SC-002**: Pour un même contenu de dossier, deux exécutions avec
  compteur réinitialisé attribuent les numéros d'occurrence dans le
  même ordre (reproductibilité du lot).
- **SC-003**: Un chemin d'entrée introuvable échoue au code 2 sans
  qu'aucun fichier ne soit écrit ; un dossier vide ou sans `.md`
  aboutit au code 0 avec un avertissement, sans aucune écriture.
- **SC-004**: Un échec de document au milieu d'un dossier laisse les
  autres documents traités et retourne le code 1 (aucune régression
  de la sémantique de lot).
- **SC-005**: Le README documente le traitement d'un dossier en une
  seule étape de commande, sans syntaxe d'énumération de shell
  (baseline : aucune mention ; contournement avancé optionnel).

## Assumptions

- Dossier vide ou sans `.md` : succès au code 0 avec avertissement,
  sans écriture — tranché en clarification du 2026-10-05 (remplace la
  piste initiale « code 2 » du handoff de décision).
- Mélange dossier + fichiers individuels : autorisé, ordre des
  arguments préservé — piste retenue du handoff.
- Filtre d'extension : `.md` seul, insensible à la casse ; `.markdown`
  refusé (ignoré) — piste retenue du handoff.
- Ordre intra-dossier : tri alphabétique du nom de fichier, suffisant
  pour la reproductibilité — piste retenue du handoff.
- L'empreinte attendue se limite à la validation et à la résolution
  des entrées ; boucle de traitement, compteur et nommage restent
  inchangés (exigence « sans modifier substantiellement » validée par
  le choix de l'Option B).
- Le corpus réel (`Examples/`) n'a pas de sous-dossiers Markdown à
  traiter ; la surface seule du dossier couvre le cas d'usage.
- Usage principal Windows/PowerShell (chemin documenté du README) ;
  le comportement reste identique sur tout shell.
- Les tests valideront via des dossiers temporaires isolés, jamais
  le dossier `Examples/` réel ni l'état du compteur du dépôt.
