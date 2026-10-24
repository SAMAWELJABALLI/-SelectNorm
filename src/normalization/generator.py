"""Synthetic Arabic -> Latin-script generator G (for the classifier regime trained with
synthetic Arabizi). Reverse TArC lexicon (most frequent Arabizi spelling of each CODA form,
training split only) and Tunisian character rules for unseen words. No vowel insertion
beyond long vowels, so unseen words come out as consonant skeletons.
"""
import json, os, re
from collections import Counter, defaultdict
from src.normalization.arabizi import read_tarc, normalize_arabic, squeeze, TOKEN, AR_CHARS

RULES = {'ع': '3', 'ح': '7', 'ق': '9', 'خ': '5', 'ء': '2', 'ش': 'ch', 'غ': 'gh', 'ث': 'th', 'ذ': 'dh',
         'ص': 's', 'ض': 'dh', 'ط': 't', 'ظ': 'dh', 'ه': 'h', 'و': 'ou', 'ي': 'i', 'ا': 'a', 'ج': 'j',
         'د': 'd', 'ر': 'r', 'ز': 'z', 'س': 's', 'ف': 'f', 'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n',
         'ب': 'b', 'ت': 't', 'ئ': '2', 'ؤ': '2', 'ى': 'a', 'پ': 'p', 'ڤ': 'v'}


class Generator:
    def __init__(self, tarc_path, train_ids):
        m = defaultdict(Counter)
        for k, toks in read_tarc(tarc_path):
            if k not in train_ids:
                continue
            for lat, cls, coda in toks:
                if cls == 'arabizi' and ' ' not in coda:
                    m[normalize_arabic(coda)][squeeze(lat)] += 1
        self.map = {a: c.most_common(1)[0][0] for a, c in m.items()}

    def word(self, w):
        if w in self.map:
            return self.map[w]
        out = ''.join(RULES.get(ch, '') for ch in w)
        return out or w

    def __call__(self, text):
        toks = TOKEN.findall(normalize_arabic(text))
        return ' '.join(self.word(t) if AR_CHARS.search(t) else t for t in toks)
