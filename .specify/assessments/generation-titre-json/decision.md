# Decision: Nommage unique et décodable des fichiers de sortie

- **Slug**: generation-titre-json
- **Decided**: 2026-10-05
- **Verdict**: go
- **Artifacts reviewed**: intake.md, research.md, problem.md, concept.md

## Scorecard

| Critère | Note |
|---------|------|
| Problem validity | strong |
| Evidence strength | adequate |
| Value vs. inaction | strong |
| Feasibility / appetite | strong |
| Strategic fit | adequate |
| Risk posture | adequate |

Justifications :

- **Problem validity — strong** : problème réel et confirmé par
  l'unique utilisateur, qui a arbitré deux fois pour l'urgence du besoin
  (format, puis suppression des sous-dossiers — le nom devient le seul
  identifiant). problem.md est cohérent avec l'arbitrage.
- **Evidence strength — adequate** : preuves internes solides (code lu,
  corpus réel mesuré : 2/9 titres absents, accents présents ; bornes de
  l'encodage vérifiées par calcul) et prior art externe cité (A1Z26,
  base 26 bijective, CRC32, ULID). Confiance globale « medium » : le cas
  d'usage en aval reste déclaré par l'utilisateur, non observé. Jamais
  `weak` : chaque affirmation est sourcée ou marquée assumption dans
  research.md.
- **Value vs. inaction — strong** : avec la suppression arbitrée des
  sous-dossiers, ne rien construire rend les sorties en collision
  directe dans `output/` — l'option C est incompatible avec la
  décision de l'utilisateur. Le nommage n'est plus un confort mais le
  seul mécanisme d'identification.
- **Feasibility / appetite — strong** : option A à appétit small :
  fonction d'encodage pure déjà validée par calcul aller-retour, module
  compteur simple, rebranchement localisé de l'écriture (`cli.py`).
  Aucune dépendance, hors-ligne.
- **Strategic fit — adequate** : conforme à la constitution (II
  local-first, IV simplicité CLI). Deux frictions : premier état
  mutable de l'outil (fichier compteur) et suppression probable de
  l'option publique `--naming` — changement d'interface à assumer
  explicitement en spécification.
- **Risk posture — adequate** : risques majeurs identifiés et
  documentés (collisions après reset, concurrence, normalisation
  accents/casse, cycle de vie du compteur, réécriture des tests
  verrouillant l'arborescence). Non encore tranchés, mais tous sont
  des décisions de spécification, pas des inconnues bloquantes ;
  aucun risque non mitigable.

## Verdict & Rationale

**GO.** Le problème est valide et rendu critique par l'arbitrage de
suppression des sous-dossiers (le nom devient le seul identifiant des
sorties). Les preuves sont d'un niveau adéquat — jamais faibles : le
format est mathématiquement validé par calcul (bornes 8/6/4 chiffres,
décodage aller-retour), le corpus réel a été mesuré, et le prior art a
été vérifié. L'option A recommandée dans concept.md sert directement les
trois métriques de succès (nommage 100 %, décodabilité, contenu
inchangé) avec un appétit small crédible. Les six questions ouvertes
restantes sont des décisions de conception, pas des lacunes d'évidence :
elles appartiennent à la spécification (`/speckit-specify`), qui
dispose d'une étape de clarification dédiée. Le seul biais à surveiller :
ce GO s'appuie sur un cas d'usage déclaré par l'utilisateur unique, non
observé en production — acceptable dans un outil personnel
mono-utilisateur.

## If go — Handoff to `/speckit-specify`

- **Problem**: les fichiers de sortie (`chunks.json`, `review.md`)
  sont indiscernables dès qu'ils quittent leur sous-dossier ; avec la
  suppression des sous-dossiers (arbitrage), le nom de fichier devient
  le seul identifiant et doit être unique et décodable.
- **Chosen approach**: Option A — nom à 18 chiffres : 8 chiffres =
  valeur bijective base 26 des 5 premières lettres du nom de fichier
  source (stem), 6 chiffres = valeur bijective des 4 premières lettres
  de `document.title`, 4 chiffres = numéro d'occurrence 0001–9999
  persisté localement ; padding zéros à gauche ; sorties écrites à plat
  dans `output/` (`<18 chiffres>.json`, `<18 chiffres>_review.md`) ;
  contenu des fichiers inchangé.
- **In scope**: fonction d'encodage pure ; compteur local persistant ;
  écriture à plat dans `output/` ; suppression de l'arborescence par
  sous-dossier ; mise à jour des tests. **Out of scope**: contenu des
  sorties (schéma JSON 1.0, review), unicité cryptographique, option
  CLI d'activation, migration des anciennes sorties, état distant,
  features 001/002.
- **Success metrics**: 100 % des fichiers produits portent le nom 18
  chiffres ; chaque bloc décodé redonne ses lettres d'origine ;
  contenu JSON identique d'une exécution à l'autre ; aucune
  régression des tests 001/002.
- **Carried-forward open questions**:

  - Casse : « A » et « a » convertis identiquement ?
  - Accents : ramenés à la lettre de base (É => E) ou ignorés comme
    les symboles ? (corpus réel concerné)
  - Emplacement exact, format et politique git du fichier compteur
    (« à la racine de l'outil ») ; comportement si absent, corrompu,
    supprimé.
  - Après 9999 : repartir à 0000 ou 0001 ? Compteur global ou par
    document ?
  - Concurrence : comportement si deux exécutions parallèles.
  - Sort de l'option CLI `--naming` (`numbered`/`title`) : supprimée,
    ignorée, ou conservée ?
