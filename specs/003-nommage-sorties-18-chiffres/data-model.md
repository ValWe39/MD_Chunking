# Data Model: Nommage des sorties (18 chiffres)

**Feature**: specs/003-nommage-sorties-18-chiffres | **Date**: 2026-10-05

## Entités

### Nom de sortie

- **Définition**: chaîne de 18 chiffres identifiant une occurrence de
  production d'un document ; utilisée comme radical des deux fichiers
  produits (`<nom>.json`, `<nom>_review.md`).
- **Attributs**: trois blocs — bloc fichier (8 chiffres), bloc titre
  (6 chiffres), bloc occurrence (4 chiffres).
- **Composition** (FR-002) :

  - bloc fichier = valeur bijective base 26 des 5 premières lettres
    du nom de fichier source sans extension (0 si aucune lettre) ;
  - bloc titre = valeur bijective base 26 des 4 premières lettres du
    `document.title` (0 si titre absent ou sans lettre) ;
  - bloc occurrence = numéro d'occurrence (0000–9999).

- **Invariants**:

  - chaque bloc est décodable sans perte vers ses lettres d'origine
    (FR-003, aller-retour) ;
  - remplissage par zéros à gauche dans chaque bloc (FR-004) ;
  - encodage insensible à la casse et aux accents (FR-005, FR-011) ;
  - deux documents d'une même exécution ne partagent jamais le bloc
    occurrence (FR-006).

### Compteur d'occurrence

- **Définition**: entier local à l'outil, 0 à 9999, mémorisé comme
  dernier numéro consommé dans `counter.txt` à la racine du projet
  (research.md D1).
- **Attributs**: valeur courante (entier 0–9999) ; fichier hôte
  (`counter.txt`, contenu « NNNN\n »).
- **Cycle de vie** (research.md D4) :

  1. lecture unique au démarrage de la commande :
     absent → 0001 ; illisible/hors bornes → erreur de configuration,
     code de sortie 2, aucun fichier écrit ;
  2. après chaque document produit : incrément, puis persistance
     atomique (fichier temporaire + remplacement) — un numéro
     consommé n'est jamais réutilisé (FR-007) ;
  3. cycle : 0001, 0002, …, 9999, 0000, 0001… (FR-008, modulo
     10000).

- **Contraintes**: partagé par tous les documents et toutes les
  exécutions ; jamais commité (FR-014) ; concurrence non garantie
  v1 (FR-013).

## Entités inchangées (garde-fous)

- **DocumentSource** (`md_chunking/models.py`) : aucun champ ajouté ;
  `path` et `title` existants suffisent aux blocs fichier et titre.
- **Chunk** (`md_chunking/models.py`) : aucun champ ajouté.
- **Index JSON** (`md_chunking/indexer.py`, contrat chunk-json.md de
  la feature 001) : schéma 1.0 strictement inchangé — le nom de
  sortie n'apparaît dans aucun champ (FR-010).
- **Rendu de relecture** (`md_chunking/reviewer.py`, feature 002) :
  contenu inchangé ; seul son nom de fichier change
  (`<nom>_review.md`).
- **Normalisation, découpage, overlap, presets** : non touchés.

## Règles de validation

- `naming.py` est pur : mêmes entrées → mêmes blocs, sans état ni
  aléa (SC-003 côté encodage).
- `counter.py` est le seul module autorisé à lire ou écrire
  `counter.txt` ; aucune autre écriture d'état.
- Le nom de sortie ne doit jamais entrer dans le contenu du JSON ni
  du rendu de relecture (FR-010, vérifié par les tests
  d'intégration).
- Tout test manipulant le compteur l'isole en répertoire temporaire ;
  le `counter.txt` du dépôt n'est jamais touché par la suite de
  tests (research.md D6).
