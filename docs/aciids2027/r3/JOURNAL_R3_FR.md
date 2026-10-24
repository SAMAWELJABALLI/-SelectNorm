# Révision 3 : journal des changements

Base : `paper_lncs_r2/` (révision 2), qui n'a pas été modifiée. Les nouvelles sources sont dans `paper_lncs_r3/`.

Résultat : `main.pdf` fait 15 pages, références et annexe comprises. Le gabarit LNCS est inchangé, tout comme les marges, la police, la géométrie et les quatre tableaux.

Aucun entraînement ni aucune inférence n'a été relancé, et aucun résultat n'a été modifié.

## 1. Figures

### Figure 2

- **Source.** Elle provient de `Figure2_lisible` ; `Figure2_methodes_separees` n'est pas utilisée.
- **Rendu à la taille LNCS.** Le PDF fourni mesure 572 × 418 pt. Réduit à la largeur LNCS (342 pt), son texte tombait vers 5 pt, ce qui est trop petit. J'ai donc relancé votre script à 4,8 in (`figures/figure2_lisible/redraw_figure2_lncs.py`).
  - Ce qui change : la taille, les polices (6,3 à 7,6 pt), les marqueurs et les espacements.
  - Ce qui ne change pas : les données, les couleurs, les marqueurs, les styles de trait, les plages verticales, la légende et les notes B0 sous les panneaux.
- **Une correction.** La note B0 chevauchait l'étiquette de l'axe x ; je l'ai descendue.

### Figure 3

- **Source.** Elle provient de `Figure3_horizontale`, avec les quatre encodeurs sur une seule ligne (1 × 4). Je ne suis pas revenu au 2 × 2.
- **Rendu à la taille LNCS.** Le PDF fourni (733 × 277 pt) aurait été réduit à environ 46 %. J'ai fait le même rendu à 4,8 in (`redraw_figure3_lncs.py`) : les polices font 6,5 à 7,6 pt et la mise en page est inchangée.
- **Troisième série en pleine précision.** Des exports non arrondis de la référence entraînée sur la cible (« target-label CV reference ») existent dans l'archive (`figures/mechanism_table.csv`). La figure utilise donc ces valeurs et leurs intervalles en pleine précision, au lieu des deux décimales des tableaux.
  - `build_figure3_data.py` construit `figure3_data_full.csv` à partir de l'archive. Il vérifie ensuite les 144 valeurs contre votre `figure3_data.csv`, à la précision de ce fichier, et s'arrête au premier écart.
  - Aucune valeur n'a été lue sur des pixels.

### Ce qui est conservé

- Vos scripts, figures (PDF, PNG, SVG), README et données sont conservés sans modification dans `figures/*/original/`.
- Le PDF de la Figure 2 envoyé à part donne le même rendu, au pixel près, que celui du zip. Seuls sa taille de fichier et son horodatage diffèrent. Il est conservé sous `Figure2_lisible_upload.pdf`.
- Les anciennes figures de la révision 2 ont été retirées de r3 et restent dans `paper_lncs_r2/`.

## 2. Légendes et texte

### Légende de la Figure 2

Elle couvre tout ce que vous avez demandé :

- macro-F1 en fonction du coût **estimé** ;
- mE5, CPU, batch size 1 ;
- un passage de l'encodeur sur l'entrée originale vaut 1 ;
- les six valeurs de λ, sans interpolation ;
- les barres sont des écarts-types sur les graines, et non des IC ;
- les règles de comptabilité pour les routeurs et B3, pour B1 et pour R ;
- les échelles verticales diffèrent selon les corpus ;
- les valeurs de B0 hors plage sont données sous les panneaux ;
- les courbes qui se superposent sont tracées à leurs coordonnées réelles.

Les durées mesurées restent dans le texte ; le coût estimé n'est pas présenté comme une latence.

### Légende de la Figure 3

