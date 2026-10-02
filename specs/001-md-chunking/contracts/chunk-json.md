# Contrat JSON : chunks.json

**Feature**: specs/001-md-chunking | **Date**: 2026-10-02

Un fichier `chunks.json` par document, écrit dans le sous-dossier
de sortie du document (contrat CLI). Le chemin du document est
porté au niveau `document` : chaque chunk de la liste se rattache
donc à ce chemin — l'exigence FR-007 (chemin + référence par
chunk) est satisfaite par la paire `document.path` + `chunks[].ref`.

## Schéma

```json
{
  "schema_version": "1.0",
  "document": {
    "path": "chemin/vers/le/document.md",
    "title": "Titre du document",
    "structure": "sections",
    "typologie": "documentation"
  },
  "params": {
    "chunk_min": 100,
    "chunk_max": 1000,
    "overlap_pct": 15,
    "unit": "chars"
  },
  "chunks": [
    {
      "ref": 1,
      "text": "Texte intégral du chunk...",
      "length": 842,
      "boundary": "section",
      "part": "Titre de la partie / sous-partie",
      "page": 3,
      "position_in_part": 2,
      "atomic": false
    }
  ]
}
```

## Règles de champs

| Champ | Présence | Règle |
|-------|----------|-------|
| schema_version | obligatoire | "1.0", versionnée (FR-013) |
| document.path | obligatoire | chemin du document (FR-007) |
| document.title | si balisé | jamais deviné (FR-007) |
| document.structure | obligatoire | niveau le plus fin utilisé |
| document.typologie | obligatoire | preset appliqué |
| params.* | obligatoire | bornes/overlap, unité `chars` (FR-002) |
| chunks[].ref | obligatoire | entier séquentiel unique (FR-007) |
| chunks[].text | obligatoire | jamais vide |
| chunks[].length | obligatoire | `len(text)` en caractères |
| chunks[].boundary | obligatoire | niveau utilisé (FR-003) |
| chunks[].part | si balisé | titre de partie (FR-007) |
| chunks[].page | si balisé | balise explicite (FR-007) |
| chunks[].position_in_part | si > 1 chunk | index (FR-007) |
| chunks[].atomic | obligatoire | true = indivisible |

Précisions : `schema_version` est incrémenté à tout changement
incompatible du schéma (FR-013) ; `atomic` vrai (bloc
code/tableau, ou section entière plus courte que min) autorise un
écart de fourchette justifié (SC-001) ; `params` reflète
exactement la configuration effective du traitement.

Invariants vérifiables : `chunk_min <= chunks[].length <=
chunk_max` pour toute entrée non `atomic` et non « section entière
plus courte que min » (SC-001) ; unicité et séquentialité des
`ref` ; `params` reflète exactement la configuration effective.

## Rendu de relecture associé

`review.md` (même sous-dossier) : un titre par chunk
(`## Chunk N — [partie] — 842 car.`), ses métadonnées en liste,
son texte intégral dans un bloc — lisible dans tout éditeur
(FR-008, réponse utilisateur Q2).
