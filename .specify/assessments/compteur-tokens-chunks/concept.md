# Concept: Visibilité sur le budget de tokens à la relecture

- **Slug**: compteur-tokens-chunks
- **Created**: 2026-10-02
- **Recommended option**: A — Estimation locale zéro-dépendance

## Options

### Option A — Estimation locale zéro-dépendance

- **Sketch**: à la relecture, chaque chunk du rapport `review.md`
  porte en métadonnées une estimation de tokens explicitement marquée
  approximative (ex. « ≈ N tokens »), calculée localement par une
  heuristique déterministe de division caractère→token, sans nouvelle
  dépendance, sans réseau. Le « X car. » existant demeure l'unité de
  référence du découpage.
- **Appetite**: small (quelques heures à un jour, test inclus)
- **Trade-offs**: gagne — conformité triviale aux principes II, III et
  IV ; déterminisme SC-005 préservé ; supprime l'incitation aux
  compteurs en ligne ; effort minimal. Sacrifie — la précision
  (±10–30 % selon langue et contenu, research.md) ; un ratio unique
  couvre mal le mélange prose FR / code du corpus réel. Risque : un
  nombre affiché, même marqué « ≈ », peut être pris pour un compte
  exact (avertissement explicite des sources).
- **Rabbit holes**: multiplication des ratios par type de contenu
  (prose FR / code / tableaux) au lieu d'un ratio simple ; extension
  de l'estimation à l'index JSON, aux presets et aux totaux par
  document ; calibrage du ratio sur le corpus qui tourne à l'étude
  sans fin.

### Option B — Compte exact par tokenizer intégré

- **Sketch**: le rapport affiche un compte exact de tokens pour un
  tokenizer choisi (p. ex. un `tokenizer.json` HF tokenizers committé
  dans le dépôt), le choix du tokenizer étant explicité dans le
  rapport.
- **Appetite**: small–medium (quelques jours : intégration, commit du
  vocabulaire ~2 Mo, tests de non-régression)
- **Trade-offs**: gagne — compte exact, aligné sur un modèle réel ;
  crédibilité maximale du nombre affiché. Sacrifie — une dépendance de
  plus (constitution IV) ; le verrouillage sur un modèle dont le
  tokenizer changera ; un vocabulaire de ~2 Mo dans le dépôt ; un
  compte « exact » qui devient faux dès que le modèle visé change de
  tokenizer. tiktoken est écarté d'office : téléchargement réseau au
  premier usage, contraire à la constitution II (research.md).
- **Rabbit holes**: choix de l'encodage (cl100k_base, o200k_base,
  tokenizer HF maison…) et son interface utilisateur ; mise à jour du
  vocabulaire à chaque génération de modèle ; dérive vers un paramètre
  `--tokenizer` généralisé, puis vers un comptage exact des coûts
  API — hors non-goals.

### Option C — Ne rien construire, documenter la règle de conversion

- **Sketch**: aucun changement de code ; le README (rubrique « Pour
  débutants ») documente la règle de conversion (prose ≈ 4
  car./token, français ~10–30 % de tokens en plus) pour que
  l'utilisateur fasse l'approximation de tête.
- **Appetite**: small (une heure de documentation)
- **Trade-offs**: gagne — zéro code, zéro risque de régression,
  YAGNI pur. Sacrifie — l'information ne se trouve pas là où le
  problème se pose (dans le rapport, chunk par chunk) ;
  l'approximation mentale demeure, erreur par erreur ; les entités
  atomiques hors fourchette restent invisibles à la relecture. Les
  metrics « 100 % des chunks portent l'info » et « repérage sans
  outil externe » ne sont pas atteintes.
- **Rabbit holes**: négligeable — c'est l'option témoin.

## Recommendation

Option A. Elle est la seule qui atteigne les quatre objectifs du
problème avec un effort minimal : visibilité au bon endroit (rapport
de relecture), suppression de l'incitation aux compteurs en ligne,
déterminisme et hors-ligne préservés par construction, et caractère
approximatif rendu explicite dans l'affichage même. L'imprécision
(±10–30 %) est acceptable au regard de l'usage visé — repérer les
chunks *à risque* de dépassement, pas facturer des tokens — et
cohérente avec le coût de l'inaction documenté : les presets par
défaut (~25–330 tokens) sont très en dessous des fenêtres courantes,
seule la détection des cas limites compte. L'option B ne se
justifierait que si l'utilisateur exige un compte exact pour un
modèle précis — c'est l'objet de la question ouverte n° 1 ; si la
réponse l'exige, B reste un repli propre sur la même structure
d'affichage. L'option C ne répond pas à la metric centrale (100 % des
chunks portent l'information).

## Out of Scope (for the recommended option)

- Tout changement de l'unité de découpage : FR-002 (caractères) et la
  décision D4 restent intacts.
- Toute application automatique d'une limite de tokens au découpage
  ou à l'overlap.
- L'index JSON : pas de champ tokens dans la sortie machine (périmètre
  = rapport de relecture ; extension possible à trancher en
  spécification, question ouverte n° 2).
- Toute dépendance nouvelle (tokenizer, vocabulaire committé, API
  distante).
- Le compte exact, la facturation, l'estimation de coût par appel.
- Les totaux par document et les ratios différenciés par typologie de
  contenu (prose/code/tableaux) — non exclus définitivement, mais pas
  dans l'appetite de base ; à trancher en spécification (question
  ouverte n° 4).

## Assumptions to Validate

- Le modèle d'embedding visé a une fenêtre suffisamment large
  (≥ 512 tokens, vraisemblablement 8191) pour qu'une estimation à
  ±30 % suffise à repérer les chunks à risque — si la fenêtre cible
  est étroite, un compte exact (option B) devient nécessaire.
- Un ratio unique (prose, ~3–4 car./token) appliqué à tout chunk
  donne une estimation jugée utile par l'utilisateur, y compris pour
  les blocs de code (~3 car./token) — l'écart entre les deux ratios
  est secondaire pour l'usage de détection de risque.
- L'utilisateur accepte un affichage explicitement approximatif
  (« ≈ ») sans exiger un compte exact.
- L'heuristique reste déterministe et ne dépend d'aucun état externe
  (pré-requis SC-005).
- Le rendu de relecture reste conforme à FR-008 et le temps de
  relecture SC-004 n'est pas dégradé par l'information
  supplémentaire.
