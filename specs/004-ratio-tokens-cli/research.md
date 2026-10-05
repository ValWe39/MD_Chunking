# Research: Ratio caracteres/tokens reglable en CLI

**Feature**: specs/004-ratio-tokens-cli | **Date**: 2026-10-05
**Sources**: spec.md (dont Clarifications du 2026-10-05), assessment
tokencpte-flottant (research.md, concept.md, decision.md), code
md_chunking/{reviewer,cli}.py, contrats features 002 et 003,
`.specify/memory/constitution.md` v1.4.0.

## D1 — Portage du ratio : parametre des fonctions de rendu

- **Decision**: le ratio devient un parametre des fonctions de
  `reviewer.py` : `estimate_tokens(text, ratio)` et
  `build_review(doc, chunks, ratio)`, avec la constante
  `DEFAULT_RATIO_CHARS_PER_TOKEN = 3.5` comme defaut ; `cli.py` lit
  l'option et route la valeur jusqu'a `build_review` dans
  `process_document`. Aucun autre module n'est modifie.
- **Rationale**: meme emplacement que la feature 002 (calcul au rendu,
  hors modele de donnees) — la responsabilite reste au seul consommateur
  (research.md D1 de la feature 002) ; le defaut 3,5 est le choix
  utilisateur confirme, la valeur affichee suit l'option (FR-004).
- **Alternatives considered**: champ calcule sur `Chunk` — rejete
  (FR-007 : `length` reste la seule mesure de taille, index inchange) ;
  module dedie `tokens.py` — rejete (YAGNI, deja ecarte en 002) ; ratio
  dans les presets — rejete (spec : parametre global, pas par
  typologie).

## D2 — Arithmetique : fractions exactes, pas de flottant

- **Decision**: l'estimation calcule `ceil(len(texte) / ratio)` via le
  module standard `fractions.Fraction`, le ratio etant converti par
  `Fraction(str(ratio))` — l'interpretation decimale de la chaine evite
  les artefacts binaires du flottant ; aucune limite de decimales n'est
  imposee a la saisie, le calcul reste exact pour 3,3 comme pour 3,5.
- **Rationale**: FR-005 (determinisme) et le cas limite documente dans
  l'assessment (arrondi flottant aux frontieres pour un ratio non
  representable en binaire) ; `Fraction` est un module standard, la
  division exacte elimine toute divergence de plateforme ; le cout est
  negligeable (une operation par chunk au rendu).
- **Alternatives considered**: `ceil(len / ratio)` en flottant pur —
  deterministe mais sujet au +-1 aux frontieres pour 3,3 ;
  `decimal.Decimal` — equivalent mais API plus lourde pour le meme
  resultat ; calcul en entiers scales (x100) — impose une limite de
  deux decimales a la saisie, refus non demande par la spec.

## D3 — Validation de l'option : bornes dans parse_args

- **Decision**: `--tokencpte` declaree avec `type=float` ; les bornes
  (0 < ratio <= 10) sont verifiees dans `parse_args` et alimentent la
  liste d'erreurs existante (ConfigError → code de sortie 2, aucun
  fichier ecrit), message explicitant les bornes au format des
  messages existants. Les valeurs non numeriques ou a virgule (ex.
  `3,5`) echouent au parsing argparse (code 2), exactement comme
  `--min abc` aujourd'hui — comportement standard, deja le contrat de
  `--min`/`--max`.
- **Rationale**: FR-003 ; coherence avec le pattern de validation
  existant (`--overlap` entre 0 et 20) ; la virgule est refusee avec le
  message argparse documentant le format, comme le fait deja la surface
  CLI pour les entiers.
- **Alternatives considered**: parseur maison acceptant la virgule —
  rejete (la spec tranche : point decimal uniquement) ; plafonner
  silencieusement hors bornes — rejete (echec rapide, jamais de
  correction implicite).

## D4 — Affichage de l'en-tete : une decimale

