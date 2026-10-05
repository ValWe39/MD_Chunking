# Concept: Nommage unique et décodable des fichiers de sortie

- **Slug**: generation-titre-json
- **Created**: 2026-10-05
- **Recommended option**: A — Nom arbitré à 18 chiffres avec compteur
  d'occurrence local

## Options

### Option A — Nom arbitré à 18 chiffres avec compteur local

- **Sketch**: À chaque exécution, l'outil écrit directement dans
  `output/` un fichier `<18 chiffres>.json` et son pendant
  `<18 chiffres>_review.md`, à la place de
  `output/<sous-dossier>/chunks.json` et `review.md`. Le nombre encode :
  les 5 premières lettres du nom de fichier source (8 chiffres,
  numération bijective base 26), les 4 premières lettres du
  `document.title` (6 chiffres), et un numéro d'occurrence à 4 chiffres
  incrémenté à chaque usage de l'outil et persisté dans un fichier local
  à la racine de l'outil. Le nom reste décodable à la main : chaque bloc
  redonne ses lettres d'origine. Le contenu des fichiers ne change pas ;
  les sous-dossiers disparaissent. — [arbitrage intake 2026-10-05]
- **Appetite**: small — jours : une fonction d'encodage pure (déjà
  validée par calcul), un module de compteur persistant, le
  rebranchement de l'écriture des sorties, la mise à jour des tests.
- **Trade-offs**: Gagne : identification décodable et autoportante (le
  nom suffit à retrouver la source), tri naturel par ordre de
  production, conformité aux non-régressions de contenu (schéma 1.0,
  déterminisme du JSON). Sacrifie : le déterminisme du *nom* (une
  ré-exécution du même document produit un nouveau numéro — assumé par
  l'arbitrage), et la simplicité d'un outil jusqu'ici sans état : le
  compteur est le premier état mutable de l'outil, avec son cycle de
  vie (fichier absent, corrompu, supprimé, git-ignoré ou non).
  Risques : collisions après remise à zéro du compteur (deux documents
  aux 12 mêmes lettres et même numéro), exécutions parallèles lisant le
  même compteur, option `--naming` de la CLI devenue sans objet
  (suppression = changement de comportement pour les scripts
  existants).
- **Rabbit holes**: la normalisation des accents et de la casse (le
  corpus réel contient « À LA DÉMOCRATIE », « CONTEXTE » — chaque règle
  choisie décale toutes les valeurs) ; la politique de cycle de vie du
  fichier compteur (emplacement exact, format, régénération) ; le sort
  de `--naming` et de la logique de collision de sous-dossiers à
  supprimer proprement ; la réécriture des tests d'intégration qui
  verrouillent aujourd'hui l'arborescence `output/NNNN/chunks.json`.

### Option B — Empreinte déterministe courte (hash)

- **Sketch**: Les sorties s'écrivent directement dans `output/` sous un
  nom dérivé déterministe : une empreinte compacte (par exemple CRC32,
  encodée sur 8 à 10 chiffres) du nom de fichier source et du
  `document.title`, suffixée du stem du fichier. Même document, même
  nom, à chaque exécution ; aucun état, aucun compteur. — [research.md :
  CRC32 déterministe, collisions rares]
- **Appetite**: small — jours : une fonction de hachage pure
  (bibliothèque standard) et le même rebranchement d'écriture, sans
  module de persistance.
- **Trade-offs**: Gagne : zéro état (l'outil reste sans état, SC-005
  totalement préservé, nom inclus), pas de fichier compteur à gérer,
  pas de remise à zéro ni de concurrence. Sacrifie : le nom n'est plus
  décodable à la main (l'empreinte ne « lit » pas comme des lettres), et
  la ré-exécution écrase le fichier précédent du même document (perte de
  l'historique des occurrences — ou l'inverse : déduplication gratuite,
  selon le point de vue). Risque résiduel de collision d'empreinte.
- **Rabbit holes**: le choix de la largeur d'empreinte et la politique
  en cas de collision ; la tentation d'ajouter un suffixe d'occurrence
  « pour être sûr », ce qui réintroduit le compteur de l'option A.

### Option C — Ne rien construire (statu quo)

- **Sketch**: Les sorties restent `output/<sous-dossier>/chunks.json` et
  `review.md`. Le rattachement d'un fichier à sa source se fait en
  conservant l'arborescence, ou manuellement. — [problem.md, Cost of
  Inaction]
- **Appetite**: aucun.
- **Trade-offs**: Gagne : aucun coût, aucune régression, aucun état.
  Sacrifie : tout l'objectif — les fichiers restent indiscernables dès
  qu'ils quittent leur dossier, et l'utilisateur a déjà arbitré le
  besoin.
- **Rabbit holes**: aucun.

## Recommendation

**Option A** — c'est la seule qui serve les trois propriétés arbitrées et
mesurées dans problem.md : nom autoportant (décodable, métrique de
décodage), distinction de toute exécution (numéro d'occurrence), et
contenu inchangé (schéma 1.0, déterminisme du contenu). L'option B perd
la décodabilité — la métrique centrale de la définition — et
l'écrasement à la ré-exécution contredit « généré à chaque
utilisation » ; l'option C ne résout rien. Le surcoût de A par rapport à
B est limité au module de compteur (small), et le risque de concurrence
est faible pour un CLI local mono-utilisateur. A n'est recommandée que
parce que l'utilisateur a arbitré le format ; le principal risque assumé
est le premier état mutable de l'outil.

## Out of Scope (for the recommended option)

- Tout changement du contenu des sorties : schéma JSON 1.0, rendu de
  relecture, champs, ordre des clés (non-goals de problem.md).
- Unicité absolue ou cryptographique (UUID, hash complet) ; gestion des
  collisions après remise à zéro du compteur au-delà de la convention
  choisie.
- État distant, synchronisation, cloud (constitution II) ; toute option
  CLI pour activer/désactiver le nommage.
- Rétro-compatibilité de l'ancienne arborescence `output/NNNN/` (pas de
  migration des sorties existantes).
- Toute évolution du pipeline de découpage, overlap ou estimation de
  tokens (features 001 et 002).

## Assumptions to Validate

- Les bornes de la numération bijective base 26 tiennent : 5 lettres
  ≤ 12 356 630 (8 chiffres), 4 lettres ≤ 475 254 (6 chiffres) — vérifié
  par calcul ce jour ; la fonction d'encodage restera pure et testable
  en aller-retour.
- La casse sera neutralisée et les accents ramenés à leur lettre de base
  avant encodage (à trancher en spécification) — sans normalisation,
  « CONTEXTE » et « contexte » produisent deux valeurs différentes et
  le corpus réel contient les deux.
- Le compteur est utilisé par une seule exécution à la fois (CLI local
  mono-utilisateur) ; la concurrence est documentée mais non résolue
  en v1.
- Les tests existants (features 001, 002) référencent l'arborescence
  `output/NNNN/chunks.json` et devront être mis à jour — ampleur à
  confirmer lors de la spécification.
- Le fichier compteur à la « racine de l'outil » doit être ignoré par
  git (sinon l'état local pollue le dépôt) — à trancher en
  spécification.
- Le sort de `--naming` (suppression, silencieux, conservé) est tranché
  en spécification ; supprimer l'option change l'interface publique.
