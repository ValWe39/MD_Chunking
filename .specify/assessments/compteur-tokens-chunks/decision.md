# Decision: Compteur de tokens approximatif par chunk dans le rapport visuel

- **Slug**: compteur-tokens-chunks
- **Decided**: 2026-10-02
- **Verdict**: go
- **Artifacts reviewed**: intake.md | research.md | problem.md |
  concept.md
- **User input at decide time**: « A me plait bien, B aussi » ; choix
  explicité en interaction : approche **A puis B** (A d'abord, B en
  extension si la précision s'avère insuffisante) ; modèle d'embedding
  aval **pas encore décidé**.

## Scorecard

| Critère | Note |
| ------- | ---- |
| Problem validity | adequate |
| Evidence strength | adequate |
| Value vs. inaction | adequate |
| Feasibility / appetite | strong |
| Strategic fit | strong |
| Risk posture | adequate |

Justifications, une par critère :

- **Problem validity (adequate)** : problème réel et exprimé par
  l'utilisateur unique visé, mais signal n=1 ; le besoin général
  (traduire des caractères en tokens à la main) est documenté dans la
  littérature RAG (research.md, arxiv 2609.29828).
- **Evidence strength (adequate)** : preuves internes high (D4,
  FR-002, FR-008, reviewer.py, venv) ; preuves externes medium mais
  multi-sources convergentes (~4 car./token, +10–30 % pour le
  français) ; comportement réseau de tiktoken corroboré par GitHub +
  Stack Overflow. Pas de score unknown bloquant.
- **Value vs. inaction (adequate)** : le coût de l'inaction est réel
  mais borné (presets par défaut très en dessous des fenêtres
  courantes) ; l'appetite small de A rend le rapport valeur/coût
  favorable.
- **Feasibility / appetite (strong)** : option A crédible en quelques
  heures à un jour, sans dépendance ; B correctement balisé comme
  extension conditionnelle avec son propre appetite (small–medium) et
  ses rabbit holes identifiés.
- **Strategic fit (strong)** : A est conforme par construction aux
  principes II (hors-ligne), III (zéro dépendance nouvelle), IV
  (YAGNI) ; B respecte II et III à condition d'un vocabulaire
  committé (stratégie documentée en research.md). D4 préservée :
  l'unité de découpage reste le caractère.
- **Risk posture (adequate)** : risques principaux identifiés :
  estimation prise pour un compte exact (mitigé par l'affichage « ≈ »
  et un objectif dédié), dérive de périmètre (mitigée par les
  exclusions explicites du concept). Le choix « A puis B » reporte le
  risque du vocabulaire committé (~2 Mo) au moment où l'insuffisance
  de A sera constatée — pas de risque caché.

## Verdict & Rationale

**GO.** Le problème est valide et borné, les preuves sont adéquates,
et l'utilisateur a endossé l'option recommandée en l'explicitant :
commencer par A (estimation locale zéro-dépendance, affichage
« ≈ N tokens » dans `review.md`), avec B (compte exact par tokenizer
committé) comme extension conditionnelle déclenchée si la précision
de A se révèle insuffisante. Le modèle d'embedding aval n'étant pas
encore décidé, A est précisément la bonne première marche : agnostique
du modèle, elle atteint les quatre objectifs du problème sans
dépendance. Le scorecard ne contient aucun critère `weak` ni
`unknown` bloquant ; le seul `adequate` fragile (value vs. inaction)
est couvert par l'appetite minimal de A.

## If go — Handoff to `/speckit-specify`

- **Problem** : à la relecture des chunks avant embedding,
  l'utilisateur n'a aucune visibilité sur leur taille en tokens — le
  rapport n'exprime les tailles qu'en caractères, poussant à
  l'approximation mentale ou vers des compteurs en ligne contraires
  au local-first.
- **Chosen approach** : Option A du concept — estimation de tokens
  par chunk dans le rapport de relecture, heuristique déterministe
  locale, zéro dépendance ; structure d'affichage conçue pour
  accueillir B plus tard (compte exact par tokenizer) sans refonte.
- **In scope** : rendu `review.md` uniquement (via
  `md_chunking/reviewer.py`) ; affichage explicitement approximatif ;
  heuristique simple (ratio caractère→token, déterministe,
  hors-ligne).
- **Out of scope** : index JSON ; changement d'unité de découpage
  (FR-002/D4 intacts) ; application automatique de limites ; compte
  exact, facturation, estimation de coût ; totaux par document et
  ratios par typologie de contenu (à trancher en spécification).
- **Success metrics** : 100 % des chunks portent l'estimation dans
  `review.md` (baseline 0 %) ; repérage des chunks à risque sans
  outil externe dans le budget SC-004 ; SC-005 (déterminisme) et
  SC-006 (zéro réseau) non régressifs ; caractère approximatif
  lisible comme tel dans le rapport.
- **Carried-forward open questions** : les quatre ci-dessous.

- [NEEDS CLARIFICATION: format d'affichage — ligne de métadonnées
  additionnelle ou remplacement du « X car. » ; total par document
  oui/non ?]
- [NEEDS CLARIFICATION: valeur du ratio et plafond d'acceptabilité de
  l'erreur (l'option A vise ±10–30 % ; à valider pendant la
  spécification, idéalement sur le corpus Examples/).]
- [NEEDS CLARIFICATION: critère de déclenchement de l'option B —
  quels constats sur A (fenêtre cible étroite, écart trop grand)
  ouvriront l'extension « compte exact », et avec quel tokenizer
  (stratégie vocabulaire committé vs premier build, constitution
  II) ?]
- [NEEDS CLARIFICATION: le modèle d'embedding aval restant non
  décidé, faut-il documenter dans le rapport le caractère
  modèle-agnostique de l'estimation ?]
