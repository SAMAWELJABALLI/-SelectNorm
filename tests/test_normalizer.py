"""Normaliser invariants on a synthetic TArC-format lexicon (no corpus needed)."""
import os
import pytest
from conftest import FIXTURES
from src.normalization.arabizi import Normalizer, TArCLexicon, rule_translit, normalize_arabic, zipf_frequency

TSV = os.path.join(FIXTURES, 'tarc_mini.tsv')


@pytest.fixture(scope='module')
def lex():
    return TArCLexicon(TSV)


def test_lexicon_reads_arabizi_and_foreign_classes(lex):
    assert lex.lookup('barcha')[0] == 'برشا' and lex.lookup('barcha')[1] == 2
    assert lex.lookup('film')[0] is None and lex.foreign['film'] == 1


def test_train_ids_restrict_the_lexicon():
    lex = TArCLexicon(TSV, train_ids={0})
    assert lex.lookup('behi')[0] is None and lex.lookup('barcha')[0] is not None


@pytest.mark.parametrize('mode', ['rule', 'lex', 'cons', 'cov'])
def test_deterministic(lex, mode):
    T = Normalizer(lex, mode)
    s = '3jebni el film barcha hhhh mouch behi 9a3da'
    assert T(s) == T(s) == Normalizer(TArCLexicon(TSV), mode)(s)


def test_rule_mode_ignores_lexicon(lex):
    out, meta = Normalizer(lex, 'rule')('barcha')
    assert out == rule_translit('barcha')[0] and meta.get('lex', 0) == 0


def test_lex_mode_uses_lexicon(lex):
    out, meta = Normalizer(lex, 'lex')('barcha behi')
    assert out == 'برشا باهي' and meta['lex'] == 2


def test_negation_words_and_circumfix(lex):
    T = Normalizer(lex, 'cons')
    out, meta = T('mouch behi')
    assert out.split()[0] == 'موش' and meta['negation'] == 1
    out, meta = T('ma7abbitch')
    assert out.startswith('ما ') and out.endswith('ش') and meta['negation'] == 1


def test_laughter_kept_as_sentiment_cue(lex):
    out, meta = Normalizer(lex, 'cons')('hhhhh')
    assert out == 'ههه' and meta['laugh'] == 1


def test_foreign_lexicon_evidence_protects_token(lex):
    # 'film' is tagged foreign in the lexicon and never as Arabizi: kept in Latin script
    out, meta = Normalizer(lex, 'cons')('film barcha behi')
    if zipf_frequency is None:
        pytest.skip('wordfreq not installed: the safeguards are disabled')
    assert out.split()[0] == 'film' and meta['protected'] >= 1


@pytest.mark.skipif(zipf_frequency is None, reason='wordfreq not installed')
def test_french_english_protection(lex):
    out, _ = Normalizer(lex, 'cons')('wallah the movie was excellent')
    assert {'movie', 'excellent'} <= set(out.split())


def test_cov_keeps_unknown_tokens_in_latin(lex):
    out, meta = Normalizer(lex, 'cov')('barcha zzqrt')
    assert out.split() == ['برشا', 'zzqrt'] and meta['kept_unknown'] == 1


def test_arabic_script_and_punctuation_untouched(lex):
    out, _ = Normalizer(lex, 'cons')('برشا !')
    assert out == 'برشا !'


def test_orthographic_normalisation():
    assert normalize_arabic('أحمد') == 'احمد'
    assert normalize_arabic('مدرسة') == 'مدرسه'
    assert normalize_arabic('هههههه') == 'هه'
