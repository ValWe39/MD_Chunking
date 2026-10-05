# Data Model: Ratio caracteres/tokens reglable en CLI

**Feature**: specs/004-ratio-tokens-cli | **Date**: 2026-10-05

## Entites

### Ratio caracteres→tokens (nouveau)

- **Definition**: parametre d'execution decimal exprimant le nombre de
  caracteres par token utilise pour l'estimation du rapport de
  relecture.
- **Attributs**: valeur decimale, bornes ]0 ; 10], defaut 3,5 ; format
  de saisie : point decimal ; nombre de decimales libre (calcul exact).
- **Cycle de vie**: lu depuis la ligne de commande (ou pris au defaut),
  valide au parsing (echec rapide code 2 si hors bornes ou mal forme),
  route jusqu'au rendu, affiche arrondi a une decimale dans l'en-tete,
  puis jete — aucun etat persistant.
- **Relations**: aucun — transitoire, ne touche aucune entite
  persistee (FR-008).

### Estimation de tokens (amendee, feature 002)

- **Definition**: valeur entiere approchee du nombre de tokens d'un
  chunk, `ceil(len(texte) / ratio)`, calculee au rendu par division
  exacte (Fraction) — jamais stockee, jamais serialisee.
- **Attributs**: valeur (entier ≥ 1 pour tout chunk non vide) ;
  marqueur d'approximation « ≈ » ; libelle « (estimation) » — inchanges.
- **Cycle de vie**: calculee pendant la construction du rapport,
  affichee, puis jetee (feature 002, research.md D1) ; seul le mode de
  calibrage change (constante de code → defaut reglable par option).

## Entites inchangees (garde-fous)

- **Chunk** (`md_chunking/models.py`) : aucun champ ajoute ; `length`
  reste la seule mesure de taille du decoupage (FR-006).
- **Index JSON** (`md_chunking/indexer.py`) : schema 1.0 strictement
  inchange ; aucun champ `tokens` ni `ratio` a aucun niveau (FR-007).
- **Compteur d'occurrence** (`md_chunking/counter.py`, `counter.txt`) :
  inchange ; le ratio ne circule jamais hors du rendu (FR-008).
- **Nom de sortie** (`md_chunking/naming.py`) : inchange ; memes noms a
  parametres constants (FR-007).
- **Presets de typologie** (`md_chunking/presets.py`) : inchange ; le
  ratio est global a l'execution, pas par typologie.

## Regles de validation

- `estimate_tokens` reste une fonction pure : meme texte et meme ratio
  → meme valeur, sans etat, sans alea (FR-005, SC-005).
- La division est exacte (Fraction construite depuis la representation
  decimale de la saisie) : aucun artefact binaire, aucune divergence de
  plateforme, verifiable y compris pour un ratio comme 3,3.
- L'affichage de l'en-tete utilise un formatage fixe a une decimale :
  meme ratio → meme en-tete, quel que soit le nombre de decimales
  saisi (FR-004).
- Tout ratio hors bornes ]0 ; 10] echoue au parsing, avant toute lecture
  de compteur et toute ecriture (FR-003, SC-003).
