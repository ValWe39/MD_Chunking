# Feature Specification: Compteur de tokens dans le rapport de relecture

> **Amendement (2026-10-05, feature 004)** : FR-T02 « ratio constant du
> code : 4 caractères par token, sans paramètre d'interface en v1 » est
> amendé par `specs/004-ratio-tokens-cli/spec.md` — le ratio devient un
> paramètre d'exécution (`--tokencpte`, bornes ]0 ; 10], point
> décimal), défaut recalé à 3,5 caractères par token. Le reste de la
> présente spécification reste en vigueur ; contrats supersédés pour
> les seuls points touchés :
> `specs/004-ratio-tokens-cli/contracts/review-render.md`.

**Feature Branch**: `004-assess2-token-compte`

**Created**: 2026-10-02

**Status**: Draft

**Input**: Handoff GO de l'assessment compteur-tokens-chunks —
afficher, pour chaque chunk du rapport de relecture (review.md), une
estimation approximative de son nombre de tokens, calculée localement
par heuristique déterministe zéro-dépendance (option A du concept).
Le découpage reste mesuré en caractères (décision D4 et FR-002 de la
feature 001 intacts). Approche « A puis B » : l'extension « compte
exact par tokenizer » (option B) reste possible plus tard sans
refonte.

## Clarifications

### Session 2026-10-02

- Q: Le ratio caractères→tokens doit-il être réglable par
  l'utilisateur en ligne de commande, ou rester une constante du code
  en v1 ? → A: Constante du code en v1, sans paramètre d'interface ;
  sa valeur est affichée dans l'en-tête du rapport et modifiable dans
  le code.
- Q: Le rapport doit-il signaler visuellement les chunks dont
  l'estimation dépasse un seuil de tokens, ou les nombres affichés
  suffisent-ils en v1 ? → A: Nombres seuls en v1, aucun signalement ;
  option à rouvrir quand un modèle cible sera choisi.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Lire une estimation de tokens par chunk (Priority: P1)

L'utilisateur ouvre le rapport de relecture d'un document découpé.
Chaque chunk y affiche, en complément de ses métadonnées existantes
(longueur en caractères, frontière, partie, page, position,
atomicité), une estimation de son nombre de tokens explicitement
marquée approximative (ex. « ≈ 250 tokens »). L'estimation est
calculée localement, sans réseau ni nouvelle dépendance, et le
découpage lui-même reste inchangé : unité, fourchette et overlap
restent mesurés en caractères.

**Why this priority**: c'est le cœur de la valeur — sans l'estimation
affichée au bon endroit, le problème (deviner ou vérifier ailleurs)
demeure entier ; les autres exigences n'en sont que des garde-fous.

**Independent Test**: découper un document, ouvrir le rapport de
relecture, vérifier que chaque chunk porte une estimation marquée
approximative et que la longueur en caractères est toujours
présente.

**Acceptance Scenarios**:

1. **Given** un document découpé, **When** l'utilisateur ouvre le
   rapport de relecture, **Then** chaque chunk y apparaît avec une
   estimation de tokens marquée approximative, en plus de ses
   métadonnées existantes.
2. **Given** un document découpé deux fois avec les mêmes paramètres,
   **When** les deux rapports sont comparés, **Then** les estimations
   sont identiques (déterminisme, SC-005 de la feature 001).
3. **Given** un environnement sans accès réseau, **When** le
   découpage et le rendu s'exécutent, **Then** le rapport est produit
   avec les estimations, sans aucun appel réseau (SC-006 de la
   feature 001).

---

### User Story 2 - Savoir ce que vaut l'estimation affichée (Priority: P2)

L'utilisateur lit l'en-tête du rapport et comprend sans ambiguïté que
le nombre affiché est une estimation modèle-agnostique fondée sur un
ratio caractères→tokens documenté, pas un compte exact d'un modèle
donné — et que la taille de référence du découpage reste le nombre de
caractères.

**Why this priority**: la crédibilité de l'information : un nombre
pris pour un compte exact devient une erreur de planification ;
l'avertissement est requis par les sources (research.md de
l'assessment) et par l'objectif 4 du problème défini.

**Independent Test**: ouvrir le rapport de relecture, vérifier que
l'en-tête mentionne le caractère approximatif et le ratio utilisé,
sans nom de modèle.

**Acceptance Scenarios**:

1. **Given** un rapport de relecture, **When** l'utilisateur lit son
   en-tête, **Then** une mention indique que les tokens sont
   estimés, avec le ratio employé, sans référence à un modèle
   précis.
2. **Given** un utilisateur qui lit l'en-tête d'un chunk, **When**
   il cherche la taille de référence du découpage, **Then** la
   longueur en caractères y figure toujours (le compte de tokens ne
   la remplace pas).

---

### Edge Cases

- Chunk très court ou vide : l'estimation vaut 0 ; affichage normal,
  pas d'erreur.
- Entité atomique très longue (bloc de code ou tableau hors
  fourchette) : l'estimation suit le même ratio ; la surestimation
  possible pour le code (ratio réel ~3 car./token contre ~4 pour la
  prose) est acceptée, l'usage étant la détection de risque et non
  le compte exact.
