# Feature Specification: Chunking de Markdown avec sortie JSON

**Feature Branch**: `002-assessment`

**Created**: 2026-10-02

**Status**: Draft

**Input**: Handoff GO de l'assessment md-chunking-json-output —
découper des documents Markdown en chunks paramétrables (taille
min/max, overlap, typologie) respectant la structure du document,
produire un JSON de traçabilité par chunk (chemin et numéro de
référence obligatoires ; titre, page, partie, position si balisés),
permettre un contrôle visuel avant embedding, sans framework
LangChain/LlamaIndex (contrainte utilisateur).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Découper un document en chunks conformes (Priority: P1)

L'utilisateur fournit un ou plusieurs fichiers Markdown à l'outil
avec une fourchette de taille (min/max) et un overlap. L'outil
découpe chaque document en chunks qui respectent au mieux la
structure : sections d'abord, paragraphes ensuite, phrases en
dernier recours. Chaque chunk tend à occuper la place maximale
autorisée sans jamais casser une frontière structurelle quand un
découpage cohérent reste possible. Le résultat est un JSON par
document.

**Why this priority**: c'est le cœur de la valeur — sans découpage
conforme et traçable, rien d'autre n'a de sens. C'est aussi le
dénominateur commun de tous les cas d'usage RAG visés.

**Independent Test**: donner à l'outil un document Markdown
structuré, vérifier que chaque chunk tient dans la fourchette et
qu'aucune frontière de section/paragraphe/phrase n'est coupée sans
nécessité, et qu'un JSON exploitable est produit.

**Acceptance Scenarios**:

1. **Given** un document Markdown titré et découpé en sections,
   **When** l'utilisateur lance le découpage avec min/max par
   défaut, **Then** chaque chunk est dans la fourchette et la
   sortie JSON contient un chunk par entrée avec son texte.
2. **Given** un document dont une section dépasse la taille max,
   **When** le découpage s'exécute, **Then** cette section est
   découpée en plusieurs chunks selon ses paragraphes (puis ses
   phrases), et chaque chunk porte le titre de la partie.
3. **Given** un document bruité (titres emboîtés dans des listes,
   fins de ligne mixtes CRLF/LF), **When** le découpage s'exécute,
   **Then** l'outil normalise l'entrée et découpe proprement sans
   produire de chunk vide ou dupliqué.
4. **Given** les mêmes documents et les mêmes paramètres, **When**
   le découpage est relancé, **Then** la sortie est identique
   (reproductibilité).

---

### User Story 2 - Exporter un index de traçabilité JSON (Priority: P1)

Pour chaque chunk, l'outil produit un index JSON : chemin du
document (obligatoire), numéro de référence du chunk (obligatoire),
titre du document, page, titre de partie/sous-partie et
positionnement dans la partie (si balisés et si plusieurs chunks
pour une même partie).

**Why this priority**: la traçabilité est le second pilier du
besoin — sans elle, impossible de rattacher un résultat de
recherche à son passage source après embedding.

**Independent Test**: produire le JSON, vérifier que chaque entrée
porte les deux champs obligatoires et que les champs conditionnels
apparaissent dès que l'information existe dans le document source.

**Acceptance Scenarios**:

1. **Given** un document balisé (titre, parties), **When** le JSON
   est produit, **Then** chaque chunk référence le chemin du
   document, son numéro de référence, le titre du document et le
   titre de sa partie.
2. **Given** un document sans balise de page, **When** le JSON est
   produit, **Then** le champ page est absent (jamais deviné).
3. **Given** une partie découpée en plusieurs chunks, **When** le
   JSON est produit, **Then** chaque chunk de cette partie indique
   sa position dans la partie.

---

### User Story 3 - Contrôler le résultat avant embedding (Priority: P2)

L'utilisateur consulte un rendu lisible du découpage — chaque chunk
numéroté, avec ses métadonnées et son texte — pour valider à l'œil
nu avant de passer à l'embedding.

**Why this priority**: la relecture humaine évite d'embedder un
découpage défectueux ; elle vient juste après la production
automatique mais n'en conditionne pas la validité technique.

**Independent Test**: ouvrir le rendu produit pour un document de
~50 chunks et vérifier qu'on peut repérer les frontières, les
métadonnées et le texte de chaque chunk sans outil supplémentaire.

