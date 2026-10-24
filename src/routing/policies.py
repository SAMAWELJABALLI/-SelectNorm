"""Routing policies g(z) in {0: keep x, 1: classify T(x)} (Modules B and C).

All scores are oriented so that a larger score means "normalize". Under 0-1 loss the
expected benefit of normalizing is
    B(z) = E[e0 - e1 | z] = P(help | z) - P(harm | z),
with e_a the error of view a, help = {e0=1, e1=0} and harm = {e0=0, e1=1}. For binary
labels, a disagreement D = 1[yhat0 != yhat1] implies that exactly one view is right, so
    B(z) = pi(z) * (2 rho(z) - 1),  pi(z) = P(D=1 | z),  rho(z) = P(yhat1 = y | D=1, z).
pi needs no labels (only both views' predictions, computed offline), so it can be
re-estimated on unlabeled text from a new domain; rho needs labels and is learned on the
source policy split only (SelectNorm). The Bayes rule normalizes iff B(z) > lambda * c.
"""
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def make_estimator(kind, seed=0):
    if kind == 'lr':
        return make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=5000))
    if kind == 'gbm':
        return HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, max_leaf_nodes=15,
                                              l2_regularization=1.0, min_samples_leaf=20, random_state=seed)
    raise ValueError(kind)


def fit_proba(kind, Z, t, w=None, seed=0):
    """Fit P(t=1 | z); returns a function z -> probability. Constant if t is single-class."""
    t = np.asarray(t).astype(int)
    if len(t) == 0:
        # no training example (e.g. no disagreement in the labelled split): uninformative 1/2
        return lambda Zq: np.full(len(Zq), 0.5)
    if t.min() == t.max():
        c = float(t[0])
        return lambda Zq: np.full(len(Zq), c)
    m = make_estimator(kind, seed)
    if w is None:
        m.fit(Z, t)
    elif kind == 'lr':
        m.fit(Z, t, logisticregression__sample_weight=w)
    else:
        m.fit(Z, t, sample_weight=w)
    return lambda Zq: m.predict_proba(Zq)[:, 1]


def outcomes(p0, p1, y):
    yh0, yh1 = (p0 > .5).astype(int), (p1 > .5).astype(int)
    e0, e1 = (yh0 != y).astype(int), (yh1 != y).astype(int)
    return dict(e0=e0, e1=e1, D=(yh0 != yh1).astype(int), help=((e0 == 1) & (e1 == 0)).astype(int),
                harm=((e0 == 0) & (e1 == 1)).astype(int))


class Factorized:
    """SelectNorm benefit estimator: B(z) = pi(z) (2 rho(z) - 1)."""

    def __init__(self, kind='lr', seed=0):
        self.kind, self.seed = kind, seed

    def fit(self, Z, D, y_win, Z_unlab=None, D_unlab=None):
        """Z, D: labelled source split; y_win[i] = 1 if the normalized view is right (used where D=1).
        Z_unlab, D_unlab: optional unlabeled target sample (D is label-free) for pi only."""
        self._Z, self._D = Z, D
        self.rho = fit_proba(self.kind, Z[D == 1], y_win[D == 1], seed=self.seed)
        if Z_unlab is None:
            self.pi = fit_proba(self.kind, Z, D, seed=self.seed)
        else:
            # equal total weight for source and target samples
            Zp = np.vstack([Z, Z_unlab])
            Dp = np.concatenate([D, D_unlab])
            w = np.concatenate([np.full(len(Z), 0.5 / len(Z)), np.full(len(Z_unlab), 0.5 / len(Z_unlab))]) * len(Zp)
            self.pi = fit_proba(self.kind, Zp, Dp, w, seed=self.seed)
        return self

    def parts(self, Z):
        return self.pi(Z), self.rho(Z)

    def score(self, Z):
        pi, rho = self.parts(Z)
        return pi * (2 * rho - 1)


