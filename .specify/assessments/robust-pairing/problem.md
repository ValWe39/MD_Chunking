# Problem Definition: Échec d'appariement .md/.json sur préfixes longs

- **Slug**: robust-pairing
- **Created**: 2026-10-28
- **Inputs used**: intake.md, research.md

## Problem Statement

Lorsqu'un utilisateur traite avec `--add-context` un dossier
contenant plusieurs paires `.md`/`.json` dont les noms partagent
un préfixe commun supérieur à 8 caractères après normalisation
(ex. `fipeco.fr-000033-nettoye.md` et
`fipeco.fr-000033-net-0063.json`), l'appariement échoue pour
chaque paire : l'outil émet un avertissement
« Appariement ambigu » et aucun contexte n'est embarqué dans la
sortie JSON, bien que les paires soient parfaitement
identifiables par un humain et que les `.json` soient valides.

## Affected Users & Stakeholders

- **Users**: l'utilisateur unique de l'outil (mono-utilisateur,
  outil local) qui prépare des corpus documentaires avec
  métadonnées bibliographiques — il est affecté par la perte
  silencieuse de contexte et la nécessité de contournements
  manuels (renommage de fichiers, déplacement en sous-dossiers)
- **Stakeholders**: le propriétaire du dépôt (ValWe39), seul
  décideur — il porte la dette technique d'un contournement
  systématique et la perte de confiance dans l'outil

## Goals

- Tous les couples `.md`/`.json` valides d'un même niveau sont
  appariés automatiquement, sans intervention manuelle sur les
  noms de fichiers
- Les appariements existants qui fonctionnent (préfixe normalisé
  commun ≤ 8 caractères) continuent de fonctionner sans
  changement
- Aucun appariement incorrect (faux positif) n'est produit :
  deux fichiers réellement distincts ne sont jamais appariés
  par erreur

## Non-Goals

- Ne pas modifier le format du `.json` de contexte (les 7 clés
  `Typologie`, `Auteur(s)`, `Titre`, `Editeur`, `Date`,
  `Référence`, `Citation` restent inchangées)
- Ne pas modifier la branche « couple » (1 `.md` + 1 `.json` au
  même niveau = appariement inconditionnel)
- Ne pas modifier le comportement sans l'option
  `--add-context`
- Ne pas ajouter de dépendance externe
- Ne pas modifier le contenu des fichiers `.md` ou `.json`
  d'entrée
- Ne pas changer le nommage des sorties (18 chiffres)

## Success Metrics

- Taux d'appariement sur `Examples/Pairing/` (3 paires Fipeco) :
  baseline 0/3 (0 %), cible 3/3 (100 %)
- Taux d'appariement sur `Examples/Extension/` (3 couples
  existants) : baseline 3/3 (100 %), cible 3/3 (100 %) — pas de
  régression
- Nombre d'avertissements « Appariement ambigu » sur
  `Examples/Pairing/` : baseline 3, cible 0
- Nombre de faux positifs (appariements incorrects détectés en
  test) : baseline 0, cible 0
- Suite de tests complète : tous les tests passent (avec
  adaptations documentées si nécessaire)

## Cost of Inaction

Si le problème n'est pas résolu, l'utilisateur doit
systématiquement intervenir manuellement avant chaque exécution
avec `--add-context` sur un corpus à préfixes longs : soit
renommer les fichiers pour différencier les 8 premiers
caractères normalisés, soit déplacer chaque paire dans un
sous-dossier dédié pour bénéficier de la branche « couple ».
Ces contournements sont pénibles sur des corpus volumineux,
introduisent un risque d'erreur humaine, et érodent la confiance
dans l'outil — la valeur de `--add-context` (enrichissement
automatique des chunks avec des métadonnées bibliographiques)
reste inaccessible sur une classe entière de corpus réels.

## Open Questions

- [NEEDS CLARIFICATION: jusqu'à quelle longueur de préfixe
  normalisé commun deux fichiers peuvent-ils être considérés
  comme appariables sans ambiguïté ?]
- [NEEDS CLARIFICATION: dans quels cas un appariement incorrect
  serait-il plus nuisible qu'aucun appariement ? Faut-il un
  seuil de confiance avant d'accepter un appariement ?]
- [NEEDS CLARIFICATION: le dossier `Examples/Pairing/` doit-il
  devenir une fixture de test de régression committée, ou
  reste-t-il un exemple local non versionné ?]
- [NEEDS CLARIFICATION: l'avertissement « Appariement ambigu »
  actuel est-il un signal utile à préserver pour détecter les
  vraies erreurs de nommage, ou un bruit à éliminer au profit
  d'un appariement automatique ?]
- [NEEDS CLARIFICATION: faut-il distinguer l'ambiguïté
  « résoluble » (préfixe long mais différenciant à plus de
  8 caractères) de l'ambiguïté « réelle » (deux fichiers
  véritablement homonymes) ?]
- [NEEDS CLARIFICATION: le changement de comportement
  (ambigu → résolu silencieusement) doit-il être accompagné
  d'un flag opt-in, ou remplace-t-il directement l'ancien
  comportement ?]
