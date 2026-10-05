# Idea Research: Usage de la CLI sur un dossier de fichiers Markdown

- **Slug**: dossier-entree-md
- **Created**: 2026-10-05
- **Evidence confidence (overall)**: medium

## Users & Demand

- Le public cible documenté est un débutant sous PowerShell : le README
  ouvre sur « Pour débutants (mode d'emploi rapide) » avec une commande
  PowerShell à un seul fichier — [source: README.md:3-21] (confidence: high)
- Le corpus réel de l'utilisateur est un dossier de fichiers Markdown :
  le README mentionne « les documents du dossier `Examples/` » comme corpus
  de validation — la situation « traiter tout un dossier » est donc
  observée dans l'usage du projet, pas seulement souhaitée —
  [source: README.md:134-136] (confidence: high)
- La demande émane du propriétaire unique du dépôt (outil local,
  mono-utilisateur, v1) — [ASSUMPTION : aucun autre utilisateur connu ;
  pas de signal externe de demande] (confidence: medium)

## Prior Art

- **Interne** : la boucle de traitement (`for fichier in args.fichiers`)
  et le compteur d'occurrence incrémenté par document existent déjà ;
  seule la validation d'entrée bloque les dossiers (`is_file()` en
  `md_chunking/cli.py:96-98`). Le pipeline aval (normalizer, splitter,
  indexer) est agnostique à la provenance des chemins —
  [source: md_chunking/cli.py:33-35, 96-98, 128-160] (confidence: high)
- **Interne** : le contrat CLI 001 définit `FICHIER` comme « un ou
  plusieurs chemins de fichiers Markdown » ; accepter un dossier serait
  un changement de surface CLI, avec précédent : la feature 003 a déjà
  modifié ce contrat (suppression de `--naming`, sortie à plat) —
  [source: specs/001-md-chunking/contracts/cli.md:9-13 ;
  specs/003-nommage-sorties-18-chiffres/contracts/cli.md:1-15]
  (confidence: high)
- **Externe** : `cloc` accepte indifféremment fichiers et répertoires en
  entrée et parcourt les répertoires — précédent direct pour un outil
  de comptage local — [source: pages de manuel cloc, via snippets de
  recherche, aucune page fetchée : linux.die.net/man/1/cloc,
  man.archlinux.org/man/extra/cloc/cloc.1] (confidence: medium)
- **Externe** : `pandoc` n'accepte que des fichiers en entrée (pas de
  répertoire) ; ses utilisateurs passent par des jokers shell —
  précédent d'un outil répandu qui a choisi de ne pas faire de
  parcours de dossier — [source: pandoc.org/MANUAL.html, via snippet
  de recherche, page non fetchée] (confidence: medium)
- **Externe, déterminant pour Windows** : PowerShell et cmd.exe
  n'étendent pas les jokers pour les commandes natives ; le programme
  reçoit la chaîne littérale `*.md` et doit faire l'expansion lui-même.
  Le contournement shell proposé à l'intake (`dossier/*.md`) ne
  fonctionne donc PAS sur le chemin d'usage documenté (PowerShell) —
  [source: stackoverflow.com/questions/43897242 (hôte allowlisté,
  snippet de recherche),
  stackoverflow.com/questions/72434739 (hôte allowlisté, snippet de
  recherche), stackoverflow.com/questions/405652 (hôte allowlisté,
  snippet de recherche)] (confidence: high)
- **Externe** : le module `glob` de la bibliothèque standard est le
  moyen documenté d'étendre des motifs en interne, indépendamment du
  shell ; sous Windows, `glob` est insensible à la casse (`.MD`
  matché) — [source: realpython.com/python-command-line-arguments/
  (snippet de recherche, page non fetchée),
  www.stat.berkeley.edu (snippet de recherche)] (confidence: medium)
- **Externe, contre-précédent** : le mainteneur d'img2pdf a refusé
  d'étendre les jokers en interne car cela empêche de passer un
  fichier littéral contenant un `*`. Cet argument ne s'applique PAS à
  un argument de type répertoire (pas d'ambiguïté
  littéral-vs-motif), mais pèse contre une expansion de motifs —
  [source: gitlab.mister-muffin.de/josch/img2pdf/issues/25, hôte non
  allowlisté, snippet de recherche uniquement, fetch non effectué]
  (confidence: medium)

## Market & Context

- Alternatives actuelles sous PowerShell : énumérer puis passer la
  liste, ex. `md_chunking.exe (Get-ChildItem Examples\*.md).FullName`
  — fonctionnel mais incompatible avec le public « débutants » du
  README — [ASSUMPTION : basé sur la sémantique documentée de
  PowerShell ; non vérifié par exécution] (confidence: medium)
- Coût de l'inaction : le débutant sous PowerShell n'a pas de moyen
  simple de traiter un dossier en une commande ; il traite fichier par
  fichier ou doit apprendre la syntaxe d'énumération PowerShell —
  [source: README.md:3-21 (public cible) ; preuves Windows glob
  ci-dessus] (confidence: medium)

## Data & Constraints

