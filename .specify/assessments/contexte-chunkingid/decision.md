# Decision: Contexte et auto-identification dans la sortie JSON

- **Slug**: contexte-chunkingid
- **Decided**: 2026-10-14
- **Verdict**: go
- **Artifacts reviewed**: intake.md, research.md, problem.md,
  concept.md (mis à jour avec la règle en cascade)

## Scorecard

| Critère | Note | Justification (résumé) |
| ---- | ---- | ---- |
| Problem validity | strong | sorties sans métadonnées, corpus préparé |
| Evidence strength | adequate | code lu, exemples vérifiés, prior art cité |
| Value vs. inaction | strong | corpus de contexte inutilisable sinon |
| Feasibility / appetite | strong | appétit small, identifiant déjà calculé |
| Strategic fit | adequate | conforme constitution, deux amendements |
| Risk posture | adequate | risques identifiés et confinés |

Justifications :

- **Problem validity — strong** : le problème est réel et confirmé
  par l'unique utilisateur, qui a préparé un corpus de test complet
  (4 dossiers, ~2,9 Mo de .md, 3 .json de contexte) et a arbitré
  les points flous (chunkingid trivial, normalisation du match,
  priorité dossier/sous-dossier).
- **Evidence strength — adequate** : code et contrats lus, exemples
  vérifiés caractère par caractère, faisabilité de la cascade
  confirmée ; prior art externe cité en snippets de recherche ;
  la demande est déclarée, non observée — acceptable pour un outil
  mono-utilisateur.
- **Value vs. inaction — strong** : sans le mécanisme, le corpus de
  contexte préparé est inutilisable par l'outil et la correspondance
  numéro ↔ contexte se fait à la main à chaque lot.
- **Feasibility / appetite — strong** : appariement pur à trois
  branches testable sur les exemples, deux champs dans l'index,
  aucune dépendance nouvelle ; `chunkingid` restitue une valeur déjà
  calculée.
- **Strategic fit — adequate** : conforme à la constitution
  (II local-first, III sans dépendance, IV simplicité CLI) ; deux
  amendements assumés : FR-008 (récursivité circonscrite) et le
  contrat chunk-json.md (FR-013).
- **Risk posture — adequate** : risques identifiés et confinés
  (normalisation réduite au cas mélangé, collisions de préfixe,
  validation de format) ; les états limites sont des décisions de
  spécification, pas des inconnues bloquantes.

## Verdict & Rationale

**GO.** Le problème est valide et le corpus de test préparé
démontre une intention d'usage réelle et imminente. Les preuves
sont d'un niveau adéquat : code et contrats lus, exemples vérifiés
caractère par caractère, faisabilité de la cascade confirmée contre
les quatre dispositions d'exemples. L'option A (cascade)
recommandée dans concept.md sert directement les cinq buts du
problem.md avec un appétit small crédible : l'appariement s'appuie
sur la co-localisation (usage principal déclaré, robuste), le
préfixe 8 caractères n'est plus qu'un recours pour le cas border,
et `chunkingid` restitue une valeur déjà calculée. Le biais à
surveiller : le cas d'usage aval reste déclaré par l'utilisateur
unique, non observé — acceptable dans un outil personnel
mono-utilisateur, déjà acté pour la spec 003.

## If go — Handoff to `/speckit-specify`

- **Problem**: les sorties du chunking (JSON à plat à 18 chiffres)
  ne portent ni métadonnées bibliographiques ni leur propre
  identité ; l'utilisateur qui prépare un .json de contexte par
  document ne peut pas l'embarquer et doit réassocier à la main
  chaque lot.
- **Chosen approach**: Option A — `--add-context` avec appariement
  en cascade : (1) dossier contenant exactement 1 .md + 1 .json →
  appariement par co-localisation, validation du format attendu
  quel que soit le nom ; (2) dossier de sous-dossiers → même règle
  par sous-dossier, récursivité circonscrite au mode actif ;
  (3) dossier mélangé → préfixe 8 caractères des noms normalisés
  (cas border). Sortie : `document.chunkingid` (stem numérique du
  fichier de sortie, sans `.json`) + `document.context` (7 champs
  verbatim, vides compris). Sans couple : avertissement et
  processus classique inchangé.
- **In scope**: option CLI `--add-context`, cascade d'appariement,
  validation de format des .json de contexte, deux sous-champs dans
  le bloc `document`, amendement FR-008 (récursivité limitée au mode
  actif), amendement du contrat chunk-json.md.
- **Out of scope**: transformation des métadonnées (verbatim
  strict), conversion CSL, modification du nommage/découpage/review,
  fusion multi-contextes, copie du .json en sortie, validation de
  contenu au-delà du format.
- **Success metrics**: les 4 dossiers d'exemples produisent les
  champs attendus verbatim (vides compris) pour chaque couple ;
  `chunkingid` = stem du fichier écrit ; les .md orphelins
  produisent des sorties identiques au processus actuel ; aucun
  couple mal apparié.
- **Carried-forward open questions**:
  - Définition exacte du « format attendu » validé (7 clés exactes ?
    types tolérés, `Auteur(s)` liste ou chaîne ? clés
    supplémentaires acceptées ?) et comportement d'un .json présent
    mais invalide (avertissement + classique, ou échec ?).
  - États intermédiaires : 1 .md + 2 .json, 2 .md + 1 .json —
    bascule en branche 3 ou avertissement + classique ?
  - Table de normalisation exacte du cas mélangé (espaces, accents,
    apostrophes, traits de soulignement/union, casse) — les exemples
    ne couvrent ni espace ni accent dans les 8 premiers caractères.
  - Statut d'un sous-dossier sans .md ou sans .json (avertissement,
    classique, aucun ?).
  - Coexistence du champ `Typologie` du contexte avec
    `document.typologie` (preset) — clés distinctes dans `document`.
  - `--add-context` s'applique-t-il aussi à un .md unique passé en
    direct ?
  - Incrément de `schema_version` (FR-013) ou simple amendement du
    contrat pour des champs optionnels.
