"""Audit of label separation in the few-label setting (src/routing/adapt.py), second revision.

The draws of adapt.py depend only on the rng stream default_rng(seed*1000 + k*10 + draw), the
fold assignment and the label-free disagreement indicator D (from the cached probabilities of f),
and the rng is consumed in a fixed order (per fold: targeted draw, then random draw). This script
REPLAYS every targeted and random draw of every few-label run (8 backends x 4 sets x 5 seeds x
5 budgets x 5 draws x 2 folds), saves the sampled indices and source identifiers, and checks for
each draw that
  (1) every sampled label (targeted or random) comes from the fold that is NOT being scored;
  (2) no source identifier of a sampled sentence occurs among the scored sentences;
  (3) no sampled sentence has the same normalized text as a scored sentence (near-copy check);
  (4) every targeted sentence is a disagreement (D = 1), and the random draw is uniform over
      the other fold (it is drawn without looking at D or labels);
and counts every violation instead of assuming none.
That the replay is the draw adapt.py actually used is checked separately: adapt.py, run with
--log-samples, writes the indices it uses (results/audit/fewlabel_samples_logged_<backend>.jsonl);
with --logged the replay is compared with that log entry by entry.
Outputs: results/audit/fewlabel_samples/<backend>.jsonl.gz, results/statistics/fewlabel_audit.json,
results/statistics/fewlabel_vs_zeroshot.csv (zero-shot reference with the same lambda = 0 threshold).
"""
import argparse, gzip, json, os, re, sys
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.routing.run import TESTS, fold_of
from src.routing.views import load_set, ROOT
from src.routing.adapt import KS

SEEDS, DRAWS = range(5), range(5)


def norm_text(t):
    return re.sub(r'\s+', ' ', t.lower()).strip()


def replay(backend):
    P = np.load(os.path.join(ROOT, 'results', 'predictions', backend, 'probs.npz'))
    out, viol, n_draws = [], dict(other_fold=0, src_overlap=0, text_overlap=0, targeted_not_disagreement=0, budget_short=0), 0
    for name in TESTS:
        rows = load_set(name)
        src = np.array([r['src_id'] for r in rows])
        txt = np.array([norm_text(r['text']) for r in rows])
        folds = fold_of(src)
        D = ((P[f'{name}__orig'] > .5) != (P[f'{name}__cons'] > .5)).astype(int)
        for seed in SEEDS:
            for k in KS:
                for r in DRAWS:
                    rng = np.random.default_rng(seed * 1000 + k * 10 + r)
                    for f in (0, 1):
                        ev, lab = folds == f, np.where(folds != f)[0]
                        dis = lab[D[lab] == 1]
                        tgt = rng.choice(dis, min(k, len(dis)), replace=False)
                        rnd = rng.choice(lab, min(k, len(lab)), replace=False)
                        n_draws += 1
                        used = np.concatenate([tgt, rnd])
                        viol['other_fold'] += int(ev[used].sum())
                        viol['src_overlap'] += int(len(set(src[used]) & set(src[ev])))
                        viol['text_overlap'] += int(len(set(txt[used]) & set(txt[ev])))
                        viol['targeted_not_disagreement'] += int((D[tgt] != 1).sum())
                        viol['budget_short'] += int(len(tgt) < k)
                        out.append(dict(set=name, seed=seed, k=k, draw=r, fold=f, targeted=tgt.tolist(), random=rnd.tolist(),
                                        targeted_src=src[tgt].tolist(), random_src=src[rnd].tolist()))
    return out, viol, n_draws


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--logged', nargs='*', default=[], help='backend=path pairs of adapt.py --log-samples files')
    a = ap.parse_args()
    backends = sorted(b for b in os.listdir(os.path.join(ROOT, 'results', 'metrics'))
                      if b.startswith('enc_') and os.path.exists(os.path.join(ROOT, 'results', 'metrics', b, 'runs_adapt.jsonl')))
    od = os.path.join(ROOT, 'results', 'audit', 'fewlabel_samples')
    os.makedirs(od, exist_ok=True)
    report = dict(backends={}, logged_comparison={})
    reps = {}
    for b in backends:
        draws, viol, n = replay(b)
        reps[b] = draws
        with gzip.open(os.path.join(od, f'{b}.jsonl.gz'), 'wt') as fh:
            for d in draws:
                fh.write(json.dumps(d) + '\n')
        report['backends'][b] = dict(draws=n, labels_sampled=int(sum(len(d['targeted']) + len(d['random']) for d in draws)), violations=viol)
        print(b, n, viol, flush=True)
    for pair in a.logged:
        b, path = pair.split('=')
        logged = [json.loads(l) for l in open(path)]
        key = lambda d: (d['set'], d['seed'], d['k'], d['draw'], d['fold'])
        rp = {key(d): d for d in reps[b]}
        mism = sum(int(rp[key(d)]['targeted'] != d['targeted'] or rp[key(d)]['random'] != d['random']) for d in logged)
        report['logged_comparison'][b] = dict(entries=len(logged), mismatches=mism, missing=len(rp) - len({key(d) for d in logged}))
    report['total_draws'] = sum(v['draws'] for v in report['backends'].values())
    report['total_violations'] = {k: sum(v['violations'][k] for v in report['backends'].values())
                                  for k in next(iter(report['backends'].values()))['violations']}
    rows = []
    for b in backends:
        ad = pd.read_json(os.path.join(ROOT, 'results', 'metrics', b, 'runs_adapt.jsonl'), lines=True)
        m = pd.read_json(os.path.join(ROOT, 'results', 'metrics', b, 'runs_main.jsonl'), lines=True)
        base = m[(m.system == 'B5_selectnorm_adapt_theory') & (m.lam == 0)].groupby('set').macro_f1.mean()
        for (sysn, s, k), v in ad.groupby(['system', 'set', 'k']).macro_f1.mean().items():
            rows.append(dict(backend=b, system=sysn, set=s, k=int(k), f1=v, zero_shot=base[s], delta=v - base[s]))
    t = pd.DataFrame(rows)
    sn = t[t.system == 'SN_targeted']
    report['sn_targeted_minus_zero_shot'] = dict(min=float(sn.delta.min()), max=float(sn.delta.max()), mean=float(sn.delta.mean()))
    t.to_csv(os.path.join(ROOT, 'results', 'statistics', 'fewlabel_vs_zeroshot.csv'), index=False)
    json.dump(report, open(os.path.join(ROOT, 'results', 'statistics', 'fewlabel_audit.json'), 'w'), indent=1)
    print(json.dumps({k: v for k, v in report.items() if k != 'backends'}, indent=1))


if __name__ == '__main__':
    main()
