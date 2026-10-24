# Figure 3 : version lisible

## Modifications

Disposition 1 × 4, un panneau par encodeur ; trois positions verticales distinctes par corpus ; couleurs et symboles redondants ; légende sur trois lignes hors des axes ; axe AUC commun ; ligne pointillée à 0,5. Aucun déplacement horizontal des estimations. Le décalage vertical sert uniquement à séparer les trois séries dans chaque corpus.

## Provenance et précision

Source : archive fournie `SelectNorm_ACIIDS2027_LaTeX.zip`.

- Estimations pi et rho-source, avec leurs bornes : `paper_lncs/figures/diagnostic_map.csv`, précision archivistique conservée.
- Référence rho-cible en validation croisée : `paper_lncs/tables/mechanism.tex`, estimations à deux décimales ; bornes de `paper_lncs/tables/mechanism_ci.tex`, à deux décimales. Les valeurs sont donc celles des tableaux, sans inventer de décimales à partir de l’image.

Les trois fichiers sources sont inclus, ainsi que le CSV combiné utilisé pour le tracé. Aucun apprentissage, bootstrap ou calcul de nouveaux intervalles n’a été réalisé. Une version disposant des exports non arrondis de rho-cible pourra remplacer ces valeurs arrondies.

## Légende anglaise proposée

AUC by encoder and test set. Circles: disagreement prediction fitted on unlabelled target text; squares: winning-view prediction among disagreements fitted on source labels; triangles: target-label cross-validated reference using the same feature and estimator family. Horizontal bars denote the archived 95% bootstrap intervals over test sentences, without refitting the estimators. The dashed line marks AUC = 0.5. Tasks, evaluation populations and information access differ; comparisons are descriptive. The target-label reference is unavailable to the zero-shot router and is not a theoretical ceiling. Values for this reference are reproduced at the two-decimal precision available in the supplied tables.

## Insertion et reproduction

Copier `Figure3_horizontale.pdf` dans le dossier figures du projet puis remplacer le chemin de l’ancienne figure dans includegraphics. Utiliser width=\linewidth. Les quatre encodeurs sont alignés sur une seule ligne. Recompiler et vérifier la taille finale des caractères et la limite de 15 pages ; ne pas réduire excessivement cette figure horizontale. Le manuscrit complet n’a pas été recompilé ici.

Reproduction : `python redraw_figure3_horizontale.py` (Python, NumPy, Matplotlib). PDF vectoriel, SVG et PNG sont générés. Le rendu du PDF a été inspecté visuellement.
