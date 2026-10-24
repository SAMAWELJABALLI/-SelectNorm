"""SelectNorm experiments: baselines, policies, ablations and operating-point sweeps.

python -m src.routing.run --backend enc:intfloat/multilingual-e5-base --seeds 0,1,2,3,4

Protocol (fixed before the encoder runs; docs/PROTOCOL.md):
  * f is frozen (src.models.classifier); the routing policies see only decision-point
    features (src.routing.features).
  * policy_pool (human Latin-script TSAC, never seen by f) is split per seed into
    policy-train (80%) and policy-dev (20%) by source sentence.
  * estimators are fitted on policy-train; thresholds are tuned on policy-dev;
    test labels are read only to score the final predictions.
  * SelectNorm-adapt re-estimates pi on unlabeled text of the target set with two-fold
    cross-fitting by source id: the fold that is scored never contributes to its own pi.
Outputs: results/metrics/<backend>/runs.jsonl (one row per seed x set x system x lambda)
and results/predictions/<backend>/routes/<system>__<set>__s<seed>.npz (g, yhat).
"""
import argparse, hashlib, json, os, sys, time
import numpy as np
from sklearn.decomposition import PCA
from sklearn.metrics import f1_score

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.routing.views import load_set, load_view, ROOT
from src.routing import features as F
from src.routing.policies import Factorized, DirectGain, AbsoluteLoss, outcomes, tune_threshold, fit_proba

TESTS = ['S3_tsac_lat', 'S4_tunizi', 'S5_narabizi', 'S6_myc_lat']
LAMBDAS = [0.0, 0.01, 0.02, 0.05, 0.1, 0.2]


def fold_of(src_ids):
    return np.array([int(hashlib.md5(s.encode()).hexdigest(), 16) % 2 for s in src_ids])


class Data:
    def __init__(self, backend, mode, groups, emb_dim=16):
        self.btag = backend.replace(':', '_').replace('/', '__')  # a '+syn' suffix selects the script-augmented f
        P = np.load(os.path.join(ROOT, 'results', 'predictions', self.btag, 'probs.npz'))
        self.P, self.mode, self.groups = P, mode, groups
        self.backend = backend
        self.emb_dim = emb_dim
        self.proj = None

    def emb(self, name):
        if not self.backend.startswith('enc:'):
            return None
        from src.models.encode import tag
        return np.load(os.path.join(ROOT, 'features', tag(self.backend[4:].split('+')[0]), f'{name}__orig.npy'))

    def fit_proj(self, idx):
        if 'emb' in self.groups and self.backend.startswith('enc:'):
            pca = PCA(self.emb_dim, random_state=0).fit(self.emb('policy_pool')[idx])
            self.proj = pca.transform

    def load(self, name, idx=None):
        rows = load_set(name)
        view = load_view(name, self.mode)
        p0 = self.P[f'{name}__orig']
        p1 = self.P[f'{name}__{self.mode}']
        c0 = self.P[f'{name}__orig__sec']
        # costs (seconds per sentence): c0 = f(x); ct = normalizer T(x); c1 = f(T(x)) only
        c1 = self.P[f'{name}__{self.mode}__sec']
        ct = np.array([v['t_norm'] for v in view])
        Z, names = F.build([r['text'] for r in rows], view, p0, self.groups, self.emb(name), self.proj)
        d = dict(y=np.array([r['label'] for r in rows]), src=np.array([r['src_id'] for r in rows]),
                 p0=p0, p1=p1, c0=c0, c1=c1, ct=ct, Z=Z)
        if idx is not None:
            d = {k: v[idx] for k, v in d.items()}
        d['names'] = names
        return d


def cost(d, g, kind='router'):
    """Measured inference cost relative to one pass of f on x, counting only what a system runs.
    router  : f(x) and T(x) always run (features need p0 and m; sunk at decision time),
              f(T(x)) only when g = 1 (the avoidable cost);
    conf    : f(x) always; T(x) and f(T(x)) only when g = 1 (decides before normalizing);
    original: f(x);  always: T(x) + f(T(x));  ensemble: f(x) + T(x) + f(T(x));
    blind   : input-independent random routing, one pass on the chosen view."""
    c0, ct, c1 = d['c0'], d['ct'], d['c1']
    tot = {'router': c0 + ct + g * c1, 'conf': c0 + g * (ct + c1), 'original': c0, 'always': ct + c1,
           'ensemble': c0 + ct + c1, 'blind': np.where(g, ct + c1, c0)}[kind]
    return float(np.mean(tot) / np.mean(c0))


