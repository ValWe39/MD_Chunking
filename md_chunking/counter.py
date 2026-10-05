"""Compteur d'occurrence persistant (FR-006 a FR-009).

Dernier numero consomme, memorise dans `counter.txt` a la racine du
projet (research.md D1), hors controle de version (FR-014).
Lecture unique au demarrage ; persistance atomique apres chaque
document produit : un numero consomme n'est jamais reutilise
(FR-007, clarification du 2026-10-05).
"""

import os
from pathlib import Path

COUNTER_PATH = Path(__file__).resolve().parent.parent / "counter.txt"
OCCURRENCE_MAX = 9999


class CounterError(Exception):
    """Compteur illisible : echec rapide, aucun fichier ecrit (FR-009)."""


def read_counter(path: Path | None = None) -> int:
    """Dernier numero consomme ; fichier absent -> 0 (premier usage
    de l'outil vaudra 0001). Illisible ou hors bornes -> erreur."""
    counter_path = path if path is not None else COUNTER_PATH
    if not counter_path.exists():
        return 0
    content = counter_path.read_text(encoding="utf-8").strip()
    try:
        value = int(content)
    except ValueError as err:
        raise CounterError(
            f"counter.txt illisible a la racine du projet : {content!r}"
        ) from err
    if not 0 <= value <= OCCURRENCE_MAX:
        raise CounterError(f"counter.txt hors bornes 0-{OCCURRENCE_MAX} : {content!r}")
    return value


def next_value(current: int) -> int:
    """Numero suivant : increment d'une unite, retour a 0000 apres
    9999 (FR-008, cycle modulo 10000)."""
    if not 0 <= current <= OCCURRENCE_MAX:
        raise ValueError(f"compteur hors bornes 0-{OCCURRENCE_MAX} : {current}")
    return (current + 1) % 10000


def persist(value: int, path: Path | None = None) -> None:
    """Memorise `value` comme dernier numero consomme. Ecriture
    atomique : fichier temporaire puis remplacement (research.md
    D4) — jamais de compteur corrompu en cas d'interruption."""
    if not 0 <= value <= OCCURRENCE_MAX:
        raise ValueError(f"compteur hors bornes 0-{OCCURRENCE_MAX} : {value}")
    counter_path = path if path is not None else COUNTER_PATH
    tmp = counter_path.with_name(counter_path.name + ".tmp")
    tmp.write_text(f"{value:04d}\n", encoding="utf-8")
    os.replace(tmp, counter_path)
