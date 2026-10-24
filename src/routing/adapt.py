"""Few-label target adaptation of the router (RQ5, second setting).

For each target set, two-fold cross-fitting by source id: the fold being scored never
contributes labels or unlabeled text to its own router. From the other fold a budget of k
labels is revealed, either at random or only among disagreements (D = 1, label-free to find).
Systems (lambda = 0, theory threshold 0 unless stated):
  SN_targeted : SelectNorm, pi re-estimated on unlabeled target text, rho shifted with k
                labelled disagreements;
  SN_random   : same, k random labels (only the disagreements among them inform rho);
  DG_random   : direct gain estimator, both heads shifted with k random labels;
  CONF_random : confidence threshold re-tuned on k random labels;
  SET_random  : dataset-level choice between B0 and B1 by accuracy on k random labels.
"""
import argparse, json, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.routing.run import Data, TESTS, fold_of, metrics
from src.routing.views import load_set, ROOT
from src.routing import features as F
from src.routing.policies import Factorized, DirectGain, FactorizedAdapted, outcomes, tune_threshold

KS = [8, 16, 32, 64, 128]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--backend', required=True)
    ap.add_argument('--mode', default='cons')
    ap.add_argument('--groups', default='conf,script,trel')
    ap.add_argument('--est', default='lr')
    ap.add_argument('--seeds', default='0,1,2,3,4')
    ap.add_argument('--draws', type=int, default=5)
    ap.add_argument('--tag', default='adapt')
    ap.add_argument('--log-samples', default=None, help='optional .jsonl path: write every sampled label index (audit; does not change results)')
    a = ap.parse_args()
    D = Data(a.backend, a.mode, tuple(a.groups.split(',')))
    fout = open(os.path.join(ROOT, 'results', 'metrics', D.btag, f'runs_{a.tag}.jsonl'), 'w')
    pool_src = np.array([r['src_id'] for r in load_set('policy_pool')])
    flog = open(a.log_samples, 'w') if a.log_samples else None
    for seed in map(int, a.seeds.split(',')):
        perm = np.random.default_rng(1000 + seed).permutation(len(pool_src))
        tr_idx = np.sort(perm[:int(0.8 * len(perm))])
        D.fit_proj(tr_idx)
        tr = D.load('policy_pool', tr_idx)
        otr = outcomes(tr['p0'], tr['p1'], tr['y'])
        win_tr = ((tr['p1'] > .5).astype(int) == tr['y']).astype(int)
        fac = Factorized(a.est, seed).fit(tr['Z'], otr['D'], win_tr)
        dg = DirectGain(a.est, seed).fit(tr['Z'], otr['help'], otr['harm'])
        for name in TESTS:
            d = D.load(name)
            n = len(d['y'])
            folds = fold_of(d['src'])
            od = outcomes(d['p0'], d['p1'], d['y'])
            win = ((d['p1'] > .5).astype(int) == d['y']).astype(int)
            negconf = -F.conf(d['p0'])['conf']
            for k in KS:
                for r in range(a.draws):
                    rng = np.random.default_rng(seed * 1000 + k * 10 + r)
                    G = {s: np.zeros(n, bool) for s in ['SN_targeted', 'SN_random', 'DG_random', 'CONF_random', 'SET_random']}
                    for f in (0, 1):
                        ev, lab = folds == f, np.where(folds != f)[0]
                        dis = lab[od['D'][lab] == 1]
                        tgt = rng.choice(dis, min(k, len(dis)), replace=False)
                        rnd = rng.choice(lab, min(k, len(lab)), replace=False)
                        rnd_dis = rnd[od['D'][rnd] == 1]
                        if flog:
                            flog.write(json.dumps(dict(seed=seed, set=name, k=k, draw=r, fold=f, targeted=tgt.tolist(), random=rnd.tolist())) + '\n')
                        Zu, Du = d['Z'][lab], od['D'][lab]
                        sn_t = FactorizedAdapted(fac, Zu, Du, d['Z'][tgt], win[tgt], a.est, seed)
                        sn_r = FactorizedAdapted(fac, Zu, Du, d['Z'][rnd_dis], win[rnd_dis], a.est, seed)
                        G['SN_targeted'][ev] = sn_t.score(d['Z'][ev]) > 0
                        G['SN_random'][ev] = sn_r.score(d['Z'][ev]) > 0
                        G['DG_random'][ev] = dg.recalibrated(d['Z'][rnd], od['help'][rnd], od['harm'][rnd])(d['Z'][ev]) > 0
                        th = tune_threshold(negconf[rnd], d['p0'][rnd], d['p1'][rnd], d['y'][rnd])
                        G['CONF_random'][ev] = negconf[ev] > th
                        G['SET_random'][ev] = od['e1'][rnd].mean() < od['e0'][rnd].mean()
                    for s, g in G.items():
                        m, _ = metrics(d, g)
                        fout.write(json.dumps(dict(seed=seed, set=name, system=s, k=k, draw=r, mode=a.mode, est=a.est, **m)) + '\n')
        print('seed', seed, 'done', flush=True)
    fout.close()
    if flog:
        flog.close()


if __name__ == '__main__':
    main()
