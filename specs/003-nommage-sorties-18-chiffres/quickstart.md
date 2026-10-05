# Quickstart: Nommage des sorties (18 chiffres)

**Feature**: specs/003-nommage-sorties-18-chiffres | **Date**: 2026-10-05

Guide de validation bout-en-bout. Prérequis : Python 3.11+, dépôt
propre, suite de tests verte avant la feature.

## Préparation

```bash
python -m pytest          # attendu : tout vert avant d'appliquer
```

## Scénario 1 — Sortie plate et nom conforme

```bash
python -m md_chunking Examples/mon-doc.md --output /tmp/verif
```

Attendu : `/tmp/verif` contient exactement deux fichiers, sans
sous-dossier — `<18 chiffres>.json` et `<18 chiffres>_review.md`
(SC-001, FR-001). Le JSON est conforme au schéma 1.0 inchangé
(FR-010).

## Scénario 2 — Décodage manuel

Prendre le nom produit, découper en 8/6/4, décoder les deux premiers
blocs en base 26 bijective :

- les 8 premiers chiffres redonnent les 5 premières lettres du nom
  de fichier source ;
- les 6 suivants redonnent les 4 premières lettres du titre du
  document (ou `000000` si sans titre) ;
- les 4 derniers sont le numéro d'occurrence.

Détail du format : [contracts/output-naming.md](contracts/output-naming.md).
Attendu : aller-retour exact (SC-002, FR-003).

## Scénario 3 — Unicité et compteur persistant

```bash
python -m md_chunking Examples/mon-doc.md --output /tmp/verif
python -m md_chunking Examples/mon-doc.md Examples/autre.md \
    --output /tmp/verif
```

Attendu : cinq fichiers, cinq noms tous différents ; les numéros
d'occurrence avancent strictement (000n, 000n+1, 000n+2) entre les
exécutions ; le fichier `counter.txt` à la racine du projet mémorise
le dernier numéro (SC-005, FR-006, FR-007). Les sorties de la première
exécution ne sont pas écrasées.

## Scénario 4 — Déterminisme du contenu

Comparer le contenu du `<18 chiffres>.json` d'un même document entre
deux exécutions : identique octet par octet, seuls les noms de
fichiers diffèrent (SC-003, FR-010).

## Scénario 5 — Compteur absent ou corrompu

1. Supprimer `counter.txt` puis exécuter : le premier document porte
   `0001` (FR-009).
2. Écrire `abcd` dans `counter.txt` puis exécuter : échec rapide,
   code de sortie 2, message explicite, aucun fichier écrit
   (FR-009, contrat [cli.md](contracts/cli.md)).

## Scénario 6 — Option --naming rejetée

```bash
python -m md_chunking Examples/mon-doc.md --naming title
```

Attendu : erreur argparse « unknown argument », code de sortie 2
(FR-012).

## Cas limites à vérifier au passage

- Nom de fichier sans lettre (ex. `9.md`) : bloc fichier à
  `00000000`.
- Titre absent (pas de H1 ni front-matter) : bloc titre à `000000`.
- Accents et casse : `DÉMOCRATIE.md` et `democratie.md` produisent le
  même bloc fichier (FR-005, FR-011).

## Validation finale

```bash
python -m pytest          # attendu : suite adaptée entièrement verte
```

Entités et garde-fous : [data-model.md](data-model.md).
