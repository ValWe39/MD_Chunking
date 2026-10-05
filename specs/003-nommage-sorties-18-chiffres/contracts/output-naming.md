# Contrat de nommage des sorties : 18 chiffres

**Feature**: specs/003-nommage-sorties-18-chiffres | **Date**: 2026-10-05

Contrat du format de nom des fichiers produits. Le contenu des
fichiers reste régi par les contrats existants (chunk-json.md de la
feature 001, review-render.md de la feature 002) — inchangés.

## Format

```text
<BBBBBBBB><TTTTTT><OOOO>.json
<BBBBBBBB><TTTTTT><OOOO>_review.md
  B = bloc fichier, 8 chiffres
  T = bloc titre,  6 chiffres
  O = occurrence,  4 chiffres
```

## Bloc fichier (8 chiffres)

- Source : nom du fichier markdown d'entrée, sans extension
  (`contexte.md` → `contexte`).
- Lettres retenues : 5 premières après normalisation — NFKD, marques
  combinantes retirées, tout caractère hors `a`–`z` ignoré, casse
  neutre (FR-005, FR-011, research.md D2).
- Encodage : numération bijective base 26, A=1 … Z=26, la chaîne lue
  comme un seul nombre (FR-003).

  ```text
  contexte → « conte » → 3×26⁴ + 15×26³ + 14×26² + 20×26 + 5
                        = 1 644 557 → « 01644557 »
  ```

- Bornes : aucune lettre → `00000000` ; 5 lettres max →
  12 356 630 (`zzzzz`), toujours 8 chiffres ou moins, remplissage à
  gauche (FR-004).

## Bloc titre (6 chiffres)

- Source : `document.title` du document JSON (H1 ou front-matter,
  jamais deviné).
- Lettres retenues : 4 premières, mêmes règles de normalisation que
  le bloc fichier.
- Titre absent ou sans lettre → `000000` (FR-004).
- Bornes : 4 lettres max → 475 254 (`wxyz`), toujours 6 chiffres ou
  moins.

## Bloc occurrence (4 chiffres)

- Numéro d'occurrence de l'outil : 0001 au premier usage, +1 par
  document produit, retour à 0000 après 9999 (FR-006, FR-008).
- Persisté après chaque document dans `counter.txt` à la racine du
  projet (FR-007, research.md D1) ; jamais réutilisé, même après
  interruption.

## Décodage

Chaque bloc de lettres se décode en division successive (base 26
bijective) et redonne exactement ses lettres d'origine :

```text
01644557 → 1 644 557 → « conte »
063252   → 63 252    → « cont »
```

Les blocs valant 0 (`00000000`, `000000`) signalent l'absence de
lettres, pas une lettre de position 0.

## Garde-fous

- Le nom ne figure jamais dans le contenu du JSON ni du rendu de
  relecture (FR-010).
- Le nom est l'identifiant d'une *occurrence* : ré-exécuter le même
  document produit un nouveau nom (bloc occurrence avancé), l'ancien
  n'est pas écrasé.
- Deux exécutions parallèles peuvent produire un même numéro
  (non garanti v1, FR-013).
