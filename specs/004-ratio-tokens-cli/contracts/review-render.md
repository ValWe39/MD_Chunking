# Contrat : rendu de relecture (review.md) — ratio reglable

**Feature**: specs/004-ratio-tokens-cli | **Date**: 2026-10-05
**Supersede** : specs/002-compteur-tokens-chunks/contracts/review-render.md
pour les seuls points touches ci-dessous.

## Perimetre

Le fichier `<nom>_review.md` reste la seule sortie modifiee. L'index
JSON, le nommage et la CLI ne changent pas au-dela de l'option
`--tokencpte` (contrat [cli.md](cli.md)). Les regles de la feature 002
non listees ici restent en vigueur.

## Format

````text
# Decoupage : <titre ou nom de fichier>

> Tokens estimes a ~{ratio, 1 decimale} caracteres par token :
> approximation locale, independante de tout modele d'embedding.

## Chunk <ref> — <longueur> car.

- frontiere : <section|paragraphe|phrase>
- partie : <titre>                        (si balise)
- page : <n>                              (si balise)
- position dans la partie : <n>           (si applicable)
- entite atomique (bloc code ou tableau)  (si atomique)
- tokens (estimation) : ≈ <n>

```
<texte integral du chunk>
```
````

## Regles

- Mention d'en-tete : le ratio affiche est le ratio effectif,
  arrondi a une decimale (defaut : `3.5` ; saisie `3.333` : `3.3`) ;
  toujours approximatif et independant de tout modele ; jamais de nom
  de modele (FR-004 ; FR-T05 de la feature 002 non regressif).
- Ligne par chunk : `- tokens (estimation) : ≈ <n>` avec
  `<n> = ceil(len(texte) / ratio)`, division exacte — inchangee dans sa
  forme (FR-001) ; presente pour 100 % des chunks du rapport.
- L'en-tete `## Chunk <ref> — <longueur> car.` est inchange (FR-T04 de
  la feature 002).
- Aucun seuil, aucun signalement de depassement (FR-T09 de la feature
  002) ; la forme future `- tokens (exact, <tokenizer>) : <n>` reste
  acceptee (FR-T08).
- Le rendu reste deterministe : a parametres constants (dont le ratio),
  aucun horodatage, aucune valeur variable (FR-005, SC-005).
