"""Seed-averaged macro-F1 (lambda = 0) of the main systems for every backend and run tag."""
import argparse, collections, glob, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.routing.views import ROOT
from src.routing.run import TESTS

SY = ['B0_original', 'B1_always', 'B3_conf', 'B4_direct_gain', 'B4b_abs_loss', 'B5_selectnorm_src', 'B5_selectnorm_adapt',
      'B5_selectnorm_adapt_theory', 'A_pi_only', 'A_rho_only', 'R_two_view_ensemble', 'B6_oracle']


def load(path):
    agg, sel = collections.defaultdict(list), collections.defaultdict(list)
    for l in open(path):
        r = json.loads(l)
        if r.get('lam') in (None, 0.0) and 'macro_f1' in r:
            agg[(r['system'], r['set'])].append(r['macro_f1'])
            sel[(r['system'], r['set'])].append(r.get('sel_rate', np.nan))
    return {k: float(np.mean(v)) for k, v in agg.items()}, {k: float(np.mean(v)) for k, v in sel.items()}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--tag', default='main')
    a = ap.parse_args()
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, 'results', 'metrics', 'enc_*', f'runs_{a.tag}.jsonl'))):
        b = f.split('/')[-2]
        f1, sel = load(f)
        out[b] = {s: {t: dict(f1=f1.get((s, t)), sel=sel.get((s, t))) for t in TESTS} for s in SY}
        print('==', b)
        for s in SY:
            print(s.ljust(28) + ''.join(f"{f1.get((s, t), np.nan):7.1f}" for t in TESTS) + '   sel ' + ' '.join(f"{sel.get((s, t), np.nan):3.0f}" for t in TESTS))
    json.dump(out, open(os.path.join(ROOT, 'results', 'metrics', f'summary_{a.tag}.json'), 'w'), indent=1)