- Texte majoritairement non latin (ex. CJK, ~1,5 car./token) :
  l'estimation reste affichée mais l'écart est documenté comme non
  couvert par le ratio par défaut (aucun CJK dans le corpus réel).
- Document découpé en zéro chunk (fichier vide) : aucun affichage
  d'estimation, aucun changement de comportement par rapport à la
  feature 001.
- L'estimation porte sur le texte du chunk tel qu'affiché dans le
  rapport (overlap inclus si le chunk l'affiche).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-T01**: Le rapport de relecture DOIT afficher pour chaque
  chunk une estimation de son nombre de tokens, explicitement
  marquée approximative (préfixe « ≈ » ou formulation équivalente
  non ambiguë).
- **FR-T02**: L'estimation DOIT être calculée localement par une
  heuristique déterministe fondée sur la longueur du texte du chunk
  (ratio caractères→tokens constant du code : 4 caractères par token,
  arrondi supérieur ; sans paramètre d'interface en v1), sans
  nouvelle dépendance ni appel réseau (constitution II et III).
- **FR-T03**: L'unité de découpage reste le caractère : la
  fourchette min/max, l'overlap et l'ensemble du découpage de la
  feature 001 DOIVENT rester inchangés ; l'estimation ne DOIT jamais
  contraindre le découpage.
- **FR-T04**: Le rapport DOIT conserver la longueur en caractères de
  chaque chunk et afficher l'estimation de tokens en complément,
  jamais en remplacement.
- **FR-T05**: L'en-tête du rapport DOIT mentionner le caractère
  approximatif et modèle-agnostique de l'estimation, avec le ratio
  utilisé, sans nom de modèle.
- **FR-T06**: L'estimation DOIT être déterministe : les mêmes chunks
  produisent la même estimation d'une exécution à l'autre (SC-005
  de la feature 001 non régressif).
- **FR-T07**: L'index JSON et toutes les sorties machine DOIVENT
  rester inchangés : aucun champ de tokens n'est ajouté hors du
  rapport de relecture.
- **FR-T08**: Le format d'affichage DOIT distinguer la valeur
  estimée de son libellé, de manière qu'un compte exact (option B,
  hors périmètre v1) puisse remplacer l'estimation ultérieurement
  sans changer la structure du rapport.
- **FR-T09**: Le rapport NE DOIT PAS signaler de seuil ni de
  dépassement de budget de tokens en v1 : l'estimation est une
  information brute, le jugement de risque appartient au lecteur ; un
  signalement pourra être ajouté quand un modèle cible sera choisi.

### Key Entities *(include if feature involves data)*

- **Estimation de tokens**: valeur approchée associée à un chunk,
  dérivée de la longueur de son texte par un ratio constant ;
  toujours accompagnée de son caractère approximatif.
- **Ratio caractères→tokens**: constante du code en v1 (4 caractères
  par token, arrondi supérieur), affichée dans l'en-tête du rapport ;
  modifiable dans le code, sans paramètre d'interface en v1.
- **Rapport de relecture**: sortie existante (FR-008 de la feature
  001), enrichie d'une métadonnée par chunk et d'une mention
  d'en-tête ; seule sortie touchée par la feature.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-T01**: 100 % des chunks du rapport de relecture portent une
  estimation de tokens marquée approximative (baseline : 0 % —
  seule la longueur en caractères est affichée aujourd'hui).
- **SC-T02**: l'en-tête du rapport rend identifiables, sans
  documentation externe, le caractère approximatif, le caractère
  modèle-agnostique et le ratio utilisé.
- **SC-T03**: un document d'environ 50 chunks peut être passé au
  crible « quels chunks risquent de dépasser mon budget de tokens ? »
  sans outil externe et dans le temps de relecture déjà budgété
  (< 10 minutes, SC-004 de la feature 001).
- **SC-T04**: la sortie reste identique d'une exécution à l'autre à
  paramètres constants (SC-005 de la feature 001 non régressif).
- **SC-T05**: aucun appel réseau n'est émis lors du traitement
  (SC-006 de la feature 001 non régressif).

## Assumptions

- Le ratio est une constante du code en v1 : 4 caractères par token,
  arrondi supérieur ; il vise la prose française et surestime
  légèrement le risque pour le code (ratio réel ~3) — acceptable
  pour la détection de risque.
- Le corpus visé ne contient pas de texte CJK (constat des quatre
  exemples réels) ; l'écart de ratio pour ces scripts est hors
  périmètre v1.
- L'estimation porte sur le texte du chunk tel qu'affiché dans le
  rapport.
- Le modèle d'embedding aval n'est pas encore choisi ; l'estimation
  est modèle-agnostique et le restera tant que l'option B n'est pas
  déclenchée.
- L'option B (compte exact par tokenizer committé) est hors
  périmètre v1 ; elle sera déclenchée si une fenêtre cible étroite
  ou un besoin d'exactitude apparaît (critère à consigner le moment
  venu).
- La décision D4 (unité de mesure : caractères) et le FR-002 de la
  feature 001 restent inchangés ; cette feature n'ajoute qu'une
  information de relecture.
- Aucun total par document ni ratio différencié par typologie de
  contenu n'est prévu en v1 (choix par défaut, à rouvrir si l'usage
  le demande).
