# Data Model: Contexte utilisateur et auto-identification dans la sortie JSON

**Feature**: 006-add-context | **Date**: 2026-10-14

La feature n'introduit aucune entité persistante : compteur
d'occurrence, nom de sortie, document et chunk restent inchangés
(data-model de la feature 001, état `counter.txt` de la feature
003). Elle ajoute des entités éphémères de résolution et amende
une entité existante : le bloc `document` de l'index JSON.

## Entités

### Contexte documentaire (éphémère)

Contenu d'un `.json` compagnon fourni par l'utilisateur, validé
puis copié verbatim dans la sortie (jamais écrit sur disque,
FR-010).

| Attribut | Valeur |
| -------- | ------ |
| source | `Path` du `.json` compagnon |
| champs | exactement les sept clés attendues (liste ci-dessous) |
| valeurs | chaîne ou liste, vide admis, jamais transformées |

Les sept clés : `Typologie`, `Auteur(s)`, `Titre`, `Editeur`,
`Date`, `Référence`, `Citation`.

Garde-fous :

- validation (D4) : objet JSON lisible, clés exactes — ni
  manquante, ni supplémentaire ; tout écart invalide le fichier ;
- format invalide → avertissement, aucun contexte embarqué,
  traitement classique (FR-008) ;
- copie verbatim y compris champs vides (FR-004, FR-006).

### Couple (éphémère)

Un `.md` apparié à son `.json` de contexte, reconnu à la
résolution (D5) ; aucune trace persistante : seul le contexte
embarqué dans l'index JSON survit au traitement.

| Attribut | Valeur |
| -------- | ------ |
| document | `Path` du `.md` |
| contexte | `Path` du `.json` validé |

Garde-fous :

- branche couple : niveau contenant exactement 1 `.md` et 1
  `.json` directs, quel que soit le nom (FR-002) ; le contenu des
  sous-dossiers ne compte jamais dans le niveau parent (D2, D5) ;
- branche mélangée : extension progressive par paliers
  (8, 12, 16, … jusqu'à la longueur maximale), unicité des
  deux côtés (FR-005, D3 amendé feature 007) ; absence ou
  ambiguïté à la longueur maximale → classique ;
- fichiers individuels : jamais appariés (D8).

### Clé d'appariement normalisée (éphémère)

Valeur dérivée d'un nom de fichier, calculée uniquement pour la
branche mélangée (D3).

| Attribut | Valeur |
| -------- | ------ |
| valeur | NFKD, minuscules, espaces → `_`, `a-z 0-9 _` (D3) |

Amendement feature 007 : plus de troncature dans `cle_normale` ;
la troncature par paliers (8, 12, 16, …) relève de
`apparie_niveau()`.

Vérifiée sur les exemples : les trois couples
d'`Examples/Extension/` coïncident au palier 8 (`premiere`,
`an_rappo`, `ecalle_o`).

### Document résolu avec contexte (éphémère)

Chaque document du lot porte, à côté de son chemin, un contexte
optionnel ; sans `--add-context`, tous les contextes sont `None`
et la résolution est celle de la feature 005, inchangée (D1, D8).

| Attribut | Valeur |
| -------- | ------ |
| chemin | `Path` du `.md` |
| contexte | objet contexte validé, ou `None` |

## Transitions d'état

Aucune : la résolution et l'appariement sont des fonctions pures
(entrées → documents + contextes + avertissements), sans écriture ;
le premier effet de bord reste la persistance du compteur par
document traité (feature 003, inchangée) ; l'ordre de traitement
déterministe (D2) garantit la reproductibilité des occurrences.

## Impact sur les entités existantes

- Index JSON — bloc `document` (amendé, D7) :

| Champ | Présence | Règle |
| ----- | -------- | ----- |
| chunkingid | obligatoire | nom de sortie sans extension (FR-007) |
| context | si apparié | sept champs verbatim, vides compris (FR-006) |

  `schema_version` reste `"1.0"` (changement compatible, FR-013) ;
  contrat amendé : [contracts/chunk-json.md](contracts/chunk-json.md).

- DocumentSource, Chunk, `params`, `chunks[]` : inchangés
  (FR-004, FR-009) ; `document.title`, `document.structure`,
  `document.typologie` inchangés — la clé `Typologie` du contexte
  vit dans `document.context`, sans collision.
- Compteur d'occurrence, nom de sortie (18 chiffres) : inchangés ;
  un lot de k documents consomme k occurrences, appariés ou non
  (FR-009).
- Review : inchangé ; il ne mentionne ni le contexte ni
  `chunkingid` (FR-009).
