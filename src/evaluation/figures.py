"""Vector figures from the run logs (no number is typed by hand).

python -m src.evaluation.figures --backends enc_intfloat__multilingual-e5-base,... --main enc_...
Writes paper/figures/{pareto,mechanism,fewlabel}.pdf and the plotted values as .csv next to them.
Okabe-Ito hues in fixed order, with markers as secondary encoding (grayscale readable).
"""
import argparse, os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.routing.views import ROOT

C = ['#0072B2', '#E69F00', '#009E73', '#CC79A7', '#56B4E9', '#D55E00']
SETS = {'S3_tsac_lat': '$S_3$ TSAC-Lat', 'S4_tunizi': '$S_4$ TUNIZI', 'S5_narabizi': '$S_5$ NArabizi (Alg.)', 'S6_myc_lat': '$S_6$ MYC (Mor.)'}
ENC = {'enc_intfloat__multilingual-e5-base': 'mE5', 'enc_FacebookAI__xlm-roberta-base': 'XLM-R',
       'enc_sentence-transformers__LaBSE': 'LaBSE', 'enc_UBC-NLP__MARBERTv2': 'MARBERTv2', 'charlr': 'char n-gram'}
plt.rcParams.update({'font.family': 'serif', 'font.serif': ['TeX Gyre Termes', 'Times New Roman', 'DejaVu Serif'],
                     'font.size': 8, 'axes.labelsize': 8, 'axes.titlesize': 8, 'legend.fontsize': 7, 'xtick.labelsize': 7,
                     'ytick.labelsize': 7, 'axes.spines.top': False, 'axes.spines.right': False, 'axes.linewidth': 0.6,
                     'pdf.fonttype': 42, 'axes.grid': True, 'grid.color': '#e6e6e6', 'grid.linewidth': 0.5})


def load(btag, tag):
    return pd.read_json(os.path.join(ROOT, 'results', 'metrics', btag, f'runs_{tag}.jsonl'), lines=True)


def pareto(btag, out, lncs=False):
    d = load(btag, 'main')
    d = d[d.system != 'DIAG']
    fig, axes = plt.subplots(1, 4, figsize=(4.8, 1.75)) if lncs else plt.subplots(1, 4, figsize=(7.0, 1.9))
    axes = np.ravel(axes)
    curves = [('B3_conf', 'B3 confidence', C[1], 's'), ('B4_direct_gain', 'B4 direct gain', C[3], '^'),
              ('B5_selectnorm_adapt', 'SelectNorm (tuned)', C[0], 'o'), ('B5_selectnorm_adapt_theory', 'SelectNorm (Bayes thr.)', C[4], 'v')]
    rows = []
    for ax, (s, title) in zip(axes, SETS.items()):
        x = d[d.set == s]
        for sysname, lab, col, mk in curves:
            g = x[x.system == sysname].groupby('lam')[['rel_cost', 'macro_f1']].agg(['mean', 'std'])
            ax.errorbar(g[('rel_cost', 'mean')], g[('macro_f1', 'mean')], yerr=g[('macro_f1', 'std')], color=col, marker=mk,
                        ms=3.5, lw=1.2, capsize=1.5, elinewidth=0.6, label=lab)
            for lam, r in g.iterrows():
                rows.append(dict(set=s, system=sysname, lam=lam, cost=r[('rel_cost', 'mean')], f1=r[('macro_f1', 'mean')], f1_sd=r[('macro_f1', 'std')]))
        for sysname, lab, col, mk in [('B0_original', 'B0 original', '#555555', 'X'), ('B1_always', 'B1 always', C[2], 'D'),
                                      ('R_two_view_ensemble', 'R two-view', C[5], 'P')]:
            r = x[x.system == sysname][['rel_cost', 'macro_f1']].mean()
            ax.plot(r.rel_cost, r.macro_f1, marker=mk, color=col, ls='none', ms=4.5, label=lab)
            rows.append(dict(set=s, system=sysname, lam=None, cost=r.rel_cost, f1=r.macro_f1, f1_sd=None))
        ax.set_title(title.replace(' (Alg.)', '').replace(' (Mor.)', '') if lncs else title, fontsize=7 if lncs else None)
        if not lncs:
            ax.set_xlabel('estimated cost (one pass on x = 1)')
        else:
            ax.tick_params(labelsize=7)
            ax.set_xticks([1.0, 1.5, 2.0])
    axes[0].set_ylabel('macro-F1')
    if lncs:
        fig.supxlabel('estimated cost (one pass of f on x = 1)', fontsize=7, y=0.13)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc='upper center', ncol=4, frameon=False, bbox_to_anchor=(0.5, 0.09 if lncs else 0.02), fontsize=7 if lncs else None)
    fig.tight_layout()
    fig.savefig(os.path.join(out, 'pareto_lncs.pdf' if lncs else 'pareto.pdf'), bbox_inches='tight')
    pd.DataFrame(rows).to_csv(os.path.join(out, 'pareto.csv'), index=False)


