# Data Model: Appariement robuste .md/.json sur préfixes longs

**Feature**: 007-robust-pairing | **Date**: 2026-10-28

La feature ne modifie aucune entité persistante. Elle
amende une entité éphémère existante (clé d'appariement
normalisée, feature 006) et en ajoute une (palier de
préfixe). Le bloc `document` de l'index JSON et le compteur
restent inchangés.

## Entités

### Clé d'appariement normalisée (éphémère, amendée)

Chaîne normalisée complète d'un nom de fichier, calculée
par `cle_normale()` sans troncature.

| Attribut | Valeur |
| -------- | ------ |
| valeur | NFKD, minuscules, espaces → `_`, `a-z 0-9 _`, sans troncature |
| longueur | nombre de caractères de `valeur` |

Amendement par rapport à la spec 006 (D3) : la troncature
`[:8]` est supprimée ; la troncature est désormais appliquée
dans `apparie_niveau()` via les paliers.

### Palier de préfixe (éphémère, nouvelle)

Longueur de troncature appliquée à la clé normalisée lors
d'une tentative d'appariement dans `apparie_niveau()`.

| Attribut | Valeur |
| -------- | ------ |
| valeur | 8, 12, 16, 20, 24, … (pas de 4) |
| max | longueur du stem normalisé le plus long du niveau |

### Document résolu avec contexte (éphémère, inchangé)

Chaque document du lot porte, à côté de son chemin, un
contexte optionnel ; inchangé par rapport à la spec 006.

| Attribut | Valeur |
| -------- | ------ |
| chemin | `Path` du `.md` |
| contexte | objet contexte validé, ou `None` |

## Transitions d'état

Aucune persistance : la résolution et l'appariement sont
des fonctions pures (entrées → documents + contextes +
avertissements), sans écriture. L'algorithme d'appariement
par paliers est déterministe :

```text
pour chaque palier dans [8, 12, 16, … jusqu'à max] :
    pour chaque .md non résolu :
        calculer clé tronquée à ce palier
        trouver les candidats .json avec la même clé tronquée
        si exactement 1 candidat et unicité des deux côtés :
            apparier le .md au .json (si valide)
            marquer le .md comme résolu
        sinon si plusieurs candidats ou plusieurs .md concurrents :
            laisser le .md non résolu (passera au palier suivant)
à la longueur maximale :
    tout .md non résolu → avertissement « Appariement ambigu »
    tout .json non apparié → avertissement « .json orphelin »
```

## Impact sur les entités existantes

- **Clé d'appariement normalisée** (spec 006) : amendée —
  suppression de la troncature `[:8]` dans `cle_normale()`,
  déplacement de la troncature dans `apparie_niveau()` via
  les paliers.
- **Contexte documentaire** (spec 006) : inchangé — 7 clés
  exactes, valeurs verbatim, jamais transformées.
- **Couple** (spec 006) : inchangé — branche couple
  (1 `.md` + 1 `.json`) inconditionnelle.
- **Document résolu avec contexte** (spec 006) : inchangé.
- **Index JSON** — bloc `document` : inchangé
  (`chunkingid` + `context` si apparié).
- **Compteur d'occurrence**, nommage des sorties : inchangés.
- **`counter.txt`**, fichiers `.md`/`.json` d'entrée :
  inchangés (lecture seule).
