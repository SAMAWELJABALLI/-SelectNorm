# SelectNorm: response to the final targeted review (second revision)

Date: 2026-10-23. This answers the four critical issues and the further improvements of the
final review (part A). It then states which findings changed and which stayed identical (part B),
the residual threats (part C), an internal reviewer recommendation (part D), and the status of the
eight findings from the first review round (part E). The data, splits, seeds, systems, metrics,
primary comparisons and decision rule are unchanged. Every new run is listed below and in
docs/DEVIATIONS.md (D5).

## A. Point-by-point response

**A1. End-to-end latency benchmark.** *Agreed: the previous benchmark used a surrogate.*
In the old `measured_cost.py`, `f()` applied a random projection to an un-normalized pooled
vector instead of the trained head. It also took routing decisions from the archived `g`; the
router score was computed only for timing. Its output is archived as
`results/archive/measured_cost_surrogate_head.json`.

The new `src/evaluation/measured_cost.py` runs the deployed pipeline on raw test text at batch
size 1, with nothing read from cached predictions or routes:
- the encoder at its pinned revision;
- masked mean pooling and L2 normalization;
- the trained logistic head and temperature, refitted deterministically from the cached training
  features with the saved C;
- the normalizer;
- decision-point features computed from the live p0 and the live normalizer metadata;
- the SelectNorm-adapt router of each seed, with its λ=0 threshold tuned on policy-dev exactly as
  in `run.py`;
- the second pass, only when the router selects it.

Checks, all in `results/metrics/measured_cost*.json` with per-sentence files in
`results/metrics/measured_cost*_live/`:

| Check | Result |
|---|---|
| (a) Refitted head vs `probs.npz` on cached features | max abs difference 0.0 for all 4 encoders |
| (b) Routing decisions replayed from cached inputs vs archived decisions | 0 mismatches (4 encoders × 4 sets × 5 seeds) |
| (c) Live probabilities vs cached | max abs difference 1.6e-4; 0 label flips in either view |
| (c) Live routing decisions vs archived | 0 of 184,400 differ (9,220 sentences × 5 seeds × 4 encoders) |
| (c) Live final predictions vs archived | 0 differ; live macro-F1 equals archived macro-F1 exactly |

No discrepancy was found. That is a measured result; it is not assumed.

Timing used 200 random sentences per set and encoder, with all four systems run back to back in
rotating order after a 300-sentence two-view warm-up:

| Measure | Result |
|---|---|
| B0 | 22–31 ms per sentence |
| B1 | 0.91–1.05 passes |
| SelectNorm-adapt | 1.31–1.97 passes |
| R | 1.91–2.07 passes |
| Gap to the token-model estimates, B1 and R | −0.02 to +0.05 passes |
| Gap to the token-model estimates, SelectNorm | +0.03 to +0.07 passes (feature computation is not in the token model) |

Previously reported (surrogate): SelectNorm 1.32–1.98, B1 0.91–1.04, R 1.92–2.07, B0 23–30 ms. The
conclusion is unchanged.

Anomaly: the first full run overlapped a concurrent CPU job (the few-label replay). That inflated
the mE5 TUNIZI timings; R came out at 1.71 passes, below SelectNorm. mE5 was re-timed alone
(`measured_cost_mE5_retime.json`). The first run is kept unchanged in `measured_cost.json`. The
reported numbers (`measured_cost_reported.json`) take mE5 from the re-time and the other encoders
from the first run. Routing and prediction checks are 0 mismatches in both runs.

**A2. Few-label audit.** *Agreed: the previous audit checked fold disjointness only.*
The new `src/evaluation/check_fewlabel.py` replays every targeted and random draw of
`src/routing/adapt.py`: 8 backends × 4 sets × 5 seeds × 5 budgets × 5 draws × 2 folds = 8,000 draws.
It saves the sampled indices and source ids in `results/audit/fewlabel_samples/<backend>.jsonl.gz`.
For each draw it counts:
- sampled labels from the scored fold: 0;
- source ids shared between sampled and scored sentences: 0;
- identical normalized texts between sampled and scored sentences: 0;
- targeted sentences that are not disagreements: 0.

To show the replay is what `adapt.py` actually used, `adapt.py` got an optional `--log-samples`
flag. It writes the indices it uses and does not change the computation. Rerunning mE5 with it:
- the 1,000 logged draws match the replay in 1,000 of 1,000 cases;
- the 2,500 result rows are identical to the archived `runs_adapt.jsonl` (max difference 0.0).

The other seven backends are verified by replay only (stated). One previously unreported fact: in
375 targeted draws (S5 NArabizi, k=128), a fold had only 97–116 disagreements. The targeted budget
there is smaller than k, and this is now stated in Section 5.

**A3. Scope of the mechanism conclusion.** *Agreed.* Wording now restricts the conclusion to the
decision-point features and estimator families tested:
- Abstract: "This is limited predictability under these choices, not unpredictability in
  principle."
- Introduction.
- M2: heading "weakly predictable from z", plus "this does not exclude that other features or
  estimators would predict it better".