class DirectGain:
    """Post-hoc gain estimation (deferral-rule style): B(z) = P(help|z) - P(harm|z), fitted directly."""

    def __init__(self, kind='lr', seed=0):
        self.kind, self.seed = kind, seed

    def fit(self, Z, help_, harm):
        self.ph = fit_proba(self.kind, Z, help_, seed=self.seed)
        self.pm = fit_proba(self.kind, Z, harm, seed=self.seed)
        return self

    def recalibrated(self, Z_lab, help_lab, harm_lab):
        """Same k-label budget as SelectNorm-adapt: intercept shifts of both heads."""
        bh = fit_shift(self.ph(Z_lab), help_lab) if len(help_lab) else 0.0
        bm = fit_shift(self.pm(Z_lab), harm_lab) if len(harm_lab) else 0.0
        ph, pm = self.ph, self.pm
        sig = lambda v: 1 / (1 + np.exp(-v))
        return lambda Z: sig(logit(ph(Z)) + bh) - sig(logit(pm(Z)) + bm)

    def score(self, Z):
        return self.ph(Z) - self.pm(Z)


class AbsoluteLoss:
    """Per-view loss prediction (learning-loss style): B(z) = P(e0=1|z) - P(e1=1|z)."""

    def __init__(self, kind='lr', seed=0):
        self.kind, self.seed = kind, seed

    def fit(self, Z, e0, e1):
        self.p0 = fit_proba(self.kind, Z, e0, seed=self.seed)
        self.p1 = fit_proba(self.kind, Z, e1, seed=self.seed)
        return self

    def score(self, Z):
        return self.p0(Z) - self.p1(Z)


def tune_threshold(score, p0, p1, y, lam=0.0, rel_cost=1.0, fixed=None):
    """Threshold on a dev split maximizing accuracy - lam * rel_cost * selection rate.
    With fixed set, return it unchanged (theory threshold)."""
    if fixed is not None:
        return fixed
    cand = np.unique(np.concatenate([np.quantile(score, np.linspace(0, 1, 101)), [np.inf, -np.inf]]))
    o = outcomes(p0, p1, y)
    best = None
    for th in cand:
        g = score > th
        acc = 1 - np.mean(np.where(g, o['e1'], o['e0']))
        J = acc - lam * rel_cost * g.mean()
        if best is None or J > best[0] + 1e-12:
            best = (J, th)
    return best[1]


def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def fit_shift(base_prob, t, prior_var=1.0):
    """MAP intercept shift b for P(t=1) = sigmoid(logit(base_prob) + b), Gaussian prior N(0, prior_var).
    Used to recalibrate a source estimator with a handful of target labels."""
    from scipy.optimize import minimize_scalar
    z = logit(base_prob)
    t = np.asarray(t, float)

    def nll(b):
        q = 1 / (1 + np.exp(-(z + b)))
        q = np.clip(q, 1e-7, 1 - 1e-7)
        return -np.sum(t * np.log(q) + (1 - t) * np.log(1 - q)) + b * b / (2 * prior_var)
    return minimize_scalar(nll, bounds=(-10, 10), method='bounded').x


class FactorizedAdapted:
    """SelectNorm with target adaptation: pi re-estimated on unlabeled target text (label-free);
    rho recalibrated by an intercept shift fitted on k labelled target *disagreements*,
    the only examples whose labels carry information about the benefit of normalizing."""

    def __init__(self, base, Z_unlab, D_unlab, Z_lab, win_lab, kind='lr', seed=0):
        self.base = base
        Zs, Ds = base._Z, base._D
        self.fa = Factorized(kind, seed)
        self.fa.rho = base.rho
        Zp = np.vstack([Zs, Z_unlab])
        Dp = np.concatenate([Ds, D_unlab])
        w = np.concatenate([np.full(len(Zs), 0.5 / len(Zs)), np.full(len(Z_unlab), 0.5 / len(Z_unlab))]) * len(Zp)
        self.fa.pi = fit_proba(kind, Zp, Dp, w, seed=seed)
        self.b = fit_shift(base.rho(Z_lab), win_lab) if len(win_lab) else 0.0

    def parts(self, Z):
        pi = self.fa.pi(Z)
        rho = 1 / (1 + np.exp(-(logit(self.base.rho(Z)) + self.b)))
        return pi, rho

    def score(self, Z):
        pi, rho = self.parts(Z)
        return pi * (2 * rho - 1)
