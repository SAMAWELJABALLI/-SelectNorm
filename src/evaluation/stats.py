"""Paired bootstrap over source sentences for seed-averaged macro-F1 differences.

python -m src.evaluation.stats --backend <tag> --tag main --pairs B5_selectnorm_adapt:B0_original,...
Resampling unit: the source sentence (every test row has a distinct src_id; RQ4 pairs share
one and are resampled together). Each resample reweights all seeds' predictions with the
same multinomial counts, so the statistic is the difference of seed-averaged macro-F1.
Two-sided p = 2 * min(P(diff <= 0), P(diff >= 0)) with the +1 correction; Holm over all pairs
and sets of one backend. Output: results/statistics/<backend>/<tag>.json
"""
import argparse, glob, json, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.routing.views import load_set, ROOT
from src.routing.run import TESTS


def macro_f1_counts(W, y, yhat):
    """W: (B, n) resample counts; returns (B,) macro-F1 for binary labels."""
    f = []
    for c in (0, 1):
        tp = W @ ((yhat == c) & (y == c)).astype(float)
        fp = W @ ((yhat == c) & (y != c)).astype(float)
        fn = W @ ((yhat != c) & (y == c)).astype(float)
        f.append(np.where(2 * tp + fp + fn > 0, 2 * tp / np.maximum(2 * tp + fp + fn, 1e-12), 0.0))
    return 100 * (f[0] + f[1]) / 2


def load_preds(pdir, tag, system, name):
    files = sorted(glob.glob(os.path.join(pdir, f'{tag}__{system}__{name}__s*.npz')))
    return [np.load(f)['yhat'] for f in files]


def holm(p):
    p = np.asarray(p)
    order = np.argsort(p)
    adj = np.empty_like(p)
    run = 0.0
    for i, j in enumerate(order):
        run = max(run, (len(p) - i) * p[j])
        adj[j] = min(run, 1.0)
    return adj


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--backend', required=True)
    ap.add_argument('--tag', default='main')
    ap.add_argument('--pairs', required=True)
    ap.add_argument('--n', type=int, default=10000)
    ap.add_argument('--seed', type=int, default=12345)
    ap.add_argument('--sets', default=','.join(TESTS))
    ap.add_argument('--name', default=None, help='output file name (default: the tag)')
    a = ap.parse_args()
    btag = a.backend.replace(':', '_').replace('/', '__')
    pdir = os.path.join(ROOT, 'results', 'predictions', btag, 'routes')
    rng = np.random.default_rng(a.seed)
    res = []
    for name in a.sets.split(','):
        rows = load_set(name)
        y = np.array([r['label'] for r in rows])
        src = [r['src_id'] for r in rows]
        assert len(set(src)) == len(src), 'resampling unit must be unique per row here'
        n = len(y)
        W = rng.multinomial(n, np.full(n, 1 / n), size=a.n).astype(np.float32)
        for pair in a.pairs.split(','):
            s1, s2 = pair.split(':')
            P1, P2 = load_preds(pdir, a.tag, s1, name), load_preds(pdir, a.tag, s2, name)
            if not P1 or not P2:
                continue
            ones = np.ones((1, n), np.float32)
            point = np.mean([macro_f1_counts(ones, y, p)[0] for p in P1]) - np.mean([macro_f1_counts(ones, y, p)[0] for p in P2])
            d = np.mean([macro_f1_counts(W, y, p) for p in P1], 0) - np.mean([macro_f1_counts(W, y, p) for p in P2], 0)
            p = min(1.0, 2 * min((np.sum(d <= 0) + 1) / (a.n + 1), (np.sum(d >= 0) + 1) / (a.n + 1)))
            res.append(dict(set=name, a=s1, b=s2, diff=float(point), lo=float(np.percentile(d, 2.5)), hi=float(np.percentile(d, 97.5)),
                            p=float(p), seeds_a=len(P1), seeds_b=len(P2)))
    for r, q in zip(res, holm([r['p'] for r in res])):
        r['p_holm'] = float(q)
        r['relevant'] = bool((r['lo'] > 0 or r['hi'] < 0) and abs(r['diff']) >= 1.0 and q < 0.05)
    out = os.path.join(ROOT, 'results', 'statistics', btag)
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, f'{a.name or a.tag}.json'), 'w'), indent=1)
    for r in res:
        print(f"{r['set']:12s} {r['a']:28s} - {r['b']:22s} {r['diff']:+6.2f} [{r['lo']:+6.2f},{r['hi']:+6.2f}] p_holm={r['p_holm']:.4f}")


if __name__ == '__main__':
    main()
