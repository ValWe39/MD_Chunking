# Contrat CLI : md_chunking

**Feature**: specs/001-md-chunking | **Date**: 2026-10-02

Interface unique du projet : une commande en ligne (constitution
IV). Contrat stable pour l'utilisateur ; les détails internes
appartiennent à tasks.md.

## Invocation

```text
python -m md_chunking [OPTIONS] FICHIER [FICHIER ...]
```

`FICHIER` : un ou plusieurs chemins de fichiers Markdown. Un
fichier = un document (assumption spec).

## Options

| Option | Type | Défaut | Règle (FR) |
|--------|------|--------|------------|
| --min | int > 0 | selon preset | taille min, caractères (FR-002) |
| --max | int | selon preset | taille max ; > --min (FR-012) |
| --overlap | int 0–20 | 15 | % du chunk (FR-005) |
| --typologie | nom | documentation | une des 5 (FR-006) |
| --output | chemin | `output/` | dossier de sortie (FR-009) |
| --naming | enum | numbered | numbered ou title (FR-009) |
| --no-review | flag | désactivé | pas de rendu (FR-008) |

Typologies acceptées : documentation, articles, conversations,
code, livre. L'overlap est appliqué aux frontières structurelles
(FR-005). Le dossier de sortie est relatif par défaut (path
isolation) et créé s'il est absent. Les options explicites
surchargent le preset (US-4).

## Codes de sortie

| Code | Signification |
|------|---------------|
| 0 | succès — tous les documents traités |
| 2 | config invalide — rien n'est écrit (FR-012) |
| 1 | un document échoue ; le lot continue (spec) |

Sur le code 1, les autres documents du lot sont traités et le
message nomme le fichier en cause (edge case spec).

## Comportements garantis

- Un sous-dossier de sortie et deux artefacts par document :
  `chunks.json` (contrat chunk-json.md) et `review.md` (sauf
  `--no-review`).
- Aucune écriture hors du dossier `--output` ; aucun accès réseau
  (constitution II) ; aucun secret requis (constitution I).
- Déterminisme : mêmes fichiers, mêmes options → sortie
  identique (SC-005) ; les artefacts excluent tout horodatage
  pour garantir la comparabilité.
- Messages d'erreur clairs, en français, avec le paramètre ou
  le fichier en cause.
