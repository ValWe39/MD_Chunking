# Idea Intake: Titre à 14 chiffres pour le document JSON de sortie

- **Slug**: generation-titre-json
- **Created**: 2026-10-05
- **Source**: pasted text (demande utilisateur, session du 2026-10-05)
- **Type**: improvement

## Idea (as captured)

> Je souhaite ajouter la fonctionnalité suivante, par défaut (ce n'est pas
> une option avec une commande spécifique) :
> Il s'agit de générer le titre du document de sortie Json de la façon
> suivante :
>
> - un nombre à 14 chiffres (ex. 00000000000001, 00000800006701)
>
> - Les 5 premiers sont une conversion des 5 premières lettres du titre du
>   mardown d'input, dans leur ordre d'apparition de l'alphabet
>   (A=1, E=5, etc.).
>   => En cas d'espace, de symbole, d'accent, on passe à la lettre suivante.
>   => si le titre contient moins de 5 lettres, les afficher à droite du
>   nombre. Exemple : titre="abc.md" =>  00123.
>
> - Les 5 suivants sont une conversion des 5 premières lettres du titre du
>   document d'après le Json ("document" => "title" dans le Json), aux
>   mêmes conditions que pour les 5 premiers chiffre (ordre d'apparition
>   de l'alphabet, etc.)
>   => si vide, afficher 00000
>
> - les 4 derniers sont un chiffre unique :
>   => généré à chaque utilisation de l'outil,
>   => dans l'ordre de création des Json, de 0001 à 9999
>   => remis à 0000 après 9999
>   => Nécéssite la sauvegarde qqpart en local de la dernière occurence
>   d'utilisation de l'outil. A la racine de l'outil.. uniquement le
>   numéro de dernière occurence.

## Restated

L'outil doit générer, par défaut et sans option CLI dédiée, un titre à 14
chiffres pour le document JSON de sortie : cinq premiers chiffres encodant
les 5 premières lettres du titre du markdown d'entrée, cinq chiffres
suivants encodant les 5 premières lettres du champ `document.title` du JSON
existant, et quatre derniers chiffres formant un numéro séquentiel persisté
localement (0001 à 9999, puis remise à zéro).

## Origin & Context

- **Raised by**: l'utilisateur (propriétaire du projet), session du
  2026-10-05
- **Trigger**: [NEEDS CLARIFICATION: motif ou cas d'usage à l'origine de la
  demande (identification unique des documents JSON ? tri ?)]

## Arbitrage (2026-10-05)

Décisions tranchées par l'utilisateur après la recherche et l'investigation
sur les méthodologies d'encodage :

1. **Encodage** : numération bijective en base 26 (A=1 … Z=26) — les
   lettres du bloc sont traitées comme les chiffres d'un seul entier,
   décodable sans perte (cf. research.md). Remplace la conversion
   position-par-position initiale (A1Z26), impossible à fixer en largeur
   constante.
2. **Format : 18 chiffres** (au lieu de 14) :

   - 8 premiers chiffres : valeur bijective des 5 premières lettres du
     **nom de fichier** du md d'input (stem, sans extension) ;
   - 6 chiffres suivants : valeur bijective des 4 premières lettres du
     titre `document.title` du JSON ;
   - 4 derniers chiffres : numéro d'occurrence (0001 à 9999, remis à
     zéro après 9999), persisté localement à la racine de l'outil
     (uniquement le dernier numéro).

3. **Padding** : les chiffres convertis sont alignés à **droite** du bloc,
   zéros de remplissage à gauche (ex. « abc » → `00000731`) — seule
   convention décodable en base 26 bijective, conforme à l'exemple initial
   `00123`. La formulation d'origine « afficher à droite » était erronée
   de la part de l'utilisateur.
4. **Destination** : le nombre à 18 chiffres nomme les fichiers de
   sortie — `<18 chiffres>.json` (remplace `chunks.json`) et
   `<18 chiffres>_review.md` (remplace `review.md`). Le **contenu** des
   fichiers (schéma JSON 1.0, review) reste inchangé.
5. **Arborescence** (arbitrage du 2026-10-05) : plus de sous-dossier par
   document — tous les fichiers produits sont écrits directement dans
   `output/` (`output/<18 chiffres>.json`,
   `output/<18 chiffres>_review.md`). Le nommage actuel des sous-dossiers
   (`--naming numbered|title`) devient sans objet. Aucun consommateur en
   aval connu n'impose de contrainte de nommage (l'utilisateur est
   l'unique consommateur).

## First-Glance Unknowns

- [NEEDS CLARIFICATION: casse — « A » et « a » sont-ils convertis
  identiquement ?]
- [NEEDS CLARIFICATION: les lettres accentuées sont-elles ramenées à
  leur lettre de base (É => E=5) ou ignorées comme les symboles ?]
- [NEEDS CLARIFICATION: emplacement exact et format du fichier de
  compteur local (« à la racine de l'outil »), et comportement si le
  fichier est absent, corrompu ou supprimé]
- [NEEDS CLARIFICATION: la remise à zéro après 9999 — repart-on à 0000
  ou à 0001, et le compteur est-il global à l'outil ou par document ?]
- [NEEDS CLARIFICATION: comportement en cas d'exécutions parallèles de
  l'outil (concurrence sur le compteur)]
- [RÉSOLU par l'arbitrage : destination du titre (noms des fichiers de
  sortie, contenu inchangé) et source du bloc 1 (nom de fichier, stem
  sans extension). Le schéma JSON 1.0 et le déterminisme du contenu ne
  sont plus en conflit ; reste à trancher les points ci-dessus.]
