# Problem Definition: Corpus Markdown sans énumération manuelle

- **Slug**: dossier-entree-md
- **Created**: 2026-10-05
- **Inputs used**: intake.md | research.md

## Problem Statement

L'utilisateur de md_chunking sous Windows/PowerShell — le chemin d'usage
documenté par le README, visant des débutants — ne peut pas traiter en une
commande l'ensemble des documents Markdown d'un dossier : l'outil n'accepte
que des chemins de fichiers, et le contournement par joker shell
(`dossier/*.md`) ne fonctionne pas car PowerShell et cmd.exe n'étendent pas
les motifs pour les commandes natives. Traiter un corpus (cas d'usage réel
du projet : le dossier `Examples/`) impose aujourd'hui d'énumérer les
fichiers un par un ou de maîtriser une syntaxe PowerShell d'énumération,
inaccessible au public cible.

## Affected Users & Stakeholders

- **Users**: débutant sous PowerShell (persona documenté du README) —
  veut découper tous les `.md` d'un dossier en une commande ; doit
  aujourd'hui connaître l'énumération PowerShell ou répéter la commande
  par fichier (source : research.md, preuves Windows glob ;
  README.md:3-21)
- **Users**: propriétaire du dépôt (utilisateur avancé, mono-utilisateur
  v1) — sait contourner mais demande une voie simple et indépendante du
  shell (source : intake.md)
- **Stakeholders**: propriétaire du dépôt — décide seul de l'opportunité,
  arbitre la conformité au principe constitutionnel IV (YAGNI) et le
  périmètre « sans modification substantielle » (source :
  .specify/memory/constitution.md, principe IV ; intake.md)

## Goals

- Un corpus de fichiers Markdown peut être traité en une seule
  commande, sans connaissance du shell au-delà de la commande de base
  documentée
- Le résultat du traitement par corpus est reproductible : mêmes
  fichiers, mêmes options → mêmes sorties et mêmes numéros
  d'occurrence (aligné sur SC-005)
- L'effort d'implémentation reste minimal : aucune refonte de la
  boucle de traitement, du compteur ou du nommage des sorties

## Non-Goals

- Parcours récursif des sous-dossiers (à trancher, mais pas de
  besoin exprimé au-delà d'un dossier simple)
- Surcharge du lot : filtrage, inclusion/exclusion de motifs, tri
  configurable
- Expansion de motifs jokers (`*.md`) en argument — le corpus de
  recherche (contre-précédent img2pdf) pèse contre ; le besoin exprimé
  est le dossier, pas le motif
- Parallélisation du traitement du lot ni garantie anti-doublon
  d'exécutions concurrentes (hors périmètre v1, déjà documenté au
  README)
- Interface autre que la CLI existante

## Success Metrics

- Une commande unique documentée traite les k fichiers `.md` d'un
  dossier et produit 2k sorties (JSON + review, sauf `--no-review`)
  — vérifiable par test d'intégration (baseline : impossible aujourd'hui,
  un dossier échoue au code 2)
- Les k numéros d'occurrence consommés sont croissants et
  reproductibles pour un même ensemble de fichiers — vérifiable par
  test (baseline : inconnu, dépendrait de l'ordre de passage manuel)
- Un dossier contenant n fichiers quelconques dont m `.md` : seuls
  les m `.md` sont traités — vérifiable par test (baseline : non
  applicable, dossier rejeté)
- Le README documente la commande corpus en une étape accessible au
  débutant (baseline : aucune mention corpus)

## Cost of Inaction

Le débutant sous PowerShell continue de traiter fichier par fichier
ou d'apprendre `(Get-ChildItem ...).FullName` — friction permanente sur
le cas d'usage corpus, qui est le cas d'usage réel du projet
(`Examples/`). L'utilisateur avancé garde son contournement shell. Un
outil local mono-utilisateur reste fonctionnel ; le coût est une
ergonomie dégradée sur le public cible, pas une panne. Aucun risque
de données, aucun concurrent à perdre (source : research.md, Market &
Context ; constitution IV pèse en faveur de l'inaction si la
solution devenait lourde).

## Open Questions

- [NEEDS CLARIFICATION: récursivité — surface du dossier seule ou
  sous-dossiers inclus ?]
- [NEEDS CLARIFICATION: dossier vide ou sans `.md` — échec rapide au
  code 2 ou succès silencieux ?]
- [NEEDS CLARIFICATION: mélange dossier + fichiers individuels dans
  une même invocation ?]
- [NEEDS CLARIFICATION: extensions retenues — `.md` seul, ou aussi
  `.markdown` / insensible à la casse sous Windows ?]
- [NEEDS CLARIFICATION: ordre de traitement des fichiers du dossier
  (tri alphabétique imposé pour SC-005 ?)]
- [NEEDS CLARIFICATION: périmètre exact de « sans modifier
  substantiellement » — quelle empreinte maximale acceptable dans
  `parse_args` ?]
