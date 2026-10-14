# Quickstart: Contexte utilisateur et auto-identification dans la sortie JSON

**Feature**: 006-add-context | **Date**: 2026-10-14

Guide de validation exécutable : chaque scénario prouve un
comportement de la spec de bout en bout, sur des copies des
exemples fournis dans `Examples/Extension/` (jamais les
originaux). Contrats complets : [contracts/cli.md](contracts/cli.md)
et [contracts/chunk-json.md](contracts/chunk-json.md) ; résolution
et garde-fous : [data-model.md](data-model.md) ; décisions :
[research.md](research.md).

## Prérequis

- Python 3.11+ et l'outil installé : `.venv\Scripts\md_chunking.exe`
  (ou `python -m md_chunking`) — voir README.
- Un dossier de travail temporaire (ex. `%TEMP%\qs006\`) et un
  `counter.txt` sous contrôle : le supprimer avant chaque
  scénario fait repartir les occurrences à 0001.
- Copier les exemples fournis (jamais les originaux) :

  ```powershell
  New-Item -ItemType Directory -Force $env:TEMP\qs006
  Copy-Item -Recurse Examples\Extension $env:TEMP\qs006\Ext
  ```

- Les commandes sont données pour PowerShell (chemin documenté).

## Scénario 1 — Dossier couple avec contexte (US-1, FR-002)

1. Lancer sur la copie du dossier `Couple` (1 .md + 1 .json) :

   ```powershell
   Remove-Item counter.txt -ErrorAction SilentlyContinue
   .venv\Scripts\md_chunking.exe $env:TEMP\qs006\Ext\Couple `
     --add-context --output $env:TEMP\qs006\out1
   ```

2. Attendu : code 0, une ligne de succès ; un JSON dans `out1\` ;
   à son lecture : `document.chunkingid` égal au nom du fichier
   sans extension ; `document.context` contenant les sept champs
   du `.json` à l'identique, `Référence` vide comprise.

## Scénario 2 — Corpus en sous-dossiers (US-2, FR-003)

1. Lancer sur la copie de `Sous-dossiers` (3 sous-dossiers, chacun
   un couple) :

   ```powershell
   Remove-Item counter.txt -ErrorAction SilentlyContinue
   .venv\Scripts\md_chunking.exe $env:TEMP\qs006\Ext\Sous-dossiers `
     --add-context --output $env:TEMP\qs006\out2
   ```

2. Attendu : code 0, trois lignes de succès, trois JSON — chacun
   embarque le contexte de son propre sous-dossier et son
   `chunkingid` ; occurrences 0001, 0002, 0003 dans l'ordre des
   sous-dossiers triés ; sans `--add-context`, la même commande
   produirait l'avertissement « Dossier sans fichier .md » et le
   code 0 (comportement 005 inchangé).

## Scénario 3 — Lot mélangé : couples et orphelins (US-3, FR-005)

1. Lancer sur la copie de `Multi-coupes mix` (3 couples + 2 .md
   orphelins) :

   ```powershell
   Remove-Item counter.txt -ErrorAction SilentlyContinue
   .venv\Scripts\md_chunking.exe "$env:TEMP\qs006\Ext\Multi-coupes mix" `
     --add-context --output $env:TEMP\qs006\out3
   ```

2. Attendu : code 0, cinq lignes de succès ; trois JSON avec
   `document.context` (couples reconnus par préfixe normalisé :
   `premiere`, `an_rappo`, `ecalle_o`), deux JSON sans contexte
   (`IFRI.md`, `Grand_Continent_article.md`) ne différant du
   comportement classique que par `chunkingid` ; aucun couple mal
   apparié.

## Scénario 4 — Sans l'option : aucune régression (FR-001, SC-002)

1. Lancer la même entrée sans `--add-context` (sortie séparée) :

   ```powershell
   .venv\Scripts\md_chunking.exe $env:TEMP\qs006\Ext\Couple `
     --output $env:TEMP\qs006\out4
   ```

2. Attendu : code 0, aucune lecture de `.json`, aucune clé
   `document.context` ; chaque fichier de sortie est identique au
   comportement antérieur au seul champ `chunkingid` près.

## Scénario 5 — Contexte invalide (FR-004, FR-008)

1. Dans une copie de `Couple`, renommer une clé du `.json` (ex.
   `Editeur` → `Publisher`).
2. Relancer le scénario 1 (sortie `out5`).

3. Attendu : code 0, avertissement
   « .json de contexte invalide : {chemin} » sur stderr, document
   traité par le processus classique (`chunkingid` présent, aucun
   `document.context`).

## Scénario 6 — .json orphelin et ambiguïté (FR-005, FR-008)

1. Dans une copie de `Multi-couples`, dupliquer un `.json` de
   contexte sous un nom sans correspondance (ex.
   `zzz-0099.json`) ; dans une autre copie, dupliquer un `.json`
   apparié (deux candidats pour le même .md).
2. Relancer avec `--add-context` sur chaque copie.

3. Attendu : avertissement « .json de contexte orphelin » pour le
   premier, « Appariement ambigu pour {md} » et traitement
   classique pour le second ; dans les deux cas le lot va à son
   terme et le code de sortie reste 0.

## Vérification rapide après les scénarios

```powershell
Get-ChildItem $env:TEMP\qs006\out1, $env:TEMP\qs006\out2,
  $env:TEMP\qs006\out3
```

Chaque document traité doit montrer son JSON au nom à 18 chiffres
décodable (contrat 003) et son review ; aucun `.json` de contexte
copié ne doit apparaître dans les sorties (FR-010) ; chaque
`chunkingid` doit être égal au nom du fichier qui le contient.
