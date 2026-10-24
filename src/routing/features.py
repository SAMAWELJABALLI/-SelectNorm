"""Decision-point features z(x) (Module B).

Every feature is computable after the original-view pass f(x) and the normalizer T(x),
and before the transformed-view pass f(T(x)). Nothing here reads a label or the
transformed-view prediction. Groups (used by the ablations):
  conf   : confidence of f on x (max-probability, margin, binary entropy);
  script : script and surface statistics of x (length, Latin share, arithmographs, emoji);
  trel   : reliability metadata of T(x) (lexicon coverage, rule fallback, ambiguity,
           protected tokens, negation and laughter handling, share of changed tokens);
  emb    : optional low-rank projection of the encoder representation of x (free at the
           decision point, because the original pass already computed it).
"""
import re
import numpy as np

AR = re.compile(r'[؀-ۿ]')
LA = re.compile(r'[A-Za-zÀ-ɏ]')
DIGIT_IN_WORD = re.compile(r'(?<=[A-Za-z])[2-9]|[2-9](?=[A-Za-z])')
EMOJI = re.compile('[\U0001F300-\U0001FAFF☀-➿❤]')

GROUPS = {
    'conf': ['conf', 'margin', 'entropy'],
    'script': ['log_len', 'latin_share', 'arith_rate', 'emoji_rate', 'upper_rate', 'ar_share'],
    'trel': ['lex_rate', 'rule_rate', 'amb_rate', 'lex_ent', 'protected_rate', 'neg_rate', 'laugh_rate', 'changed_rate'],
}


def surface(text):
    toks = text.split()
    n = max(len(toks), 1)
    letters = LA.findall(text)
    a = len(AR.findall(text))
    return dict(log_len=np.log1p(len(toks)),
                latin_share=len(letters) / max(len(letters) + a, 1),
                ar_share=a / max(len(letters) + a, 1),
                arith_rate=len(DIGIT_IN_WORD.findall(text)) / n,
                emoji_rate=len(EMOJI.findall(text)) / n,
                upper_rate=sum(c.isupper() for c in letters) / max(len(letters), 1))


def trel(meta):
    m = meta or {}
    lat = max(m.get('latin', 0), 1)
    return dict(lex_rate=m.get('lex', 0) / lat, rule_rate=m.get('rule', 0) / lat,
                amb_rate=m.get('amb', 0) / lat, lex_ent=m.get('lex_ent', 0) / max(m.get('lex', 0), 1),
                protected_rate=m.get('protected', 0) / lat, neg_rate=m.get('negation', 0) / lat,
                laugh_rate=m.get('laugh', 0) / lat,
                changed_rate=(m.get('latin', 0) - m.get('protected', 0)) / max(m.get('latin', 0) + m.get('other', 0), 1))


def conf(p):
    p = np.clip(p, 1e-7, 1 - 1e-7)
    return dict(conf=np.maximum(p, 1 - p), margin=np.abs(2 * p - 1), entropy=-(p * np.log(p) + (1 - p) * np.log(1 - p)))


def build(raw_texts, view_rows, p0, groups=('conf', 'script', 'trel'), emb=None, emb_proj=None):
    cols, names = [], []
    if 'conf' in groups:
        c = conf(p0)
        for k in GROUPS['conf']:
            cols.append(c[k])
            names.append(k)
    if 'script' in groups:
        s = [surface(t) for t in raw_texts]
        for k in GROUPS['script']:
            cols.append(np.array([d[k] for d in s]))
            names.append(k)
    if 'trel' in groups:
        r = [trel(v.get('meta')) for v in view_rows]
        for k in GROUPS['trel']:
            cols.append(np.array([d[k] for d in r]))
            names.append(k)
    Z = np.column_stack(cols) if cols else np.zeros((len(p0), 0))
    if 'emb' in groups and emb is not None and emb_proj is not None:
        E = emb_proj(emb)
        Z = np.column_stack([Z, E])
        names += [f'emb{i}' for i in range(E.shape[1])]
    return Z, names
