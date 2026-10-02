# Idea Research: Chunking de Markdown avec sortie JSON

- **Slug**: md-chunking-json-output
- **Created**: 2026-10-02
- **Evidence confidence (overall)**: medium

> Contrainte utilisateur explicite (session du 2026-10-02) : éviter
> LangChain et LlamaIndex ; privilégier une solution maison ou Haystack
> (deepset). Cette contrainte oriente la recherche ci-dessous.

## Users & Demand

- Le demandeur est l'utilisateur du dépôt MD_Chunking lui-même : besoin
  direct, formulé dans l'intake (confidence: high, cited).
  source: `.specify/assessments/md-chunking-json-output/intake.md`
- Le chunking structurel est un sujet très actif chez les praticiens
  RAG : les guides de Weaviate et Unstructured recommandent
  explicitement de tester itérativement taille/overlap et de faire
  relire les chunks par des humains (confidence: high, cited).
  source: weaviate.io/blog/chunking-strategies-for-rag ;
  unstructured.io/blog/chunking-for-rag-best-practices
- Signal communautaire fort que la stratégie de découpage pèse autant
  ou plus que le choix du modèle d'embedding : « 10–15% de gain de
  recall juste en ajustant taille, overlap et hiérarchie »
  (confidence: low, anecdotal, cited).
  source: reddit.com/r/Rag — thread « Why Chunking Strategy Decides
  More Than Your Embedding Model »
- ASSUMPTION : le besoin est interne (pipeline personnel d'embedding
  pour RAG), pas un produit commercial — aucune donnée de demande
  externe n'existe. (confidence: low, assumption)

## Prior Art

### Haystack (deepset) — piste privilégiée par l'utilisateur

- `DocumentSplitter` : découpe par unités word / sentence / passage
  (paragraphe) / page / line / period / function, avec `split_length`
  (taille de chunk) et `split_overlap` (overlap) — couvre le découpage
  par paragraphes et par phrases de l'idée (confidence: high, cited).
  source: docs.haystack.deepset.ai/docs/documentsplitter
- `MarkdownHeaderSplitter` (nouveau) : découpe aux titres Markdown
  (`#`, `##`, …), préserve la hiérarchie des titres en métadonnées, et
  applique optionnellement un découpage secondaire (word, passage,
  period, line) à chaque chunk — correspond très étroitement au besoin
  « sections d'abord, puis paragraphes, puis phrases »
  (confidence: high, cited).
  source: docs.haystack.deepset.ai/reference/preprocessors-api
- `RecursiveDocumentSplitter` : applique une liste de séparateurs dans
  l'ordre (ex. `\n\n`, `\n`, point, espace) ; si un chunk dépasse
  `chunk_size` après tous les séparateurs, split dur — même philosophie
  que le « dernier recours » de l'idée (confidence: high, cited).
  source: docs.haystack.deepset.ai/docs/recursivesplitter
- `HierarchicalDocumentSplitter` : blocs parent/enfant avec `parent_id`,
  `children_ids`, `level` — utile pour le positionnement des chunks
  dans une partie/sous-partie (confidence: medium, cited).
  source: docs.haystack.deepset.ai/docs/hierarchicaldocumentsplitter
- Métadonnées produites par les splitters Haystack : `source_id`
  (traçabilité du document d'origine), `page_number`, `split_id` (index
  du chunk dans le parent), `split_idx_start` (position) — recouvre
  une grande partie des champs JSON demandés (chemin, page,
  positionnement, numéro de référence) (confidence: high, cited).
  source: docs.haystack.deepset.ai/reference/preprocessors-api
- Défauts connus de Haystack : (1) bug d'overlap — chunks finaux
  redondants « overlap-only » en modes caractère (issue #12686,
  corrigé seulement pour le mode token) ; (2) le splitting de phrases
  « par point » est jugé basique (issue #8111, demande de splitting
  sémantique ouverte) (confidence: high, cited).
  source: github.com/deepset-ai/haystack — issues #12686 et #8111

### Solution maison (sans framework)

- Parseurs Markdown Python utilisables pour un découpage maison par
  AST : `markdown-it-py` (utilisé par Haystack lui-même pour
  `MarkdownToDocument`) et `mistune` (le plus rapide des parseurs purs
  Python, plugins et rendus personnalisables) (confidence: high,
  cited).
  source: github.com/lepture/mistune ;
  haystack.deepset.ai — tutorial 30 (file type preprocessing)
