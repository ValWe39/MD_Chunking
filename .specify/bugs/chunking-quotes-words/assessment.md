# Bug Assessment: Guillemets, marqueurs de coupure et niveau mot

- **Slug**: chunking-quotes-words
- **Created**: 2026-10-05
- **Source**: pasted text (trois points de correction issus des
  investigations read-only du 2026-10-05 sur `output/0007` et
  `output/059707222116970002.json`)
- **Verdict**: valid
- **Severity**: medium

## Report (verbatim or summarized)

Trois points à corriger, en lien avec les investigations précédentes :

1. Respecter les guillemets dans le découpage des chunks afin d'éviter,
   dans la limite de la taille des chunks, d'avoir un guillemet ouvert
   non fermé (de type français comme anglo-saxon). Cette règle a une
   valeur hiérarchique plus faible que les règles générales de
   chunking. Prévoir une commande spécifique (« `--guillemets` »),
   paramétrée active par défaut.
2. Si une phrase ou un extrait (guillemet ouvert non fermé) est coupé
   par le chunking, ajouter `...`, que ce soit en début ou en fin de
   chunk. Inclure ces caractères dans le calcul de la taille des
   chunks, en amont de leur réalisation (afin d'éviter que les `...`
   engendrent un dépassement de limite de chunk).
3. Ajouter le découpage par mot à la fin de la hiérarchie de découpage
   des chunks (partie / sous-partie > paragraphe > phrase > mot).
   La règle 2 ci-dessus est alors appliquée.

## Symptom

Les chunks produits peuvent contenir des guillemets déséquilibrés
(`«` ouvert jamais fermé dans le chunk, ou `»` orphelin détaché de sa
citation) : 16/65 chunks d'Exemple3 et 14/111 d'Exemple4 sont
concernés. Par ailleurs, l'overlap entre chunks est quasi absent
(couverture utile 15 % et 12 % des paires intra-part) car le découpage
de phrases ne descend jamais au niveau du mot, et aucune coupure
n'est signalée par des marqueurs.

## Reproduction

1. Produire les chunks d'`Examples/Exemple3/markdown.md` (sortie
   existante : `output/0007/chunks.json`).
2. Constater : chunk 7 se termine par un fragment isolé `»` ; chunk 31
   commence par `» En qualifiant ce réflexe...` (guillemet fermant
   collé à la phrase qui suit la citation) ; chunk 6 contient une
   citation ouverte non fermée (fermée dans le chunk 7).
3. Constater sur `output/059707222116970002.json` (Exemple4) : chunk 44
   commence par `»` suivi d'une ligne vide (queue d'overlap d'un
   caractère) ; 66/98 paires intra-part sans overlap (dernière phrase
   du chunk précédent trop longue pour la fenêtre cible).
4. Vérifier : aucune occurrence de guillemets français dans le code du
   pipeline (`grep` vide sur `md_chunking/*.py`).

## Suspected Code Paths

- `md_chunking/splitter.py:24` : `_SENTENCE_SPLIT` coupe après toute
  ponctuation suivie d'un espace, y compris à l'intérieur d'un span
  `«` ... `»` non fermé et entre une ponctuation et le `»` qui la suit
  (motif ponctuation + espace + `»` : 25 occurrences dans Exemple3,
  22 dans Exemple4). Cause racine des guillemets déséquilibrés.
- `md_chunking/splitter.py` (`_sentence_packs`, `_fill`) : une phrase
  plus longue que `chunk_max` reste indivisible, aucun recours au
  niveau mot.
- `md_chunking/overlap.py:19-32` : `_tail_at_boundary` renvoie `None`
  quand aucune frontière de phrase ne tient dans la fenêtre cible
  (deux échecs sur trois sur les corpus) ; réutilise la même regex
  aveugle aux guillemets, d'où les queues `»` orphelines d'un
  caractère préfixées au chunk suivant.
- `md_chunking/overlap.py:50-56` : budget `chunk_max - length - 2`,
  ne réserve rien pour d'éventuels marqueurs `...`.
