# Idea Intake: Option CLI --tokencpte pour un ratio caracteres/tokens flottant

- **Slug**: tokencpte-flottant
- **Created**: 2026-10-05
- **Source**: pasted text (conversation du 2026-10-05), relatif au
  depot courant (md_chunking, feature 002)
- **Type**: improvement

## Idea (as captured)

> Serait-ce compliquer de rendre ce paramètre flottant par l'ajout d'une
> commande dédiée ("--tokencpte") ? et de le paramétrer par défaut à
> 1 token à 3,5 caractères (j'ai essentiellement des textes en français).

Contexte de capture : question posée à la suite d'une investigation en
lecture seule sur le calcul des tokens dans `md_chunking/reviewer.py`
(constante `RATIO_CHARS_PER_TOKEN = 4`, fonction `estimate_tokens`), et de
l'analyse de faisabilité qui a suivi (rayon d'impact limité à `reviewer.py`
et au fichier `_review.md` ; décision spec v1 contraire à rouvrir).

## Restated

Rendre le ratio caracteres→tokens paramétrable depuis la ligne de commande
via une option dédiée `--tokencpte` acceptant une valeur flottante, avec un
défaut changé de 4 à 3,5 caractères par token, justifié par un corpus
essentiellement en français. L'estimation resterait locale, déterministe et
modèle-agnostique.

## Origin & Context

- **Raised by**: l'utilisateur (propriétaire du dépôt), le 2026-10-05
- **Trigger**: investigation en lecture seule sur le calcul des tokens
  (`estimate_tokens`, ratio fixe 4) suivie d'une question de faisabilité ;
  constat que le corpus visé est majoritairement francophone et que le ratio
  par défaut de 4, documenté comme visant la prose française, pourrait être
  affiné à 3,5

## First-Glance Unknowns

- [NEEDS CLARIFICATION: réouverture de la décision spec — FR-T02 et la
  clarification du 2026-10-02 tranchent « constante du code, sans paramètre
  d'interface en v1 » : amendement de la feature 002 ou nouvelle feature ?]
- [NEEDS CLARIFICATION: valeur par défaut — le passage de 4 à 3,5 contredit
  FR-T02 et les hypothèses documentées ; quelle justification retient-on
  pour 3,5 (mesure sur corpus réel, référence de tokenizer, choix
  conservateur ?)]
- [NEEDS CLARIFICATION: validation de l'option — bornes acceptables du
  ratio flottant (> 0 seulement ? fourchette ? nombre de décimales ?)]
- [NEEDS CLARIFICATION: comportement en cas d'arrondi flottant — un ratio
  non représentable en binaire (ex. 3,3) crée des cas limites d'arrondi ;
  calcul en entiers, restriction du format, ou acceptation du risque ?]
- [NEEDS CLARIFICATION: affichage de l'en-tête du rapport — format du ratio
  flottant dans la ligne « Tokens estimes a ~X caracteres par token »]
- [NEEDS CLARIFICATION: impact exact sur les artefacts spec et tests à
  mettre à jour (contrats review-render.md et cli.md, tests test_reviewer.py
  et test_cli.py, README)]
