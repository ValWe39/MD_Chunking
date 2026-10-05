# Idea Research: Titre à 14 chiffres pour le JSON de sortie

- **Slug**: generation-titre-json
- **Created**: 2026-10-05
- **Evidence confidence (overall)**: medium

## Users & Demand

- L'utilisateur unique identifié est le propriétaire du projet, qui a
  formulé la demande directement — signal exprimé, aucune donnée d'usage
  tierce ni ticket externe. — [source: session du 2026-10-05, intake.md]
  (confidence: high)
- Usage observé : 9 exécutions dans `output/`, toutes avec le nommage
  numéroté par défaut (`0001`…`0009`), aucune trace d'usage de
  `--naming title`. La numérotation séquentielle existe déjà dans l'outil
  (sous-dossiers), mais pas dans le contenu des JSON. — [source:
  `output/`, `md_chunking/cli.py:116-139`] (confidence: high)
- Aucune mesure de la taille du besoin réel : la demande ne mentionne pas
  le cas d'usage du titre généré (recherche, rattachement, unicité, tri).
  — [ASSUMPTION : la finalité est probablement un identifiant stable et
  lisible, mais rien ne l'étaye] (confidence: low)

## Prior Art

- **Interne — nommage par slug du titre déjà existant** :
  `md_chunking/cli.py:28` (`_slugify`) convertit déjà un titre en
  identifiant (minuscules, accents retirés par NFKD, 30 car. max) pour
  l'option `--naming title`. Précédent direct d'une conversion
  titre→identifiant dans l'outil, avec un choix technique différent
  (slug textuel, pas d'encodage numérique). — [source:
  `md_chunking/cli.py`] (confidence: high)
- **Interne — le titre n'est jamais deviné** : `detect_title`
  (`md_chunking/normalizer.py:54`) lit le front-matter YAML ou le premier
  H1, sinon retourne `None` et le champ `title` est absent du JSON. Le cas
  « si vide, afficher 00000 » de la demande est donc un cas réel, pas un
  cas d'école. — [source: `md_chunking/normalizer.py:54-62`,
  `md_chunking/indexer.py:34`] (confidence: high)
- **Donnée de corpus** : sur les 9 JSON existants, 2 n'ont pas de
  `document.title` (`None`) et 3 portent des titres accentués ou avec
  apostrophe (« Qu'est-ce que le Model Context Protocol ? », « À LA
  DÉMOCRATIE »). La règle « en cas d'accent, on passe à la lettre
  suivante » et la question de la casse auront un effet concret sur le
  corpus réel. — [source: `output/*/chunks.json`, relevé du 2026-10-05]
  (confidence: high)
- **Externe — Soundex et familles d'encodages lettre→chiffre** : Soundex
  (1918) encode un nom en 1 lettre + 3 chiffres pour rapprocher des
  orthographes différentes ; les encodages de ce type sont conçus pour
  la *recherche approximative* et souffrent de collisions connues. Le but
  ici (identifiant unique ?) n'est pas celui de Soundex (rapprochement).
  — [source: https://en.wikipedia.org/wiki/Soundex, snippets de
  recherche, pas de fetch direct] (confidence: medium)
- **Externe — compteurs séquentiels persistants** : le schéma
  « lire-modifier-écrire un compteur dans un fichier » est un pattern
  documenté et une source classique d'IDs dupliqués en cas d'exécutions
  concurrentes (deux processus lisent la même valeur). Les systèmes
  distribués le résolvent par incrément atomique ou UUID. Pour un CLI
  local mono-utilisateur le risque est faible mais non nul. — [source:
  https://github.com/Growth-Circle/cadis/issues/3126 (host github.com,
  allowlisted, snippets seulement) ;
  https://softwareengineering.stackexchange.com/questions/361491
  (host stackexchange, allowlisted, snippets seulement)]
  (confidence: medium)
- **Externe — UUID vs séquentiel** : les discussions d'ingénierie
  convergent : les IDs séquentiels « font plaisir aux humains » mais
  n'apportent pas d'unicité technique là où un UUID l'apporte ; un ID
  séquentiel exposé doit être géré par une seule autorité (ici, le
  fichier de compteur local). — [source:
  https://softwareengineering.stackexchange.com/questions/361491,
  snippets seulement] (confidence: medium)

