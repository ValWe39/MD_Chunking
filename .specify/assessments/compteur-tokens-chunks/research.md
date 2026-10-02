# Idea Research: Compteur de tokens par chunk dans le rapport visuel

- **Slug**: compteur-tokens-chunks
- **Created**: 2026-10-02
- **Evidence confidence (overall)**: medium (interne : high ; externe :
  medium, sources SEO convergentes mais non académiques pour les
  ratios)

## Users & Demand

- La demande émane directement de l'unique utilisateur visé par
  l'outil (spéc. : utilisateur unique, ~50–150 chunks/document) —
  signal réel mais n=1. — [source:
  `.specify/assessments/compteur-tokens-chunks/intake.md` +
  `specs/001-md-chunking/spec.md` Assumptions] (confidence: high)
- Le besoin général est documenté dans la littérature : les splitters
  à compte de caractères (LangChain RecursiveCharacterTextSplitter,
  Chonkie par défaut) imposent à l'utilisateur « de traduire
  manuellement un plafond de caractères en nombre approximatif de
  tokens ». — [source: arxiv.org/html/2609.29828, Section 7.3]
  (confidence: medium)
- Cas d'usage typique du comptage : vérifier qu'un texte tient dans la
  fenêtre de contexte avant un appel d'API d'embedding. — [source:
  tools.gera.services/chars-to-tokens-converter] (confidence: medium)

## Prior Art

### Interne

- **D4 (décision opposée en apparence)** : la recherche de la feature
  001 (`specs/001-md-chunking/research.md`, D4) a écarté les tokens
  comme *unité de mesure des tailles* sur réponse utilisateur
  explicite (Q1 du 2026-10-02) : dépendance à un tokenizer, comptage
  variable, limite du modèle d'embedding en aval « responsabilité du
  consommateur du JSON ». L'idée actuelle rouvre D4 partiellement —
  comme *information affichée*, pas comme unité de découpage
  (FR-002 inchangé). Toute décision devra distinguer ces deux plans. —
  [source: `specs/001-md-chunking/research.md` D4] (confidence: high)
- **D2** : le bug Haystack #12686 des modes caractère est contourné
  par filtrage ; « passer au mode token » avait été jugé incompatible
  avec FR-002. Un affichage de tokens n'implique pas de changer de
  mode de découpage. — [source:
  `specs/001-md-chunking/research.md` D2] (confidence: high)
- **Render actuel** : `md_chunking/reviewer.py` affiche déjà par chunk
  un en-tête `## Chunk <ref> — <N> car.` ; ajouter une ligne de tokens
  dans les métadonnées existantes est un point d'extension naturel. —
  [source: `md_chunking/reviewer.py`] (confidence: high)
- **Dépendances actuelles** : `haystack-ai 2.31.0` + `markdown-it-py`
  uniquement ; aucune bibliothèque de tokenisation installée dans le
  venv (vérifié par `pip list`). — [source: `pyproject.toml` +
  inspection du venv] (confidence: high)

### Externe

- **tiktoken** (openai, MIT) : tokenizer BPE de référence pour les
  modèles OpenAI ; mais il télécharge son fichier d'encodage depuis
  `openaipublic.blob.core.windows.net` au premier appel de
  `get_encoding()` — appel réseau à l'exécution, largement
  documenté comme casse-tête offline (workaround : amorcer
  `TIKTOKEN_CACHE_DIR`). Conflit direct avec la constitution II
  (Network Surface : appels sortants limités à l'URL demandée par
  l'utilisateur) et FR-011/SC-006, sauf vocabulaire pré-chargé et
  committé. — [source: github.com/openai/tiktoken/issues/232 ;
  stackoverflow.com/questions/76106366 ;
  github.com/openai/tiktoken/blob/main/LICENSE (MIT)] (confidence:
  high)
- **HuggingFace tokenizers** (Rust, Apache-2.0) : fonctionne 100 %
  hors-ligne à condition de fournir un `tokenizer.json` local ; mais
  ajoute une dépendance et impose de choisir *quel* tokenizer (le
  compte varie selon le modèle visé). — [source:
  github.com/huggingface/tokenizers] (confidence: medium)
- **Heuristique zéro-dépendance** : ratio empirique ~4
  caractères/token pour la prose anglaise ; le français « proche de
  l'anglais, peut-être 10–30 % de tokens en plus » ; le code ~3
  caractères/token ; CJK ~1,5. Ratio « remarquablement stable entre
  fournisseurs ». Une estimation `len(chunk)/ratio` est déterministe,
  hors-ligne et sans dépendance. — [source:
  calcis.dev/convert/characters-to-tokens ;
  tokencounter.cc/blog/tokens-vs-words-characters ; abacktools.com ;
  calctrail.com — sources multiples convergentes mais de nature SEO]
  (confidence: medium)
- **Précédents chez les concurrents** : LangChain expose un
  `TokenTextSplitter` et des méthodes `from_tiktoken_encoder()`
  (comptage par tiktoken) ; Chonkie compte en caractères par défaut
  et peut être pointé vers un tokenizer ; LlamaIndex
  `SentenceSplitter` prend une limite en tokens fournie par
  l'utilisateur. L'affichage d'un compte de tokens à côté d'un
  découpage en caractères n'est pas un standard établi — c'est un vide
  que l'idée propose de combler. — [source: docs.langchain.com —
  splitters/split_by_token ; arxiv.org/html/2609.29828]
  (confidence: medium)

