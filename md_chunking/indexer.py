"""Export JSON de tracabilite (FR-007, FR-013, contrat chunk-json.md).

Schema version 1.0 : le chemin du document est porte au niveau
``document`` ; chaque chunk se rattache par la paire
``document.path`` + ``chunks[].ref``. Les champs conditionnels sont
presents si et seulement si l'information existe (jamais devinee).
"""

import json
from pathlib import Path

from .models import Chunk, DocumentSource
from .presets import Preset

SCHEMA_VERSION = "1.0"


def _omit_none(values: dict) -> dict:
    return {k: v for k, v in values.items() if v is not None}


def build_index(
    doc: DocumentSource,
    preset: Preset,
    preset_name: str,
    chunks: list[Chunk],
    nom: str,
    contexte: dict | None = None,
) -> dict:
    """Construit l'index conforme au contrat 001, amendé par le
    contrat chunk-json.md de la feature 006 : ``chunkingid``
    inconditionnel (FR-007), ``context`` si et seulement si un
    contexte validé a été apparié (FR-006)."""
    document: dict = {"path": doc.path.as_posix(), "chunkingid": nom}
    document.update(
        _omit_none(
            {
                "title": doc.title,
                "structure": doc.structure,
                "typologie": preset_name,
            }
        )
    )
    if contexte is not None:
        document["context"] = contexte
    return {
        "schema_version": SCHEMA_VERSION,
        "document": document,
        "params": {
            "chunk_min": preset.chunk_min,
            "chunk_max": preset.chunk_max,
            "overlap_pct": preset.overlap_pct,
            "guillemets": preset.guillemets,
            "unit": "chars",
        },
        "chunks": [
            _omit_none(
                {
                    "ref": c.ref,
                    "text": c.text,
                    "length": c.length,
                    "boundary": c.boundary,
                    "part": c.part,
                    "page": c.page,
                    "position_in_part": c.position_in_part,
                    "atomic": c.atomic,
                }
            )
            for c in chunks
        ],
    }


def write_index(index: dict, path: Path) -> None:
    """Ecrit l'index JSON de facon deterministe (aucun horodatage)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
