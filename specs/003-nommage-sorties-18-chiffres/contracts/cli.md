# Contrat CLI : nommage des sorties (18 chiffres)

**Feature**: specs/003-nommage-sorties-18-chiffres | **Date**: 2026-10-05

Évolution de la surface CLI décrite par le contrat
`specs/001-md-chunking/contracts/cli.md` (interface unique du projet,
constitution IV). Le présent contrat documente les seuls changements ;
tout le reste du contrat 001 reste en vigueur.

## Options

| Option | Type | Défaut | Règle (FR) |
| ------ | ------ | -------- | ------------ |
| --naming | — | — | SUPPRIMÉE (FR-012) |

- `--naming` disparaît : un appel qui la fournit échoue avec le
  message argparse standard des options inconnues, code de sortie 2.
- Les options `--min`, `--max`, `--overlap`, `--typologie`, `--output`
  et `--no-review` sont inchangées.

## Sorties

- Plus de sous-dossier par document : tous les fichiers sont écrits
  directement dans `--output` (FR-001).
- Chaque document produit `<18 chiffres>.json` et, sauf `--no-review`,
  `<18 chiffres>_review.md` — format détaillé dans
  [output-naming.md](output-naming.md).
- Le dossier de sortie est créé s'il est absent (inchangé, path
  isolation).

## Codes de sortie

| Code | Signification |
| ------ | --------------- |
| 0 | succès — tous les documents traités |
| 1 | échec d'exécution — certains documents en échec |
| 2 | configuration invalide — y compris `counter.txt` illisible |

Nouveau cas de code 2 : compteur d'occurrence présent mais illisible
(non numérique ou hors 0–9999) — échec rapide, aucun fichier écrit
(FR-009, research.md D4).

## Messages console

- Succès (par document) :

  ```text
  {fichier} : {n} chunks -> {output}/{nom 18 chiffres}.json
  ```

- Échec compteur illisible (avant tout traitement) :

  ```text
  Erreur de configuration :
  counter.txt illisible à la racine du projet : {détail}
  ```

## État local

- `counter.txt`, à la racine du projet, hors contrôle de version
  (FR-014) : dernier numéro d'occurrence consommé, uniquement ce
  numéro.
- Absent → le premier document produit porte `0001` (FR-009).
- Supprimé à la main → retour à `0001` au prochain usage (Data
  retention : l'utilisateur contrôle l'état).
