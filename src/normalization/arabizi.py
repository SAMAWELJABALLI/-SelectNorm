"""Conservative Arabizi -> Arabic-script normalization (Module A).

Three transformation strategies share one tokenizer:
  T_rule : character rules applied to every Latin-script token (no lexicon, no safeguards);
  T_lex  : TArC-derived token lexicon, then character rules for unseen tokens (no safeguards);
  T_cons : T_lex plus linguistic safeguards (protected French/English tokens, negation
           circumfix handling, laughter and non-lexical tokens kept as sentiment cues);
  T_cov  : T_cons restricted to tokens with lexical evidence; tokens that would need the
           character-rule fallback stay in Latin script (token-level selective normalization).

Every call returns the transformed text and token-level reliability metadata, which the
routing policy may read because it is computed before the classifier sees T(x).
"""
import json
import math
import re
import unicodedata
from collections import Counter, defaultdict

try:
    from wordfreq import zipf_frequency
except ImportError:  # the safeguards need wordfreq; T_rule and T_lex do not
    zipf_frequency = None

AR_CHARS = re.compile(r'[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]')
LAT_TOKEN = re.compile(r"^[A-Za-zÀ-ɏ0-9']+$")
HAS_LETTER = re.compile(r'[A-Za-zÀ-ɏ]')
TOKEN = re.compile(r"[A-Za-zÀ-ɏ0-9']+|[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]+|\S")
DIACRITICS = re.compile(r'[ً-ْٰـ]')
LAUGH = re.compile(r'^(?:[hx]+|(?:h[aeiou]){2,}h?|(?:ha|he|hi)+|mdr+|lol+|ptdr+)$')

# Tunisian Arabizi conventions (TArC; Mdhaffar et al. 2017). 8 is h in Tunisian usage.
DIGRAPHS = [('ch', 'ش'), ('sh', 'ش'), ('kh', 'خ'), ('gh', 'غ'), ('th', 'ث'), ('dh', 'ذ'),
            ('ou', 'و'), ('oo', 'و'), ('ee', 'ي'), ('ph', 'ف'), ('qu', 'ك')]
SINGLE = {'2': 'ء', '3': 'ع', '4': 'ذ', '5': 'خ', '6': 'ط', '7': 'ح', '8': 'ه', '9': 'ق',
          'b': 'ب', 't': 'ت', 'j': 'ج', 'd': 'د', 'r': 'ر', 'z': 'ز', 's': 'س', 'f': 'ف',
          'q': 'ق', 'k': 'ك', 'l': 'ل', 'm': 'م', 'n': 'ن', 'h': 'ه', 'w': 'و', 'y': 'ي',
          'g': 'ق', 'p': 'ب', 'v': 'ف', 'x': 'كس', 'c': 'ك', 'i': 'ي', 'u': 'و'}
# Function words whose reading depends on the surrounding language (French article or
# Arabic particle); resolved from the sentence context by T_cons only.
CONTEXT_AMBIGUOUS = {'la', 'le', 'ma', 'mais', 'el', 'il', 'a', 'w', 'fi', 'men', 'ki', 'ya', 'li', 'de', 'des', 'les', 'et', 'en'}
NEGATION = re.compile(r'^(ma|me|mo|mi)([a-z0-9]{2,}?)(chh|chi|shi|ch|sh)$')
NEG_WORDS = {'mouch': 'موش', 'moch': 'موش', 'mech': 'مش', 'mich': 'ميش', 'manich': 'مانيش', 'mahouch': 'ماهوش',
             'mahich': 'ماهيش', 'mahech': 'ماهاش', 'manech': 'مانيش', 'la': 'لا', 'le': 'لا', 'lé': 'لا', 'lee': 'لا'}


def normalize_arabic(s):
    """Orthographic normalization applied to every classifier input (both views)."""
    s = unicodedata.normalize('NFKC', s)
    s = DIACRITICS.sub('', s)
    s = re.sub('[إأآٱ]', 'ا', s)
    s = s.replace('ى', 'ي').replace('ة', 'ه').replace('ڨ', 'ق').replace('گ', 'ق')
    return re.sub(r'(.)\1{2,}', r'\1\1', s)


def squeeze(w):
    return re.sub(r'(.)\1{2,}', r'\1', w.lower())


def deaccent(w):
    return ''.join(c for c in unicodedata.normalize('NFKD', w) if not unicodedata.combining(c))


def rule_translit(w):
    """Character-rule transliteration of one Latin-script token, with an ambiguity count."""
    w = deaccent(squeeze(w)).replace("'", '')
    w = re.sub(r'([b-df-hj-np-tv-z])\1', r'\1', w)
    out, i, amb = [], 0, 0
    n = len(w)
    while i < n:
        two = w[i:i + 2]
        hit = next((a for d, a in DIGRAPHS if d == two), None)
        if hit:
            out.append(hit)
            i += 2
            continue
        c = w[i]
        if c in 'aeo':
            # word-initial vowel -> alef; final a -> alef or ta marbuta (ambiguous); medial short vowels dropped
            if i == 0:
                out.append('ا' if c != 'o' else 'او')
            elif i == n - 1:
                out.append('ا' if c == 'a' else ('ه' if c == 'o' else ''))
                amb += c == 'a'
            elif w[i + 1:i + 2] == c:
                out.append('ا' if c != 'o' else 'و')
                i += 1
            else:
                amb += 1
            i += 1
            continue
        if c in SINGLE:
            out.append(SINGLE[c])
            amb += c in 'gc8'
        elif c.isalpha():
            amb += 1
        i += 1
    return ''.join(out), amb


