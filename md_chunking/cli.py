"""Point d'entree CLI (constitution IV) : validation, orchestration,
codes de sortie 0/1/2 (contrat contracts/cli.md, feature 003)."""

import argparse
import sys
from pathlib import Path

from .counter import CounterError, next_value, persist, read_counter
from .indexer import build_index, write_index
from .models import Chunk, DocumentSource
from .naming import build_output_name
from .normalizer import build_document
from .overlap import apply_overlap
from .presets import DEFAULT_PRESET, PRESETS, Preset, get_preset
from .reviewer import build_review
from .splitter import split_document

_EXIT_OK = 0
_EXIT_RUN = 1
_EXIT_CONFIG = 2


class ConfigError(Exception):
    """Erreur de configuration : echec rapide, aucun fichier ecrit."""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Analyse et valide les arguments (FR-012 de la feature 003 :
    plus d'option --naming)."""

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
        "--guillemets",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="respecter les guillemets dans le decoupage "
        "(defaut : actif ; --no-guillemets pour desactiver)",
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
        errors.append(f"--min ({args.min}) doit etre < --max ({args.max})")
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
        Preset(preset.name, chunk_min, chunk_max, overlap, args.guillemets),
        preset.name,
    )


def process_document(
    doc: DocumentSource,
    preset: Preset,
    preset_name: str,
    output: Path,
    nom: str,
    with_review: bool,
) -> list[Chunk]:
    """Pipeline complet d'un document : decoupe, overlap, exports a
    plat dans `output` sous le nom `nom` (FR-001 de la feature 003)."""
    chunks = apply_overlap(split_document(doc, preset), preset)
    write_index(build_index(doc, preset, preset_name, chunks), output / f"{nom}.json")
    if with_review:
        (output / f"{nom}_review.md").write_text(
            build_review(doc, chunks), encoding="utf-8"
        )
    return chunks


def main(argv: list[str] | None = None) -> int:
    """Point d'entree : 0 succes, 1 echec d'execution, 2 config
    invalide (y compris compteur illisible, FR-009)."""
    try:
        args = parse_args(argv)
    except ConfigError as err:
        print(f"Erreur de configuration :\n{err}", file=sys.stderr)
        return _EXIT_CONFIG

    try:
        dernier = read_counter()
    except CounterError as err:
        print(f"Erreur de configuration :\n{err}", file=sys.stderr)
        return _EXIT_CONFIG

    preset, preset_name = _preset_effectif(args)
    failures = 0
    for fichier in args.fichiers:
        try:
            doc = build_document(fichier)
        except (OSError, ValueError) as err:
            print(f"Echec : {fichier} : {err}", file=sys.stderr)
            failures += 1
            continue
        occurrence = next_value(dernier)
        nom = build_output_name(fichier.stem, doc.title, occurrence)
        try:
            chunks = process_document(
                doc, preset, preset_name, args.output, nom, not args.no_review
            )
            persist(occurrence)
        except (OSError, ValueError) as err:
            print(f"Echec : {fichier} : {err}", file=sys.stderr)
            failures += 1
            continue
        dernier = occurrence
        print(f"{fichier} : {len(chunks)} chunks -> {args.output / (nom + '.json')}")
    if failures:
        print(
            f"{failures} document(s) en echec ; les autres ont ete traites.",
            file=sys.stderr,
        )
        return _EXIT_RUN
    return _EXIT_OK
