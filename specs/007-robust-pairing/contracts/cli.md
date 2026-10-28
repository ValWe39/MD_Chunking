# Contrat CLI : amendement de l'appariement par paliers

**Feature**: 007-robust-pairing | **Date**: 2026-10-28

Amendement du contrat
`specs/006-add-context/contracts/cli.md` (section
« Niveau mélangé »). Tout le reste du contrat 006 reste
en vigueur.

## Section amendée : Niveau mélangé

Dans un dossier contenant plusieurs `.md` ou plusieurs
`.json`, l'appariement se fait par **extension progressive
par paliers** :

1. Calculer la clé normalisée complète de chaque fichier
   (NFKD, minuscules, espaces convertis en `_`, seuls
   `a-z 0-9 _` conservés, **sans troncature**).
2. Pour chaque palier dans `[8, 12, 16, 20, 24, …]`
   (pas de 4) jusqu'à la longueur maximale du stem
   normalisé le plus long du niveau :
   - Tronquer chaque clé normalisée à ce palier.
   - Chaque `.md` non encore résolu tente de s'apparier :
     un `.md` est apparié à un `.json` si leurs clés
     tronquées coïncident et que la correspondance est
     **unique des deux côtés**.
   - Les `.md` résolus sans ambiguïté sont retirés de la
     boucle ; les autres avancent au palier suivant.
3. À la longueur maximale, tout `.md` non résolu émet
   l'avertissement « Appariement ambigu pour {md} » et
   passe en traitement classique.
4. Tout `.json` non apparié à la fin de tous les paliers
   émet l'avertissement « .json de contexte orphelin :
   {chemin} ».

### Exemples de résolution

- **Cas Fipeco 33** : `fipeco.fr-000033-nettoye.md` +
  `fipeco.fr-000033-net-0063.json` — clés normalisées
  `fipecofr000033nettoye` / `fipecofr000033net0063` ;
  palier 8 : `fipecofr` (identique) ; palier 12 :
  `fipecofr0000` (identique) ; **appariés au palier 16**.
- **Cas Fipeco 34** : `fipeco.fr-000034-nettoye.md` +
  `fipeco.fr-000034-net-0055.json` — clés normalisées
  `fipecofr000034nettoye` / `fipecofr000034net0055` ;
  palier 8 : `fipecofr` (identique) ; **appariés au
  palier 16**.
- **Cas existant** : `premiere-0034.json` +
  `premiere-seance-du-v-nettoye.md` — clés normalisées
  `premiere0034` / `premiereseanceduvnettoye` ; palier 8 :
  `premiere` (identique) ; **appariés au palier 8**.

### Garanties

- **Compatibilité ascendante** : les couples qui
  fonctionnaient à 8 caractères continuent de s'apparier
  au palier 8 (SC-002).
- **Zéro faux positif** : deux fichiers dont les clés
  normalisées complètes diffèrent ne sont jamais appariés
  (FR-009).
- **Déterminisme** : l'ordre de traitement reste celui de
  la spec 006 (D2) ; les numéros d'occurrence sont
  reproductibles.
- **Aucun changement** : branche « couple », comportement
  sans `--add-context`, messages d'avertissement, format du
  `.json` de contexte, nommage des sorties.