def mechanism(btags, out):
    rows = []
    for b in btags:
        d = load(b, 'main')
        g = d[d.system == 'DIAG'].groupby('set')[['disagree_rate', 'pi_src_mean', 'win_rate_given_D', 'rho_src_mean_on_D']].mean()
        for s, r in g.iterrows():
            rows.append(dict(encoder=ENC.get(b, b), set=s, **r.to_dict()))
    t = pd.DataFrame(rows)
    t.to_csv(os.path.join(out, 'mechanism.csv'), index=False)
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 1.9), sharey=False)
    xs = np.arange(len(SETS))
    for i, (b, col, mk) in enumerate(zip(btags, C, 'osD^')):
        e = t[t.encoder == ENC.get(b, b)].set_index('set').reindex(list(SETS))
        axes[0].plot(xs, e.disagree_rate, marker=mk, color=col, lw=1.2, ms=4, label=ENC.get(b, b))
        axes[0].plot(xs, e.pi_src_mean, marker=mk, color=col, lw=0.8, ls=':', ms=3, mfc='white')
        axes[1].plot(xs, e.win_rate_given_D, marker=mk, color=col, lw=1.2, ms=4, label=ENC.get(b, b))
        axes[1].plot(xs, e.rho_src_mean_on_D, marker=mk, color=col, lw=0.8, ls=':', ms=3, mfc='white')
    axes[1].axhline(0.5, color='#888888', lw=0.6)
    axes[1].text(len(SETS) - 1, 0.5, ' normalizing\n stops paying', fontsize=6, va='center', color='#555555')
    for ax, yl in zip(axes, [r'disagreement rate $\pi$', r'win rate of $T(x)$ given disagreement $\rho$']):
        ax.set_xticks(xs, [v.split(' ')[0] for v in SETS.values()])
        ax.set_ylabel(yl)
    axes[0].legend(frameon=False, ncol=2, loc='lower left')
    fig.text(0.5, -0.02, 'solid: observed on the test set (labels used for analysis only); dotted, open markers: predicted from source training', ha='center', fontsize=6.5)
    fig.tight_layout()
    fig.savefig(os.path.join(out, 'mechanism.pdf'), bbox_inches='tight')


def fewlabel(btag, out, lncs=False):
    d = load(btag, 'adapt')
    base = load(btag, 'main')
    sysmap = [('SN_targeted', 'SelectNorm, labels on disagreements', C[0], 'o'), ('SN_random', 'SelectNorm, random labels', C[4], 'v'),
              ('DG_random', 'B4 direct gain, random labels', C[3], '^'), ('CONF_random', 'B3 confidence, random labels', C[1], 's'),
              ('SET_random', 'set-level B0/B1 choice', C[2], 'D')]
    fig, axes = plt.subplots(2, 2, figsize=(4.8, 3.9)) if lncs else plt.subplots(1, 4, figsize=(7.0, 1.9))
    axes = np.ravel(axes)
    rows = []
    for ax, (s, title) in zip(axes, SETS.items()):
        x = d[d.set == s]
        for k, lab, col, mk in sysmap:
            g = x[x.system == k].groupby('k').macro_f1.agg(['mean', 'std'])
            ax.errorbar(g.index, g['mean'], yerr=g['std'], color=col, marker=mk, ms=3, lw=1.1, capsize=1.2, elinewidth=0.5, label=lab)
            for kk, r in g.iterrows():
                rows.append(dict(set=s, system=k, k=kk, f1=r['mean'], sd=r['std']))
        o = base[(base.set == s) & (base.system == 'B6_oracle')].macro_f1.mean()
        b0 = base[(base.set == s) & (base.system == 'B0_original')].macro_f1.mean()
        b1 = base[(base.set == s) & (base.system == 'B1_always')].macro_f1.mean()
        ax.axhline(b0, color='#555555', lw=0.7, ls='--')
        ax.axhline(b1, color=C[2], lw=0.7, ls=':')
        ax.set_xscale('log', base=2)
        ax.set_xticks([8, 16, 32, 64, 128], ['8', '16', '32', '64', '128'])
        ax.minorticks_off()
        ax.set_title(title)
        ax.set_xlabel('target labels $k$')
    for ax in (axes[::2] if lncs else axes[:1]):
        ax.set_ylabel('macro-F1')
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc='upper center', ncol=2 if lncs else 3, frameon=False, bbox_to_anchor=(0.5, 0.02))
    fig.tight_layout()
    fig.savefig(os.path.join(out, 'fewlabel_lncs.pdf' if lncs else 'fewlabel.pdf'), bbox_inches='tight')
    pd.DataFrame(rows).to_csv(os.path.join(out, 'fewlabel.csv'), index=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--backends', required=True)
    ap.add_argument('--main', required=True)
    ap.add_argument('--out', default=os.path.join(ROOT, 'paper', 'figures'))
    ap.add_argument('--lncs', action='store_true', help='2x2 layouts for the LNCS text width (pareto_lncs.pdf, fewlabel_lncs.pdf)')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    pareto(a.main, a.out, a.lncs)
    if not a.lncs:
        mechanism(a.backends.split(','), a.out)
    if os.path.exists(os.path.join(ROOT, 'results', 'metrics', a.main, 'runs_adapt.jsonl')):
        fewlabel(a.main, a.out, a.lncs)


if __name__ == '__main__':
    main()
