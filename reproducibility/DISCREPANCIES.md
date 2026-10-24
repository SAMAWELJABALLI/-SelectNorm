# Discrepancy and limitation register

Each entry gives what was found, where, the diagnosis and the action taken. No archived number and no manuscript value was changed.

| # | Finding | Diagnosis | Action / status |
|---|---|---|---|
| 1 | `src/evaluation/tables.py` writes "normalize", "normalizer"; `paper/tables/main.tex`, `main_syn.tex`, `ablation.tex` say "normalise", "normaliser" | British spelling applied by hand to row labels during the LNCS revisions; every number is identical | documented; `verify_results.py` C6 maps the spellings before comparing. Resolved |
| 2 | `docs/DEVIATIONS.md` D4 says "all lambda = 0 rows have identical macro-F1 and selection (0 of 12,480 changed)" | 12,480 is the number of non-diagnostic rows in the eight `main` logs, of which 5,280 are λ = 0 rows. None of them changed; 593 λ > 0 rows changed macro-F1 (as stated) and 1,027 changed selection rate | wording imprecision in a historical note; the conclusion holds (C9). Not edited, recorded here |
| 3 | The RQ4 consistency figures (73–77%, Sect. 6.4) cannot be regenerated from the repository | they need the NArabizi gold transliterations in `data/prepared`, which are not distributed | AVAILABLE_NOT_EXECUTED; reproducible after `fetch_data.sh` and `prepare` |
| 4 | Mechanism AUCs (Table 3, Fig. 3) are verified only from their archived JSON to the table and figure | computing them needs the encoder features (`features/`, 1.1 GB, not distributed) | AVAILABLE_NOT_EXECUTED for the AUC computation itself |
| 5 | `src/routing/policies.py::fit_proba` raised `ValueError` on an empty training set (e.g. no disagreement in a labelled split) | edge case never met by an archived run: every run completed and every number is reproduced after the change | fixed in a separate commit (returns 1/2, i.e. no evidence either way); covered by a test |
| 6 | `src/data/prepare.py` refers to `docs/DATA.md`, which did not exist | documentation gap | `docs/DATA.md` added, pointing to `reproducibility/DATASETS.md` |
| 7 | MARBERTv2 states no licence; TUNIZI, MYC and the NArabizi sentiment layer state none either | upstream | not redistributed; research use only; the authors should confirm before making the repository public |
| 8 | The TArC README heading reads "Attribution 4.0 International (CC BY-NC-SA 4.0)" | inconsistent heading upstream | read as the more restrictive CC BY-NC-SA 4.0; only sentence indices are included |
| 9 | Per-row gold labels of TUNIZI and MYC are part of the per-example exports | needed for independent statistics; contain no text | kept in the private repository; decision for the authors before public release (`DATASETS.md`) |
| 10 | The first mE5 end-to-end timing overlapped a concurrent job | recorded in D5 | both runs kept; the reported values come from the re-timing (`measured_cost_reported.json`) |
| 11 | The development reference `charlr` was inspected on test data, and two design decisions followed | disclosed in `docs/PROTOCOL.md` | not reported; marked `development` in the experiment matrix |
| 12 | The `+syn` regime and `T_cov` were added after the first mE5 results | deviation D1, labelled exploratory | reported as exploratory in the paper |
| 13 | A full re-execution (level 3) has not been run from this repository, and nothing has been run on a second machine | time and data access | stated in `VERIFICATION_REPORT.md` |
| 14 | The manuscript carries placeholders (authors, affiliations, ORCID, e-mail, AI-use statement, `[GITHUB_REPOSITORY_URL]`) | intentional | to be completed by the authors; anonymise the link if the review is double-blind |