## Market & Context

- Alternatives déjà disponibles dans l'outil pour identifier un document :
  le sous-dossier numéroté (`0001`…), le slug du titre
  (`--naming title`), et la paire `document.path` + `ref` du schéma JSON
  1.0. Coût de ne rien faire : les JSON restent identifiés par leur
  emplacement, sans identifiant embarqué dans le document. — [source:
  `md_chunking/cli.py`, `md_chunking/indexer.py`] (confidence: high)
- Sans la fonctionnalité, un utilisateur qui veut un ID stable doit le
  dériver lui-même du `path` ou du `title` en dehors de l'outil.
  — [ASSUMPTION] (confidence: low)

## Data & Constraints

- **Contradiction de format — bloquante telle que spécifiée** : avec
  A=1…Z=26, les lettres J à Z (10–26) occupent deux chiffres ; 5 lettres
  ne tiennent pas dans 5 positions à un chiffre par lettre. L'exemple
  fourni `00000800006701` découpé en 5/5/4 donne `00000` / `80000` /
  `6701` : `80000` ne peut pas être 5 positions alphabétiques (max 26),
  et `6701` dépasse le plafond annoncé du compteur à 4 chiffres si l'on
  lit `67`+`01`. L'exemple `abc.md` => `00123` implique un padding à
  gauche (zéros à gauche, valeurs à droite), contredisant la formulation
  « les afficher à droite du nombre ». Le format doit être re-spécifié
  avant toute décision. — [source: intake.md, analyse du format 5/5/4]
  (confidence: high)
- **Déterminisme non régressif (SC-005, feature 001)** : « toute sortie du
  pipeline à paramètres constants reste identique d'une exécution à
  l'autre ». Un compteur persistant incrémenté à chaque exécution
  rendrait le titre — et donc le JSON qui l'embarque — différent d'une
  exécution à l'autre sur le même document. Conflit direct si le titre
  est écrit dans `chunks.json`. — [source:
  `specs/002-compteur-tokens-chunks/data-model.md` (règles de
  validation), `specs/002-compteur-tokens-chunks/spec.md` FR-T06]
  (confidence: high)
- **Schéma JSON 1.0 figé** : la feature 002 a verrouillé l'index JSON
  (FR-T07 : « aucune modification »). Ajouter un champ titre dans
  `chunks.json` imposerait soit une dérogation, soit un passage de
  schéma en 1.1, soit de loger le titre hors du JSON (nom de fichier,
  review). — [source: `specs/002-compteur-tokens-chunks/spec.md:144-146`,
  `specs/002-compteur-tokens-chunks/data-model.md:37-40`]
  (confidence: high)
- **Constitution compatible sur le fond** : compteur local = conforme au
  principe II (local-first, hors-ligne). En revanche « à la racine de
  l'outil » pose une question d'emplacement concret : racine du dépôt
  (risque de commit accidentel d'un fichier d'état) vs répertoire
  utilisateur ; si l'outil est installé via pip, la « racine de
  l'outil » est un emplacement paquet, non un espace de données.
  — [source: `.specify/memory/constitution.md` II et IV]
  (confidence: medium)
- **Volume** : 9 documents produits à ce jour ; la limite 9999 du
  compteur et sa remise à zéro ne seront atteintes qu'à très long terme
  dans l'usage observé. La remise à zéro crée par conception des
  collisions d'identifiants après 9999 usages, mais surtout, deux
  documents partageant leurs 10 premières lettres ET arrivant sur le
  même numéro de compteur (après reset) auraient un titre identique :
  le format n'a pas de garantie d'unicité. — [source: `output/`
  (volume) ; analyse du format] (confidence: medium)
- **Casse et unicité non traitées dans la demande** : le corpus contient
  des titres tout en majuscules (« CONTEXTE », « À LA DÉMOCRATIE ») et
  mixtes ; la demande ne dit pas si A et a donnent le même chiffre.
  — [source: `output/*/chunks.json`] (confidence: high)

