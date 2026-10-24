"""Where does selective normalization fail? Four mechanisms, measured separately.

For one backend (encoder, classifier regime) and normalizer mode, per test set:
 (M1) disagreement detection: AUC of pi-hat for D, source-trained and target-cross-fitted
      (the latter is label-free, so it is deployable);
 (M2) conditional advantage: AUC of rho-hat for W on target disagreements, source-trained,
      and a diagnostic ceiling cross-validated on the TARGET labels (5 folds by source id;
      not deployable); calibration gap = mean rho-hat - observed win rate on D=1;
 (M3) expected benefit: macro-F1 of the Bayes rule (lambda = 0) with source rho, with the
      target-CV rho ceiling, and of the oracle, against the best single view;
 (M4) irreducible noise: disagreement and oracle headroom between two bootstrap-resampled
      classifiers on the same input x (no normalization involved).
Seeds: the policy split of seed 0..4 for source models; noise control: 5 bootstrap pairs.
Labels of test sets are used for analysis only. Output: results/statistics/<btag>/mechanism_<mode>.json
"""
import argparse, json, os, sys
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, roc_auc_score

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.routing.run import Data, TESTS, fold_of
from src.routing.views import ROOT, load_set
from src.routing.policies import Factorized, outcomes, fit_proba
from src.models.encode import tag


def f1(y, p):
    return 100 * f1_score(y, p, average='macro')


def auc(t, s):
    return float(roc_auc_score(t, s)) if 0 < t.mean() < 1 else float('nan')


def kfold_ids(src, k=5):
    import hashlib
    return np.array([int(hashlib.md5(('cv' + s).encode()).hexdigest(), 16) % k for s in src])


def noise_control(model, C, sets, pairs=5):
    fd = os.path.join(ROOT, 'features', tag(model))
    Xtr = np.load(os.path.join(fd, 'clf_train_ar__orig.npy'))
    ytr = np.array([r['label'] for r in load_set('clf_train_ar')])
    rng = np.random.default_rng(0)
    out = {}
    for s in sets:
        X = np.load(os.path.join(fd, f'{s}__orig.npy'))
        y = np.array([r['label'] for r in load_set(s)])
        dis, head = [], []
        for _ in range(pairs):
            P = []
            for _ in range(2):
                i = rng.integers(0, len(ytr), len(ytr))
                P.append(LogisticRegression(C=C, max_iter=5000).fit(Xtr[i], ytr[i]).predict(X))
            dis.append(np.mean(P[0] != P[1]))
            head.append(f1(y, np.where(P[0] == y, P[0], P[1])) - np.mean([f1(y, q) for q in P]))
        out[s] = dict(noise_disagree=float(np.mean(dis)), noise_headroom=float(np.mean(head)), noise_headroom_sd=float(np.std(head)))
    return out


def wf1(w, y, p):
    """Weighted macro-F1 (weights = bootstrap counts)."""
    f = []
    for c in (0, 1):
        tp = np.sum(w * ((p == c) & (y == c)))
        fp = np.sum(w * ((p == c) & (y != c)))
        fn = np.sum(w * ((p != c) & (y == c)))
        f.append(2 * tp / max(2 * tp + fp + fn, 1e-12))
    return 50 * (f[0] + f[1])


