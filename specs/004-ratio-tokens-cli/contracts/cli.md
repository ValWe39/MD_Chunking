# Contrat CLI : option --tokencpte (ratio caracteres/tokens)

**Feature**: specs/004-ratio-tokens-cli | **Date**: 2026-10-05

Evolution de la surface CLI decrite par le contrat
`specs/003-nommage-sorties-18-chiffres/contracts/cli.md` (lui-meme
supersedeur du contrat 001, constitution IV). Le present contrat
documente les seuls changements ; tout le reste du contrat 003 reste
en vigueur.

## Options

| Option | Type | Defaut | Regle (FR) |
| ------ | ------ | -------- | ------------ |
| --tokencpte | decimal (point) | 3.5 | NOUVELLE (FR-001, FR-002) |

- `--tokencpte <ratio>` : ratio caracteres→tokens de l'estimation du
  rapport de relecture, applique a tous les documents de l'execution.
- Bornes : `0 < ratio <= 10` ; toute valeur hors bornes echoue avant
  toute lecture de compteur et toute ecriture (FR-003).
- Valeur nulle, negative ou non numerique (y compris virgule decimale
  `3,5`) : echec au parsing, code de sortie 2, comportement identique
  a `--min abc` (surface standard existante).
- Les options `--min`, `--max`, `--overlap`, `--guillemets`,
  `--typologie`, `--output` et `--no-review` sont inchangees.
- Avec `--no-review`, l'option est acceptee et sans effet : aucun
  rapport n'est produit, aucune estimation calculee (FR-009).

## Codes de sortie

| Code | Signification |
| ------ | --------------- |
| 0 | succes — tous les documents traites |
| 1 | echec d'execution — certains documents en echec |
| 2 | configuration invalide — compteur illisible ou ratio invalide |

Nouveau cas de code 2 : ratio hors bornes ]0 ; 10] — echec rapide,
aucun fichier ecrit (FR-003).

## Messages console

- Erreur de bornes (dans le bloc standard `Erreur de configuration :`) :

  ```text
  --tokencpte doit etre > 0 et <= 10 (recu : {valeur})
  ```

- Valeur mal formee (parsing argparse standard, code 2) :

  ```text
  invalid float value: '3,5'
  ```

- Le message de succes par document est inchange (contrat 003).

## Sorties et etat local

- Inchanges (contrats 001 et 003) : index JSON schema 1.0, noms de
  fichiers a 18 chiffres, ecriture a plat dans `--output`,
  `counter.txt`.
- Le ratio n'est persiste nulle part ; il n'apparait qu'en en-tete du
  rapport de relecture (contrat [review-render.md](review-render.md)).
