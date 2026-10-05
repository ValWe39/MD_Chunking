# Data Model: Entrée dossier pour la CLI

**Feature**: 005-dossier-entree-cli | **Date**: 2026-10-05

La feature n'introduit aucune entité persistante : compteur
d'occurrence, nom de sortie, document et chunk restent inchangés
(data-model de la feature 001, état `counter.txt` de la feature 003).
Elle ajoute une entité éphémère de résolution d'entrée.

## Entités

### Argument d'entrée (éphémère)

Valeur d'un argument positionnel de la CLI, discriminée au moment de
la validation de configuration (D1).

| Attribut | Valeur |
| -------- | ------ |
| chemin | `Path` fourni par l'utilisateur |
| type | fichier \| dossier \| introuvable \| ni-fichier-ni-dossier |

Garde-fous :

- introuvable ou ni-fichier-ni-dossier → échec rapide au code 2,
  message « fichier d'entree introuvable : {chemin} », aucun fichier
  écrit (FR-005, D5) ;
- dossier → résolu en documents (voir ci-dessous) ; fichier →
  conservé tel quel.

### Document résolu (éphémère)

Un `Path` de fichier `.md` prêt à être traité, produit par la
résolution (D1) ; il rejoint le lot sans distinction avec un fichier
passé individuellement.

| Attribut | Valeur |
| -------- | ------ |
| chemin | `Path` d'un fichier `.md` |
| provenance | fichier individuel \| contenu d'un dossier |

Garde-fous :

- filtre : suffixe `.md` insensible à la casse, autres fichiers
  ignorés sans avertissement (FR-002, D2) ;
- ordre : arguments dans l'ordre de la ligne de commande, chaque
  dossier développé à sa position, fichiers d'un dossier triés par
  nom casse neutre (FR-003, FR-004, D3) ;
- doublons : conservés à chaque occurrence, un numéro d'occurrence
  consommé par passage (FR-001, D6) ;
- dossier sans `.md` : aucun document produit, avertissement émis,
  code 0 sans écriture (FR-005b, D4) ;
- surface seule : `iterdir` filtré sur `is_file()`, aucun sous-dossier
  ni motif joker (FR-008, D7).

## Transitions d'état

Aucune : la résolution est une fonction pure (entrées → liste de
chemins + avertissements), sans écriture ; le premier effet de bord
reste la persistance du compteur par document traité (feature 003,
inchangée).

## Impact sur les entités existantes

- Compteur d'occurrence : inchangé ; consommé uniquement si la
  résolution produit au moins un document (D4).
- Nom de sortie (18 chiffres) : inchangé ; un dossier de k documents
  consomme k occurrences consécutives.
- DocumentSource, Chunk, index JSON, review : inchangés
  (FR-006, FR-007).
