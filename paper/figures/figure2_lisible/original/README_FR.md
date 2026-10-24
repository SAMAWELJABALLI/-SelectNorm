# Figure 2 — versions lisibles

Les deux figures sont reconstruites depuis les 108 lignes du fichier `pareto_original.csv`, extrait de l’archive LaTeX fournie (`paper_lncs/figures/pareto.csv`). Aucun score, coût ou écart-type n’a été modifié. Aucun modèle n’a été exécuté.

## Choix de la figure

- `Figure2_lisible.pdf` : version compacte, quatre corpus, légende extérieure, styles et marqueurs distincts, flèches supprimées. C’est le remplacement conseillé dans le manuscrit. Certaines courbes restent confondues parce que leurs coordonnées sont identiques ou très proches ; aucun décalage artificiel n’est appliqué. Les valeurs B0 hors de la plage verticale sont indiquées sous les panneaux, avec leur valeur exacte arrondie à une décimale.
- `Figure2_methodes_separees.pdf` : une méthode par panneau, toutes les références B0/B1/R dans la plage affichée. Cette version permet de lire chaque méthode séparément. Elle demande davantage de place et ne doit pas être réduite à une petite vignette. Elle constitue une alternative de mise en page, pas un supplément obligatoire.

Les échelles verticales varient selon le corpus ; elles sont communes aux méthodes d’un même corpus dans la version séparée. Les segments relient les six valeurs de lambda archivées ; ils ne sont pas une interpolation de résultats mesurés supplémentaires. Les barres représentent les écarts-types archivés, pas des intervalles de confiance.

## Légende anglaise proposée — version compacte

Macro-F1 versus estimated cost for mE5 (batch size 1, CPU), with one original-input encoder pass normalised to 1. Curves connect the six evaluated operating points, lambda in {0, .01, .02, .05, .1, .2}; error bars show standard deviations over seeds. Router costs include the first encoder pass and normalisation, plus the second pass when selected; B1 includes normalisation and one pass, and R includes both passes. Colours, line styles and markers identify methods. Vertical scales differ across corpora. B0 values outside the displayed range are reported beneath the corresponding panels. Coincident curves retain their actual coordinates.

## Insertion LaTeX

```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=\linewidth]{figures/Figure2_lisible.pdf}
  \caption{Insert the caption above, adapting method names to the manuscript.}
  \label{fig:cost_f1}
\end{figure}
```

Copier le PDF dans `figures/`, remplacer l’ancienne illustration et recompiler le manuscrit. Le nombre final de pages et la lisibilité à la taille LNCS doivent être vérifiés après insertion ; le manuscrit complet n’a pas été recompilé dans cette intervention. Ne pas supposer qu’un supplément est accepté par la conférence.

## Reproduction

Python avec NumPy et Matplotlib :

```bash
python redraw_figure2.py
```

Le script produit les deux versions en PDF vectoriel, SVG et PNG. Les PDF/PNG ont été inspectés visuellement. Les données archivées sont incluses pour permettre la reproduction exacte.
