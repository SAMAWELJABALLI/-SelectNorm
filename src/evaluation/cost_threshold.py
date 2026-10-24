"""Exploratory analysis (second revision): mean vs input-dependent avoidable cost in the Bayes threshold.

The Bayes rule is g* = 1[B(z) > lambda * E[c1 | z]]. The paper's SelectNorm-adapt (Bayes threshold)
replaces E[c1 | z] by the mean cost of the second pass on policy-train, c_bar. Under the token-length
cost model, c1 of an input is a + b * tokens(T(x)), and T(x) is known at the decision point, so
an input-dependent threshold lambda * c1(x) is also deployable. This script compares the two
thresholds for every encoder, test set, seed and lambda > 0, with the same scores
(SelectNorm-adapt, pi cross-fitted on unlabeled target text, rho from the source split).
Check: the mean-cost variant must reproduce the archived B5_selectnorm_adapt_theory rows.
Output: results/statistics/cost_threshold.csv and .json
"""
import json, os, sys
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.routing.run import Data, TESTS, LAMBDAS, fold_of, cost
from src.routing.views import load_set, ROOT
from src.routing.policies import Factorized, outcomes

BACKENDS = ['enc:intfloat/multilingual-e5-base', 'enc:FacebookAI/xlm-roberta-base', 'enc:sentence-transformers/LaBSE', 'enc:UBC-NLP/MARBERTv2']


def main():
    pool_src = np.array([r['src_id'] for r in load_set('policy_pool')])
    rows = []
    for be in BACKENDS:
        D = Data(be, 'cons', ('conf', 'script', 'trel'))
        arch = pd.read_json(os.path.join(ROOT, 'results', 'metrics', D.btag, 'runs_main.jsonl'), lines=True)
        arch = arch[arch.system == 'B5_selectnorm_adapt_theory'].set_index(['seed', 'set', 'lam'])
        for seed in range(5):
            perm = np.random.default_rng(1000 + seed).permutation(len(pool_src))
            tr = D.load('policy_pool', np.sort(perm[:int(0.8 * len(perm))]))
            otr = outcomes(tr['p0'], tr['p1'], tr['y'])
            win_tr = ((tr['p1'] > .5).astype(int) == tr['y']).astype(int)
            m0 = float(np.mean(tr['c0']))
            cbar = float(np.mean(tr['c1']) / m0)
            for s in TESTS:
                d = D.load(s)
                folds = fold_of(d['src'])
                od = outcomes(d['p0'], d['p1'], d['y'])
                sc = np.zeros(len(folds))
                for f in (0, 1):
                    m = folds == f
                    sc[m] = Factorized('lr', seed).fit(tr['Z'], otr['D'], win_tr, d['Z'][~m], od['D'][~m]).score(d['Z'][m])
                c1_rel = d['c1'] / m0
                for lam in LAMBDAS[1:]:
                    for kind, thr in (('mean', lam * cbar), ('input', lam * c1_rel)):
                        g = sc > thr
                        yhat = np.where(g, d['p1'] > .5, d['p0'] > .5).astype(int)
                        rows.append(dict(backend=D.btag, seed=seed, set=s, lam=lam, threshold=kind,
                                         macro_f1=100 * f1_score(d['y'], yhat, average='macro'), sel=100 * g.mean(),
                                         rel_cost=cost(d, g, 'router'),
                                         archived_f1=float(arch.loc[(seed, s, lam), 'macro_f1']) if kind == 'mean' else np.nan))
        print(be, 'done', flush=True)
    t = pd.DataFrame(rows)
    t.to_csv(os.path.join(ROOT, 'results', 'statistics', 'cost_threshold.csv'), index=False)
    chk = t[t.threshold == 'mean']
    a = t.groupby(['backend', 'set', 'lam', 'threshold'])[['macro_f1', 'rel_cost', 'sel']].mean().unstack('threshold')
    diff_f1 = a[('macro_f1', 'input')] - a[('macro_f1', 'mean')]
    diff_c = a[('rel_cost', 'input')] - a[('rel_cost', 'mean')]
    out = dict(check_max_abs_diff_vs_archived=float(np.max(np.abs(chk.macro_f1 - chk.archived_f1))),
               delta_f1_input_minus_mean=dict(min=float(diff_f1.min()), max=float(diff_f1.max()), mean=float(diff_f1.mean())),
               delta_cost_input_minus_mean=dict(min=float(diff_c.min()), max=float(diff_c.max()), mean=float(diff_c.mean())),
               per_lambda={str(l): dict(d_f1=float(diff_f1.xs(l, level='lam').mean()), d_cost=float(diff_c.xs(l, level='lam').mean())) for l in LAMBDAS[1:]})
    json.dump(out, open(os.path.join(ROOT, 'results', 'statistics', 'cost_threshold.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
