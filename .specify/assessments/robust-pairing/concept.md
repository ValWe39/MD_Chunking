# Concept: Appariement robuste .md/.json sur préfixes longs

- **Slug**: robust-pairing
- **Created**: 2026-10-28
- **Recommended option**: A — Extension progressive par paliers

## Options

### Option A — Extension progressive par paliers

- **Sketch**: au lieu de comparer les noms sur un préfixe tronqué
  fixe, l'outil essaie d'abord les 8 premiers caractères
  normalisés. Si l'appariement reste ambigu, il essaie 12
  caractères, puis 16, et ainsi de suite par paliers jusqu'à ce
  qu'une correspondance devienne unique des deux côtés ou que la
  longueur maximale soit atteinte. L'utilisateur constate que ses
  paires à préfixe long (ex. Fipeco) sont appariées
  automatiquement, sans renommage, tout en conservant le
  comportement actuel pour les préfixes courts.
- **Appetite**: small (quelques jours — modification d'une
  fonction pure, réécriture de la boucle d'appariement, et
  adaptation de 2 tests existants)
- **Trade-offs**: gagne en robustesse et en ergonomie (zéro
  contournement manuel) ; sacrifie la simplicité de
  l'algorithme actuel (boucle sur paliers au lieu d'une
  comparaison directe) et introduit un risque de faux positifs
  si deux paires distinctes partagent un préfixe très long
  identique ; change le comportement de cas auparavant ambigus
  (avertissement) en cas résolus silencieusement
- **Rabbit holes**: définition des paliers (de 4 en 4 ?
  jusqu'où ?) ; seuil de confiance pour accepter un appariement
  à un palier supérieur ; adaptation des 2 tests d'ambiguïté
  existants qui deviendraient résolus ; décision de modifier D3
  de la spec 006 ou créer une spec 007

### Option B — Augmenter la troncature fixe (8 → 20 caractères)

- **Sketch**: simplement augmenter la limite de troncature dans
  la fonction de normalisation de 8 à 20 caractères. Les paires
  Fipeco seraient appariées car leurs clés à 20 caractères
  diffèrent (`fipecofr000033nettoy` vs `fipecofr000034nettoy`).
- **Appetite**: small (quelques heures — une seule constante à
  changer)
- **Trade-offs**: extrêmement simple à implémenter et à tester ;
  mais casse les 3 couples d'exemples existants
  (`premiere-0034` et `premiere-seance-du-v-nettoye` auraient
  des clés différentes à 20 caractères) ; nécessite de renommer
  tous les fichiers d'exemples existants ou de les déplacer en
  sous-dossiers ; ne résout pas le problème général (deux paires
  avec un préfixe commun > 20 caractères auraient toujours une
  collision)
- **Rabbit holes**: renommage de tous les exemples existants ;
  mise à jour de tous les tests qui dépendent de la troncature à
  8 ; la limite de 20 est arbitraire et pourrait à son tour être
  dépassée

### Option C — Ne rien faire, documenter le contournement

- **Sketch**: aucune modification de code. Documenter dans le
  README que les noms de fichiers d'une même branche mélangée
  doivent avoir des préfixes normalisés distincts sur 8
  caractères, et recommander de déplacer les paires dans des
  sous-dossiers dédiés (branche « couple », appariement
  inconditionnel).
- **Appetite**: small (quelques heures de rédaction)
- **Trade-offs**: zéro risque technique, zéro changement de
  comportement ; mais l'utilisateur continue de contourner
  manuellement chaque corpus à préfixes longs, ce qui est
  pénible et source d'erreurs ; la valeur de `--add-context`
  reste inaccessible sans préparation manuelle
- **Rabbit holes**: aucun

## Recommendation

**Option A — Extension progressive par paliers.**

Elle seule atteint les trois goals du problème : appariement
automatique de tous les couples valides, préservation des
appariements existants (les cas à préfixe court sont résolus au
palier 8, inchangés), et (sous réserve de tests) zéro faux
positif. L'appetite est small, la portée est confinée à un
module (`contexts.py`) et à ses tests. Les risques identifiés
(faux positifs, changement de comportement silencieux) sont
maîtrisables par des tests ciblés et une spécification claire.

L'Option B est rejetée car elle casse la compatibilité
ascendante — un non-goal implicite du problème (préserver ce qui
fonctionne). L'Option C est rejetée car elle ne résout pas le
problème, elle le documente.

## Out of Scope (for the recommended option)

- Ne pas modifier le format du `.json` de contexte (7 clés)
- Ne pas modifier la branche « couple » (1 `.md` + 1 `.json`)
- Ne pas modifier le comportement sans `--add-context`
- Ne pas ajouter de dépendance externe
- Ne pas modifier le contenu des fichiers `.md` ou `.json`
- Ne pas changer le nommage des sorties (18 chiffres)
- Ne pas introduire de flag opt-in : le nouveau comportement
  remplace l'ancien (à confirmer en spécification)
- Ne pas introduire de seuil de confiance configurable
- Ne pas modifier les messages d'avertissement existants

## Assumptions to Validate

- Les 3 couples d'exemples `Examples/Extension/` continuent de
  s'apparier au palier 8 (pas de régression)
- Les 2 tests d'ambiguïté existants
  (`test_melee_ambiguite_deux_json_meme_prefixe`,
  `test_melee_ambiguite_json_partage_par_deux_md`) peuvent être
  adaptés pour refléter le nouveau comportement sans perdre
  leur valeur de couverture
- Aucun faux positif n'est introduit sur les cas de test
  (vérification par un test dédié avec deux paires à préfixe
  long identique)
- Le dossier `Examples/Pairing/` peut servir de fixture de test
  de régression (copié en `tmp_path` comme les autres exemples)
- La spec 006 peut être amendée (D3) ou une spec 007 créée
  sans conflit avec le processus SDD établi
