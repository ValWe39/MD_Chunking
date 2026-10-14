# Problem Definition: Enrichir le JSON de sortie avec un contexte fourni par l'utilisateur

- **Slug**: contexte-chunkingid
- **Created**: 2026-10-14
- **Inputs used**: intake.md, research.md, notes utilisateur du 2026-10-14

## Problem Statement

Les sorties du chunking (JSON à plat, nommées par 18 chiffres) ne portent
aucune métadonnée descriptive ou bibliographique du document source :
l'utilisateur qui prépare pour chaque document un fichier de contexte
JSON (typologie, auteurs, éditeur, date, référence, citation) ne peut
pas faire entrer ces informations dans la sortie, et doit réassocier à
la main chaque fichier produit à son contexte — sans lien fiable entre
les deux. De plus, la sortie ne s'auto-identifie pas : rien dans le JSON
ne désigne le nom (numéro) du fichier de sortie lui-même.

## Affected Users & Stakeholders

- **Users**: le propriétaire du dépôt, unique utilisateur de l'outil —
  il traite par lots des corpus Markdown (ex. comptes rendus, rapports,
  ouvrages) et veut que chaque JSON produit embarque la citation
  complète de son document pour un usage aval (traçabilité, citation,
  filtrage) — [source: research.md, corpus Examples/Extension/]
- **Stakeholders**: le même propriétaire — il arbitre seul l'appétit et
  les compromis avec les décisions existantes (spec 003 nommage, spec
  005 entrée dossier).

## Goals

- Chaque document Markdown apparié à un fichier de contexte JSON produit
  une sortie dont le bloc `document` embarque les champs du contexte
  **exactement tels quels, y compris les champs vides** (jamais devinés,
  jamais transformés).
- Chaque sortie embarque, dans un champ dédié, le nom numérique du
  fichier de sortie lui-même, sans le suffixe `.json` (clarification
  utilisateur du 2026-10-14 : « le titre en numéro de ce même json »).
- L'appariement entre un .md et son .json de contexte est fiable y
  compris quand le nom du .md contient espaces et accents que le nom du
  .json convertit en `_` ou simplifie (clarification utilisateur : « à
  tenir compte dans la règle de match ») — la comparaison des 8
  premiers caractères doit donc opérer sur des noms normalisés, pas
  bruts.
- Le mécanisme est optionnel : sans contexte fourni, le processus
  classique reste inchangé, y compris dans un lot mixte (couples
  appariés au nouveau processus, .md sans contexte au processus
  classique).
- Le traitement par lots fonctionne pour les trois dispositions
  observées dans les exemples : couple simple, sous-dossiers de
  couples, mélange couples + .md orphelins.

## Non-Goals

- Aucune extraction, déduction ou normalisation des métadonnées : les
  champs sont copiés verbatim ; pas de conversion CSL-JSON/BibTeX.
- Aucune modification du nommage des sorties (le nom à 18 chiffres de
  la spec 003 reste le seul identifiant ; `chunkingid` le restitue, il
  ne le remplace pas).
- Aucune modification du découpage, du contenu des chunks, ni du rendu
  de relecture.
- Aucune dépendance nouvelle, aucun accès réseau (constitution II, III).

## Success Metrics

- Sur les 4 dossiers d'exemples `Examples/Extension/`, chaque couple
  apparié produit un JSON contenant les 7 champs du contexte verbatim,
  champ vide compris (baseline : 0 champ de contexte embarqué aujourd'hui).
- `chunkingid` est égal au stem du fichier de sortie écrit
  (vérifiable : la valeur du champ = nom du fichier sans `.json`).
- Les .md sans contexte (ex. `Grand_Continent_article.md`, `IFRI.md`)
  produisent des sorties identiques au processus actuel (baseline :
  comportement actuel inchangé, mesurable par comparaison bit à bit).
- Aucun couple des exemples n'est mal apparié (baseline : pas de
  mécanisme d'appariement aujourd'hui).

## Cost of Inaction

Les sorties restent muettes sur l'origine documentaire : pour chaque
chunk utilisé en aval, l'utilisateur reconstruit manuellement le lien
fichier de sortie ↔ contexte bibliographique, avec risque d'erreur
d'affectation dans les lots (les noms à 18 chiffres ne sont lisibles
qu'après décodage). Le corpus de contexte préparé dans
`Examples/Extension/` resterait inutilisable par l'outil.

## Open Questions

- [NEEDS CLARIFICATION: parcours récursif des sous-dossiers — le cas
  « Sous-dossiers » nécessite la récursivité, contraire à FR-008 de la
  spec 005 ; récursivité globale ou limitée au mode contexte ?]
- [NEEDS CLARIFICATION: définition exacte de la normalisation des noms
  pour la règle de match — table précise des transformations (espaces
  et accents convertis en `_` ou simplifiés, traitement des
  apostrophes, traits d'union, casse) ; les exemples fournis ne
  couvrent ni espace ni accent dans les 8 premiers caractères]
- [NEEDS CLARIFICATION: coexistence du champ `Typologie` du contexte
  avec `document.typologie` existant (nom du preset) — remplacement ou
  champ distinct ?]
- [NEEDS CLARIFICATION: `--add-context` s'applique-t-il aussi à un
  fichier .md unique passé en direct, ou seulement aux entrées
  dossier ?]
- [NEEDS CLARIFICATION: comportement des états limites — .json de
  contexte orphelin (ignoré ou avertissement ?), collision de préfixe
  (deux .md matchant le même .json, .json matchant plusieurs .md)]
- [NEEDS CLARIFICATION: incrément de `schema_version` (FR-013) ou
  simple amendement du contrat pour des champs optionnels]
