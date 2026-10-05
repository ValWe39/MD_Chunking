# Bug Fix: Guillemets, marqueurs de coupure et mots dans le découpage

- **Slug**: chunking-quotes-words
- **Fixed**: 2026-10-05
- **Assessment**: ./assessment.md
- **Status**: applied

## Summary

Le découpage respecte désormais les guillemets (français et
anglo-saxons) grâce à une option `--guillemets` active par défaut,
marque par `...` toute coupure de phrase ou de citation entre chunks
(marqueurs comptés dans la taille via réservation en amont), et
descend aux frontières de mots en dernier recours — côté chunks comme
côté overlap, avec une queue d'overlap minimale de 30 caractères qui
élimine les queues d'un ou deux caractères de type `»`.

## Changes

- `md_chunking/presets.py` (modifié) : champ `guillemets: bool = True`
  dans `Preset`.
- `md_chunking/models.py` (modifié) : frontière `mot` acceptée
  (validation et docstring).
- `md_chunking/cli.py` (modifié) : option `--guillemets` /
  `--no-guillemets` (BooleanOptionalAction, défaut actif),
  transportée dans le preset effectif.
- `md_chunking/indexer.py` (modifié) : paramètre `guillemets` tracé
  dans le JSON de sortie.
- `md_chunking/splitter.py` (modifié) : split de phrases conscient des
  guillemets (aucune coupe dans une citation ouverte, ni entre
  ponctuation et fermant) ; `_word_packs` pour les phrases plus
  longues que `chunk_max` (règle 3, marqueurs `...` comptés) ;
  `_mark_cut_quotes` marque les citations tranchées entre chunks ;
  réservation de 6 caractères dans les sections contenant des
  guillemets.
- `md_chunking/overlap.py` (modifié) : recours aux mots en dernier
  recours (`_word_tail`), queue minimale de 30 caractères, marqueurs
  `...` sur les queues coupées, budget étendu (séparateur et
  marqueurs), retrait du marqueur de fin du donneur avant extraction.
- `tests/unit/test_splitter.py` (ajouté) : dix tests — citation
  multi-phrases, fermant détaché (ancien comportement épinglé),
  guillemets anglo-saxons, exemption pouce (`6"`), mots et marqueurs
  avec reconstruction, citation tranchée marquée, option désactivée,
  citation entière, unité atomique jamais marquée.
- `tests/unit/test_overlap.py` (ajouté) : six tests — queue au
  niveau mot marquée, queue minuscule remplacée, queue complète sans
  marqueur, receveur plein, pas d'overlap inter-parties, queue de
  citation marquée des deux côtés.
- `tests/unit/test_presets.py`, `tests/unit/test_indexer.py`,
  `tests/integration/test_split.py`, `tests/integration/test_cli.py`
  (modifiés) : défaut actif, `--no-guillemets`, paramètre `guillemets`
  dans le JSON, frontière `mot` admise.
- `README.md` (modifié) : option `--guillemets`, hiérarchie partie >
  paragraphe > phrase > mot, marqueurs.

## Diff Highlights (optional)

Split conscient des guillemets (`splitter.py`) — la frontière n'est
retenue que si aucune citation n'est ouverte et si le fermant ne suit
pas immédiatement :

```python
for m in _SENTENCE_SPLIT.finditer(text):
    consumed = text[pos : m.start()]
    fr += quote_balance(consumed)
    en += english_quote_count(consumed)
    pos = m.start()
    if fr > 0 or en % 2 == 1 or text[m.end() :].startswith("»"):
        continue  # frontiere refusee : citation ouverte
    segments.append(text[start : m.start()])
    start = m.end()
```

Réservation des marqueurs en amont (`splitter.py`, `split_document`) :

```python
if preset.guillemets and any(c in text for c in _QUOTE_CHARS):
    eff = replace(preset, chunk_max=preset.chunk_max - _MARKER_BUDGET)
```

Dernier recours aux mots dans l'overlap (`overlap.py`) :

```python
tail = _tail_at_boundary(source, target)
if not tail or len(tail) < _MIN_TAIL:
    tail = _word_tail(source, target)  # regle 3
```

