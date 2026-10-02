# Research: Compteur de tokens dans le rapport de relecture

**Feature**: specs/002-compteur-tokens-chunks | **Date**: 2026-10-02
**Sources**: spec.md (dont Clarifications du 2026-10-02),
assessment compteur-tokens-chunks (research.md, concept.md,
decision.md), `.specify/memory/constitution.md` v1.4.0, code
`md_chunking/{models,reviewer,indexer}.py`.

## D1 — Emplacement du calcul : au rendu, pas dans le modèle

- **Decision**: l'estimation est calculée dans `reviewer.py` au
  moment du rendu, à partir de `chunk.text` ; l'entité `Chunk` et
  `indexer.py` ne sont pas modifiés.
- **Rationale**: FR-T07 (index JSON inchangé) est garanti par
  construction — l'estimation ne transite par aucune structure de
  données partagée et ne peut donc fuiter dans une future
  sérialisation ; la responsabilité reste celle du seul
  consommateur.
- **Alternatives considered**: champ calculé sur `Chunk` — inutile
  et risqué (le data-model de la feature 001 fait de `length` la
  seule mesure de taille) ; module dédié `tokens.py` —
  surdimensionné pour une constante et une division (YAGNI).

## D2 — Formule : division entière, arrondi supérieur

- **Decision**: `estimate_tokens(text) = ceil(len(text) / 4)` avec
  la constante `RATIO_CHARS_PER_TOKEN = 4` ; résultat entier,
  supérieur ou égal à 1 pour tout chunk (texte jamais vide par
  contrat du modèle).
- **Rationale**: FR-T02 (ratio constant, arrondi supérieur,
  déterministe) ; l'arrondi supérieur penche du côté du risque,
  préférable pour la détection de dépassement ; division entière :
  aucun flottant, aucune divergence entre plateformes (SC-T04).
- **Alternatives considered**: arrondi au plus proche — peut
  sous-estimer un chunk limite ; flottant affiché — bruit visuel
  et source de nondéterminisme.

## D3 — Affichage : ligne de métadonnée + mention d'en-tête

- **Decision**: par chunk, une ligne ajoutée à la liste des
  métadonnées existantes : `- tokens (estimation) : ≈ N` ; en tête
  du rapport, sous le titre, une ligne indiquant que les tokens
  sont estimés à ~4 caractères par token, de façon approximative
  et indépendante de tout modèle ; l'en-tête
  `## Chunk <ref> — <N> car.` est conservé tel quel.
- **Rationale**: FR-T01 (marquage « ≈ »), FR-T04 (complément,
  jamais remplacement), FR-T05 (mention d'en-tête avec ratio, sans
  nom de modèle) ; la ligne suit le format des métadonnées
  existantes (frontière, partie, page) — aucune nouvelle structure
  de rendu.
- **Alternatives considered**: remplacer le « X car. » de
  l'en-tête — interdit par FR-T04 ; afficher l'estimation dans
  l'en-tête du chunk — surcharge la ligne de titre déjà longue.

## D4 — Extensibilité option B (FR-T08)

- **Decision**: le libellé « (estimation) » distingue la valeur
  affichée ; un compte exact futur pourra être rendu sous la forme
  `- tokens (exact, <tokenizer>) : N` sans changer la structure de
  la liste de métadonnées.
- **Rationale**: FR-T08 ; la décision GO de l'assessment prévoit
  « A puis B » sans refonte.
- **Alternatives considered**: format typé clé/valeur —
  surdimensionné pour un rapport de relecture humain.

## D5 — Stratégie de test

- **Decision**: tests unitaires dans `tests/unit/test_reviewer.py`
  (estimate_tokens : multiples exacts, arrondi supérieur, texte
  minimal ; rendu : ligne présente par chunk, mention d'en-tête
  présente, « X car. » conservé, déterminisme sur deux appels) ;
  test d'intégration dans `tests/integration/test_cli.py`
  (exécution complète sur un exemple réel : review.md contient
  les estimations, l'index JSON ne contient aucun champ tokens).
- **Rationale**: couverture directe de FR-T01 à FR-T09 et de
  SC-T01 à SC-T05 ; le test « index sans champ tokens » verrouille
  FR-T07 contre toute régression future.
- **Alternatives considered**: calibrage du ratio sur le corpus
  complet — aucun oracle exact disponible sans tokenizer (hors
  périmètre, cf. assessment).
