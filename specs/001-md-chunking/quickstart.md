# Quickstart : valider le chunking de Markdown

**Feature**: specs/001-md-chunking | **Date**: 2026-10-02

Guide de validation de bout en bout. Les corpus de référence sont
les 4 documents de `Examples/` (locaux, gitignorés) ; les
mini-fixtures committées de `tests/fixtures/` couvrent les mêmes
pathologies en réduit (décision D7 de research.md).

## Prérequis

- Python 3.11+
- Dépendances installées : `pip install -e .` (ou équivalent une
  fois le packaging défini par tasks.md)
- Corpus : dossier `Examples/` présent (optionnel mais recommandé)

## Scénario 1 — Document propre (Exemple2, article web)

```text
python -m md_chunking Examples/Exemple2/nettoye.md
```

Attendu :

- `output/0001/chunks.json` et `output/0001/review.md` créés ;
- 100% des chunks entre 100 et 1000 caractères (preset
  documentation) ;
- chaque chunk porte `boundary`, la plupart `part` (97 titres
  détectés dans ce document) ;
- ouverture de `review.md` : repérage des frontières possible en
  moins de 10 minutes (SC-004).

## Scénario 2 — Document bruité (Exemple1, titres en listes)

```text
python -m md_chunking Examples/Exemple1/nettoye.md
```

Attendu :

- la normalisation (FR-010) neutralise les 210 titres emboîtés
  dans des puces : des chunks avec `part` et `boundary` cohérents
  sont produits, sans chunk vide ni dupliqué ;
- la relecture de `review.md` ne montre pas de texte perdu.

## Scénario 3 — Prose longue (Exemple4, livre)

```text
python -m md_chunking --typologie livre Examples/Exemple4/markdown.md
```

Attendu : les sections très longues (~700 mots et plus)
descendent au niveau paragraphes, puis phrases en dernier recours
(FR-003/FR-004) ; l'overlap respecte les frontières (FR-005).

## Scénario 4 — Déterminisme (SC-005)

```text
python -m md_chunking Examples/Exemple2/nettoye.md --output out_a
python -m md_chunking Examples/Exemple2/nettoye.md --output out_b
diff -r out_a out_b
```

Attendu : aucune différence (les artefacts excluent tout
horodatage).

## Scénario 5 — Échec rapide (FR-012)

```text
python -m md_chunking --min 1000 --max 100 Examples/Exemple2/nettoye.md
```

Attendu : code de sortie 2, message clair, aucun fichier écrit.

## Scénario 6 — Hors ligne et sans trackers (constitutions II/III)

- Exécuter les scénarios 1–4 réseau débranché : aucun échec.
- Au premier build, vérifier l'absence de télémétrie Haystack
  (recherche de variables d'environnement de télémétrie,
  inspection du trafic) et consigner le résultat dans le README
  (décision D3).

## Scénario 7 — Tests automatisés

```text
pytest
```

Attendu : tests unitaires verts (normalisation, overlap, presets,
index) et tests d'intégration verts sur `tests/fixtures/` ; les
tests marqués « corpus Examples » sont sautés sans erreur si
`Examples/` est absent.