**Acceptance Scenarios**:

1. **Given** un document découpé, **When** l'utilisateur ouvre le
   rendu de relecture, **Then** chaque chunk y apparaît avec son
   numéro, ses métadonnées et son texte intégral.
2. **Given** un rendu de ~50 chunks, **When** l'utilisateur le
   parcourt, **Then** il peut identifier un découpage incohérent
   (chunk hors frontière, chunk vide) en moins de 10 minutes.

---

### User Story 4 - Presets par typologie et sorties (Priority: P3)

L'utilisateur choisit un preset de typologie (documentation par
défaut ; articles ; conversations ; code ; livre/littérature) qui
préréglent taille et overlap, ou définit ses propres valeurs. Par
défaut, l'outil crée un dossier de sortie et range les résultats de
chaque document dans un sous-dossier dédié, numéroté ou construit à
partir des premières lettres du titre du document.

**Why this priority**: confort d'usage et hygiène des sorties —
utile dès que plusieurs documents se succèdent, mais non
bloquant pour la première utilisation.

**Independent Test**: lancer le traitement de 2 documents avec la
typologie « documentation », vérifier que les paramètres par défaut
de la typologie s'appliquent et que chaque document a son
sous-dossier de résultats.

**Acceptance Scenarios**:

1. **Given** aucun paramètre fourni, **When** l'utilisateur traite
   un document, **Then** le preset « documentation » s'applique et
   un sous-dossier dédié est créé dans le dossier de sortie.
2. **Given** un titre de document disponible, **When** le
   sous-dossier est créé, **Then** son nom est dérivé des
   premières lettres du titre ou d'un numéro si le titre est absent
   ou ambigu.
3. **Given** une typologie choisie, **When** le découpage
   s'exécute, **Then** la fourchette et l'overlap du preset
   s'appliquent, et l'utilisateur peut les surcharger.

---

### Edge Cases

- Une partie/sous-partie entière tient sous la taille min : elle
  forme un chunk unique plus court que min (jamais fusionnée
  arbitrairement avec sa voisine au prix du non-respect des
  frontières).
- Un paragraphe unique dépasse la taille max : découpage en
  phrases en dernier recours, avec overlap pour préserver la
  continuité.
- Document sans aucune structure (ni titres ni paragraphes
  nets) : découpage par phrases, signalé dans les métadonnées.
- Blocs de code et tableaux : traités comme atomiques (jamais
  coupés en leur sein), quitte à dépasser ponctuellement la
  fourchette, l'écart étant signalé.
- Titre du document absent : champ absent du JSON, sous-dossier de
  sortie numéroté.
- Paramètres invalides (min > max, overlap > 20%, typologie
  inconnue) : échec rapide avec un message clair, aucun fichier
  écrit.
- Fichier d'entrée illisible ou non-Markdown : échec rapide avec
  un message clair, les autres documents du lot continuent d'être
  traités.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: L'outil DOIT accepter en entrée un ou plusieurs
  fichiers Markdown et produire exactement un JSON par document.
- **FR-002**: L'outil DOIT découper chaque document en chunks dont
  la taille est bornée par une fourchette min/max paramétrable,
  mesurée en caractères (défaut : 100–1000).
- **FR-003**: L'outil DOIT respecter l'ordre de découpage : sections
  Markdown si disponibles, sinon paragraphes, sinon phrases en
  dernier recours.
- **FR-004**: L'outil DOIT tendre à l'occupation maximale de la
  fourchette pour chaque chunk, sans couper une frontière
  structurelle quand un découpage cohérent reste possible.
- **FR-005**: L'outil DOIT proposer un overlap paramétrable entre 0
  et 20% du chunk (défaut 15%), découpé selon les mêmes frontières
  structurelles que le chunk (parties, sinon paragraphes, sinon
  phrases).
- **FR-006**: L'outil DOIT fournir des presets par typologie en
  valeurs par défaut modifiables : documentation (par défaut),
  articles, conversations, code, livre/littérature à longue prose.
- **FR-007**: Le JSON de sortie DOIT contenir pour chaque chunk le
  chemin du document et un numéro de référence (obligatoires), et
  le titre du document, la page, le titre de partie/sous-partie et
  la position dans la partie (uniquement si balisés dans le
  document).
