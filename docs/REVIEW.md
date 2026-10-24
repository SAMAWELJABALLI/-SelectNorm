# Internal adversarial review (five roles), after all runs

Each item: concern -> evidence checked -> action taken.

## R1 PI / novelty
- Is the framing honest after the results? SelectNorm-adapt vs B4: no significant difference in any of
  16 cells (results/statistics/*/main.json). Paper says so in abstract, intro, §6.1, discussion. OK.
- Overclaims: grep for "first", "novel", "state of the art", "outperform": none. Factorization is
  presented as an exact identity with consequences, not as new theory; Learning Loss and post-hoc
  deferral are named as closest methods (related work, discussion). OK.
- Selective reporting risk: the one favourable ablation seen during development (mE5 + embedding
  features on S5, +1.1) is reported with its cross-encoder range (-1.2 to +1.1), not as a result.

## R2 Computational linguist
- Normalizer validity outside Tunisian: intrinsic accuracy on NArabizi 46.8 vs TArC 69.1; no
  Moroccan gold. Stated in limitations; MYC conclusions are phrased as encoder-dependent, not as
  dialect facts.
- Taxonomy conditions were fixed in code before inspection (src/evaluation/taxonomy.py docstring).
  Claims restricted to patterns holding across encoders; the one exception (XLM-R, TUNIZI, foreign)
  is named.
- Dialect vs corpus confound: stated in limitations.

## R3 ML design
- Primary SelectNorm variant: the protocol defines B5-adapt with a dev-tuned threshold. An earlier
  table script used the Bayes-threshold variant; corrected so tables, statistics and text all use
  the protocol variant, with the Bayes threshold as a reported variant.
- Target labels: used only in (a) the few-label setting, reported separately, (b) the diagnostic
  target-CV ceiling in the mechanism table, labelled "not deployable", (c) evaluation.
- Noise control is computed only for the Arabic-script regime (the +syn classifier has a different
  training set); the table states which regime it uses.

## R4 Experiments / statistics
- Holm family = protocol's 20 main comparisons per encoder; secondary comparisons (Bayes threshold,
  B4b, ensemble) in a separate family (results/statistics/*/main_secondary.json).
- "Relevant" = >= 1 point, CI excludes 0, Holm p < .05, as pre-specified.
- Every number in the prose was checked against generated tables or JSON; corrections made:
  B1-vs-B0 range (2.3-18.6, not 5-19), T_lex/T_rule loss (4-11), cost saving (12-19%), few-label
  range (-1.2 to +1.4), foreign-token exception, one relevant +syn gain (MARBERTv2 S4).
- Container restart: three runs resumed with identical commands (docs/DEVIATIONS.md D3).

## R5 Writer / reviewer
- Page budget: 13 pages including references and appendices (limit 15).
- No PENDING markers left; no overfull boxes; all cross-references resolve.
- Residual weaknesses a reviewer will raise: binary task only; linear heads on frozen encoders;
  one task (sentiment); mechanism numbers without CIs. All four are in Limitations.
