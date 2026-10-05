# Research: Nommage des sorties (18 chiffres)

**Feature**: specs/003-nommage-sorties-18-chiffres | **Date**: 2026-10-05

Résolution des inconnues du plan et des questions reportées par la
spécification. Chaque décision cite ses alternatives écartées.

## D1 — Emplacement et format du fichier compteur

- **Decision**: `counter.txt` à la racine du projet, c'est-à-dire le
  répertoire parent du paquet `md_chunking`, résolu dynamiquement
  depuis le module (`Path(__file__).resolve().parent.parent`).
  Contenu strictement « NNNN\n » : le numéro sur 4 chiffres
  zéro-paddés, aucun autre champ. L'entrée `counter.txt` est ajoutée
  au `.gitignore` racine (FR-014).
- **Rationale**: « à la racine de l'outil » (intake) désigne la racine
  du projet ; la résolution dynamique évite tout chemin absolu codé en
  dur (constitution, Path isolation) et reste correcte en
  installation éditable, le mode d'usage réel du projet. Le contenu
  minimal (« uniquement le numéro ») rend le fichier lisible et
  réinitialisable à la main (Data retention : suppression = retour à
  0001, FR-009).
- **Alternatives considered**: répertoire courant au lancement
  (dépend du lieu d'invocation, contredit « racine de l'outil ») ;
  répertoire utilisateur type `~/.md_chunking` (robuste pour une
  installation pip, mais éloigné de la demande et ajoute un second
  emplacement à documenter) ; fichier JSON avec métadonnées
  (sur-ingénierie, YAGNI).

## D2 — Extraction et normalisation des lettres

- **Decision**: pour chaque bloc, normalisation NFKD de la chaîne
  d'entrée, suppression des marques combinantes et de tout caractère
  hors `a`–`z`, neutralisation de la casse (A=a=1), puis prise des
  N premiers caractères restants dans l'ordre d'apparition (5 pour le
  nom de fichier sans extension, 4 pour le titre).
- **Rationale**: reproduit la normalisation éprouvée de `_slugify`
  (`cli.py`, feature 001) : « À LA DÉMOCRATIE » → `alade...`, et
  satisfait FR-005 (casse) et FR-011 (accents ramenés à la base).
  Les chiffres, espaces et symboles sont ignorés (FR-011).
- **Alternatives considered**: ignorer les lettres accentuées
  (formulation initiale de l'intake — écartée par le choix utilisateur
  du 2026-10-05) ; table de translittération complète (YAGNI : le
  NFKD couvre le corpus réel français).

## D3 — Encodage bijectif base 26 et son module

- **Decision**: fonction pure dans un nouveau module
  `md_chunking/naming.py`. Valeur d'une chaîne de k lettres :
  `somme position(lettre) × 26^rang` (A=1 … Z=26). Bloc rendu en 8
  chiffres (5 lettres, max 12 356 630) ou 6 chiffres (4 lettres,
  max 475 254), zéros de remplissage à gauche (FR-004). Fonction de
  décodage symétrique (division successive) pour l'aller-retour
  FR-003. Bloc vide (aucune lettre) = `00000000` / `000000`.
- **Rationale**: bornes vérifiées par calcul le 2026-10-05 (round-trip
  « abcde » ↔ 494265) ; module dédié car `cli.py` orchestre et
  `indexer.py` ne change pas (FR-010) ; la pureté garantit le
  déterminisme de l'encodage, seul le compteur varie.
- **Alternatives considered**: fonctions dans `cli.py` (mélange
  orchestration/pure logique, tests moins isolés) ; encodage
  position-par-position type A1Z26 (impossible en largeur fixe,
  écarté par l'arbitrage) ; hachage CRC32 (non décodable, écarté au
  shape).

## D4 — Cycle de vie et robustesse du compteur

- **Decision**: lecture unique du compteur au démarrage de la
  commande ; s'il est absent → 0001 ; s'il est illisible (non
  numérique, hors 0–9999) → erreur de configuration immédiate, code
  de sortie 2, aucun fichier écrit (FR-009). Après chaque document
  produit : incrément (modulo 10000, 9999 → 0000, FR-008) puis
  persistance par écriture dans un fichier temporaire suivi d'un
  remplacement atomique (`os.replace`) pour ne jamais laisser de
  compteur corrompu en cas de crash pendant l'écriture (FR-007).
- **Rationale**: la lecture au démarrage donne l'échec rapide exigé
  par la constitution (Config Validation) ; la persistance après
  chaque document (clarification du 2026-10-05) empêche toute
  réutilisation de numéro après interruption ; l'écriture atomique
  élimine la principale cause de « compteur corrompu » détectée en
  recherche (cadis#3126 : read-modify-write non sérialisé).
- **Alternatives considered**: persistance unique en fin d'exécution
  (réutilise les numéros après interruption — écartée par la
  clarification) ; verrouillage fichier contre la concurrence
  (hors périmètre v1, FR-013).

## D5 — Retrait de l'interface de sous-dossiers

- **Decision**: suppression de l'option `--naming` et des fonctions
  associées (`_slugify`, `TITLE_SLUG_MAX`, `_subdir_name`,
  `_resolve_subdir`). Un appel avec `--naming` échoue avec le message
  argparse standard des options inconnues, code de sortie 2
  (FR-012). La ligne de succès console devient
  « {fichier} : {n} chunks -> {output}/{nom 18 chiffres}.json ».
  README mis à jour (nommage, compteur, disparition des
  sous-dossiers).
- **Rationale**: la sortie plate rend l'option morte ; la garder
  silencieuse serait mensonger, la déprécier ajouterait un état
  transitoire sans utilisateur autre que le propriétaire (choix
  utilisateur du 2026-10-05).
- **Alternatives considered**: conservation silencieuse (écartée au
  specify) ; avertissement de dépréciation (palliatif inutile pour un
  outil mono-utilisateur).

## D6 — Stratégie de test

- **Decision**: trois volets. (1) `tests/unit/test_naming.py` :
  aller-retour encodage/décodage, bornes (zzzzz, zzzz), padding
  (abc → 00000731), casse (CONTEXTE = contexte), accents
  (DÉMOCRATIE = DEMOCRATIE), blocs vides, noms courts, plus de 5
  lettres. (2) `tests/unit/test_counter.py` : fichier absent → 0001,
  corrompu → erreur, cycle 9999 → 0000, persistance par document,
  atomicité (pas de fichier temporaire résiduel). (3)
  `tests/integration/test_cli.py` : adaptation des 7 assertions
  verrouillant `output/NNNN/chunks.json` vers la sortie plate, noms
  uniques sur une exécution multi-fichiers, compteur strictement
  croissant sur deux exécutions, `--naming` rejetée, contenu du JSON
  identique entre deux exécutions (SC-003).
- **Rationale**: couverture directe de SC-001 à SC-005 ; les tests
  existants des features 001 et 002 restent verts à adaptation
  près (SC-004) ; le compteur est testé en isolation pour ne pas
  dépendre de l'ordre d'exécution pytest (fixture tmp_path).
- **Alternatives considered**: tests du compteur via la seule CLI
  (moins isolés, échecs difficiles à diagnostiquer) ; réinitialisation
  du compteur réel du dépôt dans les tests (jamais : les tests doivent
  utiliser des répertoires temporaires et un compteur injecté).
