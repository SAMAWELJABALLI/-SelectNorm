"""End-to-end execution of the deployed pipeline at batch size 1: measured latency and a check
that live routing decisions reproduce the archived ones (second revision).

The per-sentence costs used in the routing runs are ESTIMATES (a + b * tokens per encoder,
src/evaluation/latency.py, plus the measured normalizer time). This script runs the deployed
systems on raw test text, with nothing taken from cached predictions or cached routes:
  f      : frozen encoder (pinned revision) -> masked mean pooling -> L2 normalization ->
           trained logistic head with its temperature (refitted deterministically from the
           cached training features with the saved C; checked against probs.npz).
  B0     : f(x)
  B1     : T(x) -> f(T(x))
  SN     : f(x) and T(x); features z from the live p0, x and the live metadata of T;
           SelectNorm-adapt score with the fold model of the sentence; g = score > threshold
           (lambda = 0, threshold tuned on policy-dev as in src/routing/run.py);
           f(T(x)) iff g = 1.
  R      : f(x), T(x), f(T(x)); average of the two probabilities.
The router is refitted for each seed exactly as in src/routing/run.py; the offline part of the
adaptation (pi re-estimated on the other fold's unlabeled target text) uses the cached
decision-point features of that unlabeled text, as a deployment would.

Checks, written to results/metrics/measured_cost.json:
  (a) replay: routing decisions recomputed from the cached inputs vs the archived decisions;
  (b) live: p0, p1 from raw text vs the cached probabilities, and live routing decisions and
      final predictions vs the archived ones, for all five seeds and every test sentence;
  (c) timing: all four systems timed back to back on a random sample of each set, in rotating
      order, after a warm-up on 300 policy-pool sentences in both views; SN timed live
      on every test sentence as well.
Per-sentence live outputs: results/metrics/measured_cost_live/<backend>/<set>.csv.gz
"""
import argparse, json, os, platform, sys, time
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.routing.views import ROOT, load_set, normalizer
from src.routing.run import Data, TESTS, fold_of
from src.routing import features as F
from src.routing.policies import Factorized, outcomes, tune_threshold
from src.normalization.arabizi import normalize_arabic
from src.models.encode import PREFIX, tag
from src.models.classifier import fit_temperature, labels

MODELS = ['intfloat/multilingual-e5-base', 'FacebookAI/xlm-roberta-base', 'sentence-transformers/LaBSE', 'UBC-NLP/MARBERTv2']
SEEDS = [0, 1, 2, 3, 4]
GROUPS = ('conf', 'script', 'trel')


def head(model):
    """The trained classifier head of src/models/classifier.py (same data, C and solver)."""
    btag = 'enc_' + tag(model)
    info = json.load(open(os.path.join(ROOT, 'results', 'predictions', btag, 'classifier.json')))
    fd = os.path.join(ROOT, 'features', tag(model))
    clf = LogisticRegression(C=info['C'], max_iter=5000).fit(np.load(os.path.join(fd, 'clf_train_ar__orig.npy')), labels('clf_train_ar'))
    T = fit_temperature(clf.decision_function(np.load(os.path.join(fd, 'clf_dev_ar__orig.npy'))), labels('clf_dev_ar'))
    P = np.load(os.path.join(ROOT, 'results', 'predictions', btag, 'probs.npz'))
    dev = max(float(np.max(np.abs(1 / (1 + np.exp(-clf.decision_function(np.load(os.path.join(fd, f'{s}__{v}.npy'))) / T)) - P[f'{s}__{v}'])))
              for s in TESTS for v in ('orig', 'cons'))
    return clf, T, dict(C=info['C'], temperature=T, saved_temperature=info['temperature'], max_abs_diff_cached_features=dev)


