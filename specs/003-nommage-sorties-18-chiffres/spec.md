# Feature Specification: Nommage des sorties (18 chiffres)

**Feature Branch**: `003-nommage-sorties-18-chiffres`

**Created**: 2026-10-05

**Status**: Draft

**Input**: User description: "handoff de decision.md en entrée et six
questions à trancher en route (casse, accents, cycle de vie du compteur,
reset après 9999, concurrence, sort de --naming)" — assessment
`.specify/assessments/generation-titre-json/` (verdict GO, option A).

## Clarifications

### Session 2026-10-05

- Q: À quel moment le numéro d'occurrence doit-il être mémorisé dans le
  fichier compteur : après chaque document produit, ou une seule fois à
  la fin de l'exécution ? → A: Après chaque document produit — un
  numéro consommé n'est jamais réutilisé, même en cas d'interruption.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Fichiers au nom unique par document (Priority: P1)

Quand l'utilisateur découpe un ou plusieurs markdowns, chaque document
traité produit ses fichiers de sortie directement dans le dossier de
sortie (pas de sous-dossier) : un document JSON et, sauf désactivation,
un rendu de relecture. Ces fichiers portent un nom unique à 18 chiffres
propre à cette occurrence de production. Deux documents différents, ou
deux traitements successifs du même document, ne portent jamais le même
nom.

**Why this priority**: c'est la valeur centrale de la feature — sans
unicité du nom, les fichiers s'écrasent ou se confondent dans le dossier
plat, et rien d'autre ne tient.

**Independent Test**: traiter deux fois le même fichier et trois
fichiers différents en une commande ; vérifier que les cinq fichiers
produits portent cinq noms distincts à 18 chiffres et qu'aucun n'a été
écrasé.

**Acceptance Scenarios**:

1. **Given** un dossier de sortie vide, **When** l'utilisateur découpe
   un fichier `contexte.md` (titre « CONTEXTE »), **Then** le dossier
   contient exactement deux fichiers : `<18 chiffres>.json` et
   `<18 chiffres>_review.md`, sans aucun sous-dossier.
2. **Given** une première exécution terminée, **When** l'utilisateur
   relance le découpage du même fichier, **Then** les nouveaux fichiers
   portent un numéro d'occurrence différent : l'ancien jeu de fichiers
   n'est pas écrasé.
3. **Given** une commande traitant trois fichiers, **When** elle se
   termine, **Then** les six fichiers produits portent six noms tous
   différents.

---

### User Story 2 - Nom décodable, rattaché à la source (Priority: P2)

À partir du seul nom de fichier, l'utilisateur peut retrouver les
informations d'origine : les 5 premières lettres du nom du fichier
markdown source (dans les 8 premiers chiffres) et les 4 premières
lettres du titre du document (dans les 6 chiffres suivants), via la
numération bijective en base 26 (A=1 … Z=26, chaque bloc lu comme un
seul nombre). Le décodage est exact — sans collision de lecture, sans
perte.

**Why this priority**: l'identifiant n'a de valeur que s'il est
lisible : c'est ce qui distingue cette feature d'un simple hash, et la
métrique de décodabilité est un critère de succès explicite de
l'assessment.

**Independent Test**: produire des sorties pour des fichiers connus,
puis décoder chaque bloc du nom et comparer aux lettres attendues du
nom de fichier source et du titre.

**Acceptance Scenarios**:

1. **Given** un fichier source nommé `contexte.md` (titre
   « CONTEXTE »), **When** on décode les 8 premiers chiffres du nom de
   sortie, **Then** on retrouve « conte » (5 premières lettres du nom
   de fichier) ; **When** on décode les 6 chiffres suivants, **Then**
   on retrouve « CONT » (4 premières lettres du titre).
2. **Given** un nom de fichier de moins de 5 lettres (ex. `abc.md`),
   **When** on décode son bloc de 8 chiffres, **Then** on retrouve
   exactement « abc » — les zéros de remplissage sont à gauche et ne
   faussent pas la valeur.
3. **Given** un document sans titre détecté (2 des 9 documents du
   corpus réel sont dans ce cas), **When** le nom est généré,
   **Then** le bloc de 6 chiffres vaut `000000` et le reste du nom est
   inchangé.

---

### User Story 3 - Numéro d'occurrence persistant (Priority: P3)

