"""The stand-alone bootstrap script: macro-F1, resampling unit and Holm correction."""
import importlib.util, os
import numpy as np
from sklearn.metrics import f1_score
from conftest import ROOT

spec = importlib.util.spec_from_file_location('rs', os.path.join(ROOT, 'scripts', 'reproduce_stats.py'))
rs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rs)


def test_macro_f1_matches_sklearn():
    rng = np.random.default_rng(0)
    y, p = rng.integers(0, 2, 300), rng.integers(0, 2, 300)
    assert np.isclose(rs.mf1(np.ones((1, 300)), y, p)[0], 100 * f1_score(y, p, average='macro'))


def test_resample_weights_equal_row_duplication():
    rng = np.random.default_rng(1)
    y, p = rng.integers(0, 2, 50), rng.integers(0, 2, 50)
    W = rng.multinomial(50, np.full(50, 1 / 50), size=1).astype(float)
    idx = np.repeat(np.arange(50), W[0].astype(int))
    assert np.isclose(rs.mf1(W, y, p)[0], 100 * f1_score(y[idx], p[idx], average='macro'))


def test_holm_against_hand_computation():
    p = np.array([0.01, 0.04, 0.03, 0.5])
    # sorted 0.01,0.03,0.04,0.5 -> 0.04, 0.09, 0.09 (monotone), 0.5
    assert np.allclose(rs.holm(p), [0.04, 0.09, 0.09, 0.5])
