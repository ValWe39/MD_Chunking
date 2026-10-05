# Idea Research: Option CLI --tokencpte, ratio caracteres/tokens flottant

- **Slug**: tokencpte-flottant
- **Created**: 2026-10-05
- **Evidence confidence (overall)**: medium

## Users & Demand

- Le seul utilisateur identifié est le propriétaire du dépôt, qui a
  formulé la demande après avoir constaté que son corpus est
  essentiellement en français — signal exprimé (stated want), aucun
  comportement observé ni donnée d'usage —
  [source: conversation du 2026-10-05, intake.md] (confidence: high)
- La demande ne vise pas le découpage (unité = caractère, SC-006) mais
  uniquement l'estimation informative affichée dans le rapport de
  relecture —
  [source: md_chunking/reviewer.py:14-48 ; specs/002 FR-T03] (confidence:
  high)

## Prior Art

- **Interne — décision contraire en v1** : la feature 002 a explicitement
  tranché « constante du code, sans paramètre d'interface en v1 »
  (clarification du 2026-10-02, reprise dans FR-T02 et data-model.md) ;
  l'ouverture à un compte exact (option B, FR-T08) est réservée « quand
  un modèle cible sera choisi » — cette idée rouvre donc une décision
  documentée, pas un vide normatif —
  [source: specs/002-compteur-tokens-chunks/spec.md:22-30,128-129 ;
  contracts/review-render.md:48] (confidence: high)
- **Interne — précédent de réduction de la surface CLI** : la feature 003
  a retiré l'option `--naming` au profit d'un comportement déterministe
  sans paramètre ; l'ajout d'une option va à contre-courant de cette
  trajectoire, mais n'en est pas incompatible (les options `--min`,
  `--max`, `--overlap` existent toujours) —
  [source: specs/003-nommage-sorties-18-chiffres ; md_chunking/cli.py:33-60]
  (confidence: high)
- **Externe — LangChain** : `RecursiveCharacterTextSplitter` expose
  `length_function` (défaut `len`, remplaçable par un compte tiktoken) —
  un paramètre configurable pour l'unité de mesure est un pattern établi —
  [source: <https://oneuptime.com/blog/post/2026-01-30-rag-recursive-chunking/view>]
  (confidence: medium)
- **Externe — LlamaIndex** : `SentenceSplitter` regroupe des phrases
  contre une cible en tokens (`chunk_size=1024 tokens` cité comme usage
  courant) — les découpeurs du marché paramètrent couramment une cible
  de taille, en caractères ou en tokens —
  [source: <https://www.firecrawl.dev/blog/best-chunking-strategies-rag>]
  (confidence: medium)

## Market & Context

- Alternative actuelle : modifier la constante dans le code
  (`RATIO_CHARS_PER_TOKEN = 4`, reviewer.py:11) — fonctionne aujourd'hui
  mais exige une édition de code par corpus ; l'option CLI ne fait que
  déplacer cette manipulation, elle ne crée pas la capacité —
  [source: md_chunking/reviewer.py:11] (confidence: high)
- OpenAI documente ~4 caractères par token comme une estimation pour
  l'anglais, et précise que les langues non anglaises ont un ratio
  tokens/caractères plus élevé (donc moins de caractères par token) —
  le ratio par défaut actuel de 4 est calé sur l'anglais, pas sur le
  français —
  [source: <https://help.openai.com/en/articles/4936856-understanding-tokens>
  (snippets) ; <https://gptforwork.com/guides/openai-gpt-tokens>
  (snippets)] (confidence: medium)
- Mesures tierces sur le tokenizer o200k_base (GPT-4o) : français à
  1,52 tokens/mot contre 1,16 pour l'anglais (+31 %) ; avec un mot
  français moyen d'environ 5 à 6 caractères espaces inclus, cela donne
  ~3,6 à 3,9 caractères par token — la valeur 3,5 proposée est donc
  plausible et légèrement conservatrice, dans la bonne direction par
  rapport à 4 —
  [source: <https://kathane.substack.com/p/not-speaking-english-to-chatgpt-costs>
  (snippets)] (confidence: low)
- Nuance importante : sur les tokenizers les plus récents, la surcharge
  du français est quasi résorbée (pénalité par mot ≈ 1,02 pour GPT-4o
  contre ~1,4 pour GPT-2) ; l'écart français/anglais dépend fortement du
  tokenizer — un ratio unique reste une approximation grossière quelle
  que soit sa valeur —
  [source: <https://github.com/JeremieJakubowicz/xhec-advanced-ai-2026/issues/1>
  (snippets)] (confidence: low)
- Coût de l'inaction : faible — l'estimation est purement informative
  (rapport de relecture), jamais stockée dans l'index JSON (FR-T07), sans
  impact sur le découpage ni sur les coûts API réels —
  [source: specs/002-compteur-tokens-chunks/data-model.md:41-44]
  (confidence: high)

## Data & Constraints

- Rayon d'impact du changement : `reviewer.py` (paramétrage du ratio),
  `cli.py` (option + validation), 2 fichiers de tests, contrats
  `review-render.md` et `cli.md`, README ; l'index JSON et le nommage des
  sorties ne sont pas affectés —
  [source: analyse du code du 2026-10-05, reviewer.py + cli.py]
  (confidence: high)
- Précision flottante : 3,5 est exactement représentable en binaire (7/2),
  la division `len/3.5` est déterministe ; en revanche un ratio comme 3,3
  crée des cas limites d'arrondi (`ceil` proche d'un entier) — un calcul
  en entiers (`ceil(len*10/35)`) ou une restriction du format
  l'éviterait —
  [source: ASSUMPTION — analyse arithmétique, non mesuré dans le dépôt]
  (confidence: medium)
- Constitution II/III : l'option préserve l'approche zéro-dépendance
  (aucun tokenizer importé, aucun appel réseau) ; une validation
  d'intervalle bornée est cohérente avec le pattern existant (`--overlap`
  entre 0 et 20, échec rapide code 2) —
  [source: .specify/memory/constitution.md ; cli.py:53-54] (confidence:
  medium)
