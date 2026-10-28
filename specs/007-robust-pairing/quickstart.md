# Quickstart: Validation de l'appariement robuste par paliers

**Feature**: 007-robust-pairing | **Date**: 2026-10-28

Guide de validation end-to-end après implémentation.

## Prérequis

- Python 3.11+, venv activé ou `.venv/Scripts/md_chunking.exe`
- Branche `013-fix-lien` checkée
- Dossier `Examples/Pairing/` présent (3 paires Fipeco)
- Dossier `Examples/Extension/` présent (3 couples existants)

## Scénario 1 — Cas Fipeco (nouveau comportement)

```powershell
.venv\Scripts\md_chunking.exe --add-context `
  "Examples\Pairing" `
  --output "output\test-pairing"
```

**Résultat attendu** :

- 3 documents traités, 3 fichiers JSON produits dans
  `output\test-pairing\`
- Chaque JSON embarque `document.context` avec les 7 champs
  du `.json` correspondant
- **Aucun** avertissement « Appariement ambigu » sur stderr
- Codes de sortie : 0

## Scénario 2 — Compatibilité ascendante (pas de régression)

```powershell
.venv\Scripts\md_chunking.exe --add-context `
  "Examples\Extension\Multi-couples" `
  --output "output\test-extension"
```

**Résultat attendu** :

- 3 documents traités, 3 fichiers JSON produits
- Chaque JSON embarque `document.context` avec les 7 champs
- Appariements identiques à la feature 006 (`premiere`,
  `an_rappo`, `ecalle_o` au palier 8)
- Codes de sortie : 0

## Scénario 3 — Sans l'option (comportement inchangé)

```powershell
.venv\Scripts\md_chunking.exe `
  "Examples\Pairing" `
  --output "output\test-sans-contexte"
```

**Résultat attendu** :

- 3 documents traités, 3 fichiers JSON produits
- **Aucun** champ `document.context` dans les sorties
- Champ `document.chunkingid` présent (comportement 006)
- Codes de sortie : 0

## Scénario 4 — Vraie ambiguïté (faux positif exclu)

Créer un dossier temporaire avec deux `.md` de même stem :

```powershell
mkdir "tmp-ambigu"
# Créer doc.md, doc.json, doc-2.md, doc-2-2.json
# avec doc et doc-2-2 de même clé normalisée complète
.venv\Scripts\md_chunking.exe --add-context `
  "tmp-ambigu" --output "output\test-ambigu"
```

**Résultat attendu** :

- Avertissement « Appariement ambigu » pour chaque `.md`
  sur stderr
- Aucun `document.context` embarqué
- Codes de sortie : 0 (avertissement, pas échec)

## Validation par les tests

```powershell
.venv\Scripts\python.exe -m pytest tests/unit/test_contexts.py -v
.venv\Scripts\python.exe -m pytest `
  tests/integration/test_cli.py -v -k add_context
```

**Résultat attendu** : tous les tests passent, y compris les
2 tests d'ambiguïté adaptés et les nouveaux tests de paliers.