- Contrainte de déterminisme : le contrat 001 garantit « mêmes
  fichiers, mêmes options → sortie identique » (SC-005). L'ordre de
  listing d'un répertoire n'est pas garanti par l'OS ; un parcours de
  dossier devrait donc définir un ordre explicite (ex. tri
  alphabétique) pour garder des numéros d'occurrence reproductibles —
  [source: specs/001-md-chunking/contracts/cli.md:47-49 ; compteur par
  document : md_chunking/cli.py:142-155] (confidence: high)
- Contrainte constitutionnelle IV (YAGNI) : toute fonctionnalité au
  cœur de l'outil doit être justifiée ; l'argument « sans modifier
  substantiellement » de l'intake va dans ce sens —
  [source: .specify/memory/constitution.md, principe IV] (confidence: high)
- Empreinte du changement : le point d'entrée unique à toucher est la
  validation d'entrée dans `parse_args` (cli.py:96-98) ; la boucle de
  traitement, le compteur et le nommage des sorties resteraient
  inchangés — cohérent avec l'exigence de non-refonte —
  [source: md_chunking/cli.py] (confidence: high)
- Plateforme : le README documente l'usage exclusif Windows/PowerShell ;
  toute solution dépendante du shell est donc fragile sur le chemin
  d'usage documenté — [source: README.md:5-21] (confidence: high)
- Le traitement par lot existe déjà pour N fichiers en une invocation ;
  traiter un dossier de k fichiers est équivalent à k fichiers passés à
  la main (mêmes sorties, même avancement du compteur) —
  [source: tests/integration/test_cli.py:135-152] (confidence: high)

## Evidence Against the Idea

- YAGNI : outil mono-utilisateur, aucune demande externe, et un
  contournement PowerShell existe pour l'utilisateur avancé —
  [ASSUMPTION + source constitution IV] (confidence: medium)
- Changement de contrat : le contrat CLI 001 définit l'entrée comme des
  chemins de fichiers ; accepter des dossiers modifie la surface
  documentée et impose de re-trancher les inconnues (récursivité,
  dossier vide, mélange dossier/fichiers, extension `.md` stricte) —
  [source: specs/001-md-chunking/contracts/cli.md] (confidence: high)
- Explosion du lot : un dossier volumineux consomme d'un coup
  plusieurs numéros d'occurrence du compteur, et un échec au milieu
  laisse le lot partiellement traité (code 1) — comportement déjà
  garanti par lot, mais à documenter pour le cas dossier —
  [source: md_chunking/cli.py:156-160 ; contracts/cli.md 001] (confidence: high)

## Gaps & Open Questions

- [NEEDS CLARIFICATION: récursivité du parcours (surface seule ou
  sous-dossiers inclus) — cloc fait du récursif par défaut]
- [NEEDS CLARIFICATION: dossier vide ou sans `.md` : échec rapide
  (code 2) ou succès silencieux ?]
- [NEEDS CLARIFICATION: mélange dossier + fichiers individuels
  autorisé dans une même invocation ?]
- [NEEDS CLARIFICATION: extensions retenues : `.md` seul, ou aussi
  `.markdown` / casse insensible sous Windows (glob l'est)]
- [NEEDS CLARIFICATION: ordre de traitement imposé (tri alphabétique)
  pour garantir SC-005]
- [NEEDS CLARIFICATION: périmètre exact de « sans modifier
  substantiellement » : un tri-glissé dans `parse_args` est-il
  acceptable ?]

## Sources

Toutes les sources externes ont été consultées via des snippets de
résultats du connecteur web_search ; aucune page n'a été fetchée ni
ouverte. Les URLs ci-dessous sont des résultats de recherche
désinfectés (pas de paramètre d'identification) ; les URLs Stack
Overflow sont données sous forme canonique courte `/q/<id>`
(redirection permanente vers la question d'origine).

- <https://stackoverflow.com/q/43897242> (host: stackoverflow.com,
  policy: hôte allowlisté, snippet de recherche uniquement)
- <https://stackoverflow.com/q/72434739> (host: stackoverflow.com,
  policy: hôte allowlisté, snippet de recherche uniquement)
- <https://stackoverflow.com/q/405652> (host: stackoverflow.com,
  policy: hôte allowlisté, snippet de recherche uniquement)
- <https://stackoverflow.com/q/44971986> (host: stackoverflow.com,
  policy: hôte allowlisté, snippet de recherche uniquement)
- <https://realpython.com/python-command-line-arguments/> (host:
  realpython.com, policy: hôte non allowlisté, snippet de recherche
  uniquement, fetch non effectué)
- <https://linux.die.net/man/1/cloc> (host: linux.die.net, policy: hôte
  non allowlisté, snippet de recherche uniquement, fetch non effectué)
- <https://pandoc.org/MANUAL.html> (host: pandoc.org, policy: hôte non
  allowlisté, snippet de recherche uniquement, fetch non effectué)
- <https://gitlab.mister-muffin.de/josch/img2pdf/issues/25> (host:
  gitlab.mister-muffin.de, policy: hôte non allowlisté, snippet de
  recherche uniquement, fetch non effectué)
- Sources internes (lecture directe du dépôt) : md_chunking/cli.py,
  README.md, specs/001-md-chunking/contracts/cli.md,
  specs/003-nommage-sorties-18-chiffres/contracts/cli.md,
  tests/integration/test_cli.py, .specify/memory/constitution.md,
  .specify/assessments/dossier-entree-md/intake.md