## Tests Added or Updated

- `test_split_respecte_une_citation_multiphrases` — le fermant n'est
  plus détaché de sa citation (régression du bug d'origine).
- `test_split_sans_guillemets_detache_le_fermant` — l'ancien
  comportement est épinglé pour `--no-guillemets`.
- `test_phrase_trop_longue_descend_aux_mots_avec_marqueurs` —
  règle 3, marqueurs comptés dans la taille, reconstruction exacte
  des mots.
- `test_citation_tranchee_par_chunks_marquee` — règle 2 : `...` en
  fin du premier chunk et en tête du second.
- `test_queue_aux_mots_quand_la_phrase_est_trop_longue` — queue
  d'overlap marquée `...` quand aucune frontière de phrase ne tient.
- `test_queue_minuscule_remplacee` — plus de queue `»` d'un caractère.
- `test_receveur_plein_ne_depasse_jamais_chunk_max` — budget
  marqueurs compris, jamais de dépassement.
- Complet : 89 tests verts, mises à jour incluses.

## Local Verification

- Commande exécutée : `.venv/Scripts/python.exe -m pytest tests -q`
  → 89 tests passés.
- Corpus réel (Exemple3 et Exemple4, preset documentation, calcul en
  mémoire sans écriture ni consommation du compteur) :
  - overlap utile (au moins 30 caractères) : Exemple3 46/48 paires
    intra-part (96 %, était 12 %) ; Exemple4 87/99 (88 %, était
    15 %) ;
  - chunks commençant par un fermant orphelin `»` : 0 (était 2 par
    corpus) ;
  - chunks hors fourchette (non atomiques) : 0 ;
  - toute citation tranchée entre chunks porte `...` des deux côtés ;
    les déséquilibres restants proviennent soit de queues d'overlap
    marquées (copies, par conception), soit d'une citation jamais
    refermée dans la source Exemple3 ligne 176, désormais signalée
    par `...` au lieu de rester silencieuse.

## Deviations from Assessment

- `md_chunking/models.py` modifié alors qu'il ne figurait pas dans
  les fichiers listés : la validation de `Chunk.boundary` refusait la
  nouvelle frontière `mot` (contrainte découverte à l'implémentation,
  expansion de périmètre minimale).
- Complément typographique du normalizer (`? »` en `?»`) NON appliqué
  : le split conscient des guillemets traite le détachement à la
  racine ; la normalisation modifierait le contenu textuel pour un
  gain nul (consigné en suivi).
- Marqueur `...` (trois points ASCII, collés au texte) retenu comme
  demandé ; l'alternative typographique `[...]` reste une décision
  ouverte.
- Décisions prises sur les trois clarifications de l'assessment :
  `guillemets` tracé dans `params` du JSON (recommandation suivie) ;
  queue minimale de 30 caractères comme constante interne non
  exposée ; guillemets anglo-saxons par alternance simple avec
  exemption d'un `"` précédé d'un chiffre (pouce), apostrophes
  ignorées.
- Limite documentée : le suivi des citations est réinitialisé à
  chaque partie ; une citation traversant un titre de section n'est
  pas marquée à la frontière des parties (règle hiérarchiquement plus
  faible que le découpage). Les unités atomiques (code, tableaux) ne
  sont ni mesurées ni marquées.

## Follow-ups

- Amender `specs/001-md-chunking/spec.md` (FR-003, FR-005) et
  `research.md` (décision D6) : la hiérarchie descend désormais au
  niveau mot et les coupures sont marquées `...` — sans cet
  amendement, le conform-check speckit contredira le code.
- Décider du marqueur typographique français (`...` contre `[...]`)
  et, le cas échéant, l'aligner entre chunks et overlap.
- Si une citation doit traverser les parties sans perte de
  signalisation, étendre `_mark_cut_quotes` à un suivi par document
  (actuellement par partie).
- `output/0001` à `0006` n'ont jamais été analysés (hors périmètre du
  bug) ; les sorties existantes d'`output/` restent à l'ancien
  comportement jusqu'à régénération.
- Commit et push effectués via la skill `commit-push-ameliore`
  (branche `009-fix-guillemets-overlap`).
