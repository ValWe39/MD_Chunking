# Decision: Ratio caracteres/tokens reglable en CLI, defaut recale pour le francais

- **Slug**: tokencpte-flottant
- **Decided**: 2026-10-05
- **Verdict**: go
- **Artifacts reviewed**: intake.md | research.md | problem.md | concept.md

## Scorecard

| Critère | Note |
| ------- | ---- |
| Problem validity | adequate |
| Evidence strength | adequate |
| Value vs. inaction | adequate |
| Feasibility / appetite | strong |
| Strategic fit | adequate |
| Risk posture | adequate |

Justifications :

- **Problem validity — adequate** : problème réel pour l'unique
  utilisateur du rapport de relecture : biais documenté d'environ 8-15 %
  (ratio 4 contre ~3,6-3,9 mesuré pour le français) et impossibilité
  d'adapter sans éditer le code ; mais information purement
  informative, aucun impact sur le découpage ni l'index (problem.md,
  research.md).
- **Evidence strength — adequate** : sources externes convergentes sur
  la direction (OpenAI : ~4 car./token pour l'anglais, langues non
  anglaises plus coûteuses ; mesures o200k_base : français 1,52
  tokens/mot vs 1,16 anglais ; témoignage communautaire : +70-100 %
  tokens/mots en français). MAIS aucune mesure locale sur le corpus
  réel et la spec 002 affirme au contraire que le ratio 4 vise la prose
  française — la valeur exacte du défaut reste à valider, pas la
  direction du changement (research.md).
- **Value vs. inaction — adequate** : le coût de l'inaction est faible
  et borné (constante éditable, champ purement informatif) ; la valeur
  tient dans le but 3 — adaptabilité sans édition de code — qu'aucune
  alternative ne couvre, pour un appétit small (problem.md, concept.md).
- **Feasibility / appetite — strong** : appétit small crédible : rayon
  d'impact restreint à reviewer.py et cli.py, index JSON non affecté
  (FR-T07), pattern d'option et de validation déjà établi dans la CLI
  (--min, --max, --overlap), précédent de marché LangChain
  length_function (concept.md, research.md).
- **Strategic fit — adequate** : aucune dépendance nouvelle ni appel
  réseau (constitution II/III respectées) ; tension documentée avec la
  clarification v1 « sans paramètre d'interface » de la feature 002,
  mais le processus spec-kit prévoit l'amendement et le propriétaire —
  seul décideur — a confirmé l'option B explicitement (research.md,
  concept.md, input utilisateur).
- **Risk posture — adequate** : risques majeurs identifiés avec
  mitigations connues : arithmétique flottante (calcul en entiers ou
  restriction du format), bornes de validation (pattern existant),
  cohérence des contrats spec à reprendre ; le risque principal
  résiduel est la valeur du défaut, explicitement conditionnée par le
  concept à une mesure locale préalable (concept.md, assumptions).

## Verdict & Rationale

Go. Les six criteres sont adequate ou mieux, aucun weak ni unknown au
scorecard. La preuve est adequate — plusieurs sources independantes convergent
sur le fait que le ratio par defaut calibre anglais sous-estime les tokens
du francais, et la valeur exacte du nouveau defaut est un parametre a fixer
pendant la specification, pas une inconnue bloquante : le concept conditionne
explicitement le figeage de la valeur par defaut a une mesure locale sur le
corpus reel du depot. L'option B est la seule qui couvre les trois buts du
probleme, pour un appetite small et un rayon d'impact borne ; l'option C
(compte exact) reste prematuree tant qu'aucun modele cible n'est choisi et
deviendra la trajectoire naturelle le jour ou il le sera. La tension avec la
clarification v1 de la feature 002 est assumee : elle se resout par
l'amendement spec, travail inclus dans le perimetre de la specification.

## If go — Handoff to `/speckit-specify`

- **Problem**: l'estimation de tokens du rapport de relecture est calibree
  pour l'anglais (ratio 4) et inadaptable sans editer le code, sur un corpus
  essentiellement francais dont la densite reelle est ~3,6-3,9 car./token.
- **Chosen approach**: Option B du concept — option CLI dediee acceptant un
  ratio decimal caracteres/tokens, defaut recale pour le francais (~3,5,
  a valider par mesure locale), affichage du ratio effectif dans l'en-tete
  du rapport.
- **In scope**: parametrage du ratio au rendu (reviewer.py), option CLI avec
  validation bornee, amendement des artefacts spec concernes (FR-T02,
  contrats review-render.md et cli.md), mise a jour des tests et du README.
- **Out of scope**: comptage exact par tokenizer et toute dependance
  nouvelle ; influence sur le decoupage, l'index JSON ou le nommage ; ratios
  par typologie de preset ; configuration par env-var ou fichier de config ;
  seuils d'alerte par chunk ; scripts non latins (CJK).
- **Success metrics**: ecart estimation/compte de reference sur le corpus
  reel dans une tolerance a definir (protocole de mesure a fixer) ; signal
  qualitatif de credibility en relecture courante.
- **Carried-forward open questions**:
  - [NEEDS CLARIFICATION: mesure locale sur le corpus reel du depot pour
    figer la valeur par defaut (3,5 proposee, ~3,6-3,9 suggere par les
    mesures externes) — faire avant d'ecrire la valeur dans la spec]
  - [NEEDS CLARIFICATION: bornes de validation et nombre de decimales
    acceptes pour l'option ; strategie arithmetique (entiers vs flottant)
    pour garantir le determinisme]
  - [NEEDS CLARIFICATION: format d'affichage du ratio decimal dans
    l'en-tete du rapport]
  - [NEEDS CLARIFICATION: amendement de la feature 002 (FR-T02 et
    clarification du 2026-10-02) selon le workflow spec-kit du depot]