Le numéro d'occurrence (4 derniers chiffres) avance d'une unité à
chaque document produit, dans l'ordre de création des JSON, et survit à
la fermeture de l'outil : le dernier numéro utilisé est mémorisé
localement, à la racine de l'outil, uniquement ce numéro. Au 9999e
usage, le cycle repart à 0000.

**Why this priority**: l'unicité du nom (US-1) repose sur ce compteur ;
il est P3 car son mécanisme interne est invisible pour l'utilisateur
tant qu'il fonctionne.

**Independent Test**: exécuter l'outil, noter le numéro produit,
exécuter à nouveau : le numéro a avancé d'autant de documents que
créés.

**Acceptance Scenarios**:

1. **Given** aucune utilisation antérieure (ou fichier de compteur
   supprimé), **When** l'utilisateur découpe un document, **Then** le
   numéro d'occurrence vaut `0001`.
2. **Given** un dernier numéro mémorisé à 0007, **When** l'utilisateur
   découpe deux documents en une commande, **Then** ils portent `0008`
   et `0009` et le fichier mémorise `0009`.
3. **Given** un dernier numéro à 9999, **When** un nouveau document est
   produit, **Then** il porte `0000`.

---

### Edge Cases

- Nom de fichier source avec moins de 5 lettres (ex. `ab.md`, `9.md`,
  `_.md`) : le bloc encode les lettres disponibles ; un nom sans aucune
  lettre donne un bloc `00000000`.
- Titre du document absent (pas de H1 ni front-matter) : bloc titre à
  `000000` (cas réel du corpus).
- Titre ou nom de fichier avec accents, espaces, chiffres ou symboles :
  les lettres sont extraites dans l'ordre d'apparition, les accents
  sont ramenés à leur lettre de base (É => E), les autres caractères
  sont ignorés (FR-011).
- Fichier de compteur illisible ou corrompu : échec rapide avec message
  explicite, aucun fichier de sortie écrit (pas de reprise silencieuse
  à 0001 qui créerait des doublons).
- Interruption de l'outil en cours d'exécution (crash, annulation) :
  les numéros déjà consommés sont mémorisés (FR-007) ; une nouvelle
  exécution reprend au numéro suivant, sans réutiliser un numéro ni
  écraser les fichiers déjà produits.
- Deux exécutions de l'outil en parallèle : hors périmètre v1
  (cf. FR-013) — le dernier incrément gagne, un doublon de numéro est
  possible, le comportement est documenté.
- Un fichier de sortie portant déjà le nom généré (ex. fichier recréé
  manuellement) : le nom n'est jamais réutilisé au sein d'une même
  exécution, l'écriture écrase le fichier existant.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Chaque document traité DOIT produire ses sorties
  directement dans le dossier de sortie, sans sous-dossier : un
  fichier `<18 chiffres>.json` et, sauf désactivation du rendu de
  relecture, un fichier `<18 chiffres>_review.md`.
- **FR-002**: Le nom à 18 chiffres DOIT se composer de trois blocs :
  8 chiffres encodant les 5 premières lettres du nom du fichier source
  (sans extension), 6 chiffres encodant les 4 premières lettres du
  titre du document (`document.title`), 4 chiffres pour le numéro
  d'occurrence.
- **FR-003**: Chaque bloc de lettres DOIT être encodé en numération
  bijective en base 26 (A=1 … Z=26, la chaîne lue comme un seul nombre)
  et DOIT être décodable sans perte : l'aller-retour bloc → lettres →
  bloc redonne la valeur initiale.
- **FR-004**: Dans chaque bloc, les chiffres convertis DOIVENT être
  alignés à droite et le remplissage DOIT se faire par des zéros à
  gauche ; un bloc sans lettre (titre absent, nom sans lettre) vaut
  zéros.
- **FR-005**: L'encodage DOIT être insensible à la casse : « Contexte »
  et « CONTEXTE » produisent la même valeur.
- **FR-006**: Le numéro d'occurrence DOIT être attribué à chaque
  document produit, dans l'ordre de création des JSON, sans doublon au
  sein d'une exécution.
- **FR-007**: Le dernier numéro utilisé DOIT être mémorisé localement
  dans un fichier texte à la racine de l'outil, contenant uniquement ce
  numéro ; il DOIT être persisté après chaque document produit : un
  numéro consommé n'est jamais réutilisé, même en cas d'interruption de
  l'exécution.
