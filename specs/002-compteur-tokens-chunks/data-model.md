# Data Model: Compteur de tokens dans le rapport de relecture

**Feature**: specs/002-compteur-tokens-chunks | **Date**: 2026-10-02

## Entités

### Estimation de tokens

- **Définition**: valeur entière approchée du nombre de tokens d'un
  chunk, calculée au rendu par `ceil(len(text) / 4)` ; jamais
  stockée, jamais sérialisée.
- **Attributs**: valeur (entier ≥ 1 pour tout chunk) ; marqueur
  d'approximation « ≈ » ; libellé « (estimation) ».
- **Cycle de vie**: calculée pendant la construction du rapport de
  relecture, affichée, puis jetée — aucun état persistant
  (research.md D1).

### Ratio caractères→tokens

- **Définition**: constante du code `RATIO_CHARS_PER_TOKEN = 4`.
- **Contraintes**: entière, strictement positive ; modifiable dans
  le code uniquement, sans paramètre d'interface en v1
  (clarification du 2026-10-02) ; affichée dans l'en-tête du
  rapport (FR-T02, FR-T05).

### Rapport de relecture (enrichissement)

- **Définition**: sortie existante (FR-008 de la feature 001),
  enrichie d'une ligne de métadonnée par chunk et d'une mention
  d'en-tête par document.
- **Contraintes**: une ligne d'estimation par chunk présent dans
  le rapport ; aucune autre modification du format (cf.
  [contracts/review-render.md](contracts/review-render.md)).

## Entités inchangées (garde-fous)

- **Chunk** (`md_chunking/models.py`) : aucun champ ajouté ;
  `length` reste la mesure de référence du découpage (FR-T03).
- **Index JSON** (`md_chunking/indexer.py`, contrat chunk-json.md
  de la feature 001) : schéma 1.0 strictement inchangé ; aucun champ
  `tokens` à aucun niveau (FR-T07).
- **CLI** (`md_chunking/cli.py`) : aucune nouvelle option, aucun
  changement de comportement.

## Règles de validation

- `estimate_tokens` est une fonction pure : même texte → même
  valeur, sans état ni aléa (FR-T06, SC-T04).
- Toute sortie du pipeline à paramètres constants reste identique
  d'une exécution à l'autre (SC-005 de la feature 001).
- Une estimation ne peut pas influencer le découpage : elle est
  calculée après, sur des chunks déjà produits (FR-T03).
