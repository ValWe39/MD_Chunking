# Idea Intake: Outil de chunking de Markdown avec sortie JSON

- **Slug**: md-chunking-json-output
- **Created**: 2026-10-02
- **Source**: pasted text (demande utilisateur, session du 2026-10-02)
- **Type**: new-capability

## Idea (as captured)

> Je veux que mon outil gère le chunking du texte à l'édition d'un json
> d'output comme décrit ci-après.
>
> Outil de chunking de MD :
>
> Paramètres à maintenir flottants :
>
> Taille min et max du chunk :
>
> Entre 0 et 2000, par défaut entre 100 et 1000.
>
> Peut être proposé par typologie de document ou d'information à
> extraire :
>
> "articles": {"chunk_size": 1500, "overlap": 200},
> "documentation": {"chunk_size": 1000, "overlap": 150}, par défaut
> "conversations": {"chunk_size": 500, "overlap": 50},
> "code": {"chunk_size": 2000, "overlap": 300},
>
> Optimiser le chunk pour qu'il "occupe" la place max en préservant au
> mieux la structure du document => viser le max + evaluer en combien
> de chunks cohérent découper chaque partie / sous-partie.
>
> Type de découpage :
>
> Dans la fourchette min / max :
>
> par section Markdown (si disponible) => par défaut
>
> par paragraphes (si disponible)
>
> par phrases (en dernier recours)
>
> Overlap : entre 0 et 20% du chunk, par défaut 15%.
>
> Rendre l'overlap "intelligent" selon les mêmes paramètres que le
> chunk (respect des parties, sinon paragraphes, sinon phrases).
>
> Autres exigences :
>
> être en mesure de vérifier à l'oeil nu le résultat du découpage avant
> l'embedding
>
> Sortie :
>
> Pour chaque texte d'input => un JSON avec :
>
> l'index du Chunk :
>
> chemin du document (obligatoire)
>
> titre du document (si balisé)
>
> page (si balisée)
>
> le titre de partie / sous partie (si balisé)
>
> le positionnement dans cette partie / sous partie (si balisé, si
> plusieurs chunks pour une partie / sous partie)
>
> le numéro de référence du chunk (obligatoire)
>
> le texte chunké
>
> Par ailleurs :
>
> L'outil doit, par défaut, proposer la création d'un dossier output et
> insérer ses résultats dans des sous dossiers dédiés, numérotés par
> défaut ou construit à partir du X premières lettres du titre du
> document.

## Restated

L'utilisateur veut que l'outil MD_Chunking découpe des documents
Markdown en chunks paramétrables (taille min/max, overlap, typologie de
document) en respectant la structure du document, et produise pour
chaque document un JSON d'output décrivant chaque chunk (métadonnées de
localisation + texte chunké), avec possibilité de vérifier visuellement
le résultat avant embedding.

## Origin & Context

- **Raised by**: l'utilisateur du dépôt MD_Chunking, sur la branche
  001-Initialisation.
- **Trigger**: suite à l'initialisation du projet (rename MD_Cleaner →
  MD_Chunking), définition du besoin fonctionnel principal de l'outil.
  [NEEDS CLARIFICATION: existe-t-il un contexte amont supplémentaire
  (cas d'usage RAG, pipeline d'embedding existant) ?]

## First-Glance Unknowns

- [NEEDS CLARIFICATION: unité de mesure de la taille de chunk —
  caractères, tokens ou mots ?]
- [NEEDS CLARIFICATION: format d'input attendu — fichiers Markdown
  uniquement ? Un fichier = un document ? Y a-t-il plusieurs textes
  d'input par exécution ?]
- [NEEDS CLARIFICATION: notion de « page » pour un document Markdown —
  balise de quel type (front-matter, HTML, frontières de pages PDF
  converties) ?]
- [NEEDS CLARIFICATION: format exact du JSON d'output — un JSON par
  document ? Schéma attendu par le pipeline d'embedding en aval ?]
- [NEEDS CLARIFICATION: « vérifier à l'oeil nu » — quel rendu est
  attendu (fichier texte lisible, markdown annoté, HTML) ?]
- [NEEDS CLARIFICATION: nommage des sous-dossiers d'output — valeur de
  X (nombre de lettres du titre) et comportement si le titre est absent
  ou dupliqué]
- [NEEDS CLARIFICATION: comportement attendu quand une partie/sous-partie
  dépasse la taille max (fusion avec découpage paragraphes/phrases ?)]
- [NEEDS CLARIFICATION: l'overlap 15% par défaut s'applique-t-il en
  nombre de caractères/tokens arrondi, et quel arrondi ?]
