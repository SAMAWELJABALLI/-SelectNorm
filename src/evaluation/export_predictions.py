"""Export per-example predictions needed to re-run the paper's statistical tests independently.

For every backend and test set: one CSV (gzip) with one row per test sentence and columns
  id, src_id, label, p_orig, p_norm, and yhat__<system>__s<seed> for every system/seed whose
  route was saved at lambda = 0 (main tag),
plus manifest.json (backends, sets, systems, seeds, row counts, sha256 of each file). Texts are
not exported (several corpora carry no redistribution licence); `id` is the row of
data/prepared/<set>.jsonl, which src/data/prepare.py rebuilds deterministically from the raw
corpora at the commits listed in the paper. Output: results/export/per_example/
"""
import glob, gzip, hashlib, json, os, re, sys
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.routing.views import ROOT, load_set
from src.routing.run import TESTS

OUT = os.path.join(ROOT, 'results', 'export', 'per_example')


def main():
    os.makedirs(OUT, exist_ok=True)
    man = {'note': __doc__, 'files': {}}
    for bdir in sorted(glob.glob(os.path.join(ROOT, 'results', 'predictions', 'enc_*'))):
        b = os.path.basename(bdir)
        P = np.load(os.path.join(bdir, 'probs.npz'))
        for s in TESTS:
            rows = load_set(s)
            df = pd.DataFrame({'id': [r['id'] for r in rows], 'src_id': [r['src_id'] for r in rows],
                               'label': [r['label'] for r in rows]})
            df['p_orig'] = np.round(P[f'{s}__orig'], 6)
            df['p_norm'] = np.round(P[f'{s}__cons'], 6)
            for f in sorted(glob.glob(os.path.join(bdir, 'routes', f'main__*__{s}__s*.npz'))):
                m = re.match(rf'main__(.+)__{s}__s(\d+)\.npz', os.path.basename(f))
                df[f'yhat__{m.group(1)}__s{m.group(2)}'] = np.load(f)['yhat'].astype(int)
            os.makedirs(os.path.join(OUT, b), exist_ok=True)
            path = os.path.join(OUT, b, f'{s}.csv.gz')
            with gzip.open(path, 'wt', compresslevel=9) as fh:
                df.to_csv(fh, index=False)
            man['files'][f'{b}/{s}.csv.gz'] = dict(rows=len(df), columns=len(df.columns),
                                                   sha256=hashlib.sha256(open(path, 'rb').read()).hexdigest())
    json.dump(man, open(os.path.join(OUT, 'manifest.json'), 'w'), indent=1)
    print(len(man['files']), 'files')


if __name__ == '__main__':
    main()
