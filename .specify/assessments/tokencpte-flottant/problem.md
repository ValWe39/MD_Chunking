# Problem Definition: Estimation de tokens calibree pour l'anglais

- **Slug**: tokencpte-flottant
- **Created**: 2026-10-05
- **Inputs used**: intake.md | research.md

## Problem Statement

L'estimation de tokens affichée dans le rapport de relecture repose sur un
ratio unique fixe de 4 caracteres par token, calibre pour la prose anglaise,
alors que le corpus traite est essentiellement en francais — langue dont la
densite reelle mesuree est d'environ 3,6 a 3,9 caracteres par token sur les
tokenizers recents. Consequence : l'utilisateur qui relit un rapport ne peut
ni corriger cette estimation pour son corpus, ni l'adapter sans editer le
code source de l'outil ; l'indication affichee peut alors sous-estimer le
risque de depassement des limites du modele aval pour les chunks limites.

## Affected Users & Stakeholders

- **Users**: le proprietaire du depot, seul lecteur des rapports de relecture
  `_review.md`, qui s'en sert pour juger du risque de taille des chunks sur
  un corpus francophone — [source: intake.md, conversation du 2026-10-05]
- **Stakeholders**: le proprietaire du depot, qui arbitre seul la reouverture
  de la decision spec v1 (« constante du code, sans parametre d'interface »,
  feature 002) ; le pipeline d'embedding aval, dont le modele cible n'est pas
  encore choisi et qui determine le ratio reel pertinent —
  [source: specs/002 spec.md:22-30 ; research.md, Gap 1]

## Goals

- L'estimation affichee est credible pour un corpus francophone : proche de
  la densite reelle du texte traite, pas d'un calibrage anglais par defaut.
- L'ecart entre l'estimation affichee et le compte reel du tokenizer cible
  reste assez faible pour que l'indication serve a detecter les chunks
  proches d'une limite de modele.
- L'utilisateur peut adapter l'estimation a son corpus ou a un changement de
  modele cible sans avoir a modifier le code source.

## Non-Goals

- Comptage exact des tokens par tokenizer (option B de la feature 002,
  reservee au choix d'un modele cible).
- Toute influence sur le decoupage : l'unite de decoupage reste le
  caractere, la fourchette min/max et l'overlap sont hors perimetre.
- Toute modification de l'index JSON (aucun champ `tokens`, FR-T07).
- Couverture des scripts non latins (CJK) — hors perimetre v1 de la
  feature 002.

## Success Metrics

- Ecart entre estimation et compte de reference sur le corpus reel du depot
  contenu dans une tolerance fixee (ex. +-20 %) — (baseline: inconnue, aucune
  mesure n'a ete faite sur le corpus reel ; la mesure reference exigerait un
  tokenizer, hors pipeline) [NEEDS CLARIFICATION: tolerance et protocole
  de mesure a definir]
- Signal qualitatif : l'utilisateur juge l'indication utile et representative
  dans ses relectures courantes — (baseline: perception actuelle non
  documentee)

## Cost of Inaction

Faible et borne. L'estimation est purement informative : elle n'alimente
aucune decision automatique, n'affecte pas le decoupage, l'index JSON ni le
nommage des sorties ; un utilisateur technique peut deja corriger le ratio en
editant une constante du code (reviewer.py:11). Ce qui persiste : une
indication systematiquement biaisse d'environ 10 a 15 % en faveur d'une
sous-estimation sur prose francaise (ratio 4 contre ~3,6-3,9 reel), et la
necessite d'une edition de code pour tout changement de calibrage.

## Open Questions

- [NEEDS CLARIFICATION: quel est le modele/tokenizer cible aval ? Sans lui,
  le ratio optimal — et donc la valeur par defaut pertinente — reste
  indetermine (research.md, Gap 1)]
- [NEEDS CLARIFICATION: une mesure de reference sur le corpus reel du depot
  a-t-elle ete faite pour etayer la valeur proposee de 3,5 ? (research.md,
  Gap 2 ; la spec 002 affirme au contraire que le ratio 4 « vise la prose
  francaise »)]
- [NEEDS CLARIFICATION: quelle tolerance d'ecart acceptable entre
  estimation affichee et compte reel, et selon quel protocole de mesure ?]
- [NEEDS CLARIFICATION: gouvernance du changement — amendement de la
  feature 002 ou nouvelle feature dans le workflow spec-kit ? (research.md,
  Gap 4)]