- **FR-008**: Le numéro d'occurrence DOIT suivre un cycle : premier
  usage à 0001, progression d'une unité par document, retour à 0000
  après 9999, puis nouveau cycle.
- **FR-009**: Si le fichier de compteur est absent, l'outil DOIT
  repartir à 0001 ; s'il est présent mais illisible ou corrompu,
  l'outil DOIT échouer rapidement avec un message explicite, sans
  écrire de sortie.
- **FR-010**: Le contenu des fichiers produits (schéma du document
  JSON, rendu de relecture) DOIT rester strictement inchangé par
  rapport aux features 001 et 002 ; seule l'organisation (dossier
  plat) et le nommage changent.
- **FR-011**: Les lettres accentuées du nom de fichier et du titre
  DOIVENT être ramenées à leur lettre de base avant encodage (É => E=5,
  À => A=1) ; « DÉMOCRATIE » et « DEMOCRATIE » produisent la même
  valeur. Espaces, chiffres et symboles restent ignorés.
- **FR-012**: L'option CLI de nommage des sous-dossiers (`--naming`)
  DOIT être supprimée : les scripts qui l'utilisent échouent avec le
  message d'erreur standard des options inconnues (changement
  d'interface assumé).
- **FR-013**: Le comportement en exécutions parallèles DOIT être
  documenté comme non garanti en v1 (CLI local mono-utilisateur) : un
  doublon de numéro est possible, sans corruption de fichiers.
- **FR-014**: Le fichier de compteur DOIT être exclu du contrôle de
  version (état local de l'outil, pas du dépôt).

### Key Entities *(include if feature involves data)*

- **Nom de sortie** : chaîne de 18 chiffres, trois blocs (8/6/4) ;
  dérivable du fichier source et du numéro d'occurrence ; décodable
  bloc par bloc.
- **Compteur d'occurrence** : entier local à l'outil (0 à 9999),
  mémorisé uniquement sous forme du dernier numéro utilisé ; avance
  d'une unité par document produit ; partagé par tous les documents et
  toutes les exécutions.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100 % des fichiers produits par une exécution portent un
  nom à 18 chiffres conforme (mesuré sur la suite de tests et sur le
  corpus réel). (baseline : 0 %, tous nommés `chunks.json`)
- **SC-002**: Sur le corpus réel, chaque bloc de lettres de chaque nom
  se décode exactement vers les lettres attendues du fichier source et
  du titre du document (aller-retour sans perte).
- **SC-003**: Le contenu du document JSON d'un même document est
  identique d'une exécution à l'autre ; seuls les noms de fichiers
  diffèrent (numéro d'occurrence avancé).
- **SC-004**: Aucune régression des suites de tests des features 001
  et 002 après adaptation des tests à la nouvelle organisation
  (dossier plat, nouveaux noms).
- **SC-005**: Deux exécutions successives de l'outil produisent des
  numéros d'occurrence strictement croissants (compteur persistant
  vérifié sur trois exécutions consécutives).

## Assumptions

- Le « titre du markdown d'input » (bloc 1) désigne le nom du fichier
  source sans extension (arbitrage intake du 2026-10-05).
- Le corpus d'entrée est en français : les accents et les majuscules
  sont fréquents (constaté sur le corpus réel) ; la casse est
  neutralisée par défaut (FR-005), sur le précédent du slug existant
  du projet.
- Le cycle du compteur est modulo 10000 : 0001–9999 puis 0000,
  conformément à la formulation de l'utilisateur (« remis à 0000
  après 9999 ») ; 0000 est donc une valeur utilisée une fois par
  cycle.
- Le compteur avance par document produit (et non par exécution de la
  commande), conformément à « dans l'ordre de création des Json ».
- Le fichier de compteur est ignoré par git (FR-014) — l'état local ne
  doit pas polluer le dépôt.
- La concurrence (deux exécutions simultanées) est hors périmètre v1 :
  outil local mono-utilisateur (assessment, Risk posture).
- Les tests d'intégration existants qui verrouillent l'arborescence
  `output/NNNN/chunks.json` devront être adaptés — ampleur confirmée
  lors du plan.
- Aucune migration des anciennes sorties n'est fournie : les anciens
  sous-dossiers restent en l'état, les nouvelles exécutions écrivent à
  plat.
