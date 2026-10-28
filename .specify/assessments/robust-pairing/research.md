# Idea Research: Robustesse du pairing .md/.json (extension progressive)

- **Slug**: robust-pairing
- **Created**: 2026-10-28
- **Evidence confidence (overall)**: high

## Users & Demand

- Le problème est **observé**, pas déclaré : l'exécution de
  `md_chunking --add-context` sur le corpus Fipeco
  (`...\Echantillon\`) a produit 3 avertissements
  « Appariement ambigu » et aucun contexte embarqué, alors que
  les 3 `.json` sont valides (7 clés exactes) et que les paires
  sont identifiables à l'œil nu —
  [source: constat investigation 2026-10-28, sortie console
  reproduite dans intake.md] (confidence: high)
- L'utilisateur a préparé un dossier `Examples/Pairing/` contenant
  les 3 paires Fipeco réelles (6 fichiers) comme cas de référence
  pour la future spécification —
  [source: `ls Examples/Pairing/`, 2026-10-28] (confidence: high)
- Le signal d'engagement est fort : l'utilisateur a explicitement
  demandé de « tenir compte des anciens exemples pour ne pas
  détruire ce qui fonctionnait déjà », ce qui montre une
  préoccupation de compatibilité ascendante —
  [source: intake.md, citation directe] (confidence: high)
- [ASSUMPTION : mono-utilisateur, outil local — aucun autre
  utilisateur connu, pas de signal externe] (confidence: medium)

## Prior Art

- **Interne, reconnaissance du problème** : la décision D3 de la
  spec 006 (`specs/006-add-context/research.md:55-70`) mentionne
  explicitement l'alternative « préfixe 8 partout (fragile) » comme
  rejetée — la fragilité de la troncature fixe est **reconnue
  dans le design original** —
  [source: specs/006-add-context/research.md, D5 alternatives
  considered] (confidence: high)
- **Interne, normalisation similaire** : `naming.extract_letters`
  (feature 003, `md_chunking/naming.py`) applique une normalisation
  proche (NFKD, casse neutre, accents supprimés) mais tronque à
  5 lettres pour le nommage des sorties — la table de caractères
  est différente (`a-z` uniquement, pas de chiffres ni `_`) —
  [source: md_chunking/naming.py, spec 003] (confidence: high)
- **Interne, contrainte de compatibilité** : les 3 couples
  d'exemples `Examples/Extension/` (Couple, Multi-couples,
  Multi-coupes mix, Sous-dossiers) fonctionnent avec la
  troncature à 8 caractères (`premiere`, `an_rappo`,
  `ecalle_o`) — toute modification doit préserver ces
  appariements —
  [source: tests/unit/test_contexts.py:62-70,
  specs/006-add-context/research.md D3] (confidence: high)
- **Interne, contournement existant** : l'utilisateur peut déjà
  contourner le problème en plaçant chaque paire dans son propre
  sous-dossier (branche « couple » : 1 `.md` + 1 `.json` =
  appariement inconditionnel, D5) — l'amélioration vise à
  éliminer ce contournement manuel —
  [source: md_chunking/contexts.py:70-78, spec 006 D5]
  (confidence: high)
- **Externe** : les algorithmes de « prefix matching » avec
  extension progressive (longest common prefix, LCP) sont un
  pattern classique en indexation (tries, suffix arrays) —
  l'approche proposée (paliers croissants jusqu'à unicité) est
  une variante éprouvée —
  [source: connaissance générale, pas de source externe
  spécifique citée] (confidence: medium)

## Market & Context

- **Coût de l'inaction** : sans amélioration, l'utilisateur doit
  soit renommer manuellement les fichiers pour que leurs 8
  premiers caractères normalisés diffèrent, soit déplacer chaque
  paire dans un sous-dossier dédié — deux contournements manuels
  pénibles sur des corpus volumineux —
  [source: analyse du contournement, contexts.py:70-78]
  (confidence: high)
- **Alternative utilisateur** : traiter les documents un par un
  (fichier individuel = jamais apparié, D8) puis réassocier les
  contextes à la main en aval — perte totale de la valeur de
  `--add-context` —
  [source: spec 006 D8, contexts.py:169-171]
  (confidence: high)
- **Contexte RAG** : l'enrichissement des chunks avec des
  métadonnées bibliographiques (auteur, titre, date, éditeur)
  améliore la pertinence de la récupération — un appariement
  fiable est un prérequis à cette valeur aval —
  [source: assessment contexte-chunkingid/research.md, section
  « Externe » RAG] (confidence: medium)

## Data & Constraints

- **Cause racine mesurée** : `cle_normale()` tronque à 8
  caractères (`contexts.py:38`, `[:8]`) ; le préfixe commun
  `fipeco.fr-00003` normalise en `fipecofr00003` (13 caractères)
  → tronqué à `fipecofr` pour les 6 fichiers —
  [source: contexts.py:31-38, exécution Python de vérification
  2026-10-28] (confidence: high)
- **Longueurs observées** : les stems Fipeco font 23-24 caractères
  (`fipeco.fr-000033-nettoye` = 24, `fipeco.fr-000033-net-0063`
  = 23) — une extension à 20 caractères suffirait pour ce cas,
  mais une limite fixe à 20 casserait les anciens exemples —
  [source: `ls Examples/Pairing/`, calcul manuel]
  (confidence: high)
- **Cas de collision** : 3 paires `.md`/`.json` dans
  `Examples/Pairing/` produisent 3 collisions (tous les `.md`
  ont la clé `fipecofr`, tous les `.json` aussi) —
  [source: `ls Examples/Pairing/`, vérification Python]
  (confidence: high)
- **Tests impactés** : 2 tests d'ambiguïté existants devront être
  adaptés — `test_melee_ambiguite_deux_json_meme_prefixe`
  (lignes 146-153) et `test_melee_ambiguite_json_partage_par_deux_md`
  (lignes 156-164) — car l'extension progressive résoudrait ces
  cas à un palier supérieur —
  [source: tests/unit/test_contexts.py:146-164]
  (confidence: high)
- **Contrat à amender** : D3 (`specs/006-add-context/research.md`),
  le contrat CLI (`specs/006-add-context/contracts/cli.md`,
  section « Niveau mélangé »), et le data-model
  (`specs/006-add-context/data-model.md`, table clé
  d'appariement) —
  [source: specs/006-add-context/] (confidence: high)

## Evidence Against the Idea

- **Complexité ajoutée** : `apparie_niveau()` passerait d'une
  comparaison sur clé fixe à une boucle sur paliers
  (8, 12, 16, 20, …), ce qui complexifie la logique et les tests
  — [ASSUMPTION : évaluation de la complexité, non mesurée]
  (confidence: medium)
- **Changement de comportement** : des cas actuellement ambigus
  (avertissement « Appariement ambigu ») deviendraient résolus
  silencieusement — un utilisateur qui comptait sur l'avertissement
  pour détecter une erreur de nommage perdrait ce signal —
  [source: tests/unit/test_contexts.py:146-164, comportement
  actuel documenté] (confidence: medium)
- **Risque de faux positifs** : si deux paires distinctes
  partagent réellement le même préfixe long (ex.
  `rapport-2024-final.md` et `rapport-2024-final-old.md` avec
  leurs `.json` respectifs), l'extension progressive pourrait les
  apparier incorrectement à un palier où la clé redevient
  identique — [ASSUMPTION : scénario hypothétique, non observé]
  (confidence: low)
- **Spec déjà livrée** : la spec 006 a été fusionnée (PR #12,
  commit `89c6f54`) — modifier son contrat D3 est un changement
  de spec post-livraison, ce qui peut nécessiter une nouvelle
  spec (007) plutôt qu'un amendement —
  [source: git log, `89c6f54 Merge pull request #12`]
  (confidence: high)
- **Alternative plus simple** : au lieu d'une extension
  progressive, l'utilisateur pourrait simplement renommer ses
  fichiers pour que les 8 premiers caractères normalisés
  diffèrent (ex. `f33-nettoye.md` / `f33-net-0063.json`) —
  zéro changement de code, mais pénible manuellement —
  [source: analyse du contournement] (confidence: high)

## Gaps & Open Questions

- [NEEDS CLARIFICATION: bornes de l'extension progressive — paliers
  de 4 en 4 (8, 12, 16, 20, 24, …) ? jusqu'à la longueur maximale
  du stem normalisé ?]
- [NEEDS CLARIFICATION: faut-il un seuil minimum de confiance
  (ex. ratio caractères communs / longueur totale, ou un nombre
  minimum de caractères différenciants) avant d'accepter un
  appariement à un palier supérieur ?]
- [NEEDS CLARIFICATION: faut-il amender D3 de la spec 006-add-context,
  ou créer une spec 007 dédiée (nouvelle feature) ?]
- [NEEDS CLARIFICATION: le dossier `Examples/Pairing/` servira-t-il
  de fixture de test de régression committée, ou reste-t-il un
  exemple local non versionné ?]
- [NEEDS CLARIFICATION: faut-il un flag opt-in (ex.
  `--pairing-progressif`) pour activer l'extension progressive,
  ou le nouveau comportement remplace-t-il silencieusement
  l'ancien ?]
- [NEEDS CLARIFICATION: que faire des cas où l'extension progressive
  atteint la longueur maximale sans trouver d'unicité ? Avertissement
  « Appariement ambigu » (comportement actuel) ou nouveau message ?]

## Sources

- `md_chunking/contexts.py` — code source de `cle_normale()` et
  `apparie_niveau()`
- `specs/006-add-context/research.md` — décisions D1-D9, dont D3
  (normalisation) et D5 (cascade)
- `specs/006-add-context/contracts/cli.md` — contrat CLI, section
  « Niveau mélangé »
- `specs/006-add-context/data-model.md` — table « Clé
  d'appariement normalisée »
- `tests/unit/test_contexts.py` — tests unitaires, dont les 2
  tests d'ambiguïté impactés
- `Examples/Pairing/` — 3 paires Fipeco réelles (6 fichiers)
- `Examples/Extension/` — 3 couples d'exemples existants
  (compatibilité ascendante)
- `.specify/assessments/robust-pairing/intake.md` — idée capturée
- `.specify/assessments/contexte-chunkingid/research.md` —
  assessment amont (contexte RAG, sidecar files)
- `git log` — historique, dont merge PR #12 (`89c6f54`)
- Exécution Python 2026-10-28 — vérification des clés normalisées
  (`fipeco.fr-000033-nettoye` → `fipecofr`, etc.)
