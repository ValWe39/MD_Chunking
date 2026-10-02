# MD_Chunking

Un outil de chunking de texte sous format Markdown 100 % local et déterministe.

## Installation

Prérequis : Python 3.11 ou plus récent.

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[dev]"   # Windows
# ou, sous Linux/macOS : .venv/bin/python -m pip install -e ".[dev]"
```

## Usage

```bash
python -m md_chunking [OPTIONS] FICHIER [FICHIER ...]
```

Options principales (contrat : `specs/001-md-chunking/contracts/cli.md`) :

- `--min` / `--max` : bornes de taille d'un chunk, en caractères
  (défauts du preset : 100 / 1000)
- `--overlap` : overlap entre chunks voisins, en pourcentage (0 a 20,
  defaut 15)
- `--typologie` : preset `documentation` (defaut), `articles`,
  `conversations`, `code` ou `livre`
- `--output` : dossier de sortie (defaut : `output/`, relatif)
- `--naming` : sous-dossiers `numbered` (defaut) ou `title`
- `--no-review` : ne pas produire le rendu de relecture

Chaque document traité produit un sous-dossier dedie contenant :

- `chunks.json` : index de tracabilite (schema
  `specs/001-md-chunking/contracts/chunk-json.md`) ;
- `review.md` : rendu annote pour relecture humaine avant embedding.

Codes de sortie : 0 succes, 1 au moins un document en echec (le lot
continue), 2 configuration invalide (rien n'est ecrit).

## Confidentialite (constitution du projet)

- Le traitement est 100 % local : aucun contenu ne quitte la machine.
- La telemetrie tierce embarquee par haystack-ai est desactivee au
  demarrage du paquet, avant tout import de la bibliotheque ; le
  resultat de cette verification est confirme par le test
  `tests/unit/test_normalizer.py::test_telemetrie_haystack_desactivee`.

## Tests

```bash
.venv/Scripts/python -m pytest
```

Corpus de validation local : les documents du dossier `Examples/`
(non versionnes) ; les tests committes utilisent des mini-fixtures
derivees (`tests/fixtures/`).