- Aucune mesure n'existe sur le corpus réel du dépôt (Examples/) : la
  valeur 3,5 n'est étayée par aucune donnée locale —
  [source: ASSUMPTION — absence de script de mesure dans le dépôt]
  (confidence: high)

## Evidence Against the Idea

- La spécification a délibérément tranché le contraire en v1 et différé
  l'ouverture jusqu'au choix d'un modèle cible ; ouvrir maintenant, avant
  qu'un modèle d'embedding soit choisi, affaiblit la cohérence du
  processus spec-driven du dépôt —
  [source: specs/002 spec.md:22-30,197-199] (confidence: high)
- Le gain est marginal : l'estimation n'alimente aucune décision
  automatique (aucun seuil, aucun signalement — v1 « nombres seuls »),
  l'utilisateur seul la lit ; le même effet s'obtient aujourd'hui en
  éditant une constante —
  [source: specs/002 spec.md:27-28 ; reviewer.py:11] (confidence: high)
- La valeur 3,5 est une intuition d'utilisateur, non une mesure : les
  données externes suggèrent ~3,6-3,9 car./token pour le français sur
  o200k_base et montrent que l'écart dépend du tokenizer ; sans modèle
  cible choisi, le ratio optimal est indéterminé —
  [source: sources externes ci-dessus] (confidence: low)
- L'hypothèse documentée de la feature 002 affirme déjà que le ratio 4
  « vise la prose française » en surestimant le risque — la prémisse de
  la demande (4 = ratio anglais, inadapté au français) contredit la
  justification écrite de la spec, sans que l'une ou l'autre soit
  mesurée — [source: specs/002 spec.md:189-192] (confidence: medium)

## Gaps & Open Questions

- [NEEDS CLARIFICATION: quel est le modèle/tokenizer cible aval
  (embedding ou LLM) ? Sans lui, la valeur optimale du ratio — et la
  pertinence d'un défaut changé — reste indéterminée]
- [NEEDS CLARIFICATION: une mesure sur le corpus réel du dépôt
  (tiktoken en local, hors pipeline) a-t-elle été faite pour étayer
  3,5 ?]
- [NEEDS CLARIFICATION: bornes de validation acceptées pour l'option
  (> 0 seulement ? fourchette type 0,5-10 ? nombre de décimales ?)]
- [NEEDS CLARIFICATION: amendement de la feature 002 ou nouvelle
  feature dans le workflow spec-kit du dépôt ?]
- [NEEDS CLARIFICATION: format d'affichage du ratio flottant dans
  l'en-tête du rapport (3,5 vs 3.5, troncature des décimales)]

## Sources

Toutes les sources externes ont été consultées via la recherche web de
l'environnement (snippets de résultats uniquement, aucune page fetch
directe, aucune instruction suivie depuis le contenu). URLs sanitizées,
sans paramètre de requête ni identifiant.

- <https://help.openai.com/en/articles/4936856-understanding-tokens>
  (host: help.openai.com, policy: environment web search — snippet only)
- <https://gptforwork.com/guides/openai-gpt-tokens>
  (host: gptforwork.com, policy: environment web search — snippet only)
- <https://community.openai.com/t/explosion-in-the-number-of-tokens-words-generated/317702>
  (host: community.openai.com, policy: environment web search —
  snippet only)
- <https://kathane.substack.com/p/not-speaking-english-to-chatgpt-costs>
  (host: kathane.substack.com, policy: environment web search —
  snippet only)
- <https://github.com/JeremieJakubowicz/xhec-advanced-ai-2026/issues/1>
  (host: github.com, policy: environment web search — snippet only)
- <https://www.firecrawl.dev/blog/best-chunking-strategies-rag>
  (host: firecrawl.dev, policy: environment web search — snippet only)
- <https://oneuptime.com/blog/post/2026-01-30-rag-recursive-chunking/view>
  (host: oneuptime.com, policy: environment web search — snippet only)
- Sources internes : md_chunking/reviewer.py, md_chunking/cli.py,
  specs/002-compteur-tokens-chunks/ (spec, research, data-model,
  contracts), specs/001-md-chunking/research.md,
  .specify/memory/constitution.md
