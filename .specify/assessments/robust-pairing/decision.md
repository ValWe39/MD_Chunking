# Decision: Appariement robuste .md/.json sur préfixes longs

- **Slug**: robust-pairing
- **Decided**: 2026-10-28
- **Verdict**: go
- **Artifacts reviewed**: intake.md, research.md, problem.md,
  concept.md

## Scorecard

- **Problem validity**: strong — problème observé sur exécution
  réelle (3 avertissements « Appariement ambigu », 0 contexte
  embarqué), cause racine identifiée (`[:8]` dans
  `cle_normale`), preuves concrètes (`Examples/Pairing/`)
- **Evidence strength**: strong — sources primaires (code,
  tests, exécution Python vérifiée), recherche haute
  confiance, peu d'ASSUMPTION non vérifiées
- **Value vs. inaction**: strong — coût de l'inaction
  documenté (contournements manuels systématiques), valeur
  claire (appariement automatique = prérequis à la valeur RAG
  de `--add-context`)
- **Feasibility / appetite**: strong — Option A retenue,
  appetite small (jours), portée confinée à `contexts.py` +
  tests, aucune dépendance nouvelle
- **Strategic fit**: strong — aligné avec la philosophie du
  projet (robustesse, pas de contournement manuel) ; D3 de la
  spec 006 reconnaît déjà la fragilité du préfixe fixe ;
  100 % local, déterministe
- **Risk posture**: adequate — risques identifiés (faux
  positifs, changement de comportement, tests à adapter) avec
  mitigations proposées (tests ciblés, spécification claire) ;
  inconnues restantes sont des détails de spécification, pas
  des bloqueurs

## Verdict & Rationale

**GO.** Le problème est réel, observé et bien compris. La
recherche est solide (confiance haute, sources primaires). La
solution retenue (Option A — extension progressive par paliers)
atteint les trois goals du problème avec un appetite small et
une portée confinée. Les risques sont identifiés et maîtrisables
par la spécification et les tests. L'Option B est rejetée
(casse la compatibilité ascendante), l'Option C est rejetée (ne
résout pas le problème). Aucun critère n'est `weak` ou
`unknown` ; le seul critère `adequate` (risk posture) reflète
des inconnues de détail (paliers exacts, seuil de confiance)
qui seront tranchées en spécification, pas des bloqueurs de
décision.

## If go — Handoff to `/speckit-specify`

- **Problem**: lorsqu'un dossier contient plusieurs paires
  `.md`/`.json` partageant un préfixe normalisé commun > 8
  caractères, l'appariement échoue silencieusement
  (« Appariement ambigu », aucun contexte embarqué), bien que
  les paires soient identifiables par un humain et les `.json`
  valides.
- **Chosen approach**: Option A — extension progressive par
  paliers (8 → 12 → 16 → 20 → … jusqu'à unicité ou longueur
  maximale) dans `apparie_niveau()` ; `cle_normale()` retourne
  la chaîne normalisée complète sans troncature.
- **In scope**: modification de `cle_normale()` et
  `apparie_niveau()` dans `md_chunking/contexts.py` ;
  adaptation des 2 tests d'ambiguïté existants ; ajout de
  tests de régression (cas Fipeco, zéro faux positif) ;
  amendement de D3 (spec 006) ou création d'une spec 007 ;
  mise à jour du contrat CLI et du data-model ; utilisation de
  `Examples/Pairing/` comme fixture de test.
- **Out of scope**: format du `.json` de contexte (7 clés) ;
  branche « couple » (1 `.md` + 1 `.json`) ; comportement sans
  `--add-context` ; dépendances externes ; contenu des fichiers
  `.md`/`.json` ; nommage des sorties (18 chiffres) ; flag
  opt-in ; seuil de confiance configurable ; messages
  d'avertissement existants.
- **Success metrics**: `Examples/Pairing/` 0/3 → 3/3 ;
  `Examples/Extension/` 3/3 → 3/3 (pas de régression) ;
  avertissements « Appariement ambigu » sur `Examples/Pairing/`
  3 → 0 ; faux positifs 0 → 0 ; suite de tests complète
  maintenue verte.
- **Carried-forward open questions**: paliers exacts (de 4 en
  4 ? jusqu'où ?) ; seuil de confiance avant appariement à un
  palier supérieur ; distinction ambiguïté « résoluble » vs
  « réelle » ; sort final de l'avertissement « Appariement
  ambigu » quand la longueur maximale est atteinte sans unicité
  ; `Examples/Pairing/` comme fixture committée ou locale ;
  amendement D3 vs spec 007 dédiée.
