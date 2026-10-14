# Research: Contexte utilisateur et auto-identification dans la sortie JSON

**Feature**: 006-add-context | **Date**: 2026-10-14

Résolution des inconnues techniques du plan. Aucun NEEDS
CLARIFICATION ne subsiste : les questions fonctionnelles ont été
tranchées par les clarifications du 2026-10-14 (spec.md) et par
l'assessment amont (cascade, clés `document.chunkingid` et
`document.context`, portée inconditionnelle).

## Décisions

### D1 — Appariement dans un module dédié `md_chunking/contexts.py`

- **Decision**: un module nouveau `md_chunking/contexts.py` expose
  une fonction publique de résolution
  `resolve_avec_contextes(chemins) -> tuple[list[tuple[Path, dict |
  None]], list[str]]` : chaque document résolu est accompagné de son
  contexte (`None` si non apparié) ; la fonction retourne aussi les
  avertissements. `cli.py` choisit le résolveur : sans
  `--add-context`, `inputs.resolve_inputs` (feature 005, surface
  seule) et contextes tous `None` ; avec l'option, la résolution
  récursive de `contexts.py`. Un chemin introuvable ou
  ni-fichier-ni-dossier lève `InputError` existante, traduite en
  code 2 sans écriture.
- **Rationale**: testable unitairement sans argparse (modèle
  `naming.py`/`inputs.py`) ; la résolution de surface de la
  feature 005 n'est pas touchée (contrat 005 inchangé sans
  l'option) ; les avertissements sont retournés, pas imprimés,
  pour rester purs et testables.
- **Alternatives considered**: étendre `inputs.resolve_inputs` d'un
  paramètre (mélange deux contrats de résolution, risque de
  régression 005) ; tout garder dans `cli.py` (moins testable) ;
  un module par branche de la cascade (sur-ingénierie, YAGNI).

### D2 — Ordre déterministe du parcours récursif

