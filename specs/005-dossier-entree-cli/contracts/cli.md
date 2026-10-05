# Contrat CLI : entrée dossier

**Feature**: 005-dossier-entree-cli | **Date**: 2026-10-05

Évolution de la surface CLI décrite par le contrat
`specs/001-md-chunking/contracts/cli.md` (interface unique,
constitution IV), amendé par `specs/003-nommage-sorties-18-chiffres/
contracts/cli.md` et `specs/004-ratio-tokens-cli/contracts/cli.md`.
Le présent contrat documente les seuls changements ; tout le reste
des contrats précédents reste en vigueur.

## Invocation

```text
python -m md_chunking [OPTIONS] ENTREE [ENTREE ...]
```

`ENTREE` : un ou plusieurs chemins, chacun étant un fichier Markdown
ou un dossier.

- Fichier : traité comme aujourd'hui (contrat 001).
- Dossier : résolu en la liste des fichiers `.md` de sa surface
  (suffixe `.md` insensible à la casse, sous-dossiers exclus), triés
  par nom casse neutre, insérés à la position de l'argument
  (FR-001 à FR-004).

Règles de résolution :

- Aucune déduplication : un même fichier apparaissant plusieurs fois
  dans la résolution est traité à chaque occurrence, consommant un
  numéro d'occurrence par passage (FR-001).
- Ordre total du lot : arguments dans l'ordre de la ligne de commande,
  fichiers d'un dossier triés entre eux (FR-003, FR-004).
- Aucune récursivité, aucun motif joker (FR-008).

## Codes de sortie

| Code | Signification |
| ---- | ------------- |
| 0 | succès — tous les documents traités |
| 1 | échec d'exécution — le lot continue |
| 2 | configuration invalide — rien n'est écrit |

Précisions :

- Nouveau cas de code 0 : un dossier existant vide ou sans `.md`
  n'échoue pas ; la commande s'achève sans écriture, compteur non
  consulté (FR-005b). Il en va de même d'une invocation dont tous les
  arguments sont de tels dossiers.
- Nouveau cas de code 2 : un chemin d'entrée introuvable ou
  ni-fichier-ni-dossier (FR-005). Le cas existant `counter.txt`
  illisible (contrat 003) ne s'applique que si la résolution produit
  au moins un document.

## Messages console

- Succès par document : inchangé (contrat 003).

  ```text
  {fichier} : {n} chunks -> {output}/{nom 18 chiffres}.json
  ```

- Avertissement dossier sans `.md` (stderr, un par dossier concerné,
  traitement continué) :

  ```text
  Dossier sans fichier .md : {dossier}
  ```

- Échec d'entrée (stderr, échec rapide avant toute écriture) :
  message existant du contrat 001 inchangé.

  ```text
  Erreur de configuration :
  fichier d'entree introuvable : {chemin}
  ```

## Exemples

```text
python -m md_chunking Notes/                     # tout le dossier
python -m md_chunking Notes/ article.md          # dossier puis fichier
python -m md_chunking Notes/ Notes/              # chaque .md deux fois
python -m md_chunking Vide/                      # code 0 + avertissement
python -m md_chunking absent.md                   # code 2, rien ecrit
```

## État local

Inchangé (contrat 003) : `counter.txt` à la racine du projet,
consommé uniquement si la résolution produit au moins un document.
