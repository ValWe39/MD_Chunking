# Idea Intake: Robustesse du pairing .md/.json (extension progressive)

- **Slug**: robust-pairing
- **Created**: 2026-10-28
- **Source**: repo path — `md_chunking/contexts.py` + constat
  investigation + `Examples/Pairing/`
- **Type**: improvement

## Idea (as captured)

> « Je veux améliorer le pairing des doublons .md .json pour le
> rendre plus robuste. Tu peux utiliser l'exemple suivant pour les
> cas réels, tout en tenant compte des anciens exemples pour ne pas
> détruire ce qui fonctionnait déjà : `Examples/Pairing` »

Contexte (constat investigation) : la fonction `cle_normale()`
(`md_chunking/contexts.py:31-38`) tronque les noms normalisés à
8 caractères. Dans le dossier `Examples/Pairing/`, les 3 paires
`.md`/`.json` partagent le préfixe `fipeco.fr-00003` (13 caractères
après filtrage des `.` et `-`), tronqué à `fipecofr` pour tous les
fichiers. Résultat : « Appariement ambigu » pour chaque `.md`,
aucun contexte embarqué.

Piste identifiée : remplacer la troncature fixe à 8 caractères par
une **extension progressive par paliers** (8 → 12 → 16 → 20 → …
jusqu'à la longueur maximale), en s'arrêtant dès qu'une
correspondance devient unique des deux côtés. Cela préserve les
anciens exemples (`Examples/Extension/`) qui fonctionnent avec
8 caractères, tout en résolvant les collisions sur préfixes longs.

## Restated

Améliorer l'algorithme d'appariement `.md` ↔ `.json` dans la branche
« mélangée » de `apparie_niveau()` pour qu'il résolve les cas où
plusieurs paires partagent un préfixe normalisé commun supérieur à
8 caractères, sans casser les appariements existants qui
fonctionnent avec le préfixe de 8 caractères.

## Origin & Context

- **Raised by**: ValWe39 (utilisateur du projet)
- **Trigger**: constat investigation — exécution réelle sur un
  corpus Fipeco (`Echantillon/`) produisant 3 avertissements
  « Appariement ambigu » et aucun contexte embarqué, alors que les
  3 `.json` sont valides et les paires sont clairement
  identifiables par un humain.

## First-Glance Unknowns

- [NEEDS CLARIFICATION: bornes de l'extension progressive — paliers
  de 4 en 4 ? jusqu'à quelle longueur max ?]
- [NEEDS CLARIFICATION: faut-il un seuil minimum de confiance
  (ex. ratio caractères communs / longueur totale) avant d'accepter
  un appariement à un palier supérieur ?]
- [NEEDS CLARIFICATION: impact sur les tests existants —
  `test_melee_ambiguite_deux_json_meme_prefixe` et
  `test_melee_ambiguite_json_partage_par_deux_md` devront être
  adaptés]
- [NEEDS CLARIFICATION: faut-il amender le contrat D3 de la spec
  006-add-context, ou créer une spec 007 dédiée ?]
- [NEEDS CLARIFICATION: le dossier `Examples/Pairing/` contient
  3 paires Fipeco — servira-t-il de fixture de test de régression ?]
