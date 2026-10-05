# Research: Entrée dossier pour la CLI

**Feature**: 005-dossier-entree-cli | **Date**: 2026-10-05

Résolution des inconnues techniques du plan. Aucun NEEDS CLARIFICATION
ne subsiste : les questions fonctionnelles ont été tranchées par la
clarification du 2026-10-05 (spec.md) et par l'assessment amont.

## Décisions

### D1 — Résolution dans un module dédié `md_chunking/inputs.py`

- **Decision**: une fonction publique unique
  `resolve_inputs(chemins: list[Path]) -> tuple[list[Path], list[str]]`
  dans un nouveau module `md_chunking/inputs.py` ; elle retourne la
  liste ordonnée des fichiers à traiter et la liste des avertissements
  (« aucun .md ») ; un chemin introuvable ou ni-fichier-ni-dossier
  lève `InputError`, traduite en code 2 par la CLI. `cli.py` remplace
  sa boucle de validation par cet appel ; `main` consomme la liste
  résolue sans autre changement.
- **Rationale**: testable unitairement sans argparse (modèle
  `naming.py`/`counter.py`, feature 003) ; diff minimal dans `cli.py`
  (exigence « sans modifier substantiellement ») ; la signature
  retourne les avertissements au lieu de les imprimer, pour rester
  pure et testable.
- **Alternatives considered**: tout garder dans `parse_args`
  (mélange parsing/résolution, moins testable) ; un module par type
  d'entrée (sur-ingénierie, YAGNI) ; imprimer directement depuis la
  résolution (effet de bord, non testable).

### D2 — Filtre d'extension : suffixe `.md` insensible à la casse

- **Decision**: `chemin.suffix.lower() == ".md"` ; `.markdown`, sans
  extension ou double suffixe (`.md.txt`) refusés ; fichiers cachés
  et système inclus ; sous-dossiers exclus par nature (un dossier
  n'est pas un fichier).
- **Rationale**: FR-002 ; la comparaison basse la casse couvre `.MD`
  sous Windows sans dépendre de la plateforme ; `Path.suffix` est
  standard et ne résout aucun type MIME.
- **Alternatives considered**: `mimetypes` (surdimensionné, dépend de
  la base locale) ; glob `*.md` insensible à la casse seulement sous
  Windows (comportement inégal entre plateformes, cf. assessment
  research.md) ; liste d'extensions configurable (hors spec, YAGNI).

### D3 — Ordre : tri alphabétique casse neutre sur le nom

- **Decision**: tri des `.md` d'un dossier par
  `(p.name.lower(), p.name)` ; un dossier à plat rend ce tri égal à un
  tri sur le chemin complet ; l'ordre des arguments de la ligne de
  commande est préservé, chaque dossier étant développé à sa position.
- **Rationale**: FR-003 et FR-004 ; déterminisme entre exécutions et
  plateformes (SC-002) ; le tie-break sur le nom brut stabilise
  `A.md` vs `a.md` (casse différente, même forme basse).
- **Alternatives considered**: ordre du listing OS
  (`iterdir` brut — non garanti, casse dépendante) ; tri par date de
  modification (non spécifié, non reproductible) ; tri par chemin
  complet (strictement équivalent ici, choix indifférent).

### D4 — Dossier vide ou sans `.md` : avertissement, code 0, aucun écrit

- **Decision**: la résolution émet un avertissement par dossier sans
  `.md` (« dossier sans fichier .md : {dossier} »), la CLI l'imprime
  sur stderr et retourne 0 ; la lecture du compteur n'a lieu qu'après
  la résolution, donc une invocation ne produisant aucun document ne
  consulte pas `counter.txt` et ne peut pas échouer au code 2 pour
  cela.
- **Rationale**: FR-005b et clarification du 2026-10-05 (« rien à
  traiter = succès ») ; ne pas lire le compteur quand rien ne sera
  écrit évite un échec de configuration sans conséquence observable.
- **Alternatives considered**: échec rapide au code 2 (piste
  initiale du handoff, remplacée par la clarification) ; avertissement
  sur stdout (les succès vont sur stdout, les avertissements sur
  stderr, cohérence avec `main`).

### D5 — Chemin introuvable ou ni-fichier-ni-dossier : code 2 existant

- **Decision**: `resolve_inputs` lève `InputError` avec le message
  actuel (« fichier d'entree introuvable : {chemin} ») ;
  `parse_args`/`main` le traduisent en `ConfigError` → code 2, aucun
  fichier écrit ; la validation a lieu avant toute écriture, comme
  aujourd'hui.
- **Rationale**: FR-005 ; réutilise le message et le code existants,
  aucune nouvelle sémantique.
- **Alternatives considered**: message distinct pour dossier
  introuvable (aucun besoin, le chemin suffit) ; ignorer les introuvables
  (changerais le contrat 001).

### D6 — Doublons : traitement à chaque occurrence, aucune déduplication

- **Decision**: aucune déduplication ; un fichier couvert par un
  dossier ET passé individuellement, ou un dossier passé deux fois,
  est traité à chaque occurrence, consommant un numéro d'occurrence
  par passage.
- **Rationale**: FR-001 et clarification du 2026-10-05 ; « comme si
  passé individuellement » est la sémantique la plus simple et
  la plus prévisible ; dédupliquer introduirait une comparaison de
  chemins (résolution, casse) coûteuse à spécifier pour un cas
  d'usage inexistant.
- **Alternatives considered**: dédupliquer silencieusement ou avec
  avertissement (rejetées en clarification).

### D7 — Listing de surface : `Path.iterdir`, pas de parcours récursif

- **Decision**: listing non récursif via `iterdir()` filtré sur
  `is_file()` ; un sous-dossier, même nommé `*.md`, n'est ni parcouru
  ni traité ni signalé ; un lien symbolique pointant vers un fichier
  `.md` est traité comme un fichier (suivi naturel de `is_file()`).
- **Rationale**: FR-008 ; `iterdir` ne descend jamais dans les
  sous-dossiers, contrairement à `os.walk` ou `rglob` ; l'exclusion
  des sous-dossiers par `is_file()` tient sans code supplémentaire.
- **Alternatives considered**: `rglob` avec limite de profondeur
  (récursivité déguisée, contredit FR-008) ; ignorer les fichiers
  cachés (non spécifié, contredit le cas limite spec « traité comme
  tout .md »).

## Vérification des inconnues du Technical Context

- Python 3.11+ confirmé (pyproject `>=3.11`, plan 003).
- pytest 8.x confirmé (suites existantes).
- Aucune dépendance nouvelle : `pathlib` uniquement.
- Aucune inconnue résiduelle : PASS.
