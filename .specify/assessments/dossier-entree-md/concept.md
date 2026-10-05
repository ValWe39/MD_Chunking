# Concept: Traiter un dossier de Markdown en une commande

- **Slug**: dossier-entree-md
- **Created**: 2026-10-05
- **Recommended option**: Option B — Dossier en argument de la CLI

## Options

### Option A — Documenter le contournement (ne rien construire)

- **Sketch**: rien ne change dans l'outil ; le README gagne une section
  « traiter un dossier » qui enseigne l'énumération PowerShell
  (`md_chunking.exe (Get-ChildItem Examples\*.md).FullName` ou
  équivalent exact vérifié). L'utilisateur avance et apprend la syntaxe
  d'énumération ; l'outil reste strictement identique.
- **Appetite**: small (quelques heures : rédaction + vérification de la
  commande exacte sur la machine)
- **Trade-offs**: gagne : zéro code, zéro risque, zéro dette de
  contrat. Sacrifie : le public « débutants » du README reste face à
  une syntaxe d'énumération peu intuitive — le problème défini
  (« accessible au public cible ») n'est résolu que partiellement ;
  la solution reste dépendante du shell (fragile si l'usage migre vers
  cmd.exe ou un autre environnement).
- **Rabbit holes**: vérification de la syntaxe exacte multi-shells
  (PowerShell 5.1 vs 7) peut tirer vers un guide par shell ; rester à
  une seule forme documentée.

### Option B — Dossier en argument de la CLI (le plus petit build qui marche)

- **Sketch**: la commande accepte en argument, à côté des fichiers
  actuels, un chemin de dossier ; l'outil traite alors les fichiers
  `.md` contenus dans ce dossier (surface seule, pas de
  sous-dossiers), dans un ordre déterministe (tri alphabétique), comme
  s'ils avaient été passés un par un. Le contournement shell disparaît
  du chemin de l'utilisateur : une seule commande, documentée en une
  étape du README, identique sur tout shell.
- **Appetite**: small (quelques jours : validation d'entrée dans
  `parse_args`, tests d'intégration et unitaires, mise à jour du
  contrat CLI et du README ; empreinte concentrée sur le bloc de
  validation `md_chunking/cli.py:96-98`, la boucle de traitement, le
  compteur et le nommage restant inchangés — research.md, Data &
  Constraints)
- **Trade-offs**: gagne : résout le problème pour le public cible,
  indépendant du shell, reproductible (ordre explicite → SC-005 tenu),
  cohérent avec le prior art (cloc) et avec la contrainte « sans
  modification substantielle ». Sacrifie : évolution du contrat CLI
  001 (précédent : feature 003 l'a déjà fait) ; il faut trancher les
  cas limites (dossier vide, mélange dossier + fichiers, extensions)
  pendant la spécification. Risque faible : explosion du nombre
  d'occurrences consommées sur un gros dossier — déjà le comportement
  du lot multi-fichiers, pas une régression.
- **Rabbit holes**: récursivité (une option `--recursive` ou un
  parcours profond tirent vers du filtrage/inclusion-exclusion —
  hors périmètre) ; extension des extensions (`.markdown`,
  insensibilité à la casse — trancher simplement et figer) ;
  sémantique du dossier vide (code 2 vs succès silencieux — trancher,
  ne pas paramétrer).

### Option C — Expansion interne des motifs jokers (`*.md` en argument)

- **Sketch**: la CLI accepterait des motifs jokers et les étendrait
  elle-même via `glob` (indépendance totale du shell, y compris pour
  des sélections fines comme `notes-2026-*.md`).
- **Appetite**: medium (petites semaines : ambiguïté littéral-vs-motif
  à gérer, comportements multi-plateformes, tests de non-régression
  des chemins contenant des métacaractères)
- **Trade-offs**: gagne : flexibilité maximale de sélection. Sacrifie :
  le contre-précédent img2pdf (research.md : un fichier littéral
  contenant `*` devient impossible à passer) ; une surface de test
  bien plus large ; l'ambiguïté casse/délimiteurs entre plateformes.
  Ne résout rien que le dossier (Option B) ne résout pas pour le cas
  d'usage réel (`Examples/`).
- **Rabbit holes**: échappement des métacaractères, différences de
  casse Windows/Unix documentées dans research.md, interaction avec
  les fichiers dont le nom contient `[` `]` `?`.

## Recommendation

Option B. Elle est la seule qui résolve le problème tel que défini —
une commande unique, indépendante du shell, accessible au débutant
PowerShell documenté du README — avec l'appétite le plus petit
(empreinte limitée à la validation d'entrée, boucle/compteur/nommage
inchangés). Elle sert directement les métriques de succès de
problem.md (k fichiers → 2k sorties en une commande, occurrences
reproductibles, README en une étape). L'Option A ne traite que le
symptôme pour l'utilisateur avancé et laisse le public cible
prisonnier du shell ; l'Option C ajoute une flexibilité que personne
n'a demandée (YAGNI, constitution IV) au prix d'une ambiguïté
documentée. L'Option A reste utile comme filet de sécurité : la
section README qu'elle rédigerait peut accompagner l'Option B pour
les utilisateurs avancés, sans rien construire de plus.

## Out of Scope (for the recommended option)

- Parcours récursif des sous-dossiers (hérité des non-goals)
- Expansion de motifs jokers (Option C écartée)
- Filtrage, inclusion/exclusion, tri configurable (tri alphabétique
  figé pour SC-005)
- Parallélisation, garantie anti-doublon d'exécutions concurrentes
- Toute écriture hors du dossier `--output` (constitution inchangée)
- Nouvelle option CLI : pas de `--recursive`, pas de `--include` —
  l'argument dossier seul porte le comportement

## Assumptions to Validate

- La surface du dossier suffit au cas d'usage réel (`Examples/` n'a
  pas de sous-dossiers à traiter — à vérifier en spécification)
- Un dossier vide ou sans `.md` échoue au code 2 (échec rapide,
  cohérent avec la Config Validation de la constitution) — à trancher
- Dossier et fichiers individuels peuvent être mélangés dans une même
  invocation — à trancher
- `.md` seul suffit, insensible à la casse sous Windows — à trancher
- Le tri alphabétique du nom de fichier suffit à garantir SC-005
  (occurrences reproductibles) — à trancher
- L'empreinte « validation d'entrée dans parse_args uniquement »
  satisfait « sans modifier substantiellement l'outil » tel que
  l'utilisateur l'entend — à confirmer avec lui en spécification
