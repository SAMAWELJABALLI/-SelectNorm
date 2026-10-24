"""Stand-alone re-computation of the paper's paired bootstrap tests from the exported files.

Needs only numpy and pandas; does not import the project. Usage:
  python scripts/reproduce_stats.py results/export/per_example enc_intfloat__multilingual-e5-base [--n 10000]
Statistic: difference in seed-averaged macro-F1 between system A and system B; resampling unit:
the test sentence (one row = one source sentence); each resample reweights every seed's
predictions with the same multinomial counts. Two-sided p with +1 correction; Holm over the
protocol family (5 comparisons x 4 sets). Seed 12345 reproduces the reported intervals exactly
when --n 10000 and the same set order are used.
"""
import argparse, json, os
import numpy as np
import pandas as pd

SETS = ['S3_tsac_lat', 'S4_tunizi', 'S5_narabizi', 'S6_myc_lat']
PAIRS = [('B5_selectnorm_adapt', b) for b in ['B0_original', 'B1_always', 'B3_conf', 'B4_direct_gain', 'B5_selectnorm_src']]


def mf1(W, y, p):
    f = []
    for c in (0, 1):
        tp = W @ ((p == c) & (y == c)).astype(float)
        fp = W @ ((p == c) & (y != c)).astype(float)
        fn = W @ ((p != c) & (y == c)).astype(float)
        f.append(np.where(2 * tp + fp + fn > 0, 2 * tp / np.maximum(2 * tp + fp + fn, 1e-12), 0.0))
    return 100 * (f[0] + f[1]) / 2


def holm(p):
    p = np.asarray(p); o = np.argsort(p); adj = np.empty_like(p); run = 0.0
    for i, j in enumerate(o):
        run = max(run, (len(p) - i) * p[j]); adj[j] = min(run, 1.0)
    return adj


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root'); ap.add_argument('backend'); ap.add_argument('--n', type=int, default=10000)
    a = ap.parse_args()
    rng = np.random.default_rng(12345)
    res = []
    for s in SETS:
        d = pd.read_csv(os.path.join(a.root, a.backend, f'{s}.csv.gz'))
        y, n = d.label.values, len(d)
        assert d.src_id.is_unique
        W = rng.multinomial(n, np.full(n, 1 / n), size=a.n).astype(np.float32)
        for A, B in PAIRS:
            ca = [c for c in d.columns if c.startswith(f'yhat__{A}__s')]
            cb = [c for c in d.columns if c.startswith(f'yhat__{B}__s')]
            one = np.ones((1, n), np.float32)
            point = np.mean([mf1(one, y, d[c].values)[0] for c in ca]) - np.mean([mf1(one, y, d[c].values)[0] for c in cb])
            diff = np.mean([mf1(W, y, d[c].values) for c in ca], 0) - np.mean([mf1(W, y, d[c].values) for c in cb], 0)
            p = min(1.0, 2 * min((np.sum(diff <= 0) + 1) / (a.n + 1), (np.sum(diff >= 0) + 1) / (a.n + 1)))
            res.append(dict(set=s, a=A, b=B, diff=float(point), lo=float(np.percentile(diff, 2.5)), hi=float(np.percentile(diff, 97.5)), p=float(p)))
    for r, q in zip(res, holm([r['p'] for r in res])):
        r['p_holm'] = float(q)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
