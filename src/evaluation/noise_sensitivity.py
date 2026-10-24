"""Sensitivity of the oracle noise reference (revision R4).

The reference compares two classifiers f_a, f_b that differ only in their training sample,
applied to the same original input x; their "pick whichever is right" gain is headroom that
needs no normalization. It is a diagnostic reference, not a decomposition. This script varies
how f_a and f_b are made, to show how much the reference depends on that choice:
  boot     : bootstrap resamples (the reference used in the paper), C as selected;
  sub80    : 80% subsamples without replacement;
  sub50    : 50% subsamples without replacement;
  boot_Cx3 : bootstrap, C three times larger (weaker regularization);
  boot_C/3 : bootstrap, C three times smaller.
Each variant: 10 pairs. Also reports the headroom between the two views, oracle(x, T(x)) - best view.
Output: results/statistics/noise_sensitivity.json
"""
import json, os, sys
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.routing.views import ROOT, load_set
from src.routing.run import TESTS
from src.models.encode import tag

MODELS = ['intfloat/multilingual-e5-base', 'FacebookAI/xlm-roberta-base', 'sentence-transformers/LaBSE', 'UBC-NLP/MARBERTv2']


def f1(y, p):
    return 100 * f1_score(y, p, average='macro')


def main(pairs=10):
    ytr = np.array([r['label'] for r in load_set('clf_train_ar')])
    out = []
    for model in MODELS:
        fd = os.path.join(ROOT, 'features', tag(model))
        btag = 'enc_' + tag(model)
        C = json.load(open(os.path.join(ROOT, 'results', 'predictions', btag, 'classifier.json')))['C']
        P = np.load(os.path.join(ROOT, 'results', 'predictions', btag, 'probs.npz'))
        Xtr = np.load(os.path.join(fd, 'clf_train_ar__orig.npy'))
        X = {s: np.load(os.path.join(fd, f'{s}__orig.npy')) for s in TESTS}
        Y = {s: np.array([r['label'] for r in load_set(s)]) for s in TESTS}
        variants = {'boot': (True, 1.0, C), 'sub80': (False, 0.8, C), 'sub50': (False, 0.5, C),
                    'boot_Cx3': (True, 1.0, 3 * C), 'boot_C/3': (True, 1.0, C / 3)}
        for vname, (repl, frac, c) in variants.items():
            rng = np.random.default_rng(0)
            acc = {s: [] for s in TESTS}
            dis = {s: [] for s in TESTS}
            for _ in range(pairs):
                preds = {s: [] for s in TESTS}
                for _ in range(2):
                    i = rng.choice(len(ytr), int(frac * len(ytr)), replace=repl)
                    m = LogisticRegression(C=c, max_iter=5000).fit(Xtr[i], ytr[i])
                    for s in TESTS:
                        preds[s].append(m.predict(X[s]))
                for s in TESTS:
                    a, b = preds[s]
                    y = Y[s]
                    acc[s].append(f1(y, np.where(a == y, a, b)) - np.mean([f1(y, a), f1(y, b)]))
                    dis[s].append(np.mean(a != b))
            for s in TESTS:
                y = Y[s]
                p0, p1 = (P[f'{s}__orig'] > .5).astype(int), (P[f'{s}__cons'] > .5).astype(int)
                view_head = f1(y, np.where(p0 == y, p0, p1)) - max(f1(y, p0), f1(y, p1))
                out.append(dict(model=model, variant=vname, set=s, noise_headroom=float(np.mean(acc[s])),
                                noise_headroom_sd=float(np.std(acc[s])), noise_disagree=float(np.mean(dis[s])),
                                view_disagree=float(np.mean(p0 != p1)), view_headroom=float(view_head),
                                excess=float(view_head - np.mean(acc[s]))))
                print(model.split('/')[-1], vname, s, round(out[-1]['noise_headroom'], 2), round(out[-1]['excess'], 2), flush=True)
    json.dump(out, open(os.path.join(ROOT, 'results', 'statistics', 'noise_sensitivity.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
