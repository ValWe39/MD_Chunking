# Idea Research: Champs context et chunkingid dans le JSON de sortie via --add-context

- **Slug**: contexte-chunkingid
- **Created**: 2026-10-14
- **Evidence confidence (overall)**: medium

## Users & Demand

- La demande émane du propriétaire unique du dépôt (outil local,
  mono-utilisateur) ; c'est un besoin déclaré, non observé en
  production — [ASSUMPTION : aucun autre utilisateur connu, pas de
  signal externe] (confidence: medium)
- Le signal d'engagement est fort : l'utilisateur a préparé un corpus
  de test réel et complet — 4 dossiers dans `Examples/Extension/`
  couvrant exactement les 3 cas d'usage annoncés (couple simple,
  sous-dossiers, multi-couples, mixte avec orphelins), soit ~2,9 Mo
  de Markdown (74 Ko à 625 Ko par fichier) et 3 fichiers de
  contexte — [source: Examples/Extension/, mesuré par `wc -c`]
  (confidence: high)
- Le cas d'usage aval (enrichir les chunks de métadonnées
  bibliographiques pour citation/traçabilité) est déclaré par
  l'utilisateur, non observé — [source: intake.md]
  (confidence: low)

## Prior Art

- **Interne, direct** : le schéma de sortie actuel
  (`md_chunking/indexer.py:27-58`, contrat
  `specs/001-md-chunking/contracts/chunk-json.md`) porte déjà la
  trace du document au niveau `document` (`path`, `title`,
  `structure`, `typologie`). La philosophie « jamais deviné »
  (FR-007) s'applique : `document.title` n'est émis que s'il est
  balisé. L'idée est cohérente avec cette philosophie : au lieu de
  deviner les métadonnées, l'utilisateur les fournit —
  [source: indexer.py, chunk-json.md] (confidence: high)
- **Interne, tension** : la décision spec 003
  (`generation-titre-json`, verdict GO, option A) a remplacé le
  nommage par titre par un nom à 18 chiffres — le nom de fichier est
  « le seul identifiant » des sorties, écrites à plat dans `output/`
  (`output/016492360000000016.json` observé). L'intake formule
  `chunkingid` comme « le titre du .json de sortie (`<titre>`.json) » :
  sous le nommage actuel, ce serait le nom à 18 chiffres, pas un
  titre — la sémantique exacte de `chunkingid` reste à trancher —
  [source: .specify/assessments/generation-titre-json/decision.md,
  md_chunking/naming.py, ls output/] (confidence: high)
- **Interne, tension** : la spec 005 (entrée dossier) a tranché
  « surface seule, aucune récursivité » (FR-008) après avoir listé
  la récursivité comme inconnue. Le cas « Sous-dossiers » de l'idée
  (dossier contenant des sous-dossiers de couples) rouvre cette
  décision pour `--add-context` — [source:
  specs/005-dossier-entree-cli/contracts/cli.md:31-33 ;
  .specify/assessments/dossier-entree-md/research.md:128-129]
  (confidence: high)
- **Externe** : les sidecar files (métadonnées à côté du fichier
  source, liées par nom) sont un précédent établi — XMP, THM,
  BIDS/Psych-DS (`.json` portant exactement le même nom que le
  fichier de données), sidematter-format. Leur faiblesse documentée :
  l'OS ignore la relation, et un renommage d'un des deux fichiers
  brise le lien — argument pour un appariement aidé par l'outil —
  [source: en.wikipedia.org/wiki/Sidecar_file,
  psychds-docs.readthedocs.io, github.com/jlevy/sidematter-format —
  snippets de recherche, pages non fetchées] (confidence: medium)
- **Externe** : la pratique RAG standard attache des métadonnées
  (document ID, source, date) à chaque chunk ou vecteur, souvent
  comme blob JSON, et les filtres de métadonnées améliorent nettement
  la pertinence de la récupération — la sortie enrichie aurait une
  valeur aval directe — [source: stackoverflow.blog (hôte
  allowlisté), gpt-trainer.com, github.com/langchain-ai/langchain
  issue #12067 — snippets de recherche, pages non fetchées]
  (confidence: medium)
- **Externe** : les 7 champs du .json de contexte (Typologie,
  Auteur(s), Titre, Editeur, Date, Référence, Citation) correspondent
  presque un à un aux variables CSL-JSON (`type`, `author[]`,
  `title`, `publisher`, `issued`, identifiant, citation) — le
  standard bibliographique d'échange. Le schéma de l'utilisateur
  n'est pas du CSL-JSON (libellés français, dates en texte libre
  « 30 septembre 2026 »), mais l'adoption verbatim demandée est
  compatible avec un stockage neutre ; une conversion CSL resterait
  possible en aval — [source: grobid.org/formats/csl-json,
  citeproc-js.readthedocs.io, citation-style-language/schema —
  snippets de recherche, pages non fetchées] (confidence: medium)

