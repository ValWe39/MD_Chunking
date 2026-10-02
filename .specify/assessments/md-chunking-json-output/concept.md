# Concept: Chunker Markdown paramétrable avec contrôle visuel

- **Slug**: md-chunking-json-output
- **Created**: 2026-10-02
- **Recommended option**: Option B — Haystack étendu par composants
  maison

## Options

### Option A — Chunker maison pur Python

- **Sketch**: un script/CLI Python autonome, sans framework : parsing
  du Markdown (regex ou parseur type markdown-it-py/mistune),
  découpage hiérarchique sections → paragraphes → phrases dans la
  fourchette min/max, overlap recalculé à chaque niveau,
  sérialisation JSON conforme au format demandé, plus un rendu texte
  lisible pour la relecture humaine. L'utilisateur lance la commande
  sur un fichier ou dossier, obtient `output/<sous-dossier>/` avec le
  JSON et le rendu de contrôle.
- **Appetite**: small (quelques jours à ~2 semaines)
- **Trade-offs**: gagne — contrôle total du comportement (overlap
  « intelligent », occupation maximale, JSON exact), zéro dépendance
  framework, code lisible et auditable par une seule personne.
  Sacrifie — réinvention de ce qui existe (hiérarchie de titres en
  métadonnées, split par unités), pas d'interopérabilité native avec
  un futur pipeline Haystack, maintenance intégrale à sa charge.
- **Rabbit holes**: (1) l'« occupation maximale » des chunks (problème
  d'optimisation combinatoire si poussé à fond — borner à une
  heuristique gloutonne) ; (2) la gestion des cas limites Markdown
  (blocs de code contenant des `#`, tableaux, front-matter) ;
  (3) l'overlap structurel aux frontières de sections.

### Option B — Haystack comme socle, extensions maison ciblées

- **Sketch**: un pipeline Haystack (deepset) : `MarkdownToDocument` en
  entrée, `MarkdownHeaderSplitter` pour le découpage par titres
  (hiérarchie préservée en métadonnées, split secondaire
  paramétrable), un composant maison pour l'overlap structurel et
  l'occupation maximale, un composant d'export qui traduit les
  Documents splittés (métadonnées `source_id`, `page_number`,
  `split_id`, `split_idx_start`) en le JSON demandé, et un composant
  de rendu lisible pour la validation à l'œil nu. L'utilisateur
  obtient les mêmes artefacts que l'option A, via des briques
  éprouvées.
- **Appetite**: small–medium (1 à ~3 semaines)
- **Trade-offs**: gagne — réutilise des composants maintenus qui
  couvrent déjà la plus grande partie du besoin (titres →
  métadonnées, splits par paragraphes/phrases, traçabilité
  `source_id`/`split_id`), voie de croissance naturelle si le
  pipeline RAG complet devient Haystack, bug d'overlap connu et
  documenté à contourner. Sacrifie — dépendance au framework
  (évolution des API entre versions Haystack 2.x/3.x), couche de
  traduction vers le JSON custom, l'overlap natif ne respecte pas
  les frontières structurelles (à réécrire de toute façon).
- **Rabbit holes**: (1) la correspondance métadonnées Haystack ↔
  champs JSON demandés (page n'existe pas en Markdown pur) ;
  (2) la migration entre versions majeures de Haystack ; (3) le
  contournement du bug #12686 (chunks de pur overlap en fin de
  document).

### Option C — Ne rien construire : Haystack tel quel

- **Sketch**: utiliser l'existant sans écrire de code : un pipeline
  Haystack minimal (`MarkdownToDocument` + `MarkdownHeaderSplitter`
  ou `DocumentSplitter`) lancé en script d'une dizaine de lignes,
  sortie consommée telle quelle (Documents Haystack), sans JSON
  normalisé ni rendu de relecture dédié.
- **Appetite**: small (quelques heures)
- **Trade-offs**: gagne — quasi zéro effort, vérifie immédiatement si
  le besoin est réellement plus large que l'existant. Sacrifie — pas
  d'overlap « intelligent », pas de JSON conforme au format demandé
  (champs manquants ou mal nommés), pas de contrôle visuel avant
  embedding, pas de presets par typologie, paramètres min/max non
  garantis. Ne satisfait que partiellement les objectifs et aucune
  des métriques de traçabilité.
- **Rabbit holes**: peu ; l'échec est visible vite — mais il ne
  produit pas le JSON exploitable en aval.

## Recommendation

