# Problem Definition: Visibilité sur le budget de tokens à la relecture

- **Slug**: compteur-tokens-chunks
- **Created**: 2026-10-02
- **Inputs used**: intake.md + research.md

## Problem Statement

Au moment de relire le découpage avant embedding, l'utilisateur de
md_chunking n'a aucune visibilité sur le nombre de tokens de chaque
chunk : le rapport de relecture n'exprime les tailles qu'en caractères
(unité FR-002), et la traduction caractères → tokens demande soit une
approximation mentale incertaine, soit un outil externe — les
compteurs en ligne transmettant le contenu du document à un tiers,
contrairement au principe local-first. La douleur se concentre sur les
cas proches des limites : presets à 2000 caractères et entités
atomiques (blocs de code, tableaux) déjà signalées comme hors
fourchette.

## Affected Users & Stakeholders

- **Users**: l'utilisateur unique de md_chunking (persona : une
  personne traitant quelques dizaines de documents Markdown, ~50–150
  chunks par document, avant de les injecter dans un pipeline
  d'embedding) — il doit aujourd'hui deviner ou vérifier ailleurs si
  un chunk dépassera la fenêtre de tokens du modèle aval.
- **Stakeholders**: le même individu, en tant que mainteneur — il
  arbitre la conformité à la constitution (II local-first, III sans
  trackers, IV YAGNI) et la décision D4 qui a placé la limite de
  tokens hors périmètre de l'outil.

## Goals

- Permettre à l'utilisateur, pendant la relecture (FR-008), de
  repérer les chunks dont la taille en tokens risque de dépasser le
  budget du modèle d'embedding visé — sans quitter sa machine ni
  utiliser d'outil tiers.
- Supprimer l'incitation à coller des chunks dans des compteurs de
  tokens en ligne, incompatible avec la constitution II.
- Préserver le déterminisme (SC-005) et le fonctionnement hors-ligne
  (SC-006) de l'outil quelle que soit l'option retenue.
- Rendre explicite le caractère approximatif de l'information
  affichée pour éviter qu'elle soit prise pour un compte exact
  (avertissement récurrent des sources, research.md).

## Non-Goals

- Changer l'unité de découpage : FR-002 (fourchette et overlap en
  caractères) et la décision D4 restent intacts — l'information
  tokens est affichée, jamais une contrainte de découpage.
- Faire respecter automatiquement une limite de tokens : la
  responsabilité de la compatibilité avec le modèle aval reste celle
  du consommateur (rationale D4).
- Produire un compte exact à visée de facturation ou de coût API.
- Couvrir l'ensemble des tokenizers du marché ou l'interopérabilité
  multi-modèles.

## Success Metrics

- 100 % des chunks du rapport de relecture portent une information de
  taille en tokens (baseline : 0 % aujourd'hui — seule la longueur en
  caractères est affichée).
- Un document d'environ 50 chunks peut être passé au crible « quels
  chunks risquent de dépasser le budget de tokens ? » sans outil
  externe et dans le temps de relecture déjà budgété par SC-004
  (< 10 minutes) (baseline : impossible aujourd'hui sans outil
  externe).
- La sortie reste bit-à-bit identique entre deux exécutions à
  paramètres constants (SC-005) (baseline : conforme — ne doit pas
  régresser).
- Zéro appel réseau lors du traitement (SC-006) (baseline :
  conforme — ne doit pas régresser).
- Qualitatif : l'utilisateur sait, à la lecture du rapport, si le
  nombre affiché est approximatif ou exact, et vis-à-vis de quel
  modèle.

## Cost of Inaction

Avec les défauts actuels (100–1000 caractères ≈ 25–330 tokens), le
risque de dépassement est faible face à une fenêtre de 8191 tokens ;
l'inaction ne bloque donc pas l'usage courant. Le coût se manifeste
dans trois scénarios : (1) presets à 2000 caractères ou entités
atomiques longues, où le dépassement de fenêtres plus étroites
(ex. 512 tokens) devient plausible et n'est découvert qu'à l'échec de
l'appel d'embedding ; (2) persistance de l'approximation mentale,
source d'erreurs de planification ; (3) tentation récurrente d'un
compteur en ligne, qui contredit la constitution II à chaque usage.
Aucun de ces coûts n'est catastrophique — ils sont réels mais bornés.

## Open Questions

- [NEEDS CLARIFICATION: quel(s) modèle(s) d'embedding en aval sont
  visés ? Détermine la précision requise — heuristique ou tokenizer
  exact — et le ratio applicable.]
- [NEEDS CLARIFICATION: le compte de tokens doit-il figurer
  uniquement dans le rapport de relecture, ou aussi dans l'index JSON
  consommable par le pipeline aval ?]
- [NEEDS CLARIFICATION: précision attendue — ordre de grandeur
  suffisant, ou écart maximal toléré vis-à-vis d'un tokenizer de
  référence ?]
- [NEEDS CLARIFICATION: format d'affichage — ligne de métadonnées
  additionnelle ou remplacement du « X car. » ? Faut-il un total par
  document ?]
- [NEEDS CLARIFICATION: si un tokenizer exact est requis, quelle
  stratégie de conformité à la constitution II — vocabulaire committé
  dans le dépôt (~2 Mo) ou acceptation d'un téléchargement au
  premier build ?]