- Les cercles, carrés et triangles sont définis.
- Les intervalles sont des bootstraps à 95 % sur les phrases de test, sans réajustement des estimateurs.
- Une ligne marque AUC = 0,5.
- La comparaison est décrite comme descriptive.
- La formule « unavailable to the zero-shot router » est employée, et la légende précise que la référence n'est pas un plafond théorique.
- Le même remplacement a été fait en M2 et dans la légende du Tableau 3. Il ne reste plus aucune occurrence de « which no deployable system can ».

### Texte (Sect. 6.2)

J'ai ajouté une phrase qui décrit ce que montre la Figure 2 :

- Tous les points des routeurs se situent, en coût, entre les vues uniques (B0, B1) et R. L'économie se fait donc par rapport à deux passages, jamais par rapport à un seul.
- Aucun routeur n'est nettement plus précis que la meilleure vue (au plus +0,6, non significatif).
- À λ égal, SelectNorm et B4 diffèrent de −0,7 à +1,2 point et d'au plus 0,09 passage. Cet écart est descriptif : seul λ = 0 est testé. La proximité visuelle n'est donc pas présentée comme une équivalence.

Toutes les valeurs ont été recalculées à partir de `pareto.csv` :

- coût des routeurs : 1,108 à 2,028 ;
- coût des vues uniques : ≤ 1,043 ;
- coût de R : 1,974 à 2,043.

Il ne reste aucune référence aux anciennes figures (flèches, gris, ▼, 2 × 2, nuage). La discussion dit « not evidence of intrinsic unpredictability ».

### Retour à 15 pages

Les figures, plus grandes, ajoutaient environ 8 lignes. Je n'ai fait que des resserrements rédactionnels, sans retirer aucun résultat, tableau ou réserve :

- résumé : suppression de la liste des dialectes, déjà dans le texte ;
- introduction, travaux connexes et protocole : formulations resserrées ;
- ablations et +syn : idem ;
- discussion, limitations et conclusion : idem ;
- le paragraphe « Information access » devient un intertitre en ligne.

La comparaison mot à mot r2 → r3 est disponible sur demande (`git diff --word-diff`).

## 3. Vérifications

- **Données.**
  - `pareto.csv` est identique octet pour octet à votre `pareto_original.csv` (108 lignes).
  - `mechanism.tex` et `mechanism_ci.tex` fournis sont identiques aux nôtres.
  - Les 144 valeurs de la Figure 3 concordent avec votre CSV.
- **Compilation** (pdfLaTeX + BibTeX).
  - 15 pages.
  - Aucune boîte trop pleine, aucune référence ou citation indéfinie.
  - Toutes les polices sont incorporées.
  - Seul l'avertissement amsmath `\vec` subsiste ; il existait déjà en r2 et est sans effet.
- **Figures à taille finale.** J'ai rendu les pages 9 (Fig. 2) et 11 (Fig. 3) à 130 dpi.
  - Aucun chevauchement ni rognage.
  - Texte d'au moins 6,3 pt.
  - Les figures sont insérées à `\textwidth`, soit environ 1:1.
- **Zip propre.**
  - J'ai décompressé l'archive et supprimé les PDF/PNG des figures et `figure3_data_full.csv`.
  - J'ai relancé les trois scripts, puis compilé.
  - Résultat : 15 pages, figures identiques au pixel près, texte du PDF identique.

## 4. Points restants

- `[GITHUB_REPOSITORY_URL]`, les auteurs, les affiliations, ORCID et e-mails sont toujours des emplacements à remplir. La phrase sur l'usage de l'IA générative reste à compléter. Si la relecture est en double aveugle, il faut anonymiser le lien.
- Le titre de la Figure 3 était demandé en « semibold ». DejaVu Sans n'a pas cette graisse, donc matplotlib utilise le gras (700), comme avec votre script d'origine.
- Les figures sont en couleur (palette Okabe–Ito) et les séries se distinguent aussi par marqueur et style de trait. En niveaux de gris, la Figure 3 reste lisible grâce aux formes ; sur la Figure 2, les courbes de routeurs qui se superposent sont difficiles à séparer en gris.
- Rien n'a été publié ni poussé. Le commit est local.
