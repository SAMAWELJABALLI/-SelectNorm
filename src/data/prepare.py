"""Build the SelectNorm data splits from the raw corpora (pinned commits, see docs/DATA.md).

Output: data/prepared/{set}.jsonl with one record per sentence:
  id, src_id, corpus, dialect, script, text, label (1 = positive, 0 = negative),
  and for NArabizi the gold Arabic-script transliteration (gold_ar) and the
  conservative gold (gold_cons: Arabic script with French tokens kept in Latin).

Leakage control: exact duplicates are removed within each set, and every
evaluation or policy sentence that is a near-copy (character 3-gram cosine >= 0.9)
of a classifier-training sentence, or of a policy sentence for test sets, is removed.
"""
import argparse, hashlib, io, json, os, re, unicodedata
from collections import Counter
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

AR = re.compile(r'[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]')
LA = re.compile(r'[A-Za-zÀ-ɏ]')


def script_of(s):
    a, l = len(AR.findall(s)), len(LA.findall(s))
    if a + l == 0:
        return 'none'
    if l / (a + l) <= 0.2:
        return 'ar'
    if a / (a + l) <= 0.2:
        return 'lat'
    return 'mix'


def norm_key(s):
    s = unicodedata.normalize('NFKC', s).lower()
    s = re.sub(r'(.)\1{2,}', r'\1\1', s)
    return re.sub(r'\W+', ' ', s).strip()


def sid(*parts):
    return hashlib.md5('|'.join(map(str, parts)).encode()).hexdigest()[:12]


def read_tsac(raw):
    rows = []
    for sp in ['train', 'test']:
        for lab, y in [('pos', 1), ('neg', 0)]:
            path = os.path.join(raw, 'TSAC', f'{sp}_{lab}.txt')
            for i, t in enumerate(open(path, encoding='utf-8', errors='replace').read().splitlines()):
                rows.append(dict(src_id=sid('tsac', sp, lab, i), corpus='TSAC', split=sp, dialect='tn', text=t.strip(), label=y))
    return rows


def read_tunizi(raw):
    rows = []
    path = os.path.join(raw, 'TUNIZI-Sentiment-Analysis-Tunisian-Arabizi-Dataset', 'TUNIZI-Dataset.txt')
    for i, line in enumerate(open(path, encoding='utf-8', errors='replace').read().splitlines()):
        lab, _, t = line.partition(';')
        lab = re.sub(r'[^0-9-]', '', lab)
        if lab not in ('1', '-1'):
            continue
        rows.append(dict(src_id=sid('tunizi', i), corpus='TUNIZI', split='test', dialect='tn', text=t.strip(), label=int(lab == '1')))
    return rows


def read_myc(raw):
    t = open(os.path.join(raw, 'MYC', 'DATA_CLEANED.csv'), 'rb').read().decode('utf-16')
    d = pd.read_csv(io.StringIO(t))
    return [dict(src_id=sid('myc', i), corpus='MYC', split='test', dialect='ma', text=str(r.sentence).strip(), label=int(r.polarity == 1))
            for i, r in enumerate(d.itertuples())]


def read_conllu(path):
    """Return {sent_id: (text, gold_ar, gold_cons, langs)} from NArabizi conllu."""
    out, cur = {}, None
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if line.startswith('# sent_id'):
            cur = dict(id=line.split('=', 1)[1].strip(), toks=[])
        elif line.startswith('# text') and cur is not None:
            cur['text'] = line.split('=', 1)[1].strip()
        elif line and not line.startswith('#') and cur is not None:
            c = line.split('\t')
            if len(c) < 10:
                continue
            if '-' in c[0] or '.' in c[0]:
                continue
            lang = re.search(r'lang=(\w+)', line)
            cur['toks'].append((c[1], c[3], c[4], lang.group(1) if lang else 'na', 'SpaceAfter=No' in c[9]))
        elif not line and cur is not None and cur.get('toks'):
            def join(k):
                s = ''
                for tok in cur['toks']:
                    s += tok[k] + ('' if tok[4] else ' ')
                return s.strip()
            out[cur['id']] = (cur.get('text', ''), join(1), join(2), [t[3] for t in cur['toks']], [t[0] for t in cur['toks']], [t[1] for t in cur['toks']])
            cur = None
    return out


def read_narabizi(raw):
    base = os.path.join(raw, 'Narabizi', 'data', 'Narabizi')
    rows = []
    for sp in ['train', 'dev', 'test']:
        conl = read_conllu(os.path.join(base, 'pos', f'{sp}_NArabizi.conllu'))
        for line in open(os.path.join(base, 'sentiment', f'{sp}_Narabizi_sentiment.txt'), encoding='utf-8').read().splitlines()[1:]:
            k, _, lab = line.partition('\t')
            k = k.split('=', 1)[1].strip()
            if lab.strip() not in ('POS', 'NEG') or k not in conl:
                continue
            text, gar, gcons, langs, toks, toks_ar = conl[k]
            rows.append(dict(src_id=sid('narabizi', k), corpus='NArabizi', split='test', dialect='dz', text=text, label=int(lab.strip() == 'POS'),
                             gold_ar=gar, gold_cons=gcons, tok_lang=langs, tok_lat=toks, tok_ar=toks_ar))
    return rows


