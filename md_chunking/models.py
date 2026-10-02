"""Entites du chunking (cf. specs/001-md-chunking/data-model.md)."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class DocumentSource:
    """Un fichier Markdown en entree, apres normalisation.

    Contraintes (data-model) :
    - ``path`` obligatoire, fourni par l'utilisateur ;
    - ``title`` lu dans le premier titre H1 ou le front-matter YAML,
      sinon ``None`` (jamais devine) ;
    - ``structure`` : niveau le plus fin reellement detecte parmi
      ``sections``, ``paragraphes``, ``phrases``.
    """

    path: Path
    raw_content: str
    normalized_content: str
    title: str | None = None
    structure: str = "paragraphes"

    def __post_init__(self) -> None:
        if not self.path:
            raise ValueError("DocumentSource : chemin obligatoire")
        if not self.normalized_content:
            raise ValueError("DocumentSource : contenu vide")
        if self.structure not in {"sections", "paragraphes", "phrases"}:
            raise ValueError(f"structure inconnue : {self.structure}")


@dataclass
class Chunk:
    """Unite de texte decoupee.

    Contraintes (data-model) :
    - ``ref`` : reference unique sequentielle par document (commence a 1) ;
    - ``text`` : jamais vide ;
    - ``length`` : ``len(text)`` en caracteres (unite de la spec, FR-002) ;
    - ``boundary`` : niveau utilise (section, paragraphe ou phrase) ;
    - ``atomic`` : vrai si entite indivisible (bloc code, tableau).
    """

    ref: int
    text: str
    boundary: str
    part: str | None = None
    page: int | None = None
    position_in_part: int | None = None
    atomic: bool = False

    def __post_init__(self) -> None:
        if not self.text:
            raise ValueError(f"chunk {self.ref} : texte vide interdit")
        if self.boundary not in {"section", "paragraphe", "phrase"}:
            raise ValueError(f"frontiere inconnue : {self.boundary}")

    @property
    def length(self) -> int:
        return len(self.text)