**Option B (Haystack étendu par composants maison).** Justification
liée aux buts et métriques de `problem.md` : la traçabilité exigée
(chemin obligatoire, numéro de référence obligatoire, titre/page/
partie/position si balisés) correspond presque un-à-un aux
métadonnées natives de Haystack ; le découpage structurel « sections
puis paragraphes puis phrases » est déjà le comportement de
`MarkdownHeaderSplitter` avec split secondaire ; la contrainte
utilisateur (ni LangChain ni LlamaIndex, maison ou Haystack) est
respectée. La part réellement nouvelle — overlap structurel,
occupation maximale, JSON normalisé, rendu de contrôle — est
circonscrite à des composants maison petits et testables, ce qui
capte aussi le principal attrait de l'option A sans payer sa
réinvention. L'option C est recommandée comme préalable de deux
heures avant même de décider : elle délimite le réel écart entre
l'existant et le besoin, et alimente `/speckit-assess-decide` en
faits.

## Out of Scope (for the recommended option)

- Embedding, stockage vectoriel, recherche (hérité des non-goals).
- Parsing/conversion de formats autres que Markdown (PDF, DOCX, HTML).
- Chunking sémantique par similarité d'embeddings.
- Interface graphique ; le contrôle visuel est un rendu lisible généré,
  pas une app.
- Découpage fin des tableaux (par lignes) et des blocs de code : ils
  restent atomiques dans un chunk.
- Indexation multi-échelles du même corpus (plusieurs tailles de
  chunks indexées ensemble).
- Tout contournement des hooks pre-commit ou publication de branche —
  hors sujet par construction.

## Assumptions to Validate

- L'unité de taille de chunk sera les tokens (cohérent avec les
  limites des modèles d'embedding), à confirmer en spécification.
- Le langage d'implémentation est Python (Haystack et parseurs
  markdown-it-py/mistune sont Python) ; à confirmer — aucun code
  existant dans le dépôt ne contraint ce choix.
- « Page » ne peut être renseigné que si l'amont (conversion PDF →
  Markdown) laisse une balise de page ; sinon le champ est absent,
  jamais deviné.
- Un seul utilisateur/périmètre personnel : pas d'exigences de
  performance au-delà de quelques dizaines de documents par exécution.
- Les presets par typologie (articles/documentation/conversations/
  code) seront fournis comme valeurs par défaut modifiables, pas comme
  vérités optimisées (non sourcées selon la research).
- Le bug Haystack #12686 est contournable dans le composant maison
  d'overlap (à vérifier sur la version retenue).

## Input Evidence (4 exemples fournis, 2026-10-02)

Analyse des 4 documents réels du dossier `Examples/` (44 à 110 KB,
~6 700 à ~15 900 mots chacun) :

- Exemple1 (`nettoye.md`) — profil : web scrappé, bruité (Cour des
  comptes). Structure : 0 titre ATX en début de ligne ; 210 titres
  `##` emboîtés dans des puces de liste (`* ## [`…) ; CRLF ;
  ~15 900 mots.
- Exemple2 (`nettoye.md`) — profil : article web propre (MCP).
  Structure : 97 titres (`#`/`##`) réguliers ; CRLF ; ~13 500 mots.
- Exemple3 (`markdown.md`) — profil : contexte littéraire/historique.
  Structure : 13 `#`, 2 `##`, majoritairement longue prose ; LF ;
  ~6 700 mots.
- Exemple4 (`markdown.md`) — profil : livre (Tocqueville). Structure :
  15 titres au total pour ~11 600 mots → sections très longues ;
  titre H1 multi-lignes ; LF.

Conséquences pour le concept (sans changer la recommandation) :

- Le découpage « sections d'abord » n'est **pas** le chemin principal
  pour tous les inputs : Exemple1 (titres malformés dans des listes)
  et Exemple4 (sections très longues) feront de la bascule
  paragraphes/phrases un cas fréquent, pas un « dernier recours ».
  L'ordre de priorité tient, mais le pipeline doit normaliser les
  titres malformés ou basculer proprement.
- Le champ « page » sera absent dans la quasi-totalité des inputs
  réels observés (aucun marqueur de page dans les 4 exemples) ; le
  champ « titre du document » n'est balisé proprement que dans
  2 exemples sur 4.
- Les presets par typologie doivent couvrir au moins un type « livre/
  littérature à longue prose » absent de la liste initiale
  (articles/documentation/conversations/code).
- Le rendu de contrôle « à l'œil nu » doit rester lisible à l'échelle
  de ~50 à ~150 chunks par document.
- Les fins de ligne sont mixtes (CRLF/LF selon le document) : la
  normalisation en entrée est requise.

Ces constats renforcent la recommandation de l'option B : les
composants maison (normalisation des titres, bascule de niveau,
overlap structurel) sont exactement là où les exemples révèlent le
besoin.
