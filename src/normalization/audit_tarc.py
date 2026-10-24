"""Audit of the TArC held-out evaluation for rule-development contamination (revision).

The 80/20 sentence split (seed 13) separates the lexicon (80%) from the held-out part (20%).
The safeguard rules of T_cons (foreign-word protection threshold, CONTEXT_AMBIGUOUS, NEG_WORDS,
the negation regex, laughter) were designed while inspecting errors on the held-out 20%, so
its scores there are development results. This script quantifies what it can:
 1. split integrity: lexicon entries are built from training-split sentences only;
 2. for every hand-listed word, its frequency in the training split and in the held-out split
    (an item that occurs only in the held-out split can only have come from inspecting it);
 3. a rule-free subset: held-out accuracy on tokens that no hand-written list or regex touches;
 4. a swapped split: lexicon built from the 20% part, rule-driven metrics (negation, foreign
    protection) measured on the 80% part, where the rules were not inspected. Word accuracy
    there uses a 4x smaller lexicon and is not comparable to the main numbers.
Output: results/metrics/tarc_audit.json
"""
import json, os, random, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.normalization.arabizi import (TArCLexicon, Normalizer, read_tarc, squeeze, deaccent, LAT_TOKEN, HAS_LETTER,
                                       CONTEXT_AMBIGUOUS, NEG_WORDS, NEGATION, LAUGH)
from src.normalization.intrinsic_eval import score, neg_check

TARC = 'data/raw/tarc/tarc.tsv'


def pairs_for(T, sents, ids):
    out = []
    for k, toks in sents:
        if k not in ids:
            continue
        keep = [(lat, cls, coda) for lat, cls, coda in toks if cls in ('arabizi', 'foreign') and LAT_TOKEN.match(lat) and HAS_LETTER.search(lat)]
        _, o, _ = T.transform_tokens([t[0] for t in keep])
        out += [(cls, coda, oo, lat) for (lat, cls, coda), oo in zip(keep, o)]
    return out


def rule_touched(lat):
    k = squeeze(lat)
    return k in CONTEXT_AMBIGUOUS or k in NEG_WORDS or bool(LAUGH.match(k)) or bool(NEGATION.match(deaccent(k)))


def main():
    sents = list(read_tarc(TARC))
    ids = [k for k, _ in sents]
    random.Random(13).shuffle(ids)
    train = set(ids[:int(0.8 * len(ids))])
    held = set(ids) - train
    saved = set(json.load(open('data/prepared/tarc_train_ids.json')))
    res = {'n_train_sentences': len(train), 'n_heldout_sentences': len(held), 'split_matches_saved_ids': saved == train}
    # 2. hand-listed items
    freq = {'train': Counter(), 'heldout': Counter()}
    for k, toks in sents:
        part = 'train' if k in train else 'heldout'
        for lat, cls, coda in toks:
            freq[part][squeeze(lat)] += 1
    items = sorted(set(CONTEXT_AMBIGUOUS) | set(NEG_WORDS))
    res['hand_items'] = {w: dict(train=freq['train'][w], heldout=freq['heldout'][w]) for w in items}
    res['hand_items_heldout_only'] = [w for w in items if freq['heldout'][w] > 0 and freq['train'][w] == 0]
    res['hand_items_absent_from_tarc'] = [w for w in items if freq['heldout'][w] == 0 and freq['train'][w] == 0]
    # 3. rule-free subset on the held-out split
    lex = TArCLexicon(TARC, train)
    res['heldout'] = {}
    for mode in ('rule', 'lex', 'cons'):
        p = pairs_for(Normalizer(lex, mode), sents, held)
        free = [q for q in p if not rule_touched(q[3])]
        res['heldout'][mode] = dict(all=score(p), rule_free=score(free), n_rule_touched=len(p) - len(free), negation=neg_check(p))
    # 4. swapped split
    lex_s = TArCLexicon(TARC, held)
    res['swapped'] = {}
    for mode in ('lex', 'cons'):
        p = pairs_for(Normalizer(lex_s, mode), sents, train)
        res['swapped'][mode] = dict(all=score(p), negation=neg_check(p))
    json.dump(res, open('results/metrics/tarc_audit.json', 'w'), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in res.items() if k != 'hand_items'}, indent=1, ensure_ascii=False))


if __name__ == '__main__':
    main()