## Evidence Against the Idea

- Le format tel que capturé est contradictoire (encodage impossible
  au-delà de I=9, exemples incohérents, padding gauche/droite) — la
  proposition n'est pas implémentable sans re-spécification. — [source:
  analyse du format, intake.md] (confidence: high)
- Le compteur persistant introduirait le premier état mutable global
  dans un pipeline aujourd'hui sans état et déterministe, en conflit
  avec SC-005 si le titre entre dans une sortie machine. — [source:
  specs/002] (confidence: high)
- Pas de garantie d'unicité : collisions possibles (mêmes 10 lettres +
  compteur répété après reset), là où le besoin exprimé (« généré à
  chaque utilisation ») suggère que le numéro doit distinguer les
  documents. — [source: analyse du format] (confidence: medium)
- Règle YAGNI (constitution IV) : le cas d'usage du titre à 14 chiffres
  n'est pas énoncé ; sans finalité claire (tri ? rattachement à un LLM ?
  unicité de fichier ?), la charge d'un compteur local est difficile à
  justifier face aux alternatives existantes (slug, numérotation des
  sous-dossiers). — [source: `.specify/memory/constitution.md` IV]
  (confidence: medium)

## Gaps & Open Questions

- [NEEDS CLARIFICATION: cas d'usage du titre à 14 chiffres — que
  résout-il que le sous-dossier numéroté, le slug ou `document.path` ne
  résolvent pas ?]
- [NEEDS CLARIFICATION: règle d'encodage exacte — que devient une lettre
  J–Z (10–26) dans une position à un chiffre ? Les exemples
  `00000800006701` et `00123` sont-ils contractuels ou illustratifs ?]
- [NEEDS CLARIFICATION: sens du padding — zéros à gauche (conforme à
  l'exemple `00123`) ou à droite (conforme au texte) ?]
- [NEEDS CLARIFICATION: « titre du markdown d'input » — nom de fichier
  ou `document.title` détecté (H1/front-matter) ? Le champ existe déjà
  et peut être `None`]
- [NEEDS CLARIFICATION: destination du titre — champ du JSON (conflit
  avec le schéma 1.0 figé), nom de fichier, review.md, ou les deux ?]
- [NEEDS CLARIFICATION: casse (A vs a), accents (É => E=5 ou lettre
  ignorée ?) — la demande dit « on passe à la lettre suivante » mais
  l'exemple Soundex interne de `_slugify` normalise ; le corpus réel
  contient les deux cas]
- [NEEDS CLARIFICATION: emplacement du fichier compteur (« à la racine
  de l'outil ») et politique git (ignoré ? commité ?) ; comportement si
  le fichier est absent, corrompu ou supprimé]
- [NEEDS CLARIFICATION: après 9999, repart-on à 0000 ou à 0001 ? Le
  compteur est-il global ou par document ?]
- [NEEDS CLARIFICATION: comportement si deux exécutions de l'outil
  tournent en parallèle]

## Sources

- Fichiers internes du dépôt (lecture directe) : `md_chunking/cli.py`,
  `md_chunking/indexer.py`, `md_chunking/models.py`,
  `md_chunking/normalizer.py`,
  `specs/002-compteur-tokens-chunks/spec.md`,
  `specs/002-compteur-tokens-chunks/data-model.md`,
  `.specify/memory/constitution.md`, `output/*/chunks.json`.
- <https://en.wikipedia.org/wiki/Soundex> (host: en.wikipedia.org,
  policy: hors liste d'allowlist — contenu issu de snippets de
  résultats de recherche, aucun fetch direct de la page)
- <https://en.wikipedia.org/wiki/Phonetic_algorithm> (host:
  en.wikipedia.org, policy: idem)
- <https://github.com/Growth-Circle/cadis/issues/3126> (host: github.com,
  policy: allowlisted — snippets de recherche uniquement, aucun fetch
  direct)
- <https://softwareengineering.stackexchange.com/questions/361491>
  (host: softwareengineering.stackexchange.com, policy: allowlisted —
  snippets de recherche uniquement, aucun fetch direct)
