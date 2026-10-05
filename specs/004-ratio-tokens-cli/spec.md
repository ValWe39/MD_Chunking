# Feature Specification: Ratio caracteres/tokens reglable en CLI

**Feature Branch**: `004-ratio-tokens-cli`

**Created**: 2026-10-05

**Status**: Draft

**Input**: assessment `.specify/assessments/tokencpte-flottant/`
(decision.md, verdict GO, Option B — handoff). Demande d'origine :
rendre le ratio caracteres/tokens parametrable via une option dediee
`--tokencpte`, defaut 1 token = 3,5 caracteres (corpus essentiellement
francais).

## Clarifications

### Session 2026-10-05

- Q: Quelle plage de valeurs l'option de ratio doit-elle accepter comme
  valide ? → A: Decimal strictement positif jusqu'a 10 inclus (bornes
  ]0 ; 10]) ; toute valeur hors bornes est rejetee par echec rapide.
- Q: Comment le ratio effectif doit-il etre affiche dans l'en-tete du
  rapport de relecture ? → A: Arrondi d'affichage a une decimale
  (ex. 3.333333 → « 3.3 » ; defaut affiche « 3.5 »).
- Q: Quel pourcentage minimal de chunks doit avoir un ecart < 20 % face
  au compte reel pour que SC-001 soit atteint ? → A: 80 % des chunks.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Estimation recalibree pour le francais (Priority: P1)

L'utilisateur lance le pipeline sur un document francais sans aucune option
nouvelle. Le rapport de relecture affiche une estimation de tokens recalculee
avec le nouveau defaut de 3,5 caracteres par token (au lieu de 4), et
l'en-tete du rapport mentionne ce ratio effectif. Aucun autre changement
n'est visible : decoupage, index JSON et nommage sont identiques a avant.

**Why this priority**: C'est la valeur minimale livrable : meme sans utiliser
l'option, chaque relecture gagne en credibilite sur un corpus francophone
(densite reelle ~3,6-3,9 car./token, l'ancien defaut 4 sous-estimait le
risque d'environ 8 a 15 %).

**Independent Test**: Executer le pipeline sur un document du corpus reel
sans option et verifier que l'en-tete du rapport affiche le nouveau defaut
et que les estimations par chunk sont coherentes (len/3,5 arrondi superieur).

**Acceptance Scenarios**:

1. **Given** un document francais a decouper, **When** l'utilisateur execute
   le pipeline sans option de ratio, **Then** le rapport de relecture
   estime chaque chunk avec le defaut 3,5 caracteres par token et affiche
   ce ratio dans son en-tete.
2. **Given** un fichier d'entree et des parametres constants, **When** le
   pipeline est execute deux fois, **Then** l'index JSON et le rapport sont
   identiques octet par octet entre les executions (determinisme non
   regressif).

---

### User Story 2 - Ratio personnalise via l'option dediee (Priority: P2)

L'utilisateur adapte l'estimation a son corpus ou a un modele cible en
passant un ratio decimal a l'option dediee (ex. `--tokencpte 3.2`). Le rapport
produit utilise ce ratio pour tous les chunks de tous les documents de
l'execution, et l'en-tete affiche la valeur effectivement utilisee. Aucune
edition de code n'est necessaire.

**Why this priority**: C'est le but d'adaptabilite du probleme (but 3) :
sans lui, le recalibrage n'est qu'une constante de code remplacee par une
autre. Mais il ne sert que si l'utilisateur veut s'ecarter du defaut.

**Independent Test**: Executer le pipeline avec et sans l'option sur le meme
document et verifier que les deux estimations different conformement au
ratio passe, l'index JSON restant identique.

**Acceptance Scenarios**:

1. **Given** un document a decouper, **When** l'utilisateur execute le
   pipeline avec un ratio valide explicite, **Then** chaque estimation du
   rapport est calculee avec ce ratio et l'en-tete l'affiche.
2. **Given** plusieurs documents fournis en une execution, **When** un
   ratio explicite est passe, **Then** le meme ratio s'applique a tous les
   documents de l'execution.
3. **Given** l'option `--no-review`, **When** le pipeline est execute avec
   un ratio explicite, **Then** aucun rapport n'est produit, l'option est
   acceptee sans erreur et aucune estimation n'est calculee.

---

### User Story 3 - Ratio invalide rejete par echec rapide (Priority: P3)

L'utilisateur saisit un ratio invalide (zero, negatif, hors bornes, mal
forme). Le pipeline echoue immediatement avec un message clair et le code de
sortie de configuration ; aucun fichier n'est ecrit, le compteur d'occurrence
n'est pas incremente.

