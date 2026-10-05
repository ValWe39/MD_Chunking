# Quickstart: Ratio caracteres/tokens reglable en CLI

**Feature**: specs/004-ratio-tokens-cli | **Date**: 2026-10-05

Prerequis : Python 3.11+, dependances installees (`pip install -e
.[dev]`), un fichier Markdown de test dans `Examples/` (ex.
`Examples/nettoye.md`).

## Scenario 1 — Defaut recale sans option (P1)

```text
md_chunking Examples/nettoye.md --output output-test
```

Attendu : code de sortie 0 ; le `*_review.md` produit porte l'en-tete
`Tokens estimes a ~3.5 caracteres par token` ; les lignes
`- tokens (estimation) : ≈ <n>` correspondent a
`ceil(longueur / 3,5)` ; l'index JSON est identique octet par octet a
celui produit avant la feature pour les memes entrees (SC-004).

## Scenario 2 — Ratio explicite (P2)

```text
md_chunking Examples/nettoye.md --output output-test --tokencpte 3.2
```

Attendu : en-tete `~3.2 caracteres par token` ; estimations recalculees
selon 3,2 ; index JSON et noms de fichiers inchanges par rapport au
scenario 1 (le ratio ne fuit jamais hors du rapport).

## Scenario 3 — Ratio hors bornes : echec rapide (P3)

```text
md_chunking Examples/nettoye.md --output output-test --tokencpte 12
```

Attendu : code de sortie 2 ; message
`--tokencpte doit etre > 0 et <= 10 (recu : 12.0)` ; aucun fichier
ecrit dans `output-test`, compteur `counter.txt` non incremente.

## Scenario 4 — Valeur mal formee : virgule refusee (P3)

```text
md_chunking Examples/nettoye.md --output output-test --tokencpte 3,5
```

Attendu : code de sortie 2 au parsing (message argparse
`invalid float value`), aucun fichier ecrit ; le format attendu (point
decimal) est documente dans le README.

## Scenario 5 — Interaction avec --no-review (P2)

```text
md_chunking Examples/nettoye.md --output output-test --no-review --tokencpte 2
```

Attendu : code de sortie 0 ; index JSON produit, aucun `_review.md`,
aucune erreur liee au ratio.

## Scenario 6 — Determinisme et non-regression (P1)

Executer deux fois le scenario 1 : sorties (index et review) identiques
octet par octet entre executions ; suite pytest complete verte :

```text
python -m pytest
```

## Verification optionnelle — mesure de reference SC-001

Hors pipeline et hors dependances du projet : dans un environnement
separe (ex. `uvx` ou un venv dedie), compter les tokens des memes
chunks avec un tokenizer de reference et verifier qu'au moins 80 % des
chunks ont un ecart < 20 % avec l'estimation du defaut 3,5. Cette
mesure ne fait partie ni du code, ni des tests, ni des dependances
commitees (constitution II et III).