- `md_chunking/cli.py:39-56` : aucune option `--guillemets` ;
  `_preset_effectif` et `Preset` à étendre pour le nouveau paramètre.
- `md_chunking/indexer.py:42` : `overlap_pct` enregistré dans les
  params de sortie, à compléter pour le nouveau paramètre.

## Root Cause Hypothesis

Confiance : élevée (confirmé par exécution de la regex sur un
paragraphe réel). Le pipeline n'a aucune notion de guillemets :
`_SENTENCE_SPLIT` coupe à l'intérieur des citations multi-phrases et
détache le `»` de sa phrase ; le remplissage glouton place ensuite
ces fragments dans des chunks sans rapport avec la citation.
Symétriquement, l'absence de recours au niveau mot rend l'overlap
quasi inexistant sur prose à phrases longues, et aucune coupure
n'est marquée. Les trois points demandés forment un correctif
cohérent de cette même zone (frontières de découpe + signalisation
des coupures + dernier recours).

## Proposed Remediation

**Preferred** — un seul correctif en trois volets interdépendants
(assessment unique, cycle unique de fix) :

1. Split conscient des guillemets (`splitter.py`) : itérer sur les
   frontières candidates de `_SENTENCE_SPLIT` et ne retenir que
   celles où aucun guillemet n'est ouvert à la position de coupe,
   pour les deux familles : français (`«` ouvrant, `»` fermant) et
   anglo-saxon (`"` apparié par alternance, guillemet de pouce
   après un chiffre ignoré). Ne jamais couper entre une ponctuation
   finale et le guillemet fermant qui la suit. Règle
   hiérarchiquement plus faible que les règles de chunking : si une
   citation entière ne tient pas dans `chunk_max`, elle reste
   découpée ; le découpage des phrases internes s'applique alors en
   veillant à ce que `«` et `»` restent chacun avec leur fragment.
   Transport du paramètre : champ `guillemets: bool = True` dans
   `Preset` (`presets.py`), option CLI `--guillemets` /
   `--no-guillemets` active par défaut (`cli.py`), enregistrée dans
   les params du JSON (`indexer.py`).
2. Marqueurs de coupure `...` (`splitter.py` + `overlap.py`) : quand
   une frontière de chunk tombe à l'intérieur d'une phrase ou d'une
   citation, suffixer la fin du chunk précédent et préfixer le début
   du chunk suivant par `...`. Faire porter les marqueurs par les
   textes des unités dès le découpage (avant le remplissage glouton)
   pour que `_size` les compte naturellement — garantit que
   `chunk_max` n'est jamais dépassé marqueurs compris. Côté overlap :
   les queues coupées au niveau mot sont préfixées de `...`, budget
   étendu d'autant.
3. Niveau mot en dernier recours (`splitter.py` + `overlap.py`) :
   étendre la hiérarchie à partie > paragraphe > phrase > mot. Dans
   `_sentence_packs`, une phrase plus longue que `chunk_max` est
   désormais découpée aux frontières de mots (marqueurs `...`
   appliqués) au lieu de rester atomique ; dans
   `_tail_at_boundary`, ajouter le recours aux mots quand aucune
   frontière de phrase ne tient dans la fenêtre cible (résultat
   mesuré : couverture d'overlap utile passerait de 15 % à 85 %
   d'Exemple4 et de 12 % à 94 % d'Exemple3 ; longueur moyenne
   91-100 caractères). Imposer en parallèle une longueur minimale de
   queue (30 caractères) pour éliminer les queues d'un ou deux
   caractères de type `»`.

**Alternatives** :

- Normalisation typographique en amont (`normalizer.py`) : resserrer
  `? »` en `?»` (47 occurrences sur les deux corpus). Peu invasif
  mais insuffisant seul : ne traite ni les citations multi-phrases,
  ni les guillemets anglo-saxons, ni le niveau mot. À faire en
  complément, pas en substitution.
- Spans `«` ... `»` quasi-atomiques comme les blocs de code et
  tableaux : rejeté — les longues citations dépasseraient `chunk_max`
  et contrediraient la fourchette du preset.

**Files likely to change** :