**Why this priority**: Garde-fou de robustesse coherent avec le comportement
existant des options (`--min`, `--overlap`) : echec rapide avant tout effet
de bord. Testable independamment des deux premieres stories.

**Independent Test**: Executer le pipeline avec successivement 0, -1, une
valeur hors bornes et une valeur mal formee, et verifier code de sortie 2,
message d'erreur et absence de toute ecriture.

**Acceptance Scenarios**:

1. **Given** un ratio saisi hors bornes autorisees, **When** le pipeline
   est execute, **Then** il echoue avec le code de sortie de configuration
   et un message explicitant les bornes, sans ecrire aucun fichier.
2. **Given** une valeur non numerique ou mal separee (ex. virgule decimale),
   **When** le pipeline est execute, **Then** il echoue avec le code de
   sortie de configuration et un message clair, sans ecriture.

---

### Edge Cases

- Ratio a la borne inferieure ou superieure des bornes documentees :
  accepte, l'estimation suit le meme arrondi superieur.
- Ratio tres petit (ex. 0,5 : 1 token = demi-caractere) : estimation tres
  elevee, affichage normal, aucune erreur — l'usage de detecteur de risque
  reste de la responsabilite du lecteur.
- Chunk tres court ou de longueur non multiple du ratio : arrondi superieur,
  estimation jamais nulle pour un chunk non vide.
- Executions melangeant plusieurs documents avec un ratio explicite : le
  ratio est global a l'execution, pas par document ni par typologie.
- Anciens rapports produits avec le defaut 4 : jamais regenere
  automatiquement ; aucune migration n'est prevue.
- Valeur avec separateur decimal a virgule (ex. `3,5`) : refusee comme
  mal formee, le message d'erreur documente le format attendu (point
  decimal).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Le rapport de relecture DOIT estimer les tokens de chaque
  chunk avec un ratio par defaut de 3,5 caracteres par token (en remplacement
  du defaut 4 de la feature 002), par division de la longueur du texte par
  le ratio, arrondi superieur.
- **FR-002**: L'outil DOIT offrir une option dediee (`--tokencpte`) acceptant
  un ratio decimal en caracteres par token ; toute valeur fournie remplace
  le defaut pour toute l'execution.
- **FR-003**: L'option DOIT rejeter par echec rapide (code de sortie de
  configuration, aucun fichier ecrit) toute valeur nulle, negative, hors des
  bornes ]0 ; 10] ou mal formee, avec un message explicitant les bornes
  et le format attendus.
- **FR-004**: Le rapport de relecture DOIT afficher dans son en-tete le ratio
  effectivement utilise, arrondi a une decimale, et marquer chaque
  estimation comme approximative (libelle et symbole existants de la
  feature 002 conserves).
- **FR-005**: L'estimation DOIT rester deterministe et modele-agnostique :
  meme texte et meme ratio donnent toujours la meme valeur, sans nouvelle
  dependance, sans tokenizer ni appel reseau (constitution II et III).
- **FR-006**: Le ratio ne DOIT avoir aucun effet sur le decoupage : l'unite
  reste le caractere ; fourchette min/max, overlap, guillemets et typologies
  ne changent pas (non regression de la feature 001).