- **FR-008**: L'outil DOIT produire un rendu de relecture lisible
  par un humain : un fichier Markdown annoté par document, où
  chaque chunk est délimité et précédé de son numéro et de ses
  métadonnées.
- **FR-009**: L'outil DOIT créer par défaut un dossier de sortie et
  ranger les résultats de chaque document dans un sous-dossier
  dédié, numéroté par défaut ou dérivé des premières lettres du
  titre du document.
- **FR-010**: L'outil DOIT normaliser les entrées irrégulières
  (fins de ligne mixtes, titres emboîtés dans des listes) sans
  perte de contenu.
- **FR-011**: L'outil DOIT fonctionner entièrement en local :
  aucune donnée, résultat ou log ne quitte la machine ; aucune
  dépendance avec trackers/télémétrie (constitution II et III).
- **FR-012**: L'outil DOIT valider sa configuration au lancement et
  échouer rapidement avec un message clair si un paramètre est
  invalide (min > max, overlap hors 0–20%, typologie inconnue,
  chemin d'entrée absent).
- **FR-013**: Le schéma du JSON de sortie DOIT être documenté et
  stable ; aucun pipeline d'embedding n'impose de schéma externe,
  le format décrit par la présente spécification fait foi.

### Key Entities *(include if feature involves data)*

- **Document source**: fichier Markdown en entrée ; chemin, titre
  éventuel, structure (sections, paragraphes, phrases).
- **Chunk**: unité de texte découpée ; son texte, sa taille, sa
  frontière structurelle d'origine.
- **Index de chunk**: entrée JSON — chemin du document, numéro de
  référence, titre du document, page, titre de partie/sous-partie,
  position dans la partie (champs conditionnels selon balisage).
- **Preset de typologie**: jeu de valeurs par défaut (fourchette,
  overlap) associé à un type de document.
- **Sortie**: dossier de sortie contenant, par document, un
  sous-dossier avec le JSON d'index et le rendu de relecture.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% des chunks produits tiennent dans la fourchette
  min/max configurée (hors entités atomiques indivisibles signalées,
  ex. très long bloc de code).
- **SC-002**: 100% des chunks portent le chemin du document et un
  numéro de référence ; chaque champ conditionnel est présent dès
  que la balise existe dans le document source.
- **SC-003**: Chaque frontière de chunk coïncide avec une frontière
  structurelle (section, paragraphe ou phrase), sauf nécessité
  documentée (entité atomique, dernier fragment).
- **SC-004**: Un utilisateur peut valider le découpage d'un
  document d'environ 50 chunks à l'œil nu en moins de 10 minutes
  grâce au rendu de relecture.
- **SC-005**: Mêmes documents et mêmes paramètres produisent une
  sortie identique d'une exécution à l'autre (déterminisme
  reproductible).
- **SC-006**: Aucun contenu de document ne transite par le réseau ;
  l'ensemble du traitement fonctionne hors ligne (constitution II).

## Assumptions

- Un fichier Markdown en entrée représente un document ; le
  périmètre visé est celui d'un utilisateur unique traitant
  quelques dizaines de documents par exécution.
- L'interface utilisateur est une commande en ligne unique
  (préférence CLI de la constitution, principe IV).
- Le titre du document est lu dans le premier titre de niveau 1 ou
  le front-matter YAML s'il existe ; sinon le champ est absent.
- La page n'est renseignée que si une balise de page explicite
  existe dans le document (aucun marqueur dans les 4 exemples
  réels : le champ sera majoritairement absent).
- Les valeurs des presets (articles 1500/200, documentation
  1000/150, conversations 500/50, code 2000/300) sont des défauts
  modifiables, pas des vérités optimisées (non sourcées).
- L'overlap de 15% (suggéré par la formation Corsen) est un défaut
  ajustable, pas une constante (une étude citée en research
  recommande de le valider par évaluation).
- Le nommage des sous-dossiers de sortie est numéroté par défaut ;
  l'option « premières lettres du titre » utilise 30 caractères
  slugifiés, avec repli sur la numérotation si le titre est absent
  ou dupliqué.
- Aucun contournement des hooks pre-commit ni de publication
  forcée n'est toléré dans le développement (gouvernance du
  projet).
