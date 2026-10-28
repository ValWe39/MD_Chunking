# Research: Appariement robuste .md/.json sur préfixes longs

**Feature**: 007-robust-pairing | **Date**: 2026-10-28

Résolution des inconnues techniques du plan. Aucun NEEDS
CLARIFICATION ne subsiste : les questions fonctionnelles ont été
tranchées par la clarification du 2026-10-28 (chaque `.md`
avance indépendamment par paliers) et par l'assessment amont
(verdict GO, Option A).

## Décisions

### D1 — Boucle d'appariement par paliers, `.md` indépendants

- **Decision**: `apparie_niveau()` itère sur les paliers
  (8, 12, 16, 20, 24, … jusqu'à la longueur maximale du stem
  normalisé le plus long du niveau). À chaque palier, chaque
  `.md` non encore résolu tente de s'apparier. L'algorithme
  s'arrête quand tous les `.md` sont résolus ou à la longueur
  maximale. Les `.md` non résolus à la longueur maximale
  émettent « Appariement ambigu » et passent en classique.
- **Rationale**: clarification du 2026-10-28 (Option A) ;
  chaque `.md` avance indépendamment, ce qui maximise le
  nombre d'appariements résolus sans attendre les autres.
- **Alternatives considered**: arrêt au premier palier où
  au moins un `.md` est résolu (rejeté : pénalise les
  `.md` qui auraient un candidat à un palier supérieur) ;
  traitement global par palier (rejeté : un `.md` résolu à
  8 caractères bloquerait l'avancement des autres).

### D2 — Paliers de 4 en 4 (8, 12, 16, 20, 24, …)

- **Decision**: les paliers augmentent de 4 caractères :
  8, 12, 16, 20, 24, … jusqu'à la longueur maximale du
  stem normalisé le plus long du niveau.
- **Rationale**: 8 caractères est le comportement actuel
  (compatibilité ascendante) ; un pas de 4 offre un bon
  compromis entre nombre d'itérations et finesse de
  discrimination. Les cas réels (Fipeco : 23-24 caractères,
  préfixe commun 13 caractères) sont résolus au palier 16.
  Un pas de 1 (8, 9, 10, …) serait plus fin mais inutilement
  verbeux ; un pas de 8 (8, 16, 24) manquerait de finesse
  pour des cas intermédiaires.
- **Alternatives considered**: pas de 1 (trop d'itérations,
  complexité inutile) ; pas de 8 (trop grossier, risque de
  collision non résolue) ; paliers dynamiques basés sur la
  distribution des longueurs (sur-ingénierie, YAGNI).

### D3 — `cle_normale()` sans troncature

- **Decision**: `cle_normale(nom)` retourne la chaîne
  normalisée complète (NFKD, minuscules, espaces → `_`,
  `a-z 0-9 _` conservés), sans troncature `[:8]`.
  L'entièreté de la troncature est déplacée dans
  `apparie_niveau()` qui applique `[:palier]` à chaque
  itération.
- **Rationale**: séparer la normalisation (pure, sans perte)
  de la comparaison (avec perte contrôlée par palier) ;
  permet à `apparie_niveau` d'appliquer n'importe quel
  palier sans recalculer la normalisation.
- **Alternatives considered**: garder `cle_normale` tronquée
  et ajouter une fonction `cle_normale_complete` (duplication,
  YAGNI) ; tronquer dans `apparie_niveau` en réappliquant
  la normalisation à chaque palier (recalcul coûteux,
  inutile).

### D4 — Adaptation des tests d'ambiguïté existants

- **Decision**: les 2 tests d'ambiguïté existants sont
  adaptés pour refléter le nouveau comportement :
  - `test_melee_ambiguite_deux_json_meme_prefixe` : les
    fichiers `premiere-0034.json` et `premiere-0035.json`
    ont des clés normalisées complètes différentes
    (`premiere0034` vs `premiere0035`) → résolus au palier
    12. Le test vérifie désormais l'appariement correct.
  - `test_melee_ambiguite_json_partage_par_deux_md` : les
    fichiers `an_rappo-1.md` et `an_rappo-2.md` ont des
    clés complètes différentes (`an_rappo1` vs `an_rappo2`)
    → résolus au palier 9 (mais le `.json` `an_rappo-0032`
    n'a pas de candidat `.md` correspondant, donc reste
    orphelin). Le test vérifie l'avertissement orphelin.
  - Un nouveau test vérifie le vrai cas d'ambiguïté :
    deux fichiers de même stem normalisé complet →
    avertissement « Appariement ambigu » à la longueur
    maximale.
- **Rationale**: FR-010 ; les anciens tests vérifiaient un
  comportement qui n'existe plus (ambiguïté à 8 caractères
  résoluble à un palier supérieur). Leur valeur de
  couverture est préservée en les adaptant au nouveau
  comportement.
- **Alternatives considered**: supprimer les 2 tests (perte
  de couverture) ; les laisser inchangés (échec, ils
  testent un comportement obsolète).

### D5 — Amendement de la spec 006 (D3) vs spec 007 dédiée

- **Decision**: la spec 006 est **amendée** (D3 modifié :
  « tronqué à 8 caractères » → « extension progressive par
  paliers ») plutôt que de créer une spec 007 dédiée.
  La spec 007 documente la modification, mais le contrat
  D3 est mis à jour in-place dans `research.md` de la
  spec 006.
- **Rationale**: la modification est un changement de
  comportement interne de la branche « mélangée », pas
  une nouvelle fonctionnalité ; l'interface CLI et le
  contrat chunk-json.md sont inchangés. Un amendement
  est plus léger qu'une spec dédiée et reflète la réalité
  (amélioration d'un mécanisme existant).
- **Alternatives considered**: spec 007 dédiée avec
  référence à la spec 006 (lourdeur documentaire, risque
  de divergence entre les deux specs) ; nouvelle feature
  avec option CLI (YAGNI, contredit le verdict GO).

### D6 — `Examples/Pairing/` comme fixture de test

- **Decision**: le dossier `Examples/Pairing/` (3 paires
  Fipeco réelles) est utilisé comme fixture de test
  d'intégration, copié en `tmp_path` comme les autres
  exemples (`Examples/Extension/`). Les fichiers originaux
  ne sont jamais modifiés.
- **Rationale**: SC-001 ; les cas réels valident
  l'acceptance sans fixture synthétique. Le compteur est
  isolé en `tmp_path`.
- **Alternatives considered**: fixture synthétique uniquement
  (n'aurait pas la valeur probante du corpus réel) ; test
  sur les originaux (risque de modification accidentelle).

## Vérification des inconnues du Technical Context

- Python 3.11+ confirmé (pyproject `>=3.11`).
- pytest 8.x confirmé (suites existantes).
- Aucune dépendance nouvelle : `unicodedata`, `pathlib`.
- Aucune inconnue résiduelle : PASS.
