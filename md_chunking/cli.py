"""Point d'entree CLI (constitution IV) : validation, orchestration,
codes de sortie 0/1/2 (contrat contracts/cli.md)."""

import argparse
import re
import sys
import unicodedata
from pathlib import Path

from .indexer import build_index, write_index
from .models import Chunk, DocumentSource
from .normalizer import build_document
from .overlap import apply_overlap
from .presets import DEFAULT_PRESET, PRESETS, Preset, get_preset
from .reviewer import build_review
from .splitter import split_document

TITLE_SLUG_MAX = 30
_EXIT_OK = 0
_EXIT_RUN = 1
_EXIT_CONFIG = 2


class ConfigError(Exception):
    """Erreur de configuration : echec rapide, aucun fichier ecrit."""


def _slugify(title: str) -> str:
    """Slug du titre : minuscules, accents retires, 30 caracteres max."""
    norm = unicodedata.normalize("NFKD", title)
    ascii_part = norm.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_part.lower()).strip("-")
    return slug[:TITLE_SLUG_MAX].rstrip("-")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Analyse et valide les arguments (FR-012)."""

    parser = argparse.ArgumentParser(
        prog="md_chunking",
        description=("Decoupe des documents Markdown en chunks traces et relisibles."),
    )
    parser.add_argument(
        "fichiers", nargs="+", type=Path, help="fichiers Markdown a decouper"
    )
    parser.add_argument(
        "--min", type=int, default=None, help="taille min d'un chunk, en caracteres"
    )
    parser.add_argument(
        "--max", type=int, default=None, help="taille max d'un chunk, en caracteres"
    )
    parser.add_argument(
        "--overlap",
        type=int,
        default=None,
        help="overlap en pourcentage du chunk (0 a 20)",
    )
    parser.add_argument(
        "--typologie",
        default=DEFAULT_PRESET,
        choices=sorted(PRESETS),
        help="preset de typologie (defaut : documentation)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output"),
        help="dossier de sortie (defaut : output/)",
    )
    parser.add_argument(
        "--naming",
        default="numbered",
        choices=["numbered", "title"],
        help="nommage des sous-dossiers (defaut : numbered)",
    )
    parser.add_argument(
        "--no-review", action="store_true", help="ne pas produire le rendu de relecture"
    )
    args = parser.parse_args(argv)

    errors = []
    if args.min is not None and args.min <= 0:
        errors.append(f"--min doit etre > 0 (recu : {args.min})")
    if args.max is not None and args.max <= 0:
        errors.append(f"--max doit etre > 0 (recu : {args.max})")
    if args.overlap is not None and not 0 <= args.overlap <= 20:
        errors.append(f"--overlap doit etre entre 0 et 20 (recu : {args.overlap})")
    preset = get_preset(args.typologie)
    chunk_min = args.min if args.min is not None else preset.chunk_min
    chunk_max = args.max if args.max is not None else preset.chunk_max
    if chunk_min >= chunk_max:
        errors.append(f"--min ({chunk_min}) doit etre < --max ({chunk_max})")
    for fichier in args.fichiers:
        if not fichier.is_file():
            errors.append(f"fichier d'entree introuvable : {fichier}")
    if errors:
        raise ConfigError("\n".join(errors))
    return args


def _preset_effectif(args: argparse.Namespace) -> tuple[Preset, str]:
    """Preset applique, surcharge par les options explicites (US-4)."""
    preset = get_preset(args.typologie)
    chunk_min = args.min if args.min is not None else preset.chunk_min
    chunk_max = args.max if args.max is not None else preset.chunk_max
    overlap = args.overlap if args.overlap is not None else preset.overlap_pct
    return (
        Preset(preset.name, chunk_min, chunk_max, overlap),
        preset.name,
    )


def _subdir_name(doc: DocumentSource, index: int, naming: str) -> str:
    """Sous-dossier dedie : numérote par defaut, sinon slug du titre
    (30 car. max) avec repli sur la numerotation (FR-009)."""
    if naming == "title" and doc.title:
        slug = _slugify(doc.title)
        if slug:
            return slug
    return f"{index:04d}"


def _resolve_subdir(output: Path, doc: DocumentSource, index: int, naming: str) -> Path:
    """Resout les collisions : un sous-dossier existant n'est jamais
    ecrase ; la numerotation avance, et un slug deja pris retombe sur
    la numerotation (FR-009, repli si titre duplique)."""
    name = _subdir_name(doc, index, naming)
    if naming == "title" and (output / name).exists():
        name = f"{index:04d}"
    if (output / name).exists():
        n = index
        while (output / f"{n:04d}").exists():
            n += 1
        name = f"{n:04d}"
    return output / name


def process_document(
    doc: DocumentSource,
    preset: Preset,
    preset_name: str,
    subdir: Path,
    with_review: bool,
) -> list[Chunk]:
    """Pipeline complet d'un document : decoupe, overlap, exports."""
    chunks = apply_overlap(split_document(doc, preset), preset)
    write_index(build_index(doc, preset, preset_name, chunks), subdir / "chunks.json")
    if with_review:
        (subdir / "review.md").write_text(build_review(doc, chunks), encoding="utf-8")
    return chunks


def main(argv: list[str] | None = None) -> int:
    """Point d'entree : 0 succes, 1 echec d'execution, 2 config invalide."""
    try:
        args = parse_args(argv)
    except ConfigError as err:
        print(f"Erreur de configuration :\n{err}", file=sys.stderr)
        return _EXIT_CONFIG

    preset, preset_name = _preset_effectif(args)
    failures = 0
    for index, fichier in enumerate(args.fichiers, start=1):
        try:
            doc = build_document(fichier)
        except (OSError, ValueError) as err:
            print(f"Echec : {fichier} : {err}", file=sys.stderr)
            failures += 1
            continue
        subdir = _resolve_subdir(args.output, doc, index, args.naming)
        try:
            chunks = process_document(
                doc, preset, preset_name, subdir, not args.no_review
            )
        except (OSError, ValueError) as err:
            print(f"Echec : {fichier} : {err}", file=sys.stderr)
            failures += 1
            continue
        print(f"{fichier} : {len(chunks)} chunks -> {subdir}")
    if failures:
        print(
            f"{failures} document(s) en echec ; les autres ont ete traites.",
            file=sys.stderr,
        )
        return _EXIT_RUN
    return _EXIT_OK
