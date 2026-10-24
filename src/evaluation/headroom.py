"""How much of the oracle headroom is selection signal and how much is noise between views?

Control: two classifiers trained on bootstrap resamples of the same Arabic-script training
data, applied to the SAME original input x. Their oracle (pick whichever is right) gains
over a single one only through classifier noise. The excess headroom of normalization is
  oracle(x, T(x)) - B_best  minus  oracle(f_a(x), f_b(x)) - mean single,
reported per test set, averaged over 5 bootstrap pairs. Labels are used for analysis only.
"""
import argparse, json, os, sys
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.routing.views import ROOT, load_set
from src.routing.run import TESTS
from src.models.encode import tag


def f1(y, p):
    return 100 * f1_score(y, p, average='macro')


def oracle(y, a, b):
    return np.where(a == y, a, b)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True)
    ap.add_argument('--pairs', type=int, default=5)
    a = ap.parse_args()
    fd = os.path.join(ROOT, 'features', tag(a.model))
    btag = 'enc_' + tag(a.model)
    info = json.load(open(os.path.join(ROOT, 'results', 'predictions', btag, 'classifier.json')))
    P = np.load(os.path.join(ROOT, 'results', 'predictions', btag, 'probs.npz'))
    Xtr = np.load(os.path.join(fd, 'clf_train_ar__orig.npy'))
    ytr = np.array([r['label'] for r in load_set('clf_train_ar')])
    rng = np.random.default_rng(0)
    out = []
    for s in TESTS:
        y = np.array([r['label'] for r in load_set(s)])
        X = np.load(os.path.join(fd, f'{s}__orig.npy'))
        p0, p1 = (P[f'{s}__orig'] > .5).astype(int), (P[f'{s}__cons'] > .5).astype(int)
        best = max(f1(y, p0), f1(y, p1))
        gain_T = f1(y, oracle(y, p0, p1)) - best
        ctrl = []
        for _ in range(a.pairs):
            preds = []
            for _ in range(2):
                i = rng.integers(0, len(ytr), len(ytr))
                m = LogisticRegression(C=info['C'], max_iter=5000).fit(Xtr[i], ytr[i])
                preds.append(m.predict(X))
            ctrl.append(f1(y, oracle(y, *preds)) - np.mean([f1(y, q) for q in preds]))
        out.append(dict(set=s, oracle_T=f1(y, oracle(y, p0, p1)), best_single_view=best, headroom_T=gain_T,
                        headroom_noise=float(np.mean(ctrl)), headroom_noise_sd=float(np.std(ctrl)),
                        excess=gain_T - float(np.mean(ctrl))))
        print(out[-1])
    json.dump(out, open(os.path.join(ROOT, 'results', 'metrics', btag, 'headroom.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