class TArCLexicon:
    """Token map Arabizi -> CODA Arabic from the TArC training split."""

    def __init__(self, path, train_ids=None):
        self.map, self.foreign = defaultdict(Counter), Counter()
        for sent_id, toks in read_tarc(path):
            if train_ids is not None and sent_id not in train_ids:
                continue
            for lat, cls, coda in toks:
                k = squeeze(lat)
                if cls == 'arabizi':
                    self.map[k][normalize_arabic(coda)] += 1
                elif cls == 'foreign':
                    self.foreign[k] += 1

    def lookup(self, w):
        c = self.map.get(squeeze(w))
        if not c:
            return None, 0, 0.0
        tot = sum(c.values())
        best, n = c.most_common(1)[0]
        ent = -sum(v / tot * math.log(v / tot) for v in c.values())
        return best, tot, ent


def read_tarc(path):
    """Yield (sentence_index, [(latin, class, coda)]) from tarc.tsv."""
    cur, k = [], 0
    with open(path, encoding='utf-8') as f:
        next(f)
        for line in f:
            r = line.rstrip('\n').split('\t')
            if len(r) < 5:
                continue
            if r[2] == '<eos>':
                if cur:
                    yield k, cur
                    k += 1
                cur = []
                continue
            cur.append((r[2], r[3], r[4]))
    if cur:
        yield k, cur


def is_foreign(w, lex, thr=3.5):
    """French/English evidence beats Arabizi-lexicon evidence."""
    if zipf_frequency is None:
        return False
    k = squeeze(w)
    zf = max(zipf_frequency(k, 'fr'), zipf_frequency(k, 'en'))
    n_ar = sum(lex.map[k].values()) if k in lex.map else 0
    n_fr = lex.foreign.get(k, 0)
    if n_fr > n_ar:
        return True
    return zf >= thr and n_ar < 3


class Normalizer:
    def __init__(self, lexicon, mode='cons', foreign_thr=3.5):
        assert mode in ('rule', 'lex', 'cons', 'cov')
        self.lex, self.mode, self.thr = lexicon, mode, foreign_thr

    def __call__(self, text):
        toks, out, meta = self.transform_tokens(TOKEN.findall(text))
        return ' '.join(out), meta

    def transform_tokens(self, toks):
        lat_idx = [i for i, t in enumerate(toks) if LAT_TOKEN.match(t) and HAS_LETTER.search(t)]
        foreign = {}
        if self.mode in ('cons', 'cov'):
            for i in lat_idx:
                k = squeeze(toks[i])
                foreign[i] = k not in CONTEXT_AMBIGUOUS and is_foreign(toks[i], self.lex, self.thr)
            unamb = [foreign[i] for i in lat_idx if squeeze(toks[i]) not in CONTEXT_AMBIGUOUS]
            fr_ctx = (sum(unamb) / len(unamb)) if unamb else 0.0
            for i in lat_idx:
                # short or function-like tokens are read in the language of their context
                if squeeze(toks[i]) in CONTEXT_AMBIGUOUS or (foreign[i] and len(squeeze(toks[i])) <= 3):
                    foreign[i] = fr_ctx > 0.5
        meta = Counter()
        out = []
        for i, t in enumerate(toks):
            if i not in lat_idx:
                out.append(t)
                meta['other'] += 1
                continue
            k = squeeze(t)
            meta['latin'] += 1
            if self.mode in ('cons', 'cov'):
                if LAUGH.match(k):
                    out.append('ههه')
                    meta['laugh'] += 1
                    continue
                if foreign.get(i):
                    out.append(t)
                    meta['protected'] += 1
                    continue
                if k in NEG_WORDS:
                    out.append(NEG_WORDS[k])
                    meta['negation'] += 1
                    continue
            if self.mode in ('lex', 'cons', 'cov'):
                a, n, ent = self.lex.lookup(k)
                if a is not None:
                    out.append(a)
                    meta['lex'] += 1
                    meta['lex_ent'] += ent
                    continue
                if self.mode in ('cons', 'cov'):
                    m = NEGATION.match(deaccent(k))
                    if m and (m.group(1) == 'ma' or len(k) >= 6):
                        stem, amb = rule_translit(m.group(2))
                        out.append('ما ' + stem + 'ش')
                        meta['negation'] += 1
                        meta['rule'] += 1
                        meta['amb'] += amb
                        continue
            if self.mode == 'cov':
                # token-level selectivity: unknown tokens are preserved rather than guessed
                out.append(t)
                meta['kept_unknown'] += 1
                continue
            a, amb = rule_translit(k)
            out.append(a if a else t)
            meta['rule'] += 1
            meta['amb'] += amb
        return toks, out, dict(meta)


def build(tarc_path, mode, train_ids=None):
    return Normalizer(TArCLexicon(tarc_path, train_ids), mode)