- M3: "with these features and a linear estimator".
- Discussion: "limits of the features and estimators we evaluated ... do not show that the
  conditional advantage is intrinsically unpredictable".
- Limitations.

Gradient boosting was evaluated only for mE5, and only as a router (not for the target-CV
ceiling); this is stated. One factual correction: the Discussion said source ρ̂ ranks direction
"below chance" for XLM-R on Algerian and Moroccan text. The Algerian interval contains 0.5, so it
now says "at or below chance".

**A4. Statistical conclusions.** *Agreed.*
- Non-significance is no longer read as equivalence.
- New Table 7 (appendix) gives every paired difference SelectNorm-adapt minus B1, B3, B4 and
  SelectNorm-src, with its 95% interval, for all four encoders. It marks Holm significance and
  intervals inside (−1, +1).
- Section 6.1: against B4, every interval lies inside [−0.63, +0.58], within the protocol's 1-point
  relevance margin in all 16 cells. This equivalence reading is labelled post hoc and is not
  corrected for multiplicity.
- Against B1 and B3, only 4 and 6 of 16 intervals lie within ±1. The remaining non-significant
  intervals extend from −1.3 to +2.4, so a small gain or loss cannot be excluded there.
- "Matches the strongest routers" is replaced by bounded statements.
- Descriptive comparisons (few-label targeted vs random, set-level choice, Pareto curves) are
  marked "descriptive".

Found during this check, and corrected:

1. *Protocol wording vs paper rule.* The protocol defines "practically relevant" as an
   unadjusted 95% interval excluding zero with |diff| ≥ 1. The paper used the stricter Holm-adjusted
   p < 0.05.
   - In the primary (Arabic-script) regime the two rules select exactly the same comparisons for
     all four encoders.
   - In the exploratory +syn regime they differ in 5 comparisons. Against the better single view,
     the protocol rule adds two gains for mE5: S3 +2.1 and S4 +1.4.
   - Section 5 states both rules, and the +syn paragraph reports both.
2. *Unreported relevant losses.*
   - Primary regime: SelectNorm-adapt is relevantly worse than B0, the better single view, on LaBSE
     MYC (−2.5). The Table 2 marker showed it; the text did not. It now does.
   - +syn regime: SelectNorm-adapt is relevantly worse than the better view in two MYC cells
     (LaBSE −2.4, MARBERTv2 −1.8). These are now reported.
   - The earlier +syn sentence ("only one such gain ... is relevant") was incomplete and has been
     replaced.

**A5. Further improvements.**

- *All four encoders' statistics reproduced.* `scripts/reproduce_stats.py` uses only the exported
  per-example files. It reproduces all 80 comparisons (4 encoders × 20): every difference,
  interval, p and Holm p, with max abs difference 0.0 and 0 changed decisions. Outputs are in
  `results/statistics/reproduced/`.
- *Seeds.*
  - f is trained once per encoder and regime, deterministically.
  - Seed s fixes the 80/20 policy split (rng 1000+s), and therefore the routers and tuned
    thresholds. It also fixes the B2 random draws and the few-label draws.
  - Logistic fits are deterministic, so seed variance reflects the policy split only. It does not
    reflect retraining of f or encoder randomness.
  - This is now stated in Section 5.
- *Mean vs input-dependent cost (exploratory).* `src/evaluation/cost_threshold.py` replaces λ·c̄
  with λ·c1(x), each input's own token-model cost of the second pass, which is known at the
  decision point because T(x) is.
  - Check: the mean-cost variant reproduces the archived Bayes-threshold rows exactly.
  - Effect: cost falls by 0–0.11 passes (mean 0.03); macro-F1 changes by −2.0 to +0.6 (mean
    −0.13).
  - The input-dependent version is no worse on both measures in 29 of 80 encoder–set–λ cells, and
    trades accuracy for cost in 48.
  - It moves operating points along the frontier; every point still costs more than one pass.
  - Reported in App. B and in one sentence in Section 6.2.
- *Pre-specified vs exploratory.* A new "Status of analyses" paragraph (Section 5) lists:
  - pre-specified in PROTOCOL.md: main comparisons and statistics, λ grid, embedding, boosting and
    T_lex ablations, few-label setting, RQ4;
  - run with pre-registered code but not named in the protocol: other ablations;
  - exploratory, logged after the first mE5 results: T_cov, +syn, M1–M4;
  - added in revision: intervals, sensitivity, equivalence readings, timing, audit,
    input-dependent cost.

  Limitations no longer says "everything follows the protocol".
- *TArC intrinsic results* remain labelled as development results (Table 6 caption, intro,
  Limitations).
- *Independent linguistic validation set.* No genuinely new blind annotations are available to
  us, so none was built. It remains a stated limitation.
- *Negative results.* All are preserved. The losses in A4.2 are newly stated.
- *15 pages.* The compiled PDF has 15 pages including references and appendices, with no overfull
  boxes and no undefined references. To fit:
  - the RQ4 table's numbers moved into the text, with per-encoder values released in
    `paper/tables/consistency.csv`;
  - the noise-sensitivity table shows ranges over sets, with per-set values in
    `paper/tables/noise_sensitivity.csv`;
  - empty appendix section headings were removed;
  - appendix text is set in \small;
  - prose was condensed.

  No result was dropped from the released files.

