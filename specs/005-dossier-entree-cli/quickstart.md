# Quickstart: Entrée dossier pour la CLI

**Feature**: 005-dossier-entree-cli | **Date**: 2026-10-05

Guide de validation exécutable : chaque scénario prouve un
comportement de la spec de bout en bout. Contrat complet :
[contracts/cli.md](contracts/cli.md) ; résolution et garde-fous :
[data-model.md](data-model.md), décisions : [research.md](research.md).

## Prérequis

- Python 3.11+ et l'outil installé : `.venv\Scripts\md_chunking.exe`
  (ou `python -m md_chunking`) — voir README.
- Un dossier de travail temporaire (ex. `%TEMP%\qs005\`) et un
  `counter.txt` sous contrôle : le supprimer avant chaque scénario
  fait repartir les occurrences à 0001.
- Les commandes sont donnés pour PowerShell (chemin documenté).

## Scénario 1 — Dossier complet en une commande (US-1)

1. Créer `Corpus\` avec `a.md` et `b.md` (quelques lignes de Markdown
   avec un titre de niveau 1 chacune) plus `notes.txt`.
2. Lancer :

   ```powershell
   .venv\Scripts\md_chunking.exe Corpus\ --output %TEMP%\qs005\out
   ```

3. Attendu : code 0 ; deux lignes de succès (une par `.md`) ;
   4 fichiers dans `out\` (2 JSON + 2 reviews au nom à 18 chiffres) ;
   le `.txt` ignoré sans message ; occurrences 0001 puis 0002.

## Scénario 2 — Ordre et mélange dossier + fichier (US-2)

1. Ajouter `z.md` hors du dossier ; dans `Corpus\`, créer `B.md`
   (casse différente de `b.md` supprimé pour le scénario).
2. Lancer :

   ```powershell
   .venv\Scripts\md_chunking.exe Corpus\ z.md --output %TEMP%\qs005\out
   ```

3. Attendu : traitement dans l'ordre `B.md` puis `z.md`,
   occurrences consécutives (0001, 0002) ; inverser les arguments
   inverse l'ordre des occurrences.

## Scénario 3 — Dossier vide ou sans `.md` (FR-005b)

1. Créer `Vide\` (vide) et `Txt\` (contenant seulement `x.txt`).
2. Lancer la commande sur chacun.

3. Attendu : code 0, avertissement « Dossier sans fichier .md :
   {dossier} » sur stderr, aucun fichier écrit, aucune ligne de
   succès ; `counter.txt` non créé.

## Scénario 4 — Entrée introuvable (FR-005)

1. Lancer :

   ```powershell
   .venv\Scripts\md_chunking.exe absent.md --output %TEMP%\qs005\out
   ```

2. Attendu : code 2, message « fichier d'entree introuvable :
   absent.md », aucun fichier écrit.

## Scénario 5 — Doublons et reproductibilité (FR-001, SC-002)

1. Lancer `Corpus\ b.md` (fichier aussi couvert par le dossier).

2. Attendu : `b.md` traité deux fois, deux occurrences consommées,
   deux sorties au nom distinct.
3. Reproductibilité : supprimer `counter.txt`, relancer deux fois la
   même commande sur `Corpus\` ; les occurrences suivent le même
   ordre d'un run à l'autre.

## Scénario 6 — Échec isolé dans un dossier (FR-006, US-3)

1. Dans `Corpus\`, rendre un `.md` illisible (ex. dossier verrouillé
   ou encodage invalide).
2. Lancer la commande sur `Corpus\`.

3. Attendu : code 1, message d'échec nommant le fichier en cause,
   les autres documents traités (une sortie chacun), lot non
   interrompu.

## Vérification rapide après les scénarios

```powershell
Get-ChildItem %TEMP%\qs005\out
```

Chaque document traité doit montrer son JSON et son review au nom à
18 chiffres décodable (contrat 003) ; aucun autre fichier ne doit
apparaître dans `out\`.
