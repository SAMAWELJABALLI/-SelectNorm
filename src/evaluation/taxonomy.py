"""Error taxonomy of normalization outcomes (Researcher 2 deliverable).

For every test sentence, the transition of the main encoder (help / harm / both right /
both wrong) is cross-tabulated with linguistic conditions read from the input and the
normalizer metadata. Condition flags are fixed before inspection:
  foreign   : >= 30% of Latin tokens protected as French/English by T_cons
  negation  : T_cons applied a negation rule
  low_cov   : < 50% of Latin tokens found in the TArC lexicon (rule fallback dominates)
  short     : <= 3 tokens
Writes results/statistics/<backend>/taxonomy.csv and examples.jsonl (verbatim instances).
"""
import argparse, json, os, sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.routing.views import ROOT, load_set, load_view
from src.routing.policies import outcomes
from src.routing.run import TESTS


def flags(raw, meta):
    lat = max(meta.get('latin', 0), 1)
    return dict(foreign=meta.get('protected', 0) / lat >= 0.3, negation=meta.get('negation', 0) > 0,
                low_cov=meta.get('lex', 0) / lat < 0.5, short=len(raw.split()) <= 3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--backend', required=True)
    ap.add_argument('--n_examples', type=int, default=4)
    a = ap.parse_args()
    P = np.load(os.path.join(ROOT, 'results', 'predictions', a.backend, 'probs.npz'))
    rows, ex = [], []
    rng = np.random.default_rng(0)
    for s in TESTS:
        data = load_set(s)
        v = load_view(s, 'cons')
        y = np.array([r['label'] for r in data])
        o = outcomes(P[f'{s}__orig'], P[f'{s}__cons'], y)
        trans = np.where(o['help'] == 1, 'help', np.where(o['harm'] == 1, 'harm', np.where(o['e0'] == 1, 'both_wrong', 'both_right')))
        F = pd.DataFrame([flags(r['text'], vv['meta']) for r, vv in zip(data, v)])
        F['trans'] = trans
        for c in ['foreign', 'negation', 'low_cov', 'short']:
            for val in (True, False):
                sub = F[F[c] == val]
                n = len(sub)
                rows.append(dict(set=s, condition=c, value=val, n=n,
                                 help=100 * (sub.trans == 'help').mean() if n else np.nan,
                                 harm=100 * (sub.trans == 'harm').mean() if n else np.nan,
                                 both_wrong=100 * (sub.trans == 'both_wrong').mean() if n else np.nan))
        for t in ('help', 'harm'):
            idx = np.where(trans == t)[0]
            for i in rng.choice(idx, min(a.n_examples, len(idx)), replace=False):
                ex.append(dict(set=s, transition=t, label=int(y[i]), text=data[i]['text'], normalized=v[i]['text'],
                               p_orig=float(P[f'{s}__orig'][i]), p_norm=float(P[f'{s}__cons'][i]), **{k: bool(x) for k, x in F.iloc[i].items() if k != 'trans'}))
    out = os.path.join(ROOT, 'results', 'statistics', a.backend)
    os.makedirs(out, exist_ok=True)
    pd.DataFrame(rows).to_csv(os.path.join(out, 'taxonomy.csv'), index=False)
    with open(os.path.join(out, 'examples.jsonl'), 'w', encoding='utf-8') as f:
        for e in ex:
            f.write(json.dumps(e, ensure_ascii=False) + '\n')
    print(pd.DataFrame(rows).round(1).to_string())


if __name__ == '__main__':
    main()