def routers(D):
    """Seed-wise SelectNorm-adapt routers exactly as in src/routing/run.py (lambda = 0)."""
    pool_src = np.array([r['src_id'] for r in load_set('policy_pool')])
    out = {}
    for seed in SEEDS:
        perm = np.random.default_rng(1000 + seed).permutation(len(pool_src))
        cut = int(0.8 * len(perm))
        tr, dv = D.load('policy_pool', np.sort(perm[:cut])), D.load('policy_pool', np.sort(perm[cut:]))
        otr = outcomes(tr['p0'], tr['p1'], tr['y'])
        win_tr = ((tr['p1'] > .5).astype(int) == tr['y']).astype(int)
        rel_cost = float(np.mean(tr['c1']) / np.mean(tr['c0']))
        fac = Factorized('lr', seed).fit(tr['Z'], otr['D'], win_tr)
        thr = tune_threshold(fac.score(dv['Z']), dv['p0'], dv['p1'], dv['y'], 0.0, rel_cost)
        fold_models = {}
        for s in TESTS:
            d = D.load(s)
            folds = fold_of(d['src'])
            od = outcomes(d['p0'], d['p1'], d['y'])
            fold_models[s] = {f: Factorized('lr', seed).fit(tr['Z'], otr['D'], win_tr, d['Z'][folds != f], od['D'][folds != f]) for f in (0, 1)}
        out[seed] = dict(thr=thr, fold=fold_models)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=200, help='sentences per set timed for all four systems')
    ap.add_argument('--threads', type=int, default=4)
    ap.add_argument('--models', default=','.join(MODELS))
    ap.add_argument('--out', default='measured_cost.json', help='file name under results/metrics')
    a = ap.parse_args()
    import torch
    from transformers import AutoModel, AutoTokenizer
    torch.set_num_threads(a.threads)
    revs = json.load(open(os.path.join(ROOT, 'experiments', 'configs', 'encoder_revisions.json')))
    Tn = normalizer('cons')
    outp = os.path.join(ROOT, 'results', 'metrics', a.out)
    report = dict(cpu=platform.processor() or platform.machine(), threads=a.threads, torch=torch.__version__,
                  n_timed_per_set=a.n, seeds=SEEDS, models={}, results=[])
    for model in a.models.split(','):
        btag = 'enc_' + tag(model)
        tok = AutoTokenizer.from_pretrained(model, revision=revs[model]['revision'])
        mod = AutoModel.from_pretrained(model, revision=revs[model]['revision']).eval()
        pre = PREFIX.get(model, '')
        clf, Tclf, hinfo = head(model)
        w, b = clf.coef_[0].astype(np.float64), float(clf.intercept_[0])

        def f(text):
            enc = tok([pre + text], truncation=True, max_length=128, return_tensors='pt')
            with torch.inference_mode():
                h = mod(**enc).last_hidden_state[0]
                v = torch.nn.functional.normalize(h.mean(0), dim=-1).numpy().astype(np.float64)
            return float(1 / (1 + np.exp(-(v @ w + b) / Tclf)))

        D = Data('enc:' + model, 'cons', GROUPS)
        R = routers(D)
        minfo = dict(head=hinfo, replay={}, live={})
        # (a) replay from cached inputs
        for s in TESTS:
            d = D.load(s)
            folds = fold_of(d['src'])
            for seed in SEEDS:
                sc = np.zeros(len(folds))
                for fo in (0, 1):
                    m = folds == fo
                    sc[m] = R[seed]['fold'][s][fo].score(d['Z'][m])
                g_arch = np.load(os.path.join(ROOT, 'results', 'predictions', btag, 'routes', f'main__B5_selectnorm_adapt__{s}__s{seed}.npz'))['g']
                minfo['replay'][f'{s}__s{seed}'] = int(np.sum((sc > R[seed]['thr']) != g_arch))
        print(model, 'replay mismatches', sum(minfo['replay'].values()), flush=True)
        for r in load_set('policy_pool')[:300]:
            f(normalize_arabic(r['text']))
            f(normalize_arabic(Tn(r['text'])[0]))
        for s in TESTS:
            rows = load_set(s)
            n = len(rows)
            d = D.load(s)
            folds = fold_of(d['src'])
            timed = set(np.random.default_rng(1).choice(n, min(a.n, n), replace=False).tolist())
            t = {k: [] for k in ('B0', 'B1', 'SN', 'R')}
            t_sn_all = np.zeros(n)
            p0l, p1l = np.zeros(n), np.zeros(n)
            zl = []
            j = 0
            for i, r in enumerate(rows):
                raw = r['text']
                x = normalize_arabic(raw)
                fr = R[0]['fold'][s][folds[i]]

                def sn():
                    p0 = f(x)
                    y, meta = Tn(raw)
                    y = normalize_arabic(y)
                    z, _ = F.build([raw], [{'meta': meta}], np.array([p0]), GROUPS)
                    g = bool(fr.score(z)[0] > R[0]['thr'])
                    p1 = f(y) if g else None
                    return p0, y, z, g, p1

                t0 = time.perf_counter()
                p0, y, z, g0, p1 = sn()
                t_sn_all[i] = time.perf_counter() - t0
                p0l[i] = p0
                p1l[i] = p1 if g0 else f(y)  # untimed second pass, for the comparison only
                zl.append(z[0])
                if i in timed:
                    order = ['B0', 'B1', 'SN', 'R']
                    order = order[j % 4:] + order[:j % 4]
                    j += 1
                    for k in order:
                        t0 = time.perf_counter()
                        if k == 'B0':
                            int(f(x) > .5)
                        elif k == 'B1':
                            int(f(normalize_arabic(Tn(raw)[0])) > .5)
                        elif k == 'SN':
                            _, _, _, g, q1 = sn()
                        else:
                            q0 = f(x); q1 = f(normalize_arabic(Tn(raw)[0])); int((q0 + q1) / 2 > .5)
                        t[k].append(time.perf_counter() - t0)
            Z = np.array(zl)
            y_true = d['y']
            live = dict(n=n, p0_max_abs_diff=float(np.max(np.abs(p0l - d['p0']))), p1_max_abs_diff=float(np.max(np.abs(p1l - d['p1']))),
                        yhat0_flips=int(np.sum((p0l > .5) != (d['p0'] > .5))), yhat1_flips=int(np.sum((p1l > .5) != (d['p1'] > .5))), seeds={})
            cols = dict(id=[r['id'] for r in rows], src_id=d['src'], p0_live=p0l, p1_live=p1l, p0_cached=d['p0'], p1_cached=d['p1'], sn_s0_seconds=t_sn_all)
            for seed in SEEDS:
                sc = np.zeros(n)
                for fo in (0, 1):
                    m = folds == fo
                    sc[m] = R[seed]['fold'][s][fo].score(Z[m])
                g = sc > R[seed]['thr']
                yhat = np.where(g, p1l > .5, p0l > .5).astype(int)
                arch = np.load(os.path.join(ROOT, 'results', 'predictions', btag, 'routes', f'main__B5_selectnorm_adapt__{s}__s{seed}.npz'))
                live['seeds'][seed] = dict(g_mismatch=int(np.sum(g != arch['g'])), yhat_mismatch=int(np.sum(yhat != arch['yhat'])),
                                           macro_f1_live=100 * f1_score(y_true, yhat, average='macro'),
                                           macro_f1_archived=100 * f1_score(y_true, arch['yhat'], average='macro'),
                                           sel_live=float(g.mean()), sel_archived=float(arch['g'].mean()))
                cols[f'g_live_s{seed}'] = g.astype(int)
                cols[f'g_archived_s{seed}'] = arch['g'].astype(int)
            od = os.path.join(ROOT, 'results', 'metrics', a.out.replace('.json', '_live'), btag)
            os.makedirs(od, exist_ok=True)
            pd.DataFrame(cols).to_csv(os.path.join(od, f'{s}.csv.gz'), index=False)
            minfo['live'][s] = live
            idx = np.array(sorted(timed))
            est = dict(B0=d['c0'], B1=d['ct'] + d['c1'], SN=d['c0'] + d['ct'] + np.load(os.path.join(ROOT, 'results', 'predictions', btag, 'routes', f'main__B5_selectnorm_adapt__{s}__s0.npz'))['g'] * d['c1'],
                       R=d['c0'] + d['ct'] + d['c1'])
            m0, e0 = np.mean(t['B0']), np.mean(est['B0'][idx])
            g0all = np.array(cols['g_live_s0'], bool)
            res = dict(model=model, set=s, n_timed=int(len(idx)), measured_B0_ms=1000 * m0,
                       measured_rel={k: float(np.mean(v) / m0) for k, v in t.items()},
                       estimated_rel={k: float(np.mean(v[idx]) / e0) for k, v in est.items()},
                       estimated_B0_ms=1000 * float(e0), routed_share_timed=float(g0all[idx].mean()),
                       sn_all_ms=1000 * float(t_sn_all.mean()), sn_all_rel_to_timed_B0=float(t_sn_all.mean() / m0),
                       routed_share_all=float(g0all.mean()))
            report['results'].append(res)
            print(json.dumps(res), json.dumps({k: v for k, v in live.items() if k != 'seeds'}),
                  json.dumps({sd: (v['g_mismatch'], v['yhat_mismatch']) for sd, v in live['seeds'].items()}), flush=True)
        report['models'][model] = minfo
        json.dump(report, open(outp, 'w'), indent=1)
    json.dump(report, open(outp, 'w'), indent=1)


if __name__ == '__main__':
    main()
