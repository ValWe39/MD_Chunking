"""Point d'entree ``python -m md_chunking`` (contrat contracts/cli.md)."""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
