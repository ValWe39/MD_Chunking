# Decision: Chunker Markdown avec JSON de sortie

- **Slug**: md-chunking-json-output
- **Decided**: 2026-10-02
- **Verdict**: go
- **Artifacts reviewed**: intake.md | research.md | problem.md |
  concept.md (+ `.specify/memory/constitution.md` v1.4.0)

## Scorecard

- **Problem validity** — strong : besoin directement vécu par
  l'utilisateur, matérialisé par 4 documents d'entrée réels fournis
  (44–110 KB) ; aucune traceabilité ni contrôle possible dans le
  flux actuel.
- **Evidence strength** — adequate : composants Haystack et
  pratiques de chunking bien sourcés (docs deepset, arxiv, guides
  Weaviate/Unstructured) ; l'overlap 15% a désormais une origine
  documentée (formation Corsen citée par l'utilisateur, page non
  fetchée — hôte hors liste d'autorisation, donc non vérifiée
  indépendamment) ; les presets par typologie restent non sourcés
  (assumptions documentées) — compensé en partie par l'évidence
  réelle des 4 exemples analysés.
- **Value vs. inaction** — strong : le coût de l'inaction est
  documenté (découpage artisanal non reproductible, zéro
  traçabilité, retrieval dégradé) ; la research établit que le
  chunking pèse autant ou plus que le modèle d'embedding sur la
  qualité RAG.
- **Feasibility / appetite** — strong : l'option B (Haystack étendu)
  est crédible en small–medium ; les 4 exemples confirment
  exactement où portent les composants maison (normalisation des
  titres, bascule de niveaux, overlap structurel).
- **Strategic fit** — strong : constitution v1.4.0 — CLI-first (IV),
  Python, open-source permissif (III), préférence outils souverains ;
  Haystack est édité par deepset (Berlin, Allemagne), licence
  Apache-2.0. Tension YAGNI (IV) avec un framework, mitigée par
  l'usage des seuls composants de preprocessing.
- **Risk posture** — adequate : risques identifiés et atténuables —
  bug Haystack #12686 (contournement dans le composant maison),
  titres malformés (normalisation en entrée, constat des exemples),
  débat sur l'overlap (paramètre ajustable, pas une constante),
  télémétrie éventuelle de Haystack à vérifier (constitution III).

## Verdict & Rationale

**Go.** Le problème est réel et vécu (validity strong), la valeur
contre l'inaction est claire, et l'option recommandée (Haystack
étendu par composants maison) tient dans un appétit small–medium tout
en respectant la contrainte utilisateur (ni LangChain ni LlamaIndex)
et la constitution (CLI, open-source, souveraineté, local-first).
L'evidence strength est `adequate` et non `strong` : l'ossature
factuelle (composants existants, pratiques de chunking, comportement
des inputs réels) est solide ; l'overlap 15% est maintenant attribué
à une source pédagogique (Corsen, citée par l'utilisateur, non
vérifiée par fetch) et les presets par typologie restent des
assumptions ; ils sont traités comme valeurs par défaut modifiables
et listés en questions ouvertes pour la spécification, pas comme des
vérités. Aucun critère n'est `weak` ou `unknown` au point de bloquer.

## If go — Handoff to `/speckit-specify`

- **Problem**: découper des documents Markdown en chunks
  paramétrables (taille min/max, overlap, typologie) respectant la
  structure, avec un index de traçabilité JSON par chunk et un
  contrôle visuel avant embedding — reproductiblement et sans
  framework LangChain/LlamaIndex.
- **Chosen approach**: Option B — pipeline Haystack (deepset) comme
  socle (`MarkdownToDocument`, `MarkdownHeaderSplitter`) + composants
  maison ciblés : normalisation des titres malformés et CRLF/LF,
  bascule sections→paragraphes→phrases avec occupation maximale de la
  fourchette, overlap structurel, export JSON normalisé, rendu de
  relecture humaine, organisation des sorties par document dans
  `output/`.
- **In scope**: fichiers `.md` ; fourchette min/max paramétrable ;
  presets par typologie (dont un type « livre/littérature à longue
  prose » à ajouter) ; JSON avec chemin + numéro de référence
  obligatoires, titre/page/partie/position si balisés ; dossier
  output numéroté ou dérivé du titre.
- **Out of scope**: embedding, stockage vectoriel, recherche ;
  parsing PDF/DOCX/HTML ; chunking sémantique ; GUI ; découpage fin
  des tableaux/blocs de code ; indexation multi-échelles.
- **Success metrics**: 100% des chunks dans la fourchette ; 100% des
  métadonnées obligatoires présentes ; frontières structurelles
  respectées ; validation à l'œil nu possible avant embedding ;
  (rétention) conformité constitution : local-only, aucun tracker,
  aucun secret.
- **Carried-forward open questions**:
  - [NEEDS CLARIFICATION: unité de taille de chunk — tokens
    (hypothèse recommandée par la research) ou caractères/mots]
  - [NEEDS CLARIFICATION: schéma JSON exact attendu par le
    consommateur en aval]
  - [NEEDS CLARIFICATION: forme du rendu de vérification « à l'œil
    nu »]
  - [NEEDS CLARIFICATION: convention de balisage pour « titre du
    document » et « page » (page sera absente sur les 4 exemples
    réels)]
  - [NEEDS CLARIFICATION: valeur de X (lettres du titre) pour le
    nommage des sous-dossiers d'output ; comportement si titre
    absent/dupliqué]
  - [NEEDS CLARIFICATION: stratégie d'occupation maximale —
    heuristique gloutonne pour borner le rabbit hole
    d'optimisation]
  - [NEEDS CLARIFICATION: base des presets par typologie — fournir
    comme défauts modifiables]
  - [NEEDS CLARIFICATION: vérifier que Haystack n'émet pas de
    télémétrie/tracker, ou documenter sa désactivation (constitution
    III)]
  - [NEEDS CLARIFICATION: version Haystack à épingler et
    contournement du bug #12686]
