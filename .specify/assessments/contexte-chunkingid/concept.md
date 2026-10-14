# Concept: Contexte et auto-identification dans la sortie JSON

- **Slug**: contexte-chunkingid
- **Created**: 2026-10-14 (mis à jour le 2026-10-14 avec la règle en
  cascade de l'utilisateur)
- **Recommended option**: Option A — `--add-context` avec appariement
  en cascade

## Options

### Option A — Option CLI `--add-context` avec appariement en cascade

- **Sketch**: l'utilisateur ajoute `--add-context` à sa commande.
  L'appariement entre un .md et son .json de contexte suit une
  cascade à trois branches, de la plus robuste à la plus
  heuristique :
  1. **Dossier couple** (exactement 1 .md + 1 .json au même
     niveau) : le .json est le contexte de l'unique .md, **quel
     que soit son nom** — la validation du format attendu (les 7
     clés) est le seul discriminant ;
  2. **Dossier de sous-dossiers** : la même règle s'applique
     dans chaque sous-dossier contenant exactement 1 .md + 1
     .json (récursivité circonscrite à `--add-context`) ;
  3. **Dossier mélangé** (plusieurs .md et plusieurs .json au
     même niveau) : appariement par les 8 premiers caractères des
     noms, après normalisation des deux côtés (accents et espaces
     du .md convertis ou simplifiés comme dans le .json) —
     simple filet de secours pour ce cas border.
  Couple trouvé : le JSON de sortie embarque `document.chunkingid`
  (le nom numérique du fichier de sortie, sans `.json`) et
  `document.context` (les 7 champs copiés verbatim, vides compris).
  Pas de couple, ou json de format invalide : avertissement et
  traitement classique inchangé, jamais d'échec du lot.
  L'utilisateur précise que l'organisation en dossiers/sous-dossiers
  est son usage principal durable ; le cas mélangé restera marginal.
- **Appetite**: small — un module d'appariement pur à trois branches,
  une option CLI, deux champs dans `build_index`, des tests sur les
  4 dossiers d'exemples déjà fournis. La cascade réduit la table de
  normalisation au seul cas border.
- **Trade-offs**: gagne les cinq buts du problem.md en réutilisant le
  nommage existant sans le toucher, et fait porter l'appariement par
  la structure des dossiers (robuste) plutôt que par les noms
  (fragile). Sacrifie : un amendement à la spec 005 (récursivité des
  sous-dossiers, circonscrite au mode actif) ; la définition du
  « format attendu » validé en branche 1 (trop lâche = risque
  d'embarquer un .json quelconque, trop strict = risque de rejeter
  un contexte valide) ; des règles pour les états intermédiaires
  (1 .md + 2 .json, 2 .md + 1 .json). Risque résiduel : collision
  de préfixe, confinée au seul cas mélangé.
- **Rabbit holes**: la définition du format validé (7 clés exactes ?
  types tolérés ? clés supplémentaires ?) ; le traitement des
  dossiers intermédiaires (2 .md + 1 .json : bascule en branche 3 ou
  avertissement ?) ; la table de normalisation du cas border ;
  l'amendement du contrat chunk-json.md et l'incrément éventuel de
  `schema_version` ; la coexistence du champ `Typologie` du contexte
  avec `document.typologie` (preset).

### Option B — Convention sidecar strict même nom, détection automatique

- **Sketch**: pas d'option CLI : l'outil détecte automatiquement un
  `.json` portant exactement le même nom que le `.md`
  (`AN_Rapport.md` ↔ `AN_Rapport.json`), façon BIDS/Psych-DS, et
  l'embarque s'il existe. `chunkingid` est ajouté dans tous les cas.
- **Appetite**: small — plus petit que l'option A (pas d'option, pas
  de cascade, pas de récursivité à amender).
- **Trade-offs**: élimine toute heuristique de match et l'amendement
  FR-008 — mais impose de renommer les fichiers de contexte actuels
  (suffixes `-00xx` interdits, `premiere-0034.json` devrait devenir
  `premiere-seance-du-v-nettoye.json`), abandonne la règle des 8
  caractères du cas mélangé, et rend l'embarquement implicite (un
  .json homonyme inattendu se retrouve dans la sortie).