## Market & Context

- Alternative actuelle de l'utilisateur : faire la division
  mentalement (1000 car. ≈ 250 tokens) ou coller le chunk dans un
  compteur en ligne — ce dernier transmettrait le contenu du document
  à un tiers, contraire à la constitution II ; un compteur intégré
  élimine cette incitation. — [ASSUMPTION — aucun comportement
  observé] (confidence: low)
- Coût de l'inaction : faible — les tailles par défaut (100–1000
  car., FR-002) donnent ~25–330 tokens par chunk, très en dessous de
  la fenêtre de 8191 tokens des modèles d'embedding OpenAI
  courants ; le risque de dépassement n'existe que pour les entités
  atomiques (blocs de code très longs) ou les presets à 2000 car. —
  [source: specs FR-002 + developers.openai.com/cookbook (8191,
  cl100k_base) + ratios tokencounter.cc] (confidence: medium)
- Nombre de modèles d'embedding BERT locaux ont une fenêtre de 512
  tokens — [ASSUMPTION, non sourcé dans cette recherche] ; à
  1000 car. ≈ 250–330 tokens, la fourchette par défaut resterait sous
  cette limite, mais un preset « code » à 2000 car. pourrait la
  frôler (~500–670 tokens).

## Data & Constraints

- **Constitution II (NON NÉGOCIABLE)** : traitement hors-ligne total ;
  tout comptage doit fonctionner sans réseau. Écarte tiktoken tel
  quel (téléchargement au premier usage) ; une heuristique locale ou
  un vocabulaire tokenizers committé la respectent. — [source:
  `.specify/memory/constitution.md` v1.4.0] (confidence: high)
- **Constitution III** : dépendances open-source sans trackers
  (tiktoken MIT et HF tokenizers Apache-2.0 y satisfont tous deux). —
  [source: idem + LICENSE cités] (confidence: high)
- **Souveraineté** : préférence pour outils hébergés en Europe « dans
  la mesure du possible » (pas un dur) ; tiktoken est américain
  (OpenAI), HF tokenizers américain également — facteur secondaire
  ici. — [source: `.specify/memory/constitution.md` Additional
  Requirements] (confidence: high)
- **Constitution IV (YAGNI)** : une heuristique ~10 lignes satisfait
  le besoin affiché ; un tokenizer exact ajoute une dépendance et une
  dépendance au choix de modèle. — [source: idem] (confidence: high)
- **SC-005 (déterminisme)** : une heuristique caractère→token est
  déterministe ; un compte par tokenizer l'est aussi une fois le
  vocabulaire fixé, mais change avec la version du modèle visé. —
  [source: spec SC-005 + comportements documentés ci-dessus]
  (confidence: high)
- **Corpus réel** : 415 chunks sur `Examples/`, prose majoritairement
  française avec blocs de code et tableaux — précisément le mélange
  (prose FR ~4 car./token, code ~3 car./token) où une heuristique
  unique est la moins précise. — [source: commit 8c8832a + ratios
  cités] (confidence: medium)

## Evidence Against the Idea

