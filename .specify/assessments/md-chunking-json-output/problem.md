# Problem Definition: Chunking Markdown fiable et contrôlable

- **Slug**: md-chunking-json-output
- **Created**: 2026-10-02
- **Inputs used**: intake.md | research.md

## Problem Statement

L'utilisateur du dépôt MD_Chunking n'a aucun moyen reproductible de
découper ses documents Markdown en chunks : le découpage manuel est
fastidieux, non traçable (impossible de savoir d'où vient un chunk une
fois embeddé) et ne respecte pas la structure des documents (titres,
parties, sous-parties), ce qui dégrade la qualité du retrieval en aval.
Avant d'embedder, il lui faut aussi pouvoir vérifier à l'œil nu que le
découpage est correct — ce qu'aucun flux actuel ne lui permet.

## Affected Users & Stakeholders

- **Users**: le propriétaire du dépôt MD_Chunking (utilisateur unique
  identifié) — il prépare manuellement ses documents Markdown pour un
  pipeline d'embedding et subit le coût du découpage artisanal, de
  l'absence de traçabilité et de l'impossibilité de contrôle.
  [NEEDS CLARIFICATION: d'autres utilisateurs sont-ils visés (équipe,
  public) ? Aucun signal d'utilisateur externe dans l'intake ou la
  research]
- **Stakeholders**: le propriétaire du dépôt — décideur unique
  (contrainte posée : éviter LangChain/LlamaIndex, privilégier maison
  ou Haystack) et bénéficiaire direct.

## Goals

- Un découpage de documents Markdown en chunks paramétrable et
  reproductible (taille min/max, overlap, typologie de document),
  respectant au mieux la structure (sections, puis paragraphes, puis
  phrases en dernier recours).
- Une occupation maximale de la plage de taille autorisée, sans casser
  la cohérence structurelle des chunks.
- Un index de traçabilité pour chaque chunk (chemin d'origine
  obligatoire, numéro de référence obligatoire, plus titre/page/
  partie/position quand l'information est balisée) exporté en JSON.
- La capacité de contrôler visuellement le résultat du découpage avant
  l'embedding.
- Une organisation des sorties par document, dans un dossier output
  structuré.

## Non-Goals

- L'embedding lui-même, le stockage vectoriel et la recherche (le
  besoin s'arrête à la production du JSON de chunks).
- Le parsing de formats autres que Markdown (PDF, DOCX, HTML) — y
  compris la conversion PDF vers Markdown. [NEEDS CLARIFICATION: la
  « page » balisée suppose un amont de conversion ; à borner]
- Le chunking sémantique par similarité d'embeddings (non demandé dans
  l'intake).
- Une interface graphique : le contrôle « à l'œil nu » vise un rendu
  lisible, pas une application interactive. [NEEDS CLARIFICATION:
  forme du rendu attendue]

## Success Metrics

- 100% des chunks produits tiennent dans la fourchette min/max
  configurée (baseline: unknown — aucun flux existant).
- 100% des chunks portent les deux métadonnées obligatoires (chemin du
  document, numéro de référence) ; les métadonnées conditionnelles
  (titre, page, partie, position) sont présentes dès que la balise
  existe dans le document (baseline: unknown).
- Chaque frontière de chunk respecte une frontière structurelle
  (section, paragraphe ou phrase) — le recours au niveau inférieur est
  la trace d'une contrainte de taille, pas d'un défaut
  (baseline: unknown).
- L'utilisateur peut valider le découpage d'un document à l'œil nu
  avant embedding, en un temps jugé raisonnable par lui (métrique
  qualitative ; baseline: impossible aujourd'hui).
- Amélioration mesurable du retrieval en aval (recall/précision) —
  dépendante de l'existence d'un jeu d'évaluation (baseline: unknown ;
  la research montre des gains de 10–15% de recall possibles par
  l'ajustement du chunking, mais non mesurés sur ce cas d'usage).

## Cost of Inaction

Sans l'outil, le découpage reste manuel et ad hoc : coût de préparation
élevé et croissant avec le volume de documents, chunks incohérents d'un
document à l'autre, aucune traçabilité entre un résultat de recherche
et son passage source dans le document, impossible d'itérer sur les
paramètres (taille/overlap) faute de sortie observable, et retrieval de
qualité inférieure — la research établit que la stratégie de chunking
pèse autant ou plus que le choix du modèle d'embedding sur la qualité
du RAG.

## Open Questions

- [NEEDS CLARIFICATION: unité de mesure de la taille de chunk —
  caractères, tokens ou mots ; les pratiques du marché s'expriment en
  tokens]
- [NEEDS CLARIFICATION: justification ou validation de l'overlap par
  défaut à 15% — une étude citée en research montre qu'un chunking
  récursif sans overlap est un défaut fort]
- [NEEDS CLARIFICATION: format et volumétrie des inputs (fichiers
  .md uniquement ? plusieurs documents par exécution ?)]
- [NEEDS CLARIFICATION: convention de balisage attendue pour « titre
  du document » et « page » (front-matter YAML, balise HTML, amont de
  conversion PDF ?)]
- [NEEDS CLARIFICATION: schéma JSON exact attendu par le consommateur
  en aval (pipeline d'embedding existant ?)]
- [NEEDS CLARIFICATION: forme du rendu de vérification « à l'œil nu »
  (texte, Markdown annoté, HTML ?)]
- [NEEDS CLARIFICATION: valeur de X (lettres du titre) pour le nommage
  des sous-dossiers d'output, et comportement si titre absent ou
  dupliqué]
- [NEEDS CLARIFICATION: stratégie d'« occupation maximale » — critère
  d'arrêt et gestion des sections hors fourchette (fusion, split ?)]
- [NEEDS CLARIFICATION: base factuelle des presets par typologie
  (articles/documentation/conversations/code) — valeurs plausibles
  mais non sourcées]
- [NEEDS CLARIFICATION: périmètre technique — maison, Haystack seul,
  ou Haystack étendu (contrainte utilisateur : ni LangChain ni
  LlamaIndex)]
