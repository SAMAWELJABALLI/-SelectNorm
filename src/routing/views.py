"""Input views of every prepared set: the original text and its transformations.

A view file data/views/<set>__<view>.jsonl holds, per sentence in prepared order:
text (the classifier input), meta (normalizer reliability metadata) and t_norm (measured
seconds spent in the normalizer). Arabic-script sets have only the original view.
"""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.normalization.arabizi import Normalizer, TArCLexicon, normalize_arabic

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PREP = os.path.join(ROOT, 'data', 'prepared')
VIEWS = os.path.join(ROOT, 'data', 'views')
TARC = os.path.join(ROOT, 'data', 'raw', 'tarc', 'tarc.tsv')
SETS = ['clf_train_ar', 'clf_dev_ar', 'policy_pool', 'S0_tsac_ar', 'S3_tsac_lat', 'S4_tunizi',
        'S5_narabizi', 'S5ar_narabizi_gold', 'S6_myc_lat', 'S6ar_myc_ar']
LATIN_SETS = {'policy_pool', 'S3_tsac_lat', 'S4_tunizi', 'S5_narabizi', 'S6_myc_lat'}
MODES = ('cons', 'lex', 'rule', 'cov')
SYN_SETS = {'clf_train_ar', 'clf_dev_ar'}


def load_set(name):
    return [json.loads(l) for l in open(os.path.join(PREP, f'{name}.jsonl'), encoding='utf-8')]


_norm = {}


def normalizer(mode):
    if mode not in _norm:
        ids = set(json.load(open(os.path.join(PREP, 'tarc_train_ids.json'))))
        _norm[mode] = Normalizer(TArCLexicon(TARC, ids), mode)
    return _norm[mode]


def build_views(name):
    rows = load_set(name)
    os.makedirs(VIEWS, exist_ok=True)
    with open(os.path.join(VIEWS, f'{name}__orig.jsonl'), 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps({'text': normalize_arabic(r['text'])}, ensure_ascii=False) + '\n')
    if name in SYN_SETS:
        from src.normalization.generator import Generator
        G = Generator(TARC, set(json.load(open(os.path.join(PREP, 'tarc_train_ids.json')))))
        with open(os.path.join(VIEWS, f'{name}__gsyn.jsonl'), 'w', encoding='utf-8') as f:
            for r in rows:
                f.write(json.dumps({'text': G(r['text'])}, ensure_ascii=False) + '\n')
    if name not in LATIN_SETS:
        return
    for mode in MODES:
        T = normalizer(mode)
        with open(os.path.join(VIEWS, f'{name}__{mode}.jsonl'), 'w', encoding='utf-8') as f:
            for r in rows:
                t0 = time.perf_counter()
                out, meta = T(r['text'])
                out = normalize_arabic(out)
                dt = time.perf_counter() - t0
                f.write(json.dumps({'text': out, 'meta': meta, 't_norm': dt}, ensure_ascii=False) + '\n')


def load_view(name, view):
    p = os.path.join(VIEWS, f'{name}__{view}.jsonl')
    if not os.path.exists(p):
        return None
    return [json.loads(l) for l in open(p, encoding='utf-8')]


def load_view_texts(name, view):
    v = load_view(name, view)
    return None if v is None else [r['text'] for r in v]


if __name__ == '__main__':
    for s in SETS:
        build_views(s)
        print(s, 'done')
