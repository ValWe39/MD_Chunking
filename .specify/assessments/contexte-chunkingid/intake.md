# Idea Intake: Champs context et chunkingid dans le JSON de sortie

- **Slug**: contexte-chunkingid
- **Created**: 2026-10-14
- **Source**: pasted text (codebase pointer: Examples/Extension/)
- **Type**: improvement

## Idea (as captured)

> Je souhaite ajouter deux sous-champs au champ "document" dans le
> .json de sortie, construits de la façon suivante :
>
> ## 1. "chunkingid"
>
> Ce champ indique le titre du .json de sortie (`<titre>`.json)
>
> ## 2. "context"
>
> Ce champ contient exactement les champs (y compris les vides) d'un
> fichier complémentaire au format .json ajouté par l'utilisateur
> par la commande optionnelle "--add-context".
>
> Ce .json contient les champs suivants :
>
> "Typologie"
> "Auteur(s)"
> "Titre"
> "Editeur"
> "Date"
> "Référence"
> "Citation"
>
> ### multi documents entrée
>
> Cette nouvelle utilisation optionnelle de l'outil doit permettre
> de fonctionner également en multi entrée dans les cas suivants (si
> l'utilisateur ajoute la commande optionnelle après sa saisie) :
>
> - Saisie en entrée par l'utilisateur d'un dossier contenant 1 .md
>   entrée classique et 1 .json entrée "context"
> - Saisie en entrée par l'utilisateur d'un dossier contenant des
>   sous-dossiers organisés comme le point 1
> - Saisie en entrée par l'utilisateur d'un dossier contenant des
>   .md entrée classique et des .json entrée "context"
>
> => dans ce cas, seuls les couples reliés par la règle suivante
> seront exécutés selon le nouveau processus, les autres seront
> traités par le processus classique.
>
> #### Règle lien couple
>
> Les 8 premiers caractères du titre du .json "context"
> (`<titre>`.json) doivent correspondre aux 8 premiers caractères du
> .md entrée classique (hors espaces, accents et symboles).
>
> ### Exemples
>
> Tu trouveras dans le dossier "\Examples\Extension", 3 exemples
> pour développer et tester la commande optionnelle. *utilise-les* !

## Restated

Ajouter à l'objet `document` du JSON de sortie deux sous-champs
optionnels : `chunkingid` (titre du fichier .json de sortie) et
`context` (copie exacte des champs d'un .json de contexte fourni par
l'utilisateur, y compris les champs vides), activés par une commande
optionnelle `--add-context` qui doit fonctionner aussi en
multi-entrées, où chaque .md est apparié à un .json de contexte par
correspondance des 8 premiers caractères du nom de fichier (hors
espaces, accents et symboles).

## Origin & Context

- **Raised by**: l'utilisateur du dépôt MD_Chunking
  [NEEDS CLARIFICATION: personne/rôle précis]
- **Trigger**: besoin d'embarquer les métadonnées descriptives d'un
  document (typologie, auteurs, éditeur, date, référence, citation)
  directement dans le .json de sortie produit par le chunking, pour
  traçabilité et enrichissement en aval. Fait suite aux specs
  existantes sur l'entrée dossier (001, 005) et le nommage des
  sorties (003, assessment `generation-titre-json`).

## Evidence available in repo

- **Exemples de test** : `Examples/Extension/` contient 4 dossiers
  couvrant les cas d'usage annoncés :
  - `Couple/` : `premiere-0034.json` +
    `premiere-seance-du-v-nettoye.md` (cas simple 1 couple)
  - `Sous-dossiers/` : 3 sous-dossiers (`1/`, `2/`, `3/`), chacun
    un couple .md + .json de contexte
  - `Multi-couples/` : 3 couples .md + .json à la racine
  - `Multi-coupes mix/` : 3 couples + 2 .md orphelins
    (`Grand_Continent_article.md`, `IFRI.md`) à traiter par le
    processus classique
- **Structure du .json de contexte** (confirmée sur
  `Examples/Extension/Couple/premiere-0034.json`) : `Typologie`
  (str), `Auteur(s)` (liste), `Titre` (str), `Editeur` (str),
  `Date` (str), `Référence` (str vide dans l'exemple), `Citation`
  (str)
- **Schéma de sortie actuel** :
  `specs/001-md-chunking/contracts/chunk-json.md` (schéma 1.0) et
  `md_chunking/indexer.py` (build_index) — la cible est le bloc
  `document`
- **Nommage des sorties actuel** : spec 003
  (`nommage-sorties-18-chiffres`) — interaction à clarifier avec
  `chunkingid`

## First-Glance Unknowns

- [NEEDS CLARIFICATION: `chunkingid` — doit-il contenir le titre
  avec ou sans extension `.json` ? Le titre du .json de sortie
  est-il celui déjà produit par le nommage actuel (spec 003) ou un
  nouveau titre ?]
- [NEEDS CLARIFICATION: la règle des 8 premiers caractères « hors
  espaces, accents et symboles » — quelle normalisation exacte
  (minuscules ? traits de soulignement comme dans
  `AN_Rappo-0032.json` vs `AN_Rapport.md` ?) et que se passe-t-il
  en cas d'égalité partielle ou d'un .json apparié à plusieurs
  .md ?]
- [NEEDS CLARIFICATION: `--add-context` s'applique-t-il aussi à
  une entrée .md unique en fichier direct, ou uniquement aux
  entrées dossier ?]
- [NEEDS CLARIFICATION: faut-il incrémenter `schema_version`
  (1.0 → 1.1) puisque le schéma du contrat chunk-json.md change
  (FR-013) ?]
- [NEEDS CLARIFICATION: en sortie multi-couples, chaque document
  conserve-t-il son propre sous-dossier de sortie avec son propre
  chunks.json, et le .json de contexte est-il copié/conservé en
  sortie ?]
- [NEEDS CLARIFICATION: si un .md apparié est absent mais qu'un
  .json de contexte existe, le .json est-il ignoré silencieusement
  ou signalé ?]