- **Decision**: l'en-tete du rapport affiche le ratio effectif arrondi a
  une decimale via un formatage fixe (`3.5` pour le defaut ; `3.3` pour
  3,333), texte conserve : « Tokens estimes a ~{ratio} caracteres par
  token : approximation locale, independante de tout modele
  d'embedding. » ; la ligne par chunk (`- tokens (estimation) : ≈ <n>`)
  et le libelle restent inchanges.
- **Rationale**: clarification du 2026-10-05 (FR-004) ; le formatage
  fixe garantit un rendu deterministe quel que soit le ratio saisi ;
  aucune mention de modele (FR-T05 de la feature 002 non regressif).
- **Alternatives considered**: affichage tel quel — ecarte en
  clarification (ratios longs illisibles) ; deux decimales — ecarte en
  clarification.

## D5 — Garde-fous : aucune fuite hors du rapport

- **Decision**: le ratio n'entre dans aucune structure persistee :
  ni `Chunk`, ni l'index JSON (schema 1.0 inchange), ni `counter.txt`,
  ni le nommage ; a ratio donne, l'index JSON et les noms de fichiers
  sont identiques octet par octet a ceux d'avant la feature. Le
  parametre traverse uniquement `process_document` → `build_review`.
- **Rationale**: FR-007, FR-008, SC-004 ; garde-fous des features 001
  et 003 non regressifs ; le ratio est affiche puis jete.
- **Alternatives considered**: tracer le ratio dans l'index (metadonnees
  d'execution) — rejete (schéma strictement inchange, FR-T07 de la
  feature 002).

## D6 — Strategie de test : trois volets

- **Decision**: (1) unitaires `test_reviewer.py` — estimation avec ratio
  explicite, arrondi superieur, cas `3,3` via Fraction (frontiere exacte),
  defaut 3,5, en-tete arrondi a une decimale, determinisme ; (2)
  unitaires de validation dans `test_cli.py` — bornes ]0 ; 10] acceptees
  et rejetees, message d'erreur, valeurs mal formees ; (3) integration —
  option effective sur le corpus temoin, `--no-review` sans erreur,
  identite octet par octet de l'index entre executions avec et sans
  option, exit 2 sans aucune ecriture (fichiers et compteur).
- **Rationale**: chaque FR est couverte par au moins un test ; SC-002 a
  SC-005 verifiables ; la non-regression de l'index est pinglee par
  comparaison octet par octet.
- **Alternatives considered**: tests uniquement d'integration — rejete
  (l'arithmetique Fraction et l'arrondi d'affichage meritent des tests
  unitaires isoles).

## D7 — Amendement de la feature 002 : supersession tracee

- **Decision**: la feature 004 publie ses propres contrats
  (`contracts/cli.md`, `contracts/review-render.md`) qui supersedent
  ceux des features 003 et 002 pour les seuls points touches ; une note
  d'amendement courte est ajoutee en tete de
  `specs/002-compteur-tokens-chunks/spec.md` (et de son contrat
  review-render.md) indiquant que FR-T02 « sans parametre d'interface en
  v1 » est amende par la feature 004 ; le reste des artefacts 002 reste
  en vigueur.
- **Rationale**: FR-010 ; governance de la constitution (tout
  amendement documente) ; meme pratique que la feature 003, qui a
  supersede le contrat CLI de la 001 sans le reecrire.
- **Alternatives considered**: reecrire les artefacts 002 — rejete
  (perte de l'historique des decisions) ; rien documenter — rejete
  (contradiction silencieuse entre FR-T02 et FR-002 de la 004).

## Reste a trancher en specification de tests

Aucun NEEDS CLARIFICATION subsiste : les quatre questions ouvertes du
decision.md ont ete tranchees (bornes, affichage, seuil SC-001 : 80 %,
amendement) ; la mesure optionnelle de SC-001 (protocole au
quickstart.md) reste hors pipeline et hors dependances du projet.
