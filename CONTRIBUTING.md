# Contributing

This repository accompanies an unpublished manuscript. Its first purpose is that the reported evidence can be traced and checked, so contributions follow three rules.

1. **Do not change archived evidence.** Files under `results/` (except `results/statistics/reproduced/`) and `paper/tables/` are outputs of recorded runs. A correction is a new run with a new tag, documented in `CHANGELOG.md` and `reproducibility/DISCREPANCIES.md`; the old files stay, or move to `results/archive/` with a note.
2. **Keep repository maintenance separate from manuscript changes.** Changes to `paper/` are revisions of the manuscript and need the authors' agreement.
3. **Never commit corpus text, features or model weights.** `scripts/verify_repository.py --check` (run by CI) fails if restricted artefacts appear.

Before opening a pull request:

```bash
python3 -m pytest -q
ruff check src scripts tests
python3 scripts/verify_repository.py --write   # only if you intentionally added or changed files
python3 scripts/verify_results.py --quick
```

Please report suspected errors in the results through an issue with the "Reproducibility problem" template, giving the file, the value and the command you ran.
