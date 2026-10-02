"""Normalisation des entrees irregulieres (FR-010, decision D5).

Responsabilites :
- unifier les fins de ligne CRLF/LF en LF (constat des exemples reels) ;
- neutraliser les titres ATX emboites dans des puces de liste
  (motif ``  * ## [ ... ]`` de l'Exemple1) sans perte de contenu ;
- detecter le titre du document (front-matter YAML puis premier H1) ;
- detecter le niveau de structure le plus fin present.
"""

import re
from pathlib import Path

from .models import DocumentSource

# Titre ATX noye dans une puce : indentation, puce, 1 a 6 '#', texte.
_HEADING_IN_LIST = re.compile(r"^(\s*)([*+-])(\s+)(#{1,6})(\s+)(.*)$")

# Bloc front-matter YAML en tete de document.
_FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL)

# Titre de niveau 1 en debut de ligne.
_H1 = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)

# Champ title d'un front-matter YAML.
_FM_TITLE = re.compile(r"^title\s*:\s*[\"']?(.+?)[\"']?\s*$", re.MULTILINE)

# Titre ATX valide en debut de ligne (hors puces).
_HEADING_LINE = re.compile(r"^#{1,6}\s+\S", re.MULTILINE)


def normalize_line_endings(text: str) -> str:
    """Unifie CRLF et CR isole en LF."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def neutralize_list_headings(text: str) -> str:
    """Retire le marqueur de titre des titres noyes dans des listes.

    ``  * ## [ Titre ... ]`` devient ``  * [ Titre ... ]`` : le texte est
    conserve integralement, seul le rang de titre (qui n'en est pas un
    pour un parseur Markdown) disparait.
    """

    def _fix(match: re.Match[str]) -> str:
        return f"{match.group(1)}{match.group(2)} {match.group(6)}"

    return "\n".join(
        _fix(m) if (m := _HEADING_IN_LIST.match(line)) else line
        for line in text.split("\n")
    )


def detect_title(normalized: str) -> str | None:
    """Titre du document : front-matter YAML, sinon premier H1.

    Jamais devine : sans balise exploitable, retourne None.
    """
    fm = _FRONT_MATTER.match(normalized)
    if fm and (m := _FM_TITLE.search(fm.group(1))):
        return m.group(1).strip()
    if m := _H1.search(normalized):
        return m.group(1).strip()
    return None


def detect_structure(normalized: str) -> str:
    """Niveau de structure le plus fin reellement present."""
    if _HEADING_LINE.search(normalized):
        return "sections"
    if "\n\n" in normalized.strip():
        return "paragraphes"
    return "phrases"


def normalize(text: str) -> str:
    """Pipeline complet de normalisation d'un contenu brut."""
    return neutralize_list_headings(normalize_line_endings(text))


def build_document(path: Path) -> DocumentSource:
    """Lit un fichier Markdown et construit le DocumentSource normalise.

    Echec rapide (edge case spec) si le fichier est illisible.
    """
    raw = path.read_text(encoding="utf-8")
    normalized = normalize(raw)
    if not normalized.strip():
        raise ValueError(f"document vide : {path}")
    return DocumentSource(
        path=path,
        raw_content=raw,
        normalized_content=normalized,
        title=detect_title(normalized),
        structure=detect_structure(normalized),
    )
