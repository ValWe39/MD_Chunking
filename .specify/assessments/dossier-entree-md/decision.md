# Decision: Traiter un dossier de Markdown en une commande

- **Slug**: dossier-entree-md
- **Decided**: 2026-10-05
- **Verdict**: go
- **Artifacts reviewed**: intake.md | research.md | problem.md | concept.md

## Scorecard

| Criterion | Rating |
| --------- | ------ |
| Problem validity | strong |
| Evidence strength | adequate |
| Value vs. inaction | strong |
| Feasibility / appetite | strong |
| Strategic fit | strong |
| Risk posture | adequate |

Justifications :

- **Problem validity (strong)** : cas d'usage réel du projet (corpus
  `Examples/`, README.md:134-136) et public cible documenté
  (débutants PowerShell, README.md:3-21) privés de toute commande
  corpus par le comportement actuel (dossier rejeté au code 2,
  cli.py:96-98)
- **Evidence strength (adequate)** : preuves internes directes (code et
  contrats lus) ; comportement Windows/glob corroboré par quatre
  sources indépendantes en snippets de recherche (research.md), mais
  aucune page fetchée — confiance medium assumée dans research.md
- **Value vs. inaction (strong)** : l'inaction laisse le public cible au
  fichier-par-fichier ou à une syntaxe d'énumération PowerShell ;
  l'Option B résout en une commande indépendante du shell
  (problem.md, Goals et Metrics servies directement)
- **Feasibility / appetite (strong)** : Option B façonnée avec appétite
  small, empreinte confinée au bloc de validation d'entrée,
  boucle/compteur/nommage inchangés (research.md, Data & Constraints) ;
  le lot multi-fichiers existe déjà et est testé
- **Strategic fit (strong)** : sert le chemin d'usage documenté
  (Windows/PowerShell) ; sans nouvelle option CLI ni récursivité, la
  tension YAGNI (constitution IV) est neutralisée par l'empreinte
  minimale
- **Risk posture (adequate)** : risques identifiés et bornés : changement
  du contrat CLI 001 (précédent feature 003), cas limites à trancher
  en spécification (dossier vide, mélange, extensions, ordre) ; le
  contre-précédent img2pdf écarte proprement l'expansion de motifs

## Verdict & Rationale

Go. Le problème est réel et observé dans l'usage du projet, la valeur
depasse clairement l'inaction pour le public cible du README, et
l'Option B recommandée par le concept — validée par l'utilisateur —
tient l'appétite small avec une empreinte confinée à la validation
d'entrée. L'exigence d'origine « sans modifier substantiellement
l'outil » est satisfaite par construction : la boucle de traitement,
le compteur d'occurrence et le nommage des sorties ne bougent pas. Le
seule score sous « strong » porte sur la force des preuves externes
(snippets de recherche, aucune page fetchée) et sur les cas limites
encore ouverts — tous deux tranchables pendant la spécification sans
remettre en cause la direction ; aucun ne justifie un retour en
clarification.

## If go — Handoff to `/speckit-specify`

- **Problem**: un utilisateur (débutant PowerShell, public cible du
  README) ne peut pas traiter en une commande les `.md` d'un dossier,
  ni par l'outil ni par le shell, Windows n'étendant pas les jokers
  pour les commandes natives.
- **Chosen approach**: Option B — la CLI accepte un chemin de
  dossier à côté des fichiers actuels ; les `.md` de sa surface
  (sans récursivité) sont traités en tri alphabétique, comme s'ils
  avaient été passés un par un.
- **In scope**: argument dossier dans la validation d'entrée ;
  filtre `.md` ; ordre déterministe ; mise à jour du contrat CLI et
  du README (commande corpus en une étape) ; tests d'intégration et
  unitaires ; possibilité de mélanger dossier et fichiers
  individuels (à trancher en spécification).
- **Out of scope**: récursivité, motifs jokers, filtrage/inclusion/
  exclusion, tri configurable, parallélisation, nouvelles options
  CLI (`--recursive`, `--include`), toute écriture hors `--output`.
- **Success metrics**: k `.md` → 2k sorties en une commande ;
  occurrences croissantes et reproductibles pour un même ensemble
  (SC-005) ; seuls les `.md` traités parmi n fichiers ; README en
  une étape accessible au débutant.
- **Carried-forward open questions**:
  - Dossier vide ou sans `.md` : échec rapide au code 2 ou succès
    silencieux ? (piste : code 2, cohérent avec la Config Validation
    de la constitution)
  - Mélange dossier + fichiers individuels autorisé dans une même
    invocation ? (piste : oui, résolution avant validation)
  - Extensions : `.md` seul, insensible à la casse sous Windows ?
    (piste : `.md` seul, casse insensible, `.markdown` refusé)
  - Tri alphabétique du nom de fichier suffit-il pour SC-005 ?
    (piste : oui, tri sur le chemin complet)
  - Confirmation utilisateur que l'empreinte « validation d'entrée
    dans `parse_args` uniquement » satisfait « sans modifier
    substantiellement »