COST_KIND = {'B0_original': 'original', 'B1_always': 'always', 'B3_conf': 'conf', 'R_two_view_ensemble': 'ensemble'}


def cost_kind(system):
    return 'blind' if system.startswith('B2_random') else COST_KIND.get(system, 'router')


def metrics(d, g, kind='router'):
    o = outcomes(d['p0'], d['p1'], d['y'])
    yhat = np.where(g, d['p1'] > .5, d['p0'] > .5).astype(int)
    n, r = len(g), max(g.sum(), 1)
    return dict(macro_f1=100 * f1_score(d['y'], yhat, average='macro'), acc=100 * np.mean(yhat == d['y']),
                sel_rate=100 * g.mean(),
                harm_rate=100 * np.sum(g & (o['harm'] == 1)) / n,
                harm_among_routed=100 * np.sum(g & (o['harm'] == 1)) / r,
                help_captured=100 * np.sum(g & (o['help'] == 1)) / max(o['help'].sum(), 1),
                rel_cost=cost(d, g, kind),
                n=int(n)), yhat


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--backend', required=True)
    ap.add_argument('--mode', default='cons')
    ap.add_argument('--groups', default='conf,script,trel')
    ap.add_argument('--est', default='lr')
    ap.add_argument('--seeds', default='0,1,2,3,4')
    ap.add_argument('--tag', default='main')
    ap.add_argument('--systems', default='all')
    a = ap.parse_args()
    groups = tuple(a.groups.split(','))
    D = Data(a.backend, a.mode, groups)
    outdir = os.path.join(ROOT, 'results', 'metrics', D.btag)
    preddir = os.path.join(ROOT, 'results', 'predictions', D.btag, 'routes')
    os.makedirs(outdir, exist_ok=True)
    os.makedirs(preddir, exist_ok=True)
    fout = open(os.path.join(outdir, f'runs_{a.tag}.jsonl'), 'w')
    pool_src = np.array([r['src_id'] for r in load_set('policy_pool')])
    for seed in map(int, a.seeds.split(',')):
        rng = np.random.default_rng(1000 + seed)
        perm = rng.permutation(len(pool_src))
        cut = int(0.8 * len(perm))
        tr_idx, dv_idx = np.sort(perm[:cut]), np.sort(perm[cut:])
        D.fit_proj(tr_idx)
        tr, dv = D.load('policy_pool', tr_idx), D.load('policy_pool', dv_idx)
        otr, odv = outcomes(tr['p0'], tr['p1'], tr['y']), outcomes(dv['p0'], dv['p1'], dv['y'])
        win_tr = ((tr['p1'] > .5).astype(int) == tr['y']).astype(int)
        # avoidable cost of routing to T: the second pass f(T(x)); f(x) and T(x) are sunk
        rel_cost = float(np.mean(tr['c1']) / np.mean(tr['c0']))
        t0 = time.perf_counter()
        fac = Factorized(a.est, seed).fit(tr['Z'], otr['D'], win_tr)
        dg = DirectGain(a.est, seed).fit(tr['Z'], otr['help'], otr['harm'])
        al = AbsoluteLoss(a.est, seed).fit(tr['Z'], otr['e0'], otr['e1'])
        fit_s = time.perf_counter() - t0
        # pi-only: label-free ranking of likely disagreements (direction unknown)
        conf_idx = D.load('policy_pool', tr_idx)['names'].index('conf') if 'conf' in groups else None

        def conf_score(d):
            return -F.conf(d['p0'])['conf']

        dev_scores = {
            'B3_conf': conf_score(dv), 'B4_direct_gain': dg.score(dv['Z']), 'B4b_abs_loss': al.score(dv['Z']),
            'B5_selectnorm_src': fac.score(dv['Z']), 'A_pi_only': fac.parts(dv['Z'])[0],
            'A_rho_only': 2 * fac.parts(dv['Z'])[1] - 1}
        thr = {}
        for lam in LAMBDAS:
            for k, s in dev_scores.items():
                thr[(k, lam)] = tune_threshold(s, dv['p0'], dv['p1'], dv['y'], lam, rel_cost)
            # theory threshold of the Bayes rule: route iff B(z) > lam * relative cost
            thr[('B5_selectnorm_src_theory', lam)] = lam * rel_cost
            thr[('B5_selectnorm_adapt_theory', lam)] = lam * rel_cost
            thr[('B5_selectnorm_adapt', lam)] = thr[('B5_selectnorm_src', lam)]
        for name in TESTS:
            d = D.load(name)
            n = len(d['y'])
            folds = fold_of(d['src'])
            od = outcomes(d['p0'], d['p1'], d['y'])
            # SelectNorm-adapt: pi re-estimated on the other fold's unlabeled text (cross-fitting)
            s_adapt = np.zeros(n)
            pi_adapt = np.zeros(n)
            for f in (0, 1):
                m = folds == f
                fa = Factorized(a.est, seed).fit(tr['Z'], otr['D'], win_tr, d['Z'][~m], od['D'][~m])
                s_adapt[m] = fa.score(d['Z'][m])
                pi_adapt[m] = fa.parts(d['Z'][m])[0]
            scores = {
                'B3_conf': conf_score(d), 'B4_direct_gain': dg.score(d['Z']), 'B4b_abs_loss': al.score(d['Z']),
                'B5_selectnorm_src': fac.score(d['Z']), 'B5_selectnorm_src_theory': fac.score(d['Z']),
                'B5_selectnorm_adapt': s_adapt, 'B5_selectnorm_adapt_theory': s_adapt,
                'A_pi_only': fac.parts(d['Z'])[0], 'A_rho_only': 2 * fac.parts(d['Z'])[1] - 1}
            t_route = time.perf_counter()
            fac.score(d['Z'])
            route_s = (time.perf_counter() - t_route) / n
            rows = []
            for lam in LAMBDAS:
                for k, s in scores.items():
                    g = s > thr[(k, lam)]
                    rows.append((k, lam, g))
            for k, g in [('B0_original', np.zeros(n, bool)), ('B1_always', np.ones(n, bool)),
                         ('B6_oracle', od['help'] == 1)]:
                rows.append((k, None, g))
            # B2: random routing at the selection rate of SelectNorm-adapt (lambda = 0), 20 draws
            rate = np.mean(scores['B5_selectnorm_adapt'] > thr[('B5_selectnorm_adapt', 0.0)])
            for r in range(20):
                rows.append((f'B2_random#{r}', None, np.random.default_rng(seed * 100 + r).random(n) < rate))
            ens = dict(d)
            for k, lam, g in rows:
                m, yhat = metrics(d, g, cost_kind(k))
                rec = dict(seed=seed, set=name, system=k, lam=lam, mode=a.mode, groups=a.groups, est=a.est, **m)
                if k.startswith('B5'):
                    rec['route_s_per_sent'] = route_s
                fout.write(json.dumps(rec) + '\n')
                if lam in (None, 0.0) and not k.startswith('B2_random#') or k == 'B2_random#0':
                    np.savez_compressed(os.path.join(preddir, f'{a.tag}__{k}__{name}__s{seed}.npz'), g=g, yhat=yhat)
            # accuracy-oriented reference: average both views' probabilities (always two passes)
            pe = (d['p0'] + d['p1']) / 2
            yhat = (pe > .5).astype(int)
            fout.write(json.dumps(dict(seed=seed, set=name, system='R_two_view_ensemble', lam=None, mode=a.mode, groups=a.groups, est=a.est,
                                       macro_f1=100 * f1_score(d['y'], yhat, average='macro'), acc=100 * np.mean(yhat == d['y']),
                                       sel_rate=100.0, rel_cost=cost(d, np.ones(n, bool), 'ensemble'), n=n)) + '\n')
            np.savez_compressed(os.path.join(preddir, f'{a.tag}__R_two_view_ensemble__{name}__s{seed}.npz'), g=np.ones(n, bool), yhat=yhat)
            # diagnostics for the factorization (test labels used for analysis only)
            win = ((d['p1'] > .5).astype(int) == d['y']).astype(int)
            pi_s, rho_s = fac.parts(d['Z'])
            fout.write(json.dumps(dict(seed=seed, set=name, system='DIAG', mode=a.mode, groups=a.groups, est=a.est,
                                       disagree_rate=float(od['D'].mean()), pi_src_mean=float(pi_s.mean()), pi_adapt_mean=float(pi_adapt.mean()),
                                       win_rate_given_D=float(win[od['D'] == 1].mean()) if od['D'].sum() else None,
                                       rho_src_mean_on_D=float(rho_s[od['D'] == 1].mean()) if od['D'].sum() else None,
                                       help=int(od['help'].sum()), harm=int(od['harm'].sum()), both_wrong=int(((od['e0'] == 1) & (od['e1'] == 1)).sum()),
                                       rel_cost_branch=float(np.mean(d['c1']) / np.mean(d['c0'])), policy_fit_s=fit_s)) + '\n')
        print('seed', seed, 'done', flush=True)
    fout.close()


if __name__ == '__main__':
    main()