def dedup(rows):
    seen, out, n = set(), [], 0
    for r in rows:
        k = norm_key(r['text'])
        if not k or k in seen:
            n += 1
            continue
        seen.add(k)
        out.append(r)
    return out, n


def near_copy_mask(query, ref, theta=0.9):
    """True where a query text has a reference text with char-3gram cosine >= theta."""
    if not query or not ref:
        return np.zeros(len(query), bool)
    v = TfidfVectorizer(analyzer='char', ngram_range=(3, 3), lowercase=True, use_idf=False, norm='l2')
    v.fit([norm_key(t) for t in ref + query])
    R, Q = v.transform([norm_key(t) for t in ref]), v.transform([norm_key(t) for t in query])
    m = np.zeros(len(query), bool)
    for i in range(0, len(query), 2000):
        s = (Q[i:i + 2000] @ R.T)
        m[i:i + 2000] = np.asarray(s.max(axis=1).todense()).ravel() >= theta
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--raw', default='data/raw')
    ap.add_argument('--out', default='data/prepared')
    ap.add_argument('--seed', type=int, default=13)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rng = np.random.default_rng(a.seed)
    report = Counter()

    def tag(rows):
        for r in rows:
            r['script'] = script_of(r['text'])
        return rows

    tsac = tag(read_tsac(a.raw))
    sets = {}
    tr = [r for r in tsac if r['split'] == 'train']
    te = [r for r in tsac if r['split'] == 'test']
    for name, rows in [('tsac_train', tr), ('tsac_test', te)]:
        for s in ('mix', 'none'):
            report[f'{name}/excluded_{s}'] = sum(r['script'] == s for r in rows)
    tr, report['tsac_train/rm_exact'] = dedup([r for r in tr if r['script'] in ('ar', 'lat')])
    # Arabic-script training sentences: classifier training (90%) and classifier dev (10%).
    tr_ar = [r for r in tr if r['script'] == 'ar']
    tr_lat = [r for r in tr if r['script'] == 'lat']
    idx = rng.permutation(len(tr_ar))
    ndev = len(tr_ar) // 10
    sets['clf_dev_ar'] = [tr_ar[i] for i in idx[:ndev]]
    sets['clf_train_ar'] = [tr_ar[i] for i in idx[ndev:]]
    # Human Latin-script TSAC training sentences: the routing-policy pool (never seen by the classifier).
    m = near_copy_mask([r['text'] for r in tr_lat], [r['text'] for r in sets['clf_train_ar']])
    report['policy_pool/rm_nearcopy_clf'] = int(m.sum())
    sets['policy_pool'] = [r for r, x in zip(tr_lat, m) if not x]

    clf_texts = [r['text'] for r in sets['clf_train_ar'] + sets['clf_dev_ar']]
    pol_texts = [r['text'] for r in sets['policy_pool']]
    te, report['tsac_test/rm_exact'] = dedup([r for r in te if r['script'] in ('ar', 'lat')])
    ext = {'S0_tsac_ar': [r for r in te if r['script'] == 'ar'], 'S3_tsac_lat': [r for r in te if r['script'] == 'lat']}
    tz = tag(read_tunizi(a.raw))
    ext['S4_tunizi'] = [r for r in tz if r['script'] == 'lat']
    report['S4_tunizi/excluded_script'] = len(tz) - len(ext['S4_tunizi'])
    na = tag(read_narabizi(a.raw))
    ext['S5_narabizi'] = [r for r in na if r['script'] == 'lat']
    report['S5_narabizi/excluded_script'] = len(na) - len(ext['S5_narabizi'])
    my = tag(read_myc(a.raw))
    ext['S6_myc_lat'] = [r for r in my if r['script'] == 'lat']
    ext['S6ar_myc_ar'] = [r for r in my if r['script'] == 'ar']
    for s in ('mix', 'none'):
        report[f'MYC/excluded_{s}'] = sum(r['script'] == s for r in my)
    ref = clf_texts + pol_texts
    for k, rows in ext.items():
        rows, report[f'{k}/rm_exact'] = dedup(rows)
        m = near_copy_mask([r['text'] for r in rows], ref)
        report[f'{k}/rm_nearcopy_train'] = int(m.sum())
        sets[k] = [r for r, x in zip(rows, m) if not x]
    # The Arabic-script NArabizi gold forms the content-controlled pair of S5 (same src_id).
    sets['S5ar_narabizi_gold'] = [dict(r, text=r['gold_ar'], script='ar', view='gold_ar') for r in sets['S5_narabizi']]
    for k, rows in sets.items():
        with open(os.path.join(a.out, f'{k}.jsonl'), 'w', encoding='utf-8') as f:
            for i, r in enumerate(rows):
                r = dict(r, id=f'{k}:{i}')
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        lab = Counter(r['label'] for r in rows)
        report[f'{k}/n'] = len(rows)
        report[f'{k}/pos'] = lab[1]
        report[f'{k}/neg'] = lab[0]
    with open(os.path.join(a.out, 'prep_report.json'), 'w') as f:
        json.dump(dict(sorted(report.items())), f, indent=1)
    for k, v in sorted(report.items()):
        print(f'{k}\t{v}')


if __name__ == '__main__':
    main()