- **D4 est une décision utilisateur explicite et récente**
  (2026-10-02) qui a rejeté les tokens ; rouvrir le sujet, même pour
  un simple affichage, demande à justifier pourquoi le rapport visuel
  a besoin de cette information alors que le consommateur du JSON
  reste responsable de la limite de son modèle. — [source:
  `specs/001-md-chunking/research.md` D4] (confidence: high)
- **« Approximatif » peut induire en erreur** : les sources
  elles-mêmes avertissent de ne jamais utiliser le ratio seul
  (« it's an estimate for planning », ±10–30 % selon langue, code,
  ponctuation) ; un nombre affiché sans intervalle peut être pris
  pour un compte exact. — [source: calcis.dev ; tokencounter.cc ;
  abacktools.com] (confidence: medium)
- **YAGNI** : le besoin sous-jacent (vérifier la compatibilité avec
  la fenêtre du modèle aval) est faible avec les défauts actuels
  (~25–330 tokens par chunk vs 8191) ; la valeur n'apparaît que pour
  presets élevés ou entités atomiques. — [source: FR-002 + OpenAI
  cookbook] (confidence: medium)
- **Coût de maintien d'un tokenizer exact** : choix de l'encodage
  (cl100k_base ? o200k_base ? tokenizer HF ?), vocabulaire à
  committer (fichier de ~1,7–2 Mo pour cl100k_base), tests de
  non-régression à chaque changement de modèle visé. — [source:
  stackoverflow.com/questions/76106366 (taille fichier) + ASSUMPTION
  sur le coût de maintien] (confidence: medium)

## Gaps & Open Questions

- [NEEDS CLARIFICATION: quel(s) modèle(s) d'embedding en aval sont
  visés ? Cela détermine si une heuristique suffit ou si un tokenizer
  exact (et lequel) est requis.]
- [NEEDS CLARIFICATION: le compte de tokens doit-il figurer aussi dans
  l'index JSON (consommable machine) ou uniquement dans review.md ?]
- [NEEDS CLARIFICATION: précision attendue — ordre de grandeur
  (heuristique ok) ou compte exact pour un modèle donné (tokenizer
  requis) ?]
- [NEEDS CLARIFICATION: format d'affichage — ligne de métadonnée
  additionnelle, ou remplacement du « X car. » de l'en-tête ?
  Faut-il un total par document ?]
- [NEEDS CLARIFICATION: si tokenizer exact, quelle stratégie de
  conformité constitution II — vocabulaire committé (alourdit le
  dépôt) ou génération au premier build avec autorisation réseau
  explicite de l'utilisateur (contradictoire avec SC-006) ?]

## Sources

Recherches via le connecteur web_search (moteur de recherche, extraits
de résultats) ; aucune page n'a été ouverte ni fetchée — les
affirmations reposent sur les extraits retournés. Politique URL :
aucun fetch effectué, donc aucune branche `allowlisted` /
`confirmed-by-user` n'a été exercée.

- <https://github.com/openai/tiktoken/issues/232> (host: github.com)
- <https://github.com/openai/tiktoken/blob/main/LICENSE>
  (host: github.com)
- <https://stackoverflow.com/q/76106366>
  (host: stackoverflow.com ; URL canonique raccourcie, redirige vers
  la question complète)
- <https://github.com/huggingface/tokenizers> (host: github.com)
- <https://docs.langchain.com/oss/python/integrations/splitters/split_by_token>
  (host: docs.langchain.com — extrait de recherche uniquement)
- <https://arxiv.org/html/2609.29828> (host: arxiv.org)
- <https://www.calcis.dev/convert/characters-to-tokens>
  (host: calcis.dev)
- <https://tokencounter.cc/blog/tokens-vs-words-characters>
  (host: tokencounter.cc)
- <https://abacktools.com/tools/ai/calculators/character-to-token-calculator>
  (host: abacktools.com)
- <https://calctrail.com/calculators/token-converter-calculator>
  (host: calctrail.com)
- <https://developers.openai.com/cookbook/examples/embedding_long_inputs>
  (host: developers.openai.com — extrait de recherche uniquement)
- Sources internes : `.specify/memory/constitution.md` v1.4.0,
  `specs/001-md-chunking/{spec,plan,research}.md`,
  `md_chunking/reviewer.py`, `pyproject.toml`, venv (pip list).
