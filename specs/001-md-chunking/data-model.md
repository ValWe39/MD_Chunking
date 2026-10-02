# Data Model: Chunking de Markdown avec sortie JSON

**Feature**: specs/001-md-chunking | **Date**: 2026-10-02

Entités issues de la spec (Key Entities) avec règles de validation
tirées des FR-001 à FR-013. Aucun stockage persistant : ces
entités vivent en mémoire pendant le traitement et sont
sérialisées en fichiers (JSON + Markdown) dans le dossier de
sortie.

## DocumentSource

Représente un fichier Markdown en entrée, après normalisation.

| Champ | Type | Règle |
|-------|------|-------|
| path | str | obligatoire, fourni par l'utilisateur |
| raw_content | str | contenu original lu, décodé UTF-8 |
| normalized_content | str | fins LF, titres neutralisés (FR-010) |
| title | str | titre H1 ou front-matter YAML (FR-007) |
| structure | enum | sections/paragraphes/phrases, le plus fin |

`title` est absent si le document n'est pas balisé ; `structure`
désigne le niveau le plus fin réellement détecté.

Validation : fichier illisible ou non-Markdown → échec rapide, le
lot continue (edge case spec).

## Chunk

Unité de texte découpée.

| Champ | Type | Règle |
|-------|------|-------|
| ref | str | référence unique séquentielle (FR-007) |
| text | str | contenu du chunk, jamais vide |
| length | int | `len(text)` en caractères (FR-002) |
| boundary | enum | section/paragraphe/phrase (FR-003) |
| part | str | titre de partie/sous-partie si balisé |
| page | int | uniquement si balise de page explicite |
| position_in_part | int | index dans sa partie si > 1 chunk |
| atomic | bool | indivisible (bloc code/tableau) |

Un `atomic` vrai (ou une section entière plus courte que min)
autorise un écart de fourchette, signalé dans le JSON (SC-001,
edge case spec).

Invariant (SC-001) : `min <= length <= max`, sauf écart signalé.

## Preset (typologie)

Valeurs par défaut par typologie (modifiables, assumption spec) ;
`chunk_min`/`chunk_max` en caractères, `overlap_pct` en % du
chunk :

- **documentation** (défaut) : min 100, max 1000, overlap 15%
- **articles** : min 150, max 1500, overlap 13%
- **conversations** : min 50, max 500, overlap 10%
- **code** : min 200, max 2000, overlap 15%
- **livre** : min 150, max 1200, overlap 15%

Les quatre premiers reprennent les tailles de l'intake (overlap
reconverti en pourcentage) ; `livre` est une proposition maison
ajoutée à la suite de l'analyse des Exemples 3/4 (prose longue),
à ajuster librement.

## SortieDocument

Artefacts produits par document.

| Champ | Type | Règle |
|-------|------|-------|
| subdir | str | numéroté (`0001`) ou slug titre 30 car. (FR-009) |
| chunks_file | fichier | `<subdir>/chunks.json` (contrat chunk-json) |
| review_file | fichier | `<subdir>/review.md` (FR-008) |

Le sous-dossier est numéroté par défaut ; le nommage par titre
s'applique si `--naming title` et si le titre est disponible, avec
repli sur la numérotation sinon (FR-009).

## Relations

`DocumentSource` 1—N `Chunk` (découpage) ; `Chunk` 1—1 entrée dans
`chunks.json` ; `Preset` fournit les bornes appliquées à un
`DocumentSource` ; `SortieDocument` agrège les artefacts d'un
`DocumentSource`.

## Transition d'états (pipeline)

```text
LU -> NORMALISE -> DECOUPE (sections -> paragraphes -> phrases)
   -> OVERLAP APPLIQUE -> INDEXE -> EXPORTÉ (json + review)
```

Chaque étape est pure et rejette en échec rapide les entrées
invalides (FR-012) ; aucun état intermédiaire n'est persisté.