- **Decision**: les arguments sont traités dans l'ordre de la
  ligne de commande ; pour un dossier, à chaque niveau les `.md`
  directement présents sont traités d'abord (tri casse neutre du
  nom, comme la feature 005), puis la descente se fait dans les
  sous-dossiers triés casse neutre (profondeur d'abord). Un niveau
  sans `.md` émet l'avertissement existant puis la descente
  continue.
- **Rationale**: la spec (FR-003) impose la récursivité mais pas
  l'ordre ; sans règle, les numéros d'occurrence ne seraient pas
  reproductibles (SC-002, FR-009) ; la profondeur d'abord est la
  lecture naturelle de « dossier de sous-dossiers » et réutilise
  la clé de tri de la feature 005.
- **Alternatives considered**: tous les fichiers avant toute
  descente (parcours en largeur — aucune valeur ajoutée, ordre
  contre-intuitif pour un corpus organisé) ; ordre du listing
  système (non déterministe, rejeté).

### D3 — Normalisation de la clé d'appariement (cas mélangé)

- **Decision**: `cle_normale(nom) =` NFKD puis suppression des
  diacritiques (encodage ASCII « ignore »), minuscules, espaces
  convertis en `_`, seuls `a-z`, `0-9` et `_` conservés, tronqué à
  8 caractères. Vérifiée sur les trois couples d'exemples :
  `premiere-0034.json`/`premiere-seance-du-v-nettoye.md` →
  `premiere` ; `AN_Rappo-0032.json`/`AN_Rapport.md` → `an_rappo` ;
  `Ecalle_o-0040.json`/`Ecalle_ouvrage.md` → `ecalle_o` (le trait
  de soulignement compte, les tirets et apostrophes sont
  supprimés).
- **Rationale**: FR-005 et clarification utilisateur du 2026-10-14
  (« le .md a potentiellement des espaces et des accents que le
  .json convertit en `_` ou simplifie ») ; la même fonction de
  normalisation existe déjà en germe dans `naming.extract_letters`
  (feature 003) — la table est ici distincte car elle conserve
  chiffres et `_` ; les trois couples d'exemples valident la table
  sans cas particulier.
- **Alternatives considered**: comparaison brute des 8 premiers
  caractères (contredite par les accents et espaces annoncés) ;
  conserver les tirets (casserait `premiere` : `premiere-0034` →
  `premiere-` ≠ `premiere`).

### D4 — Validation du format de contexte

- **Decision**: un `.json` de contexte est valide si `json.loads`
  réussit, produit un objet, et que ses clés sont exactement les
  sept attendues — `Typologie`, `Auteur(s)`, `Titre`, `Editeur`,
  `Date`, `Référence`, `Citation` — ni manquante, ni
  supplémentaire ; les valeurs ne sont pas contraintes (chaîne ou
  liste, vide admis) et copiées verbatim. Tout écart (illisible,
  non-objet, clés en trop ou manquantes) invalide le fichier :
  avertissement « .json de contexte invalide : {chemin} » et
  traitement classique ; jamais d'échec du lot.
- **Rationale**: FR-004 et FR-008 ; la validation stricte est le
  discriminant de la branche couple (FR-002) où le nom ne compte
  pas ; « exactement les champs » est la formulation de
  l'utilisateur depuis l'intake ; un format invalide ne fait
  jamais échouer le lot (sémantique de lot existante).
- **Alternatives considered**: validation lâche (au moins les 7
  clés, extras copiés — contredit « exactement » et affaiblit le
  discriminant) ; types contraints (rejeterait les dates en texte
  libre des exemples réels).

### D5 — Cascade d'appariement par niveau

- **Decision**: à chaque niveau, ne comptent que les fichiers
  directement présents (le contenu des sous-dossiers n'y compte
  jamais) ; si le niveau contient exactement 1 `.md` et 1 `.json`,
  le `.json` est le contexte du `.md` après validation (D4) ; sinon
  (plusieurs `.md` ou plusieurs `.json`), un `.md` est apparié à un
  `.json` si leurs clés normalisées (D3) coïncident et que la
  correspondance est unique des deux côtés ; toute absence de
  candidat, ambiguïté ou fichier non apparié reste en traitement
  classique ; un `.json` non apparié par la cascade émet
  l'avertissement « .json de contexte orphelin : {chemin} » ; une
  ambiguïté émet « Appariement ambigu pour {md} ».
- **Rationale**: FR-002, FR-003, FR-005 et clarifications du
  2026-10-14 (cascade à chaque niveau, comptage par niveau) ; la
  co-localisation couvre l'usage principal sans aucune heuristique
  de nom ; le préfixe reste un recours confiné aux niveaux
  mélangés.
- **Alternatives considered**: préfixe 8 partout (fragile, contredit
  la clarification) ; apparier au `.json` le plus proche par
  similarité (heuristique non spécifiée, imprévisible).

### D6 — Avertissements : libellés et flux

- **Decision**: tous les avertissements de contexte partent sur
  stderr, en français, nommant le fichier en cause :
  « .json de contexte invalide : {chemin} », « .json de contexte
  orphelin : {chemin} », « Appariement ambigu pour {md} », et
  l'existant « Dossier sans fichier .md : {dossier} » réutilisé
  pour tout niveau sans `.md` du mode récursif. Aucun ne change le
  code de sortie ni n'interrompt le lot ; le compteur n'est pas
  consulté avant la fin de la résolution.
- **Rationale**: FR-008 ; cohérence avec la feature 005 (avertis-
  sements sur stderr, succès sur stdout) ; un dossier argument
  dont toute la récursivité ne trouve aucun `.md` reste code 0
  avec avertissement, comme la feature 005.
- **Alternatives considered**: échec au code 2 pour un contexte
  invalide (contredit FR-008 « jamais faire échouer le lot ») ;
  avertissements sur stdout (incohérent avec l'existant).

### D7 — Injection dans l'index et version de schéma

- **Decision**: `build_index` reçoit le nom de sortie et
  l'éventuel contexte ; le bloc `document` gagne
  `chunkingid` (le nom de sortie sans extension, émis pour chaque
  document, avec ou sans `--add-context`) et `context` (l'objet
  verbatim des sept champs, uniquement si apparié et validé).
  `schema_version` reste `"1.0"` : l'ajout de champs optionnels
  est un changement compatible (FR-013 : incrément réservé aux
  changements incompatibles) ; le contrat chunk-json.md est
  amendé pour documenter les deux champs.
- **Rationale**: FR-006, FR-007, FR-011 et clarification du
  2026-10-14 (choix A : inconditionnel) ; `cli.py` calcule déjà
  le nom avant d'écrire l'index — aucune valeur nouvelle à
  calculer ; les consommateurs existants du JSON ignorent les
  clés inconnues (JSON additif compatible).
- **Alternatives considered**: incrément `1.1` (changement
  compatible, l'incrément ferait échouer les comparaisons strictes
  de version pour rien) ; émettre `chunkingid` seulement avec
  `--add-context` (rejeté en clarification, choix A).

### D8 — Fichiers individuels et dossiers sans l'option

- **Decision**: un `.md` passé individuellement n'est jamais
  apparié, même avec `--add-context` (le dossier parent n'est pas
  une unité de couple) ; sans l'option, la résolution, les
  sorties et les codes de la feature 005 sont inchangés au champ
  `chunkingid` près, ajouté partout ; les `.json` présents dans
  un dossier sont ignorés comme tout fichier non `.md`.
- **Rationale**: hypothèse de spec (« Appariement limité aux
  entrées dossier ») et FR-001 ; empêche d'embarquer par accident
  un `.json` voisin d'un fichier passé en direct ; SC-002 verrouille
  l'absence de régression.
- **Alternatives considered**: apparier un fichier individuel à un
  `.json` de son dossier parent (implicite et surprenant,
  contredit l'hypothèse tranchée en spécification).

### D9 — Stratégie de tests sur les exemples fournis

- **Decision**: la suite unitaire `tests/unit/test_contexts.py`
  couvre la normalisation (table D3 + les trois couples d'exemples
  réels), la validation (D4 : 7 clés, vide, extra, illisible), la
  cascade (D5 : couple, mélangé, ambigu, orphelin, niveaux
  intermédiaires) et l'ordre (D2) ; l'intégration CLI lance
  `--add-context` sur des copies temporaires (`tmp_path`) des
  quatre dossiers `Examples/Extension/` (Couple, Sous-dossiers,
  Multi-couples, Multi-coupes mix) — jamais les originaux ; le
  compteur est isolé en `tmp_path` ; `tests/unit/test_indexer.py`
  est mis à jour pour `chunkingid` (toujours) et `context`
  (verbatim, vides compris) ; un test dédié verrouille SC-002 :
  sans `--add-context`, le JSON ne diffère de l'existant que par
  `chunkingid`.
- **Rationale**: SC-001 à SC-004 ; les exemples fournis par
  l'utilisateur couvrent exactement les quatre dispositions de la
  spec — les utiliser garantit l'acceptance sans fixture
  synthétique ; l'assomption de spec impose copies et compteur
  isolé.
- **Alternatives considered**: fixtures synthétiques seulement
  (n'auraient pas la valeur probante du corpus réel, dont les
  noms portent les cas difficiles : `_`, tirets, suffixes).

## Vérification des inconnues du Technical Context

- Python 3.11+ confirmé (pyproject `>=3.11`, plan 005).
- pytest 8.x confirmé (suites existantes, Python 3.14 constaté en
  local, cible `>=3.11` inchangée).
- Aucune dépendance nouvelle : `json`, `unicodedata`, `pathlib`.
- Aucune inconnue résiduelle : PASS.
