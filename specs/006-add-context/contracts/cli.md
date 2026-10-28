# Contrat CLI : option --add-context

**Feature**: 006-add-context | **Date**: 2026-10-14

Évolution de la surface CLI décrite par le contrat
`specs/001-md-chunking/contracts/cli.md` (interface unique,
constitution IV), amendé par les contrats des features 003
(nommage), 004 (`--tokencpte`) et 005 (entrée dossier). Le présent
contrat documente les seuls changements ; tout le reste des
contrats précédents reste en vigueur.

## Invocation

```text
python -m md_chunking [OPTIONS] ENTREE [ENTREE ...] [--add-context]
```

`--add-context` : option booléenne, désactivée par défaut.

- **Sans l'option** : comportement des contrats précédents
  intégralement inchangé (résolution de surface de la feature 005,
  `.json` ignorés comme tout fichier non `.md`). La seule
  différence de sortie est le champ `document.chunkingid`,
  émis dans tous les cas (contrat chunk-json.md).
- **Avec l'option** : chaque argument dossier est parcouru
  récursivement à toute profondeur ; un argument fichier est
  traité comme aujourd'hui, jamais apparié.

## Résolution avec --add-context

À chaque niveau d'un dossier, ne comptent que les fichiers
directement présents (le contenu d'un sous-dossier ne compte
jamais dans le niveau parent) :

1. **Niveau couple** — exactement 1 `.md` et 1 `.json` : le
   `.json` est le contexte du `.md`, quel que soit son nom, après
   validation du format attendu (les sept clés exactes — voir
   contrat chunk-json.md). Les autres fichiers du niveau sont
   ignorés.
2. **Niveau mélangé** — plusieurs `.md` ou plusieurs `.json` :
   appariement par **extension progressive par paliers**
   (amendement feature 007) : à chaque palier (8, 12, 16, …
   jusqu'à la longueur maximale des clés normalisées du
   niveau), chaque `.md` non résolu est apparié à un `.json` si
   leurs noms, après normalisation (accents supprimés,
   minuscules, espaces convertis en `_`, seuls `a-z 0-9 _`
   conservés), tronqués à ce palier coïncident, et si cette
   correspondance est unique des deux côtés ; chaque `.md`
   avance indépendamment jusqu'à résolution ou longueur
   maximale ; à la longueur maximale, un `.md` avec plusieurs
   candidats ou des concurrents émet « Appariement ambigu
   pour {md} » (un `.md` sans candidat reste silencieux).
3. **Descente** — chaque sous-dossier est parcouru de la même
   façon (profondeur d'abord), même si le niveau courant est vide
   de `.md`.

Ordre du lot : arguments dans l'ordre de la ligne de commande ;
à chaque niveau, `.md` du niveau triés casse neutre, puis
sous-dossiers triés casse neutre — les numéros d'occurrence restent
reproductibles à contenu égal.

## Format de contexte

Un `.json` de contexte est valide s'il est lisible et si ses clés
sont exactement : `Typologie`, `Auteur(s)`, `Titre`, `Editeur`,
`Date`, `Référence`, `Citation` — ni manquante, ni supplémentaire.
Les valeurs ne sont pas contraintes (chaîne ou liste, vide admis).
Tout écart (illisible, non-objet, clés en trop ou manquantes)
invalide le fichier : avertissement, aucun contexte embarqué,
traitement classique.

## Codes de sortie

Inchangés (contrat 005) : 0 succès (y compris un dossier dont
aucun niveau ne contient de `.md`, avec avertissements), 1 échec
d'exécution (le lot continue), 2 configuration invalide (chemin
introuvable, compteur illisible si des documents sont résolus).
Aucun état de contexte ne change le code final.

## Messages console

- Succès par document : inchangé (contrat 003).

  ```text
  {fichier} : {n} chunks -> {output}/{nom 18 chiffres}.json
  ```

- Avertissements de contexte (stderr, un par fichier concerné,
  traitement continué) :

  ```text
  .json de contexte invalide : {chemin}
  .json de contexte orphelin : {chemin}
  Appariement ambigu pour {md}
  Dossier sans fichier .md : {dossier}
  ```

  Le dernier message est celui de la feature 005, réutilisé pour
  tout niveau sans `.md` du parcours récursif.

## État local

Inchangé (contrat 005) : `counter.txt` à la racine du projet,
consommé uniquement si la résolution produit au moins un
document. Le `.json` de contexte est lu et embarqué dans la
sortie ; il n'est jamais recopié, renommé ni déplacé.

## Exemples

```text
python -m md_chunking Corpus/ --add-context
python -m md_chunking Corpus/ article.md --add-context
python -m md_chunking Examples/Extension/Couple --add-context
python -m md_chunking Corpus/                  # inchangé, sans contexte
```