def bootstrap_ci(runs, B, seed=0):
    """95% percentile intervals over test sentences. Each resample reweights the sentences of
    every seed with the same counts and averages the statistic over seeds (repeated measures).
    Estimators are not refitted: the intervals cover evaluation sampling only."""
    n = len(runs[0]['y'])
    rng = np.random.default_rng(seed)
    stats = {k: [] for k in ['auc_pi_tgt', 'auc_rho_src', 'auc_rho_tgt_ceiling', 'rho_calib_gap', 'win_rate',
                             'd_bayes_src', 'd_bayes_tgt_ceiling', 'd_oracle']}
    for _ in range(B):
        w = rng.multinomial(n, np.full(n, 1 / n)).astype(float)
        acc = {k: [] for k in stats}
        for r in runs:
            m = r['D'] == 1
            wm = w[m]
            acc['auc_pi_tgt'].append(roc_auc_score(r['D'], r['pi_t'], sample_weight=w))
            acc['auc_rho_src'].append(roc_auc_score(r['W'][m], r['rho_s'][m], sample_weight=wm))
            acc['auc_rho_tgt_ceiling'].append(roc_auc_score(r['W'][m], r['rho_t'][m], sample_weight=wm))
            acc['rho_calib_gap'].append(np.average(r['rho_s'][m] - r['W'][m], weights=wm))
            acc['win_rate'].append(np.average(r['W'][m], weights=wm))
            best = max(wf1(w, r['y'], r['y0']), wf1(w, r['y'], r['y1']))
            acc['d_bayes_src'].append(wf1(w, r['y'], np.where(r['rho_s'] > .5, r['y1'], r['y0'])) - best)
            acc['d_bayes_tgt_ceiling'].append(wf1(w, r['y'], np.where(r['rho_t'] > .5, r['y1'], r['y0'])) - best)
            acc['d_oracle'].append(wf1(w, r['y'], np.where(r['help'] == 1, r['y1'], r['y0'])) - best)
        for k in stats:
            stats[k].append(np.mean(acc[k]))
    return {k + '_ci': [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] for k, v in stats.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--backend', required=True)
    ap.add_argument('--mode', default='cons')
    ap.add_argument('--seeds', default='0,1,2,3,4')
    ap.add_argument('--noise', action='store_true', help='bootstrap noise control (orig-only f; skip for +syn)')
    ap.add_argument('--groups', default='conf,script,trel')
    ap.add_argument('--ci', type=int, default=0, help='bootstrap resamples for 95%% intervals (0 = none)')
    a = ap.parse_args()
    D = Data(a.backend, a.mode, tuple(a.groups.split(',')))
    pool = load_set('policy_pool')
    res = {s: [] for s in TESTS}
    keep = {s: [] for s in TESTS}
    for seed in map(int, a.seeds.split(',')):
        perm = np.random.default_rng(1000 + seed).permutation(len(pool))
        tr_idx = np.sort(perm[:int(0.8 * len(perm))])
        D.fit_proj(tr_idx)
        tr = D.load('policy_pool', tr_idx)
        o = outcomes(tr['p0'], tr['p1'], tr['y'])
        fac = Factorized('lr', seed).fit(tr['Z'], o['D'], ((tr['p1'] > .5).astype(int) == tr['y']).astype(int))
        for s in TESTS:
            d = D.load(s)
            od = outcomes(d['p0'], d['p1'], d['y'])
            W = ((d['p1'] > .5).astype(int) == d['y']).astype(int)
            m = od['D'] == 1
            pi_s, rho_s = fac.parts(d['Z'])
            # label-free target pi (two-fold cross-fitting)
            folds = fold_of(d['src'])
            pi_t = np.zeros(len(W))
            for f in (0, 1):
                pi_t[folds == f] = fit_proba('lr', d['Z'][folds != f], od['D'][folds != f])(d['Z'][folds == f])
            # diagnostic ceiling: rho cross-validated on target labels (5 folds)
            cv = kfold_ids(d['src'])
            rho_t = np.zeros(len(W))
            for f in range(5):
                trm = (cv != f) & m
                rho_t[cv == f] = fit_proba('lr', d['Z'][trm], W[trm])(d['Z'][cv == f])
            y0, y1 = (d['p0'] > .5).astype(int), (d['p1'] > .5).astype(int)
            best = max(f1(d['y'], y0), f1(d['y'], y1))
            keep[s].append(dict(y=d['y'], D=od['D'], W=W, pi_s=pi_s, pi_t=pi_t, rho_s=rho_s, rho_t=rho_t, y0=y0, y1=y1, help=od['help']))
            res[s].append(dict(
                disagree=float(m.mean()), win_rate=float(W[m].mean()),
                auc_pi_src=auc(od['D'], pi_s), auc_pi_tgt=auc(od['D'], pi_t),
                auc_rho_src=auc(W[m], rho_s[m]), auc_rho_tgt_ceiling=auc(W[m], rho_t[m]),
                rho_calib_gap=float(rho_s[m].mean() - W[m].mean()),
                f1_b0=f1(d['y'], y0), f1_b1=f1(d['y'], y1), f1_best_view=best,
                f1_bayes_src=f1(d['y'], np.where(rho_s > .5, y1, y0)),
                f1_bayes_tgt_ceiling=f1(d['y'], np.where(rho_t > .5, y1, y0)),
                f1_oracle=f1(d['y'], np.where(od['help'] == 1, y1, y0))))
    out = {}
    for s, rows in res.items():
        out[s] = {k: float(np.nanmean([r[k] for r in rows])) for k in rows[0]}
        out[s].update({k + '_sd': float(np.nanstd([r[k] for r in rows])) for k in rows[0]})
    if a.noise:
        info = json.load(open(os.path.join(ROOT, 'results', 'predictions', D.btag, 'classifier.json')))
        nc = noise_control(a.backend[4:].split('+')[0], info['C'], TESTS)
        for s in TESTS:
            out[s].update(nc[s])
            out[s]['excess_headroom'] = out[s]['f1_oracle'] - out[s]['f1_best_view'] - nc[s]['noise_headroom']
    if a.ci:
        for s in TESTS:
            out[s].update(bootstrap_ci(keep[s], a.ci, seed=0))
    d = os.path.join(ROOT, 'results', 'statistics', D.btag)
    os.makedirs(d, exist_ok=True)
    suffix = '' if a.groups == 'conf,script,trel' else '_' + a.groups.replace(',', '-')
    json.dump(out, open(os.path.join(d, f'mechanism_{a.mode}{suffix}.json'), 'w'), indent=1)
    for s in TESTS:
        r = out[s]
        print(s, ' '.join(f"{k}={r[k]:.3f}" for k in ['disagree', 'win_rate', 'auc_pi_src', 'auc_pi_tgt', 'auc_rho_src', 'auc_rho_tgt_ceiling', 'rho_calib_gap',
                                                      'f1_best_view', 'f1_bayes_src', 'f1_bayes_tgt_ceiling', 'f1_oracle'] + (['noise_headroom', 'excess_headroom'] if a.noise else [])))


if __name__ == '__main__':
    main()
