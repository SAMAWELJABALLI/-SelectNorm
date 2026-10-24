"""Downstream classifier f_theta: a logistic head on frozen representations.

Backends
  enc:<hf model id>  frozen encoder embeddings from src.models.encode (main experiments);
  charlr             character n-gram TF-IDF (sparse lexical reference, not an encoder).

f is trained on Arabic-script TSAC only (clf_train_ar). The regularization constant is
chosen on clf_dev_ar by macro-F1, and a temperature is fitted on clf_dev_ar by NLL.
Nothing from the policy pool or the test sets is used here.
Output: results/predictions/<backend_tag>/probs.npz with p(y=1) for every (set, view),
and per-sentence measured inference seconds.
"""
import argparse, json, os, sys, time
import numpy as np
from scipy.optimize import minimize_scalar
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.routing.views import SETS, LATIN_SETS, MODES, load_set, load_view_texts, ROOT
from src.models.encode import tag as enc_tag


def labels(name):
    return np.array([r['label'] for r in load_set(name)])


class CharLR:
    def __init__(self):
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.vec = TfidfVectorizer(analyzer='char_wb', ngram_range=(1, 5), sublinear_tf=True, min_df=2, max_features=300000)

    def fit_transform(self, texts):
        return self.vec.fit_transform(texts)

    def transform(self, texts):
        return self.vec.transform(texts)


def features(backend, name, view, charlr=None):
    """Return (X, per-sentence representation seconds) for one set and view, or (None, None)."""
    if backend == 'charlr':
        texts = load_view_texts(name, view)
        if texts is None:
            return None, None
        t0 = time.perf_counter()
        X = charlr.transform(texts)
        return X, np.full(len(texts), (time.perf_counter() - t0) / len(texts))
    d = os.path.join(ROOT, 'features', enc_tag(backend.split(':', 1)[1]))
    p = os.path.join(d, f'{name}__{view}.npy')
    if not os.path.exists(p):
        return None, None
    t = json.load(open(p[:-4] + '.time.json'))['per_sentence_s']
    return np.load(p), np.array(t)


def fit_temperature(z, y):
    def nll(T):
        q = 1 / (1 + np.exp(-z / T))
        q = np.clip(q, 1e-7, 1 - 1e-7)
        return -np.mean(y * np.log(q) + (1 - y) * np.log(1 - q))
    return minimize_scalar(nll, bounds=(0.05, 20), method='bounded').x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--backend', required=True)
    ap.add_argument('--out', default=os.path.join(ROOT, 'results', 'predictions'))
    ap.add_argument('--syn', action='store_true', help='also train on the synthetic Latin view (gsyn) of the training data')
    a = ap.parse_args()
    btag = a.backend.replace(':', '_').replace('/', '__') + ('+syn' if a.syn else '')
    charlr = None
    if a.backend == 'charlr':
        charlr = CharLR()
        charlr.fit_transform(load_view_texts('clf_train_ar', 'orig') + (load_view_texts('clf_train_ar', 'gsyn') if a.syn else []))
    Xtr, _ = features(a.backend, 'clf_train_ar', 'orig', charlr)
    Xdv, _ = features(a.backend, 'clf_dev_ar', 'orig', charlr)
    ytr, ydv = labels('clf_train_ar'), labels('clf_dev_ar')
    if a.syn:
        from scipy import sparse
        stack = sparse.vstack if sparse.issparse(Xtr) else np.vstack
        Xtr = stack([Xtr, features(a.backend, 'clf_train_ar', 'gsyn', charlr)[0]])
        Xdv = stack([Xdv, features(a.backend, 'clf_dev_ar', 'gsyn', charlr)[0]])
        ytr, ydv = np.concatenate([ytr, ytr]), np.concatenate([ydv, ydv])
    best = None
    for C in [0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30, 100]:
        m = LogisticRegression(C=C, max_iter=5000).fit(Xtr, ytr)
        f1 = f1_score(ydv, m.predict(Xdv), average='macro')
        if best is None or f1 > best[0]:
            best = (f1, C, m)
    f1dv, C, clf = best
    T = fit_temperature(clf.decision_function(Xdv), ydv)
    out, info = {}, {'backend': a.backend, 'syn': a.syn, 'C': C, 'dev_macro_f1': f1dv, 'temperature': T}
    for name in SETS:
        for view in ('orig',) + (MODES if name in LATIN_SETS else ()):
            X, trep = features(a.backend, name, view, charlr)
            if X is None:
                continue
            t0 = time.perf_counter()
            z = clf.decision_function(X)
            thead = (time.perf_counter() - t0) / X.shape[0]
            out[f'{name}__{view}'] = 1 / (1 + np.exp(-z / T))
            out[f'{name}__{view}__sec'] = trep + thead
    os.makedirs(os.path.join(a.out, btag), exist_ok=True)
    np.savez_compressed(os.path.join(a.out, btag, 'probs.npz'), **out)
    json.dump(info, open(os.path.join(a.out, btag, 'classifier.json'), 'w'), indent=1)
    print(json.dumps(info))


if __name__ == '__main__':
    main()
