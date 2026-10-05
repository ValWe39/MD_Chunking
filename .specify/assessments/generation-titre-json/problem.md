# Problem Definition: Identifier les fichiers JSON et review produits

- **Slug**: generation-titre-json
- **Created**: 2026-10-05
- **Inputs used**: intake.md, research.md

## Problem Statement

Tous les documents JSON produits par l'outil portent le même nom de
fichier (`chunks.json`, et `review.md` pour la relecture), chacun isolé
dans un sous-dossier numéroté (`0001`, `0002`…) qui n'encode rien du
document traité. Dès qu'un fichier de sortie est déplacé, copié ou
manipulé hors de son sous-dossier, il n'est plus identifiable ni
rattachable au markdown source ou au titre du document qui l'a produit.
L'utilisateur a arbitré : les sous-dossiers disparaissent, les fichiers
sont écrits directement dans `output/` — le nom de fichier devient donc
le seul identifiant.

## Affected Users & Stakeholders

- **Users**: le propriétaire du projet, unique utilisateur de l'outil —
  il réutilise les JSON de chunks en aval (relecture, envoi vers d'autres
  outils) et ne peut pas distinguer deux `chunks.json` provenant de
  documents différents. — [source: intake.md, session du 2026-10-05]
- **Stakeholders**: le même propriétaire, décideur et mainteneur —
  arbitrages déjà rendus (intake.md, section Arbitrage) et
  non-régressions à préserver (schéma JSON 1.0, déterminisme du
  contenu). — [source: specs/002, constitution]
- **Consommateurs en aval des JSON** (outils tiers recevant les chunks) :
  [RÉSOLU par arbitrage : aucun consommateur en aval connu n'impose de
  contrainte de nommage — l'utilisateur est l'unique consommateur.]

## Goals

- Chaque exécution produit des fichiers de sortie dont le nom identifie
  le document source et le distingue de tout autre, sans modifier le
  contenu des fichiers.
- Le nom de fichier reste décodable : à partir du nom seul, on peut
  retrouver les éléments d'origine (nom de fichier source, titre du
  document, ordre de production).
- Le comportement reste l'action par défaut de l'outil, sans option ni
  commande spécifique (arbitrage intake).
- Les non-régressions acquises sont préservées : contenu du JSON
  conforme au schéma 1.0, déterminisme du contenu d'une exécution à
  l'autre, fonctionnement hors-ligne. — [source:
  specs/002-compteur-tokens-chunks, FR-T07 ; research.md]

## Non-Goals

- Aucun changement du contenu des sorties : pas de nouveau champ dans le
  JSON, pas de modification du schéma 1.0 ni du rendu de relecture.
  — [arbitrage intake 2026-10-05]
- Pas d'option CLI ni de mode activable : le nommage s'applique par
  défaut. — [arbitrage intake 2026-10-05]
- Pas de garantie d'unicité absolue : le format arbitré (18 chiffres)
  peut produire des collisions après remise à zéro du numéro
  d'occurrence ; une unicité cryptographique (UUID, hash complet) est
  explicitement hors périmètre. — [research.md, Evidence Against]
- Pas d'état distant ni de synchronisation : le numéro d'occurrence
  reste un compteur local (constitution II).
- Hors périmètre : toute autre évolution du pipeline (découpage,
  overlap, tokens — feature 002).

## Success Metrics

- 100 % des fichiers produits par une exécution portent le nom arbitré
  à 18 chiffres (mesurable sur la suite de tests et sur le corpus
  réel). (baseline: 0 %, tous nommés `chunks.json`)
- Le nom est décodable : un test décode chaque bloc et retrouve les
  lettres du nom de fichier source et du titre du document.
  (baseline: aucune information dans le nom)
- Le contenu du JSON d'un même document est identique d'une exécution à
  l'autre, seul le nom de fichier diffère (le numéro d'occurrence
  avance). (baseline: SC-005 de la feature 001 — critère qualitatif
  existant, à adapter au nommage)
- Aucune régression des tests existants (features 001 et 002).
  (baseline: suite verte à ce jour)

## Cost of Inaction

Les sorties restent des `chunks.json` indiscernables : tout usage en aval
exige de conserver l'arborescence des sous-dossiers pour savoir d'où
vient un fichier ; deux JSON copiés au même endroit s'écrasent ou se
confondent ; le coût de rattachement (manuel) est payé à chaque
réutilisation. — [source: research.md, Market & Context]

## Open Questions

- [NEEDS CLARIFICATION: casse — « A » et « a » sont-ils convertis
  identiquement ? Le corpus réel contient les deux (« CONTEXTE », « À LA
  DÉMOCRATIE »).]
- [NEEDS CLARIFICATION: lettres accentées — ramenées à la lettre de
  base (É => E) ou ignorées comme les symboles ?]
- [NEEDS CLARIFICATION: emplacement exact et format du fichier de
  compteur local (« à la racine de l'outil »), politique git (ignoré ?),
  et comportement si le fichier est absent, corrompu ou supprimé]
- [NEEDS CLARIFICATION: après 9999, le compteur repart à 0000 ou à
  0001 ? Compteur global à l'outil ou par document ?]
- [NEEDS CLARIFICATION: comportement si deux exécutions de l'outil
  tournent en parallèle (concurrence sur le compteur)]
- [RÉSOLU par arbitrage : plus de sous-dossier par document — écriture
  directe dans `output/` ; l'option `--naming` devient sans objet]
- [NEEDS CLARIFICATION: l'option CLI `--naming` existante
  (`numbered`|`title`, `md_chunking/cli.py`) devient inutile avec la
  disparition des sous-dossiers : supprimée, ignorée silencieusement, ou
  conservée pour compatibilité ? Supprimer une option publique est un
  changement de comportement pour les scripts existants]