- Approche regex par niveaux de titres documentée pour le chunking
  Markdown sans framework (confidence: medium, cited).
  source: theneuralbase.com/chunking/qna/how-to-chunk-markdown-documents
- Projets tiers « maison » comparables (preuve que le besoin est
  récurrent) : `markdown-chunker` (chunks sémantiques par titres/
  blocs de code), `split-markdown4gpt` (split par limite de tokens avec
  front-matter YAML géré) (confidence: medium, cited).
  source: github.com/razorback16/markdown-chunker ;
  github.com/twardoch/split-markdown4gpt
- `ragnar::markdown_chunk` (R) : retourne un tableau avec plages de
  caractères, contexte de titres et texte pour chaque chunk, avec
  `target_size` et `target_overlap` — concept quasi identique au
  besoin (chunks + index de localisation) (confidence: medium,
  cited).
  source: ragnar.tidyverse.org/reference/markdown_chunk.html

### Alternatives écartées par la contrainte utilisateur

- LangChain `MarkdownHeaderTextSplitter` et LlamaIndex
  `MarkdownNodeParser` : prior art structurel direct (split par titres
  avec métadonnées de hiérarchie), mais exclus par la contrainte
  explicite — cités pour mémoire, non retenus (confidence: high,
  cited).
  source: docs.langchain.com ; docs.llamaindex.ai
- Chonkie (lib légère de chunking, intégration Haystack existante
  `ChonkieRecursiveDocumentSplitter`) : option intermédiaire
  compatible Haystack si le besoin dépasse les splitters natifs
  (confidence: medium, cited).
  source: haystack.deepset.ai/integrations/chonkie ;
  github.com/feyninc/chonkie

## Market & Context

- Plage de référence « sweet spot » pour le RAG généraliste : 256–1024
  tokens avec 10–20% d'overlap ; conseil de démarrage courant « 512
  tokens, 10% d'overlap » — les bornes proposées (100–1000 par défaut,
  overlap 15%) tombent dans les pratiques courantes, sous réserve de
  l'unité (caractères vs tokens, non tranchée) (confidence: medium,
  cited).
  source: ai-tldr.dev/learn/rag/chunking-and-ingestion/
  chunk-size-and-overlap
- Recommandation d'overlap 15% : le demandeur indique que cette valeur
  lui a été suggérée par la formation Corsen « Embeddings & RAG
  Mistral » (chapitre 4) — cité par l'utilisateur le 2026-10-02 ;
  page non fetchée : hôte corsen.ai hors liste d'hôtes autorisés ;
  contenu non vérifié indépendamment (confidence: low–medium,
  user-cited, unfetched).
  source: corsen.ai/fr/formations/mistral-ai/embeddings-rag-mistral/4/
- Recommandation récurrente : traiter l'overlap comme un paramètre à
  ajuster et à valider par évaluation (recall/qualité de réponse),
  pas comme une constante (confidence: high, cited).
  source: unstructured.io/blog/chunking-for-rag-best-practices
- Limite dure : un chunk doit rester sous la limite de tokens du
  modèle d'embedding, sinon l'embedding échoue — justifie la borne
  max (confidence: high, cited).
  source: unstructured.io/blog/chunking-for-rag-best-practices
- Coût de l'inaction : mauvais chunking = retrieval dégradé ; le
  chunking conditionne toute la suite du pipeline RAG
  (confidence: high, cited).
  source: weaviate.io/blog/chunking-strategies-for-rag
- La relecture humaine avant embedding, exigée par l'idée, correspond
  aux pratiques recommandées (« involve humans to review retrieved
  chunks ») (confidence: medium, cited).
  source: weaviate.io/blog/chunking-strategies-for-rag

## Data & Constraints

- Étude systématique (chimie) : chunking récursif non-chevauchant
  (100 tokens, overlap 0) = meilleur défaut dans ce domaine ;
  variation d'IoU d'un facteur 10 selon la stratégie de segmentation
  (confidence: medium, cited — single domain).
  source: arxiv.org/html/2506.17277v1
- La taille de chunk optimale dépend de la requête ; l'indexation
  multi-échelles (100/200/500 tokens + RRF) améliore le retrieval de
  1–37% (confidence: medium, cited).
  source: ai21.com/blog/query-dependent-chunking
- Évaluations multi-jeux de données du chunking à taille fixe :
  l'effet varie selon le jeu de données, pas de taille universelle
  (confidence: medium, cited).
  source: arxiv.org/html/2505.21700v2
