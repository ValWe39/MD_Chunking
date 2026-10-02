# Quickstart: Compteur de tokens dans le rapport de relecture

**Feature**: specs/002-compteur-tokens-chunks | **Date**: 2026-10-02

## Prérequis

- Python 3.11+ et le venv du projet (`.venv`) ;
- aucun accès réseau requis à aucune étape (constitution II).

## Scénarios de validation

### 1. Estimation présente par chunk (FR-T01, SC-T01)

```text
.venv\Scripts\md_chunking.exe "Examples\Exemple1\nettoye.md"
```

Attendu : dans `output/<sous-dossier>/review.md`, chaque chunk
porte une ligne `- tokens (estimation) : ≈ <n>` et son en-tête
`## Chunk <ref> — <N> car.` est inchangé.

### 2. Mention d'en-tête (FR-T05, SC-T02)

Attendu : sous le titre du rapport, une mention indique l'estimation
à ~4 caractères par token, approximative et indépendante de tout
modèle ; aucun nom de modèle.

### 3. Index JSON inchangé (FR-T07)

Attendu : `index.json` ne contient aucun champ `tokens` à aucun
niveau ; sur le même document et les mêmes paramètres, son contenu
est identique à celui produit avant la feature (vérifiable par
diff avec une sortie antérieure).

### 4. Déterminisme (FR-T06, SC-T04)

Relancer deux fois la même commande et comparer les deux
`review.md` : identiques octet à octet.

### 5. Hors-ligne (SC-T05)

Couper le réseau et rejouer le scénario 1 : comportement identique.

### 6. Tests automatisés

```text
.venv\Scripts\python.exe -m pytest
```

Attendu : suite verte, incluant les nouveaux tests d'estimation
(tests/unit/test_reviewer.py) et d'intégration
(tests/integration/test_cli.py).

## Références

- Contrat du rendu : [contracts/review-render.md](contracts/review-render.md)
- Modèle de données : [data-model.md](data-model.md)
- Décisions : [research.md](research.md)
