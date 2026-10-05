# Concept: Ratio reglable en ligne de commande, defaut francais

- **Slug**: tokencpte-flottant
- **Created**: 2026-10-05
- **Recommended option**: Option B — ratio CLI reglable, defaut recale

## Options

### Option A — Recalibrer la constante (sans option d'interface)

- **Sketch**: la valeur par defaut du ratio passe de 4 a 3,5 (ou a la valeur
  issue d'une mesure locale), en editant uniquement la constante du code.
  L'utilisateur voit une estimation plus proche de la realite francaise ;
  tout changement de calibrage reste une edition de code, ce que la spec
  v1 autorise deja explicitement (« modifiable dans le code »).
- **Appetite**: small (quelques heures code + tests + mise a jour des
  artefacts spec, la valeur 4 etant ecrite dans FR-T02 et les contrats)
- **Trade-offs**: gagne la credibility de l'estimation (but 1) sans rouvrir
  la decision « sans parametre d'interface » ; sacrifie le but 3 (adapter
  sans toucher au code) et laisse le calibrage fige pour tout corpus futur.
  Risque : la nouvelle valeur 3,5 reste une intuition non mesuree — meme
  defaut que la valeur 4 actuelle, autre chiffre.
- **Rabbit holes**: derail de la mesure — vouloir « bien » choisir 3,5 peut
  entrainer un protocole de mesure complet qui n'etait pas demande.

### Option B — Ratio reglable en ligne de commande, defaut recale

- **Sketch**: une option CLI dediee accepte une valeur decimale pour le ratio
  caracteres/tokens (defaut recale autour de 3,5 pour le francais) ; le
  rapport de relecture affiche le ratio effectivement utilise. L'utilisateur
  adapte l'estimation a son corpus ou a un futur modele cible sans toucher au
  code ; le decoupage, l'index JSON et le nommage ne changent pas.
- **Appetite**: small (une a deux journees code + tests ; s'y ajoute le
  travail de gouvernance spec : amendement FR-T02 et contrats)
- **Trade-offs**: gagne les trois buts du probleme, calibrage ET adaptabilite ;
  sacrifie la sobriete de la surface CLI (trajectoire recente du depot :
  retrait de --naming) et rouvre une clarification spec v1 documentee.
  Risques : validation d'un parametre decimal (bornes, decimales, arithmetique
  flottante pour des ratios non representables comme 3,3) ; coherence des
  contrats review-render.md et cli.md a reprendre.
- **Rabbit holes**: extension vers des ratios par typologie de preset, vers
  une variable d'environnement ou un fichier de config, ou vers des seuils
  d'alerte par chunk (deja ecarte en v1 par la spec : « nombres seuls ») —
  chacun est un elargissement de portee non demande.

### Option C — Compte exact par tokenizer local

L'« acheter » plutot que le construire.

- **Sketch**: l'estimation est remplacee par un compte exact produit par un
  tokenizer de reference (ex. tiktoken) appele localement au rendu ; le
  ratio arbitraire disparait, remplace par la mesure.
- **Appetite**: medium (dependance nouvelle a auditer, contrats et tests
  a reecrire, choix du tokenizer)
- **Trade-offs**: gagne la precision exacte et supprime definitivement la
  question du calibrage ; sacrifie le principe zero-dependance de
  l'outil (constitution II/III) et la nature modele-agnostique de
  l'estimation, alors que le modele cible n'est pas encore choisi — la
  spec reserve precisement cette option (option B, FR-T08) au moment ou
  un modele sera choisi. Le probleme actuel (calibrage francais) ne
  justifie pas d'anticiper ce saut.
- **Rabbit holes**: choix et geler d'un tokenizer cible alors qu'aucun
  modele aval n'est choisi ; maintenance d'une dependance pour une
  information purement informative.

## Recommendation

Recommander l'option B, conditionnee par une mesure locale prealable.
Seule l'option B satisfait les trois buts du probleme — credible pour le
francais, ecart faible face au compte reel, adaptable sans edition de
code — pour un appetite small ; l'option A ne couvre que le calibrage et
laisse le probleme d'adaptabilite entier ; l'option C est prematuree tant
qu'aucun modele cible n'est choisi et contredit la trajectoire
zero-dependance documentee. La condition : la valeur par defaut (3,5
proposee) doit etre validee par une mesure sur le corpus reel du depot
avant d'etre figee dans la spec — la recherche montre ~3,6-3,9 car./token
pour le francais sur o200k_base, mais aucune mesure locale n'existe, et
la spec actuelle affirme au contraire que le ratio 4 vise la prose
francaise.

## Out of Scope (for the recommended option)

- Comptage exact par tokenizer (option B de la feature 002 / FR-T08) et
  toute dependance nouvelle.
- Toute influence sur le decoupage (unite caractere, fourchette, overlap)
  et sur l'index JSON (aucun champ `tokens`).
- Ratios differencies par typologie de preset, configuration par variable
  d'environnement ou fichier de config, seuils d'alerte par chunk.
- Couverture des scripts non latins (CJK).
- Changement du format du rapport en dehors de la ligne d'en-tete portant
  le ratio.

## Assumptions to Validate

- La valeur par defaut retenue (3,5 ou autre) est confirmee par une mesure
  sur le corpus reel du depot, mesure qui reste hors du pipeline de
  l'outil (script ponctuel, dependance non ajoute au projet).
- L'amendement de la decision spec v1 (FR-T02 et clarification du
  2026-10-02) est faisable dans le workflow spec-kit du depot sans
  invalider les features 001 et 003.
- Le parametre decimal est valide en entree (bornes, decimales) et son
  arithmetique deterministe est garantie quel que soit le ratio saisi.
- Le modele cible aval reste non choisi a court terme ; si un modele est
  choisi, l'option C (compte exact) redevient la trajectoire naturelle et
  ce concept devient transitoire.
