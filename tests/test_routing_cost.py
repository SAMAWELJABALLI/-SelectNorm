"""Branch selection and cost accounting (sunk vs avoidable)."""
import numpy as np
from src.routing.run import cost, cost_kind, metrics, fold_of


def d(n=4):
    return dict(c0=np.full(n, 1.0), ct=np.full(n, 0.1), c1=np.full(n, 1.2),
                y=np.array([1, 0, 1, 0]), p0=np.array([.9, .8, .2, .3]), p1=np.array([.6, .1, .9, .7]))


def test_router_pays_sunk_cost_and_second_pass_only_when_routing():
    x = d()
    assert np.isclose(cost(x, np.zeros(4, bool)), 1.1)            # f(x) + T(x); f(T(x)) not evaluated
    assert np.isclose(cost(x, np.ones(4, bool)), 2.3)             # + f(T(x)) on every input
    assert np.isclose(cost(x, np.array([1, 0, 0, 0], bool)), 1.1 + 1.2 / 4)


def test_baseline_cost_kinds():
    x = d()
    g0 = np.zeros(4, bool)
    assert cost(x, g0, 'original') == 1.0
    assert np.isclose(cost(x, g0, 'always'), 1.3)
    assert np.isclose(cost(x, g0, 'ensemble'), 2.3)
    assert cost(x, g0, 'conf') == 1.0                               # decides before normalising
    assert cost_kind('B2_random#3') == 'blind' and cost_kind('B5_selectnorm_adapt') == 'router'
    assert cost_kind('R_two_view_ensemble') == 'ensemble' and cost_kind('B0_original') == 'original'


def test_branch_selection_uses_the_chosen_view():
    x = d()
    g = np.array([0, 0, 1, 1], bool)
    m, yhat = metrics(x, g)
    assert yhat.tolist() == [1, 1, 1, 1]
    assert m['sel_rate'] == 50.0
    m0, y0 = metrics(x, np.zeros(4, bool), 'original')
    assert y0.tolist() == [1, 1, 0, 0]


def test_folds_group_by_source_id():
    src = ['a', 'b', 'a', 'c', 'b']
    f = fold_of(src)
    assert f[0] == f[2] and f[1] == f[4] and set(f) <= {0, 1}
    assert np.array_equal(f, fold_of(src))