- **Rabbit holes**: la migration du corpus de contexte déjà préparé
  dans `Examples/Extension/` ; la gestion implicite (comment exclure
  un contexte sans déplacer le fichier ?).

### Option C — Ne rien construire, fusion manuelle en aval

- **Sketch**: l'utilisateur maintient un petit script de
  post-traitement (jq ou Python) qui fusionne les .json de contexte
  dans les .json de sortie après le chunking, en s'appuyant sur les
  suffixes d'occurrence.
- **Appetite**: small — mais hors de l'outil, à maintenir à la main.
- **Trade-offs**: aucune modification de l'outil ni des contrats ;
  mais la correspondance numéro ↔ contexte reste entièrement
  manuelle (l'ordre de traitement détermine les numéros), donc
  fragile à chaque lot, et le but « sortie auto-identifiée » n'est
  pas couvert. C'est le statu quo du cost of inaction du
  problem.md.
- **Rabbit holes**: réinvention partielle de l'appariement dans le
  script, dérive silencieuse entre numéros et contextes.

## Recommendation

**Option A (cascade).** La cascade demandée par l'utilisateur
renforce l'option déjà recommandée : l'appariement s'appuie d'abord
sur la co-localisation (1 .md + 1 .json par dossier ou
sous-dossier), qui ne dépend d'aucune normalisation de nom et
correspond à l'usage principal déclaré (organisation en
dossiers/sous-dossiers, jugée plus robuste pour la suite) ; le
préfixe 8 caractères devient un simple recours pour le cas mélangé
marginal. Les quatre dossiers d'exemples restent compatibles tels
quels : `Couple/` (branche 1), `Sous-dossiers/` (branche 2),
`Multi-couples/` et `Multi-coupes mix/` (branche 3). `chunkingid`
reprend une valeur déjà calculée par `build_output_name` — aucun
calcul nouveau. L'option B reste plus simple mais exige de renommer
le corpus existant ; l'option C ne fait que déplacer le problème.

## Out of Scope (for the recommended option)

- Tout hérité des non-goals : pas d'extraction ni de transformation
  des métadonnées (verbatim strict), pas de conversion CSL, pas de
  modification du nommage, du découpage ni du review.
- Pas de fusion multi-contextes ni de priorité entre contextes
  concurrents : une ambiguïté (branche 3) est un avertissement, pas
  une résolution.
- Pas d'option pour personnaliser la longueur du préfixe (fixée à
  8), la profondeur de récursivité ou la table de normalisation.
- Pas de copie du .json de contexte dans la sortie : il est embarqué
  dans le JSON, jamais recopié en fichier.
- `chunkingid` ne change pas le nommage : il le restitue.
- La branche 1 ne fait pas de validation de contenu au-delà du
  format (pas de vérification que le contexte « correspond » au
  document).

## Assumptions to Validate

- La définition du « format attendu » (clés présentes, types
  tolérés, clés supplémentaires) peut être figée en spécification de
  façon à valider les 3 .json d'exemples sans cas particulier ad hoc.
- Les états intermédiaires (1 .md + 2 .json, 2 .md + 1 .json dans un
  même dossier) basculent en branche 3 ou produisent un avertissement
  avec traitement classique — à trancher en spécification.
- La récursivité des sous-dossiers n'est acceptable que sous
  `--add-context` (amendement FR-008 circonscrit), pas en mode
  classique ; un sous-dossier sans .md ne fait pas échouer le lot.
- Dans le cas mélangé, l'appariement se fait par préfixe de noms de
  fichiers normalisés (pas par rapprochement du champ `Titre` du
  .json avec le titre du .md, qui peut être absent — FR-007).
- Le champ `Typologie` du contexte coexiste avec `document.typologie`
  (preset) sous des clés distinctes dans le bloc `document`.
- Ajouter deux sous-champs optionnels à `document` n'exige pas
  d'incrément de `schema_version` (changement compatible), mais le
  contrat chunk-json.md doit être amendé — à trancher en
  spécification.
