# MD_Chunking

Un outil de chunking de texte sous format Markdown 100 % local et déterministe.

## Pour débutants (mode d'emploi rapide)

Pas à pas, pour découper un document sans rien connaître à Python :

1. Ouvre PowerShell dans le dossier du projet : le prompt doit
   afficher `...\GitHub_Projects\MD_Chunking>`.
2. Saisis l'unique commande d'utilisation. L'outil est rangé dans le
   coffre `.venv` du projet ; le préfixe est simplement son adresse :

   ```powershell
   .venv\Scripts\md_chunking.exe "Examples\Exemple1\nettoye.md"
   ```

3. L'outil répond une ligne du genre
   `nettoye.md : 117 chunks -> output\007871010302730001.json` :
   le nombre de morceaux (chunks) et le fichier produit.
4. Ouvre le dossier `output\` : le document traité y a écrit deux
   fichiers portant un nom unique à 18 chiffres —
   `<18 chiffres>.json` est la fiche technique de chaque chunk (à
   envoyer à l'embedding) ; `<18 chiffres>_review.md` présente le
   même découpage pour lecture à l'œil nu. Chaque chunk y affiche
   aussi une estimation approximative de son nombre de tokens
   (« ≈ N », ~4 caractères par token, indépendante de tout modèle
   d'embedding).
5. Pour régler la découpe, ajoute des options entre l'outil et le
   document :

   ```powershell
   .venv\Scripts\md_chunking.exe --typologie livre "mon-document.md"
   ```

Pas d'activation de venv nécessaire avec cette forme. Si tu préfères
la commande nue `md_chunking` directement après le prompt, deux
options :

- activer le venv en début de session :
  `.\.venv\Scripts\Activate.ps1` (si PowerShell le refuse, voir la
  politique d'exécution `about_Execution_Policies`, ou passe la
  commande `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`) ;
- ou installer l'outil dans ton Python global, une seule fois :
  `pip install -e .` (haystack vivra alors dans ton Python Windows).

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

Options principales (contrat :
`specs/001-md-chunking/contracts/cli.md`, évolutions feature 003 :
`specs/003-nommage-sorties-18-chiffres/contracts/cli.md`) :

- `--min` / `--max` : bornes de taille d'un chunk, en caractères
  (défauts du preset : 100 / 1000)
- `--overlap` : overlap entre chunks voisins, en pourcentage (0 a 20,
  defaut 15)
- `--typologie` : preset `documentation` (defaut), `articles`,
  `conversations`, `code` ou `livre`
- `--output` : dossier de sortie (defaut : `output/`, relatif)
- `--no-review` : ne pas produire le rendu de relecture

Chaque document traité écrit directement dans le dossier de sortie
deux fichiers au nom unique à 18 chiffres (contrat :
`specs/003-nommage-sorties-18-chiffres/contracts/output-naming.md`) :

- `<18 chiffres>.json` : index de tracabilite (schema
  `specs/001-md-chunking/contracts/chunk-json.md`, inchangé) ;
- `<18 chiffres>_review.md` : rendu annote pour relecture humaine avant
  embedding ; chaque chunk porte une estimation approximative de
  ses tokens (`≈ N`, ~4 caractères par token, modele-agnostique,
  cf. `specs/002-compteur-tokens-chunks/contracts/review-render.md`).

Le nom se décode à la main : 8 chiffres pour les 5 premières lettres
du nom de fichier source, 6 chiffres pour les 4 premières lettres du
titre du document (numération bijective base 26, A=1 … Z=26, casse et
accents neutralisés), 4 chiffres pour le numéro d'occurrence. Ce
numéro avance à chaque document produit et survit aux exécutions : il
est mémorisé dans `counter.txt` à la racine du projet (hors git) ;
supprimer ce fichier ramène le prochain numéro à 0001. Deux
exécutions parallèles de l'outil ne sont pas garanties sans doublon
(v1, usage local).

Codes de sortie : 0 succes, 1 au moins un document en echec (le lot
continue), 2 configuration invalide, y compris `counter.txt` illisible
(rien n'est ecrit). L'option `--naming` a été supprimée avec les
sous-dossiers.

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
