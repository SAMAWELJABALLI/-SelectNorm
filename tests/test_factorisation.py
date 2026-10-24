"""B(z) = pi(z)(2 rho(z) - 1): exact per-example identity and the estimators built on it."""
import numpy as np
from src.routing.policies import outcomes, Factorized, DirectGain, fit_proba, tune_threshold, fit_shift


def synth(n=4000, seed=0):
    rng = np.random.default_rng(seed)
    y = rng.integers(0, 2, n)
    p0, p1 = rng.random(n), rng.random(n)
    return y, p0, p1


def test_identity_per_example():
    y, p0, p1 = synth()
    o = outcomes(p0, p1, y)
    win = ((p1 > .5).astype(int) == y).astype(int)
    # binary labels: a disagreement means exactly one view is right
    assert np.array_equal(o['help'] - o['harm'], o['D'] * (2 * win - 1))
    assert np.array_equal(o['e0'] - o['e1'], o['help'] - o['harm'])


def test_identity_in_expectation_on_known_strata():
    # z takes 3 values with known pi and rho; the plug-in estimate of pi(2rho-1) equals the mean benefit
    rng = np.random.default_rng(1)
    z = rng.integers(0, 3, 30000)
    pi, rho = np.array([.1, .5, .9])[z], np.array([.8, .5, .2])[z]
    D = rng.random(len(z)) < pi
    W = rng.random(len(z)) < rho
    b = np.where(D, 2 * W - 1, 0)
    for k in range(3):
        m = z == k
        est = D[m].mean() * (2 * W[m & D].mean() - 1)
        assert abs(est - b[m].mean()) < 1e-12
        assert abs(est - pi[m][0] * (2 * rho[m][0] - 1)) < 0.03


def test_factorised_router_recovers_sign():
    rng = np.random.default_rng(2)
    n = 6000
    Z = rng.normal(size=(n, 2))
    D = (rng.random(n) < 0.5).astype(int)
    win = (rng.random(n) < 1 / (1 + np.exp(-3 * Z[:, 0]))).astype(int)
    f = Factorized('lr', 0).fit(Z, D, win)
    s = f.score(np.array([[2.0, 0.0], [-2.0, 0.0]]))
    assert s[0] > 0 > s[1]
    pi, rho = f.parts(Z[:5])
    assert np.allclose(f.score(Z[:5]), pi * (2 * rho - 1))


def test_single_class_target_gives_constant():
    f = fit_proba('lr', np.zeros((5, 2)), np.ones(5))
    assert np.all(f(np.ones((3, 2))) == 1.0)


def test_empty_disagreement_subset():
    # no disagreement in the labelled split: rho is undefined; the router must not crash and must not normalise
    Z = np.random.default_rng(3).normal(size=(50, 2))
    f = Factorized('lr', 0).fit(Z, np.zeros(50, int), np.ones(50, int))
    assert np.all(f.score(Z) <= 0)


def test_threshold_large_lambda_never_routes():
    y, p0, p1 = synth(500)
    th = tune_threshold(np.random.default_rng(0).random(500), p0, p1, y, lam=10.0)
    assert th == np.inf or not np.any(np.random.default_rng(0).random(500) > th)


def test_theory_threshold_is_returned_unchanged():
    y, p0, p1 = synth(50)
    assert tune_threshold(np.zeros(50), p0, p1, y, fixed=0.123) == 0.123


def test_fit_shift_moves_towards_labels():
    base = np.full(200, 0.5)
    assert fit_shift(base, np.ones(200)) > 0 > fit_shift(base, np.zeros(200))
    assert abs(fit_shift(base, np.r_[np.ones(100), np.zeros(100)])) < 1e-3


def test_direct_gain_matches_help_minus_harm_scale():
    rng = np.random.default_rng(4)
    Z = rng.normal(size=(2000, 2))
    help_ = (rng.random(2000) < .3).astype(int)
    harm = ((rng.random(2000) < .1) & (help_ == 0)).astype(int)
    s = DirectGain('lr', 0).fit(Z, help_, harm).score(Z)
    assert abs(s.mean() - (help_.mean() - harm.mean())) < 0.02
