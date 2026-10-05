# Idea Intake: Usage de la CLI sur un dossier de fichiers Markdown

- **Slug**: dossier-entree-md
- **Created**: 2026-10-05
- **Source**: conversation utilisateur (pasted text), suite à une
  investigation en lecture seule du dépôt courant
- **Type**: improvement

## Idea (as captured)

> « Est-il possible de prévoir l'usage sur un dossier de md ? sans
> avoir à modifier substantivement l'outil actuel ? »

Contexte de la demande : l'investigation précédente a établi que la CLI
(`python -m md_chunking`) accepte plusieurs fichiers en une invocation
(`nargs="+"`, boucle sur `args.fichiers` dans `md_chunking/cli.py`), mais
qu'un dossier passé en argument est rejeté dès la validation de
configuration (test `is_file()` en `md_chunking/cli.py:96-98` -> message
« fichier d'entree introuvable », code de sortie 2). Aucune logique de
parcours de répertoire (`is_dir`/`glob`/`iterdir`) n'existe dans le
paquet. Le contournement actuel est l'expansion par le shell
(`python -m md_chunking dossier/*.md`), dépendante du shell utilisé.

## Restated

Étendre l'entrée de la CLI pour accepter un dossier contenant des fichiers
Markdown et traiter tous les `.md` qu'il contient, avec la contrainte
explicite que l'outil actuel ne soit pas substantiellement modifié.

## Origin & Context

- **Raised by**: utilisateur (propriétaire du dépôt), le 2026-10-05
- **Trigger**: investigation en lecture seule de la session du même jour
  confirmant qu'un dossier est aujourd'hui refusé (code de sortie 2)
  alors que l'invocation multi-fichiers est déjà supportée ; l'utilisateur
  cherche à éviter une refonte lourde de `md_chunking/cli.py`

## First-Glance Unknowns

- [NEEDS CLARIFICATION: parcourt-on uniquement le dossier en surface ou
  aussi récursivement dans les sous-dossiers ?]
- [NEEDS CLARIFICATION: que faire d'un dossier vide, ou sans aucun
  `.md` (échec rapide au code 2, succès silencieux, autre) ?]
- [NEEDS CLARIFICATION: un dossier peut-il être mélangé à des fichiers
  individuels dans la même invocation (ex. `python -m md_chunking
  dossier/ note.md`) ?]
- [NEEDS CLARIFICATION: l'exigence « sans modifier substantiellement »
  exclut-elle toute écriture de code, ou seulement une refonte (ex. un
  tri-glissé minimal dans `parse_args` serait-il acceptable) ?]
- [NEEDS CLARIFICATION: l'option documentée du shell glob
  (`dossier/*.md`) suffit-elle comme réponse, ou la résolution
  doit-elle être interne à l'outil pour être indépendante du shell
  (notamment cmd.exe sous Windows) ?]
- [NEEDS CLARIFICATION: ordre de traitement des fichiers d'un dossier
  (tri alphabétique, ordre du système de fichiers) et interaction avec
  le compteur d'occurrence incrémenté par document]
- [NEEDS CLARIFICATION: faut-il filtrer uniquement l'extension `.md`
  ou aussi `.markdown` ou une casse quelconque (`.MD` sous Windows) ?]