## Market & Context

- Alternative actuelle : l'utilisateur n'a aucun moyen d'associer
  des métadonnées aux sorties — la sortie à plat à 18 chiffres ne
  porte que `document.path`/`title` du .md lui-même ; la
  réassociation se ferait à la main en aval — [source: indexer.py,
  naming.py] (confidence: high)
- Coût de l'inaction : modéré — les chunks produits restent
  utilisables ; seule l'enrichissement bibliographique est absent.
  Mais le corpus de test préparé montre une intention d'usage
  réelle et imminente — [ASSUMPTION] (confidence: medium)
- Constitution : II local-first (aucun réseau requis, JSON en
  stdlib), III sans dépendance nouvelle ; IV simplicité — une
  nouvelle option CLI et une règle d'appariement sont des ajouts de
  surface à justifier — [source: .specify/memory/constitution.md]
  (confidence: high)

## Data & Constraints

- Les 3 fichiers de contexte d'exemple sont structurés et
  cohérents : 7 champs exacts, `Auteur(s)` toujours une liste,
  `Référence` vide dans 1 cas sur 3 (confirmant l'exigence « y
  compris les vides »), dates en texte libre français —
  [source: `Examples/Extension/*/*-00xx.json`, lus intégralement]
  (confidence: high)
- **Contradiction règle/exemples sur la normalisation** : la règle
  d'appariement annonce « hors espaces, accents et symboles », mais
  les couples fournis ne matchent que si le trait de soulignement
  est conservé : `Ecalle_o-0040.json` → `Ecalle_o` = 8 premiers
  caractères de `Ecalle_ouvrage.md` uniquement si `_` compte ; en
  le supprimant on compare `Ecalleo0` à `Ecalleou` (échec). Idem
  `AN_Rappo` / `AN_Rapport`. Aucun exemple ne contient d'espace,
  d'accent ni de différence de casse dans les 8 premiers
  caractères : la clause de normalisation est non testée par les
  exemples — [source: Examples/Extension/, vérification caractère
  par caractère] (confidence: high)
- Risque de collision du préfixe 8 caractères : deux .md partageant
  les 8 premiers caractères (ex. `Rapport_2024.md` /
  `Rapport_2025.md`) matcheraient le même .json de contexte ; aucun
  exemple ne couvre ce cas — [ASSUMPTION] (confidence: medium)
