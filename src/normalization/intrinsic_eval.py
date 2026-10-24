"""Intrinsic validity of the transformation strategies, independent of any classifier.

TArC (Tunisian): 80/20 split by sentence; the lexicon is built on the 80% part and every
metric is computed on the held-out 20%. NArabizi (Algerian): out-of-dialect check against
the human Arabic-script transliteration (gold_ar) and the conservative gold (gold_cons,
French tokens kept in Latin script). Writes results/metrics/intrinsic_<mode>.json.
"""
import argparse, json, os, random, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.normalization.arabizi import (TArCLexicon, Normalizer, read_tarc, normalize_arabic, squeeze, LAT_TOKEN, HAS_LETTER)


def lev(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def score(pairs):
    """pairs: (gold_class, gold_form, output, latin) per token -> metrics."""
    c = Counter()
    for cls, gold, out, lat in pairs:
        prot = out == lat
        if cls == 'foreign':
            c['foreign'] += 1
            c['foreign_kept'] += prot
        else:
            c['arabizi'] += 1
            c['arabizi_kept_latin'] += prot
            g = normalize_arabic(gold).replace(' ', '')
            o = normalize_arabic(out).replace(' ', '')
            c['exact'] += g == o
            c['edits'] += lev(o, g)
            c['chars'] += len(g)
        if prot:
            c['kept'] += 1
            c['kept_correct'] += cls == 'foreign'
    return dict(
        n_arabizi=c['arabizi'], n_foreign=c['foreign'],
        arabizi_word_acc=c['exact'] / max(c['arabizi'], 1),
        arabizi_cer=c['edits'] / max(c['chars'], 1),
        arabizi_wrongly_kept=c['arabizi_kept_latin'] / max(c['arabizi'], 1),
        foreign_recall=c['foreign_kept'] / max(c['foreign'], 1),
        foreign_precision=c['kept_correct'] / max(c['kept'], 1))


def neg_check(pairs):
    """Negation preservation: gold forms containing a negation particle or circumfix."""
    c = Counter()
    for cls, gold, out, lat in pairs:
        g = normalize_arabic(gold)
        k = squeeze(lat)
        is_neg = g in ('موش', 'مش', 'لا', 'ميش') or (g.startswith('ما') and (g.endswith('ش') or g.endswith('شي')))
        if cls != 'arabizi' or not is_neg:
            continue
        o = normalize_arabic(out)
        c['n'] += 1
        c['kept'] += (o.startswith('ما') and (o.endswith('ش') or o.endswith('شي'))) or o in ('موش', 'مش', 'لا', 'ميش', 'مانيش', 'ماهوش', 'ماهيش')
    return dict(n_negation=c['n'], negation_preserved=c['kept'] / max(c['n'], 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tarc', default='data/raw/tarc/tarc.tsv')
    ap.add_argument('--narabizi', default='data/prepared/S5_narabizi.jsonl')
    ap.add_argument('--out', default='results/metrics')
    ap.add_argument('--seed', type=int, default=13)
    a = ap.parse_args()
    sents = list(read_tarc(a.tarc))
    ids = [k for k, _ in sents]
    random.Random(a.seed).shuffle(ids)
    train_ids = set(ids[:int(0.8 * len(ids))])
    json.dump(sorted(train_ids), open('data/prepared/tarc_train_ids.json', 'w'))
    lex = TArCLexicon(a.tarc, train_ids)
    nar = [json.loads(l) for l in open(a.narabizi, encoding='utf-8')]
    res = {}
    for mode in ('rule', 'lex', 'cons'):
        T = Normalizer(lex, mode)
        pairs = []
        for k, toks in sents:
            if k in train_ids:
                continue
            keep = [(lat, cls, coda) for lat, cls, coda in toks if cls in ('arabizi', 'foreign') and LAT_TOKEN.match(lat) and HAS_LETTER.search(lat)]
            _, out, _ = T.transform_tokens([t[0] for t in keep])
            pairs += [(cls, coda, o, lat) for (lat, cls, coda), o in zip(keep, out)]
        r = dict(tarc_heldout=score(pairs), tarc_negation=neg_check(pairs))
        pairs = []
        for row in nar:
            golds = row['tok_ar']
            lats = row['tok_lat']
            if len(golds) != len(lats):
                continue
            keep = [(l, 'foreign' if lg == 'fr' else 'arabizi', g) for l, lg, g in zip(lats, row['tok_lang'], golds)
                    if LAT_TOKEN.match(l) and HAS_LETTER.search(l) and lg in ('fr', 'ar_dz')]
            _, out, _ = T.transform_tokens([t[0] for t in keep])
            pairs += [(cls, g, o, l) for (l, cls, g), o in zip(keep, out)]
        r['narabizi'] = score(pairs)
        res[mode] = r
        print(mode, json.dumps(r, indent=1))
    os.makedirs(a.out, exist_ok=True)
    json.dump(res, open(os.path.join(a.out, 'intrinsic.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
