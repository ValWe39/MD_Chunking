# Idea Intake: Compteur de tokens approximatif par chunk dans le rapport visuel

- **Slug**: compteur-tokens-chunks
- **Created**: 2026-10-02
- **Source**: pasted text (idée pointant vers le codebase :
  `md_chunking/reviewer.py`, rendu `review.md`)
- **Type**: improvement

## Idea (as captured)

> Est-il possible d'ajouter un compteur de token (respectant la
> constitution évidemment). Le but est d'avoir le nombre de token
> (approximatif) pour chaque chunk dans le rapport visuel ...

## Restated

Ajouter au rapport visuel de relecture (`review.md`, produit par
`md_chunking/reviewer.py`) un nombre de tokens approximatif pour
chaque chunk, sous la contrainte explicite de conformité à la
constitution du projet (`.specify/memory/constitution.md`).

## Origin & Context

- **Raised by**: l'utilisateur, via `/speckit-assess-intake` le 2026-10-02.
- **Trigger**: [NEEDS CLARIFICATION: ce qui a motivé la demande — par
  exemple vérifier un budget de tokens pour un pipeline aval, ou
  comparer les tailles de chunks à une limite de modèle. À confirmer
  par l'utilisateur.]
- **Contexte codebase** : le rendu actuel affiche par chunk un en-tête
  `## Chunk <ref> — <longueur> car.` suivi de métadonnées (frontière,
  partie, page, position, atomicité). Le compteur de tokens s'ajouterait
  à ces métadonnées existantes.

## First-Glance Unknowns

- [NEEDS CLARIFICATION: quelle méthode d'estimation est attendue —
  heuristique locale (hors-ligne, déterministe) ou tokenizer d'un
  modèle précis — et laquelle respecte la constitution (notamment les
  principes de confidentialité / pas de télémétrie) ?]
- [NEEDS CLARIFICATION: le compteur doit-il apparaître uniquement dans
  le rapport visuel, ou aussi dans l'index JSON ?]
- [NEEDS CLARIFICATION: le nombre de tokens complète-t-il ou
  remplace-t-il le « X car. » existant dans l'en-tête de chunk ?]
- [NEEDS CLARIFICATION: faut-il aussi un total (somme des tokens) par
  document, et le respect de la fourchette de taille doit-il
  s'exprimer en tokens ou rester en caractères ?]
- [NEEDS CLARIFICATION: quelle précision acceptable pour
  « approximatif » — ordre de grandeur suffisant, ou écart maximal
  toléré par rapport à un tokenizer de référence ?]
