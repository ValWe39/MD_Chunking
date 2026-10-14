# Contrat JSON : amendement chunkingid et context

**Feature**: 006-add-context | **Date**: 2026-10-14

Amendement du contrat `specs/001-md-chunking/contracts/chunk-json.md`
(schéma 1.0). Le présent contrat documente les seuls changements ;
tout le reste du contrat 001 reste en vigueur : `schema_version`,
`document.path`, `document.title`, `document.structure`,
`document.typologie`, `params`, `chunks[]` et leurs règles de
présence sont inchangés.

## Schéma du bloc document (amendé)

```json
{
  "schema_version": "1.0",
  "document": {
    "path": "chemin/vers/le/document.md",
    "chunkingid": "016492360000000016",
    "title": "Titre du document",
    "structure": "sections",
    "typologie": "documentation",
    "context": {
      "Typologie": "Compte-rendu",
      "Auteur(s)": ["Assemblée nationale"],
      "Titre": "Compte rendu de la première séance",
      "Editeur": "Assemblée nationale",
      "Date": "09 octobre 2026",
      "Référence": "",
      "Citation": "Assemblée nationale, \"...\", 09 octobre 2026"
    }
  },
  "params": { "...": "inchangé" },
  "chunks": [ { "...": "inchangé" } ]
}
```

## Règles de champs (nouveaux champs uniquement)

| Champ | Présence | Règle |
| ----- | -------- | ----- |
| document.chunkingid | obligatoire | nom de sortie sans extension (FR-007) |
| document.context | si apparié | sept champs verbatim, vides compris (FR-006) |

Précisions :

- `chunkingid` restitue le nom à 18 chiffres produit par le
  nommage existant (contrat 003) ; il n'introduit aucun nommage
  nouveau et ne modifie jamais le nom du fichier écrit ;
- `context` est présent si et seulement si le document a été
  apparié à un `.json` de contexte validé via `--add-context`
  (contrat cli.md) ; sans appariement, la clé est absente —
  jamais `null`, jamais vide ;
- les valeurs de `context` sont copiées verbatim : aucune
  normalisation, complétion ni transformation (FR-004) ; la clé
  `Typologie` du contexte vit dans `document.context` et
  n'entre pas en collision avec `document.typologie` (preset) ;
- le `.json` de contexte n'est jamais recopié dans le dossier de
  sortie (FR-010).

## Version de schéma

`schema_version` reste `"1.0"` : l'ajout de champs est un
changement compatible pour tout consommateur JSON (les clés
inconnues sont ignorées) ; le contrat 001 réserve l'incrément aux
changements incompatibles (FR-013). Le contrat 001 est amendé par
le présent document, qui fait foi pour les deux nouveaux champs.

## Invariants vérifiables (additionnels)

- `document.chunkingid` = nom du fichier qui le contient, sans
  extension `.json` (vérifiable par toute lecture du fichier) ;
- `document.context` présent ssi le document était apparié à un
  `.json` validé ; ses clés sont exactement les sept attendues,
  valeurs identiques au fichier source (verbatim, vides compris) ;
- sans `--add-context`, aucun `document.context` n'apparaît et
  chaque fichier de sortie ne diffère du comportement antérieur
  que par le seul champ `chunkingid` (SC-002) ;
- `chunks[]`, `params` et les invariants du contrat 001
  (`chunk_min <= length <= chunk_max` hors `atomic`, unicité et
  séquentialité des `ref`) sont inchangés.
