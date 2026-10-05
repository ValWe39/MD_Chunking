"""Nommage des sorties : nombre a 18 chiffres decodable.

Trois blocs (contrat contracts/output-naming.md de la feature 003) :
- 8 chiffres : numeration bijective base 26 des 5 premieres lettres
  du nom de fichier source (sans extension) ;
- 6 chiffres : idem, 4 premieres lettres du titre du document ;
- 4 chiffres : numero d'occurrence (compteur local).

Fonctions pures : memes entrees -> memes blocs, sans etat (FR-003).
"""

import unicodedata

BLOC_FICHIER = 8
BLOC_TITRE = 6
LETTRES_FICHIER = 5
LETTRES_TITRE = 4


def extract_letters(text: str | None, count: int) -> str:
    """Premieres `count` lettres latines, NFKD, casse neutre (FR-005,
    FR-011, research.md D2). Les autres caracteres sont ignores."""
    if not text:
        return ""
    norm = unicodedata.normalize("NFKD", text)
    ascii_part = norm.encode("ascii", "ignore").decode("ascii")
    letters = [ch for ch in ascii_part.lower() if "a" <= ch <= "z"]
    return "".join(letters[:count])


def encode_block(letters: str, width: int) -> str:
    """Valeur bijective base 26 (A=1 ... Z=26) de `letters`, zéros de
    remplissage a gauche (FR-004). Chaine vide -> bloc de zeros."""
    value = 0
    for ch in letters:
        value = value * 26 + (ord(ch) - ord("a") + 1)
    return f"{value:0{width}d}"


def decode_block(block: str) -> str:
    """Lettres d'origine d'un bloc encode (aller-retour FR-003).
    Un bloc de zeros correspond a l'absence de lettres."""
    value = int(block)
    letters = []
    while value > 0:
        digit = (value - 1) % 26 + 1
        letters.append(chr(ord("a") + digit - 1))
        value = (value - digit) // 26
    return "".join(reversed(letters))


def build_output_name(
    stem: str | None,
    title: str | None,
    occurrence: int,
) -> str:
    """Nom de sortie a 18 chiffres : bloc fichier (8) + bloc titre
    (6) + occurrence (4) (FR-002)."""
    if not 0 <= occurrence <= 9999:
        raise ValueError(f"occurrence hors bornes 0-9999 : {occurrence}")
    blocs = (
        encode_block(extract_letters(stem, LETTRES_FICHIER), BLOC_FICHIER),
        encode_block(extract_letters(title, LETTRES_TITRE), BLOC_TITRE),
        f"{occurrence:04d}",
    )
    return "".join(blocs)
