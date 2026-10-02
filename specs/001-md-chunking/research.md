# Research: Chunking de Markdown avec sortie JSON

**Feature**: specs/001-md-chunking | **Date**: 2026-10-02
**Sources**: assessment md-chunking-json-output (research, concept,
decision), spec.md, `.specify/memory/constitution.md` v1.4.0,
corpus local `Examples/` (4 documents réels).

## D1 — Socle technique : Haystack étendu par composants maison

- **Decision**: pipeline Haystack (deepset) comme socle
  (`MarkdownToDocument`, `MarkdownHeaderSplitter`), complété par
  des composants maison : normalisation des entrées, overlap
  structurel, export JSON normalisé, rendu de relecture.
- **Rationale**: les métadonnées natives de Haystack (`source_id`,
  `page_number`, `split_id`, `split_idx_start`, hiérarchie de
  titres) recouvrent la plupart des champs JSON demandés ; le
  découpage sections → split secondaire est le comportement natif
  du `MarkdownHeaderSplitter` ; contrainte utilisateur respectée
  (ni LangChain ni LlamaIndex) ; éditeur souverain (Berlin),
  licence Apache-2.0 conforme à la constitution.
- **Alternatives considered**: (A) 100% maison — contrôle total
  mais réinvente hiérarchie de titres et splits par unités, sans
  interopérabilité future ; (C) Haystack tel quel — rapide mais
  sans overlap intelligent, sans JSON conforme, sans rendu de
  relecture ; Chonkie (intégration Haystack) — retenue en repli si
  les splitters natifs s'avèrent insuffisants, non retenue d'abord
  (YAGNI, une dépendance de moins).

## D2 — Version de Haystack et contournement du bug #12686

- **Decision**: épingler `haystack-ai` en version 2.x stable dans
  les métadonnées du projet au premier build ; le composant maison
  d'overlap ignore les chunks « overlap-only » (fenêtre entièrement
  couverte par le chunk précédent) pour contourner le bug #12686
  des modes caractère.
- **Rationale**: le bug est documenté (issue #12686, corrigé en
  mode token seulement) ; un filtrage maison par chevauchement
  est déterministe et testable.
- **Alternatives considered**: attendre un correctif amont — non
  bloquant pour nous grâce au filtrage ; passer au mode token —
  incompatible avec l'unité « caractères » décidée en spec
  (FR-002).

## D3 — Télémétrie Haystack (constitution III)

- **Decision**: vérifier au premier build qu'aucune télémétrie
  n'est active (recherche de variables d'environnement de
  télémétrie propres à Haystack et de trafic sortant) ; si un
  mécanisme existe, le désactiver explicitement et le consigner
  dans le README du projet.
- **Rationale**: la constitution interdit trackers et télémétrie ;
  l'ancienne télémétrie de Haystack 1.x n'existe plus en 2.x mais
  la vérification doit être documentée, pas supposée.
- **Alternatives considered**: supposer l'absence de télémétrie —
  rejeté : une exigence NON NÉGOCIABLE se prouve, elle ne se
  suppose pas.

## D4 — Unité de mesure : caractères

- **Decision**: tailles de chunks et overlap comptés en
  caractères (défaut 100–1000, overlap 15%).
- **Rationale**: réponse utilisateur Q1 du 2026-10-02 ;
  déterministe, indépendant de tout tokenizer, cohérent avec le
  rendu de relecture humain ; la limite du modèle d'embedding
  en aval reste la responsabilité du consommateur du JSON (hors
  périmètre).
- **Alternatives considered**: tokens — standard du marché mais
  introduit une dépendance à un tokenizer et un comptage
  variable ; mots — approximatif. Écartées par décision
  utilisateur.

## D5 — Normalisation des entrées irrégulières

- **Decision**: composant maison `normalizer` en tête de pipeline :
  unification des fins de ligne (CRLF/LF, constat des 4 exemples),
  neutralisation ou réécriture des titres emboîtés dans des puces
  de liste (motif `* ## [` de l'Exemple1) avant tout découpage.
- **Rationale**: le `MarkdownHeaderSplitter` ne reconnaît pas les
  titres ATX noyés dans des listes ; l'Exemple1 compte 210 titres
  dans ce état — sans normalisation, tout le document basculerait
  sur du paragraphes/phrases sans métadonnées de partie.
- **Alternatives considered**: laisser Haystack découper tel quel
  — produirait des chunks sans hiérarchie sur l'Exemple1 ;
  réécrire les titres en titres propres systématiquement —
  risqué (faux positifs), la neutralisation est plus sûre.

## D6 — Overlap structurel

- **Decision**: composant maison `overlap` : l'overlap est découpé
  selon les mêmes frontières que le chunk (parties, sinon
  paragraphes, sinon phrases) et tronqué à 20% max de la taille du
  chunk ; filtrage des fenêtres entièrement redondantes (D2).
- **Rationale**: l'overlap natif de Haystack est un compte de
  mots/caractères sans respect des frontières ; la spec exige un
  overlap « intelligent » (FR-005).
- **Alternatives considered**: overlap caractère glissant simple —
  coupe les phrases au milieu, contraire à la spec.

## D7 — Corpus de développement : dossier Examples/

- **Decision**: les 4 documents de `Examples/` servent de corpus
  de validation principal (tests d'intégration, mesures de
  volumétrie ~50–150 chunks) ; ces fichiers étant gitignorés,
  des mini-fixtures dérivées (extraits réduits, mêmes
  pathologies : titres en listes, prose longue, CRLF/LF mixtes)
  sont committées dans `tests/fixtures/` pour les tests
  reproductibles partout ; les tests Examples-dependent sont
  marqués et sautés proprement si le dossier est absent.
- **Rationale**: demande utilisateur explicite (2026-10-02) ;
  les 4 exemples couvrent les typologies visées (article web,
  web scrappé bruité, littérature longue prose, livre structuré).
- **Alternatives considered**: committer Examples/ — rejeté :
  données volumineuses (44–110 KB) exclus de la version par
  décision utilisateur ; tests uniquement sur fixtures
  synthétiques — rejeté : les pathologies réelles (210 titres
  malformés) ne s'inventent pas.

## D8 — Schéma JSON et contrat CLI

- **Decision**: le schéma JSON est défini dans
  [data-model.md](data-model.md) et documenté comme contrat dans
  [contracts/chunk-json.md](contracts/chunk-json.md) ; le contrat
  CLI dans [contracts/cli.md](contracts/cli.md). Aucun
  consommateur externe n'impose de format (réponse utilisateur
  Q3), la spec fait foi (FR-013).
- **Rationale**: stabilité et auditabilité ; le rendu de relecture
  est un fichier Markdown annoté par document (réponse Q2).
- **Alternatives considered**: schéma aligné sur un pipeline
  Mistral hypothétique — rejeté : aucun consommateur existant.

## Bilan

Toutes les inconnues du contexte technique sont résolues (D1–D8).
Le point restant est une vérification de build (D3), pas une
inconnue de conception.