- Chevauchement sémantique : le champ `Typologie` du contexte
  (« Compte-rendu », « Rapport », « Ouvrage ») entre en collision
  potentielle avec `document.typologie` existant (nom du preset de
  découpage) et l'option `--typologie` de la CLI — [source:
  Examples/Extension/*/*.json, indexer.py, cli.py]
  (confidence: high)
- Le compteur d'occurrence est à 0018 ; les suffixes `-0032`,
  `-0034`, `-0040` des fichiers de contexte d'exemple ressemblent au
  bloc occurrence du nommage spec 003 mais ne correspondent à
  aucune sortie existante (`output/` s'arrête à 0018) — leur
  signification pour `chunkingid` est indéterminée — [source:
  counter.txt, ls output/] (confidence: medium)
- Changement de schéma : le contrat chunk-json.md impose
  `schema_version` incrémenté à tout changement incompatible
  (FR-013) ; ajouter des sous-champs optionnels à `document` est a
  priori compatible pour un consommateur JSON existant, mais le
  contrat doit être amendé — [source: chunk-json.md:60-62]
  (confidence: high)

## Evidence Against the Idea

- La clause « hors symboles » de la règle de lien contredit les
  exemples fournis (le `_` doit être compté) : telle quelle, la
  règle ne fait matcher aucun des 3 couples — [source: analyse
  caractère par caractère ci-dessus] (confidence: high)
- Le cas « Sous-dossiers » impose la récursivité, contraire à
  FR-008 (spec 005, décidé) ; il faudrait soit l'amender, soit
  restreindre le parcours récursif au seul mode `--add-context` —
  [source: specs/005-dossier-entree-cli/contracts/cli.md]
  (confidence: high)
- Constitution IV (YAGNI) : l'option ajoute une surface CLI, une
  règle d'appariement heuristique par préfixe et deux champs
  conditionnels — pour un outil mono-utilisateur, la même valeur
  pourrait être obtenue par convention de nommage stricte (sidecar
  même nom, cf. BIDS) sans option — [source: constitution.md ;
  en.wikipedia.org/wiki/Sidecar_file] (confidence: medium)
- L'appariement par préfixe de nom est fragile par nature :
  renommage, collision de préfixe, .json orphelin ou .md sans
  contexte sont autant d'états mal définis que les sidecar files
  documentent comme point de défaillance classique — [source:
  en.wikipedia.org/wiki/Sidecar_file — snippet de recherche,
  page non fetchée] (confidence: medium)
- La formulation « `<titre>.json` » de `chunkingid` entre en
  conflit frontal avec la décision spec 003 (nommage à 18 chiffres,
  pas de titre) — sans clarification, l'implémentation risquerait
  de rouvrir un arbitrage clos — [source:
  generation-titre-json/decision.md] (confidence: high)

## Gaps & Open Questions

- [NEEDS CLARIFICATION: `chunkingid` — contenu exact (nom à 18
  chiffres avec ou sans extension ?) et lien avec les suffixes
  `-00xx` des fichiers de contexte d'exemple]
- [NEEDS CLARIFICATION: normalisation exacte de la clé
  d'appariement — les 8 premiers caractères sont-ils pris bruts
  (exemples compatibles) ou normalisés NFKD sans accents ni
  symboles (exemples incompatibles) ? Sensibilité à la casse ?]
- [NEEDS CLARIFICATION: comportement en collision — deux .md
  matchant le même .json, ou un .json matchant plusieurs .md ;
  comportement d'un .json de contexte orphelin (ignoré
  silencieusement ? avertissement ?)]
- [NEEDS CLARIFICATION: la récursivité des sous-dossiers
  s'applique-t-elle seulement avec `--add-context`, et comment
  s'articule-t-elle avec FR-008 de la spec 005 ?]
- [NEEDS CLARIFICATION: `--add-context` s'applique-t-il à un
  fichier .md unique en direct, ou uniquement aux entrées
  dossier ?]
- [NEEDS CLARIFICATION: le champ `Typologie` du contexte
  remplace-il ou coexiste-t-il avec `document.typologie` (preset)
  dans le JSON de sortie ?]
- [NEEDS CLARIFICATION: incrément de `schema_version` (1.0 → 1.1)
  ou simple amendement du contrat pour des champs optionnels ?]

## Sources

- Exemples du dépôt : `Examples/Extension/` (Couple, Multi-couples,
  Multi-coupes mix, Sous-dossiers) — lecture directe des 3 .json de
  contexte et des 8 .md (aucune écriture).
- Code et contrats internes : `md_chunking/indexer.py`, `cli.py`,
  `naming.py`, `inputs.py`, `counter.txt`, `output/`,
  `specs/001-md-chunking/contracts/chunk-json.md`,
  `specs/005-dossier-entree-cli/contracts/cli.md`,
  `.specify/assessments/generation-titre-json/decision.md`,
  `.specify/assessments/dossier-entree-md/research.md`,
  `.specify/memory/constitution.md` — lecture directe.
- <https://stackoverflow.blog/2024/12/27/breaking-up-is-hard-to-do-chunking-in-rag-applications/>
  (hôte : stackoverflow.blog ; snippet de recherche, page non
  fetchée)
- <https://github.com/langchain-ai/langchain/issues/12067>
  (hôte : github.com, allowlisté ; snippet de recherche, page non
  fetchée)
- <https://grobid.org/formats/csl-json>
  (hôte : grobid.org ; snippet de recherche, page non fetchée)
- <https://citeproc-js.readthedocs.io/en/latest/csl-json/markup.html>
  (hôte : citeproc-js.readthedocs.io ; snippet de recherche, page
  non fetchée)
- <https://en.wikipedia.org/wiki/Sidecar_file>
  (hôte : en.wikipedia.org ; snippet de recherche, page non
  fetchée)
- <https://psychds-docs.readthedocs.io/en/latest/reference/rules_and_conventions/>
  (hôte : psychds-docs.readthedocs.io ; snippet de recherche, page
  non fetchée)
- <https://github.com/jlevy/sidematter-format>
  (hôte : github.com, allowlisté ; snippet de recherche, page non
  fetchée)
- <https://gpt-trainer.com/blog/rag+chunking+strategy>
  (hôte : gpt-trainer.com ; snippet de recherche, page non
  fetchée)