- **FR-007**: L'index JSON et le nommage des sorties DOIVENT rester
  strictement inchanges : aucun champ `tokens` ni `ratio` a aucun niveau,
  memes noms de fichiers a parametres constants (garde-fous features 001 et
  003 ; FR-T07 de la feature 002 non regressif).
- **FR-008**: Le ratio fourni DOIT s'appliquer uniformement a tous les
  documents d'une meme execution et ne DOIT jamais etre persiste au-dela du
  rapport : aucune ecriture dans le compteur d'occurrence, l'index ou tout
  autre etat.
- **FR-009**: L'option DOIT interagir avec `--no-review` sans erreur :
  acceptee, ignoree pour l'affichage, aucune estimation produite.
- **FR-010**: L'usage de l'option (nom, format, bornes, defaut, effet) DOIT
  etre documente dans le README, et les artefacts de la feature 002
  amendes en consequence (FR-T02 et contrats) — le present changelog spec
  fait foi de la reouverture assumee de la decision v1 « sans parametre
  d'interface ».

### Key Entities *(include if feature involves data)*

- **Ratio caracteres->tokens** : parametre d'execution decimal, bornes
  documentees, defaut 3,5 ; transitoire (jamais stocke, jamais serialise) ;
  affiche dans l'en-tete du rapport de relecture.
- **Estimation de tokens** (entite existante de la feature 002, amendee) :
  valeur entiere approchee, calculee au rendu, marquee approximative ;
  seul son mode de calibrage change (constante de code -> defaut modifiable
  par option).
- Entites inchangees (garde-fous) : **Chunk**, **Index JSON**, **Compteur
  d'occurrence**, **Nom de sortie**, **Presets de typologie**.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Sur le corpus reel du depot, au moins 80 % des chunks ont un
  ecart inferieur a 20 % entre l'estimation du defaut 3,5 et le compte de
  reference d'un tokenizer moderne (mesure ponctuelle hors pipeline, aucun
  ajout de dependance au projet ; l'ecart des chunks atypiques — code,
  tableaux — est documente et attendu).
- **SC-002**: Tout ratio valide explicite modifie les estimations affichees
  conformement au ratio, et l'en-tete du rapport affiche toujours le ratio
  effectif — verifiable sur un document temoin sans connaissance de
  l'implementation.
- **SC-003**: Tout ratio invalide (nul, negatif, hors bornes, mal forme)
  conduit a un echec rapide sans aucune ecriture, verifiable par le code
  de sortie et l'absence de fichiers produits.
- **SC-004**: Pour les memes entrees et ratios, les sorties (index JSON,
  rapport, noms) sont identiques d'une execution a l'autre ; a ratio
  identique, l'index JSON est identique octet par octet a celui produit
  avant la feature (non regression mesurable).
- **SC-005**: La suite de tests existante (70 tests des features 001-003)
  reste verte apres extension aux nouveaux comportements.

## Assumptions

- Le defaut 3,5 caracteres par token est un choix utilisateur assume,
  legerement conservateur face aux mesures externes (~3,6-3,9 car./token
  pour le francais sur tokenizers recents) ; aucune mesure locale sur le
  corpus reel n'a ete faite a ce jour, et SC-001 prevoit cette mesure
  ponctuelle hors pipeline.
- Bornes de validation : ratio decimal strictement positif, borne superieure
  a 10 caracteres par token — couvre largement les densites connues (CJK
  ~1,5, code ~3, prose ~4) ; au-dela, la saisie est consideree erronee.
- Separateur decimal : le point (ex. `3.5`), convention CLI usuelle ; la
  virgule est refusee avec un message documentant le format attendu.
- Le ratio est un parametre global d'execution, pas par typologie de preset
  ni par document ; les ratios differencies par typologie restent hors
  perimetre (option ecartee dans le concept).
- L'amendement des artefacts de la feature 002 (FR-T02, contrats
  review-render.md et cli.md) fait partie du perimetre de planification de
  cette feature ; le modele cible aval reste non choisi, et le compte exact
  par tokenizer (option B de la feature 002) reste hors perimetre.