- AUCUNE donnée publiée ne justifie les presets par typologie proposés
  (« articles » 1500/200, « documentation » 1000/150,
  « conversations » 500/50, « code » 2000/300) : valeurs plausibles
  mais non sourcées (confidence: low, assumption).
- Aucune volumétrie de documents, ni contrainte de performance, ni
  exigence de conformité n'a été fournie (confidence: low, gap).

## Evidence Against the Idea

- Le bénéfice de l'overlap est contesté : une étude systématique
  récente conclut qu'un chunking récursif sans overlap est un défaut
  fort (moindre coût d'indexation), l'overlap ajoutant redondance ;
  l'overlap par défaut à 15% mérite donc une justification, pas une
  généralisation (confidence: medium, cited).
  source: arxiv.org/html/2506.17277v1
- Haystack natif ne fournit pas tout : overlap « intelligent »
  (respectant parties/paragraphes) non documenté comme tel, splitting
  de phrases basique (point), bug résiduel d'overlap en modes
  caractère — un assemblage ou un développement maison restera
  nécessaire pour l'overlap intelligent et le JSON d'output
  personnalisé (confidence: medium, cited).
  source: github.com/deepset-ai/haystack — #8111, #12686
- La notion de « page » n'existe pas nativement dans un Markdown pur
  (elle provient de PDF convertis) : le champ « page (si balisée) »
  suppose une convention d'entrée à définir (confidence: medium,
  cited via docs Haystack page_number sur PDF).
- L'unité de mesure (caractères / tokens / mots) n'est pas fixée dans
  l'idée ; les pratiques du marché s'expriment en tokens, l'idée en
  valeurs brutes non typées — comparer ou régler 100–1000 sans unité
  est impraticable en l'état (confidence: high, cited via sources
  ci-dessus sur tailles en tokens).
- Risque de duplication d'existant : Haystack + MarkdownHeaderSplitter
  couvre déjà « sections puis découpage secondaire avec
  métadonnées » ; la valeur ajoutée doit se concentrer sur l'overlap
  intelligent, le JSON d'output normalisé et le rendu de relecture
  humaine — sinon, utiliser l'existant tel quel (confidence: medium,
  inference from cited docs).

## Gaps & Open Questions

- [NEEDS CLARIFICATION: unité de la taille de chunk — caractères,
  tokens ou mots ?]
- [NEEDS CLARIFICATION: format et volumétrie des inputs (fichiers .md
  uniquement ? un fichier = un document ? plusieurs documents par
  exécution ?)]
- [NEEDS CLARIFICATION: convention de balisage attendue pour « page »
  et « titre du document » (front-matter YAML, balise HTML, conversion
  PDF ?)]
- [NEEDS CLARIFICATION: schéma JSON exact attendu en aval (pipeline
  d'embedding existant ? consommateur du JSON ?)]
- [NEEDS CLARIFICATION: forme du rendu de vérification « à l'œil nu »
  (fichier texte, Markdown annoté, HTML ?)]
- [NEEDS CLARIFICATION: valeur de X (lettres du titre) pour le nommage
  des sous-dossiers d'output, et comportement si titre absent ou
  dupliqué]
- [NEEDS CLARIFICATION: stratégie d'« occupation maximale » — viser le
  max dans la fourchette min/max : critère d'arrêt et gestion des
  sections hors fourchette (fusion, split dur ?)]
- [NEEDS CLARIFICATION: périmètre technique — 100% maison (parser type
  markdown-it-py/mistune), Haystack seul, ou Haystack étendu par
  composants maison ?]

## Sources

Recherches effectuées via le connecteur web_search (résultats/snippets
du moteur Brave) ; aucune page n'a été ouverte directement (open_url
non utilisé), donc aucun fetch soumis à la politique d'hôtes n'a eu
lieu. Hôtes des sources citées ci-dessus : docs.haystack.deepset.ai,
github.com, arxiv.org, weaviate.io, unstructured.io, ai-tldr.dev,
ai21.com, reddit.com, ragnar.tidyverse.org, theneuralbase.com,
corsen.ai (cité par l'utilisateur, non fetché), docs.langchain.com et
docs.llamaindex.ai (cités pour mémoire, exclus par contrainte).
Politique : recherche par mots-clés via connecteur connecté
(allowlisted connector) ; aucune URL non fiable fetchée ; aucun
secret manipulé. Les URLs sont données sans préfixe `https://` pour
respecter la limite de 80 caractères par ligne ; le préfixe est
implicite pour tous les hôtes listés.