## B. What changed and what stayed identical

Identical (verified):
- every accuracy result and λ=0 decision;
- Table 2 and all significance decisions;
- all paired-test statistics, re-derived independently for 4 encoders;
- the mechanism point estimates and intervals;
- the few-label results (rerun identical for mE5);
- the noise-reference values;
- the cost-fixed λ>0 results;
- the framing decision: no consistent, statistically supported gain over competitive baselines.

Changed:

| # | Item | Before | After |
|---|---|---|---|
| 1 | End-to-end timing | surrogate head, cached routes | real pipeline, live routes; numbers in A1 (SN 1.31–1.97 vs 1.32–1.98); conclusion unchanged |
| 2 | Similarity claims | "matches", "same" | paired differences with intervals; equivalence vs B4 is post hoc |
| 3 | Mechanism conclusion | general | restricted to the features and estimators tested |
| 4 | XLM-R Algerian direction | "below chance" | "at or below chance" |
| 5 | Relevant losses | not in the text | stated: LaBSE MYC vs B0 (−2.5); +syn LaBSE and MARBERTv2 MYC (−2.4, −1.8) |
| 6 | +syn relevant gains | 1 (Holm) | 1 (Holm), plus 2 more under the protocol's unadjusted rule |
| 7 | Few-label | — | targeted budget below k on S5 at k=128 is now stated |
| 8 | Audit claim | "1,000 draws found no overlap" | 8,000 draws replayed and checked against a logged rerun |

## C. Residual threats to validity

1. Single task (binary sentiment); frozen encoders with linear heads only.
2. No independent transliteration test set; intrinsic normalizer scores are development results.
3. Dialect is confounded with corpus, platform, topic, period and label balance.
4. Costs are token-model estimates on one 4-core CPU. The end-to-end check covers 200 sentences per
   set and λ=0, and its timings are sensitive to concurrent load (one rerun was needed).
5. Mechanism intervals cover evaluation sampling, not estimator refitting. The target-CV ceiling
   is linear only; gradient boosting was tried for mE5 routing only.
6. The equivalence reading against B4 is post hoc and uncorrected for multiplicity. Many
   comparisons with B1 and B3 are inconclusive.
7. Two relevance rules (Holm vs unadjusted) disagree in the exploratory +syn regime.
8. The noise reference depends strongly on how the reference classifiers are built.
9. charlr test results were inspected during development; this motivated the few-label setting.
10. The few-label replay is verified against a logged rerun for mE5 only; the other seven
    backends rely on the deterministic replay.
11. Seed variation covers the policy split only, not retraining of f.
12. TUNIZI, NArabizi and MYC state no licence, and MARBERTv2 has none on its model card.

## D. Internal reviewer recommendation

*Recommendation: accept as an analysis paper after this revision. Do not accept as a method
paper.*

- Code and results are now reproducible end to end:
  - the deployed pipeline reproduces every archived decision;
  - an independent script reproduces every reported test;
  - the few-label label separation is verified at the level of sampled source ids.
- The claims are calibrated. The paper reports a well-controlled negative result for per-input
  routing with frozen encoders (no consistent gain, higher cost than a single view). It also gives
  a measured account of why: weak conditional-advantage prediction from decision-point features.
- Remaining weaknesses:
  - limited scope (one task, frozen encoders);
  - development-only normalizer evaluation;
  - the empirical rather than intrinsic nature of the predictability limit, now stated plainly;
  - modest methodological novelty (the factorization is elementary).
- Likely reviewer score at a CORE A/A* venue: borderline. The contribution is the careful
  negative evidence and the reproducibility; reviewers who want a new method or a positive result
  will rate it lower.

I would not change the scientific claims further to improve acceptance prospects.

## E. Status of the eight findings from the first review round

| Finding | Status | Where |
|---|---|---|
| 1 Cost formulation | Addressed; this round also validated it with the real pipeline | Sec. 3, 6.2, App. A–B (B = Reproducibility) |
| 2 Normalizer leakage | Addressed by relabelling and audit; no independent test set exists (threat 2) | Table 6, Limitations |
| 3 Novelty | Addressed (elementary identity, standard bound) | Title, abstract, Sec. 1, 3 |
| 4 Oracle noise | Addressed (reference, sensitivity) | Sec. 6.3 M4, Table 11 |
| 5 Few-label separation | Addressed, now at the level of sampled ids | Sec. 5, App. B |
| 6 Mechanism uncertainty | Addressed (seed-averaged bootstrap intervals; refitting not covered) | Table 3, Table 10 |
| 7 Scope | Addressed (frozen encoders), plus the mechanism scope from this round | Title, Sec. 1, 6.3, 7, Limitations |
| 8 Presentation | Addressed (Table 2 panels, Fig. 3 ticks, Fig. 1 costs) | — |

Partially open: finding 2 cannot be fully resolved without new blind annotations.