- `md_chunking/splitter.py`
- `md_chunking/overlap.py`
- `md_chunking/presets.py`
- `md_chunking/cli.py`
- `md_chunking/indexer.py`
- `md_chunking/normalizer.py` (complément typographique, optionnel)
- `tests/unit/test_splitter.py` (créer)
- `tests/unit/test_overlap.py` (créer)
- `tests/unit/test_presets.py`, `tests/integration/test_split.py`,
  `tests/integration/test_cli.py`
- `README.md` (nouvelle option, nouvelle hiérarchie, marqueurs)

**Tests to add or update** :

- équilibre des guillemets français et anglo-saxons par chunk quand
  la citation tient dans `chunk_max` (chunks 7 et 31 d'Exemple3 en
  régression) ;
- citation plus longue que `chunk_max` : découpée sans jamais
  produire de fragment réduit à un guillemet ;
- marqueurs `...` présents en début et fin de chunk à chaque coupure
  intra-phrase ou intra-citation, et longueur des chunks (marqueurs
  compris) inférieure ou égale à `chunk_max` ;
- phrase plus longue que `chunk_max` : découpée aux frontières de
  mots (fin de l'indivisibilité) avec marqueurs ;
- overlap : queue au niveau mot en dernier recours, préfixée `...`,
  jamais inférieure à 30 caractères, jamais un guillemet isolé ;
- `--guillemets` actif par défaut, `--no-guillemets` désactive
  (paramètre visible dans le JSON de sortie) ;
- revalidation des corpus réels : plus aucun chunk déséquilibré sur
  Exemple3/Exemple4, couverture d'overlap d'au moins 80 % des paires
  intra-part.

## Risks & Considerations

- **Contradiction partielle avec la spec 001** : FR-003, FR-005 et la
  décision D6 posent la phrase comme frontière indivisible en dernier
  recours et rejettent l'overlap glissant. Les points 2 et 3
  (marqueurs, niveau mot) inversent volontairement ces choix —
  `specs/001-md-chunking/spec.md` et `research.md` doivent être
  amendés en parallèle, sinon le conform-check speckit échouera.
- **Changement de comportement par défaut** : les phrases plus
  longues que `chunk_max` n'étaient jamais coupées (atomiques) ;
  elles le seront désormais au niveau mot avec marqueurs. Les
  consommateurs des JSON qui s'appuient sur `atomic=True` pour ces
  phrases doivent être identifiés.
- **Budget de taille** : les marqueurs `...` (3 caractères) et la
  queue d'overlap au niveau mot doivent être réservés dans le budget
  avant remplissage, sinon des chunks dépasseront `chunk_max`
  (règle 2 explicite du demandeur).
- **Guillemets anglo-saxons** : l'appariement de `"` est ambigu
  (ouverture et fermeture identiques) ; l'heuristique par alternance
  est fragile sur du texte contenant des pouces (`6"`) ou des
  apostrophes typographiques. Commencer par l'alternance simple avec
  exemption des chiffres, et documenter la limite.
- **Choix du marqueur** : le demandeur spécifie `...` (trois points
  ASCII) ; la convention typographique française pour une omission
  dans une citation est `[...]`. Décision à trancher au moment du
  fix ; le présent assessment retient `...` comme demandé.
- **Performance** : le suivi de l'état ouvert ou fermé des guillemets
  lors du split de phrases est linéaire, impact négligeable sur des
  documents de quelques centaines de kilo-octets.

## Open Questions

- [NEEDS CLARIFICATION: `--guillemets` doit-il apparaître dans le
  JSON de sortie (section `params`) comme les autres options —
  recommandé oui — et sous quelle forme booléenne ?]
- [NEEDS CLARIFICATION: la longueur minimale de queue d'overlap
  (recommandée d'au moins 30 caractères) est-elle validée comme
  règle, ou reste-t-elle un paramètre interne non exposé ?]
- [NEEDS CLARIFICATION: pour les guillemets anglo-saxons,
  l'appariement par alternance simple est-il acceptable en première
  version, ou faut-il un état plus robuste (détecteur d'ouverture
  et de fermeture par contexte) ?]
