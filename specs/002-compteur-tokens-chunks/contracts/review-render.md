# Contrat : rendu de relecture (review.md)

**Feature**: specs/002-compteur-tokens-chunks | **Date**: 2026-10-02
**Enrichit** : FR-008 de la feature 001 (specs/001-md-chunking).

## Périmètre

Le fichier `review.md` produit par document est la seule sortie
modifiée par la feature. L'index JSON (contrat chunk-json.md de la
feature 001) et l'interface CLI ne changent pas.

## Format

````text
# Decoupage : <titre ou nom de fichier>

> Tokens estimes a ~4 caracteres par token : approximation
> locale, independante de tout modele d'embedding.   <-- NOUVEAU

## Chunk <ref> — <longueur> car.

- frontiere : <section|paragraphe|phrase>
- partie : <titre>                        (si balise)
- page : <n>                              (si balise)
- position dans la partie : <n>           (si applicable)
- entite atomique (bloc code ou tableau)  (si atomique)
- tokens (estimation) : ≈ <n>             <-- NOUVEAU (par chunk)

```
<texte integral du chunk>
```
````

## Règles

- Mention d'en-tête : indique que les tokens sont estimés à
  ~4 caractères par token, de façon approximative et indépendante
  de tout modèle ; jamais de nom de modèle (FR-T05).
- Ligne par chunk : `- tokens (estimation) : ≈ <n>` où
  `<n> = ceil(len(texte) / 4)` (FR-T01, FR-T02) ; présente pour
  100 % des chunks du rapport (SC-T01).
- L'en-tête `## Chunk <ref> — <longueur> car.` est inchangé
  (FR-T04).
- Aucun seuil, aucun signalement de dépassement (FR-T09).
- La valeur et son libellé restent séparés afin qu'un compte exact
  puisse remplacer l'estimation sans changer la structure
  (FR-T08) ; forme future acceptée :
  `- tokens (exact, <tokenizer>) : <n>`.
- Le rendu reste déterministe : aucun horodatage, aucune valeur
  variable à paramètres constants (SC-T04, SC-005 de la feature
  001).
