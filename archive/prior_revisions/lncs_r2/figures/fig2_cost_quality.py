"""Figure 2: macro-F1 against estimated inference cost (mE5), one panel per test set.

Reads figures/pareto.csv (archived values written by src/evaluation/figures.py from the run logs) and writes
figures/fig2_cost_quality.pdf (vector, used by main.tex) and figures/fig2_cost_quality.png (control image).
No value is modified: every marker is drawn at its archived (cost, macro-F1); B0 is drawn at the lower edge of a
panel, with its value printed, only when it lies below the panel's range (stated in the caption).

    cd paper_lncs_r2 && python3 figures/fig2_cost_quality.py
"""
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
plt.rcParams.update({'font.family': 'serif', 'font.serif': ['TeX Gyre Termes', 'Nimbus Roman', 'Times New Roman', 'DejaVu Serif'],
                     'mathtext.fontset': 'stix', 'font.size': 8, 'axes.titlesize': 8, 'axes.labelsize': 8,
                     'xtick.labelsize': 7, 'ytick.labelsize': 7, 'legend.fontsize': 7, 'axes.linewidth': 0.6,
                     'axes.spines.top': False, 'axes.spines.right': False, 'pdf.fonttype': 42,
                     'xtick.major.width': 0.6, 'ytick.major.width': 0.6})

SETS = [('S3_tsac_lat', '$S_3$ TSAC-Lat (Tunisian)'), ('S4_tunizi', '$S_4$ TUNIZI (Tunisian)'),
        ('S5_narabizi', '$S_5$ NArabizi (Algerian)'), ('S6_myc_lat', '$S_6$ MYC-Lat (Moroccan)')]
# system, label, grey level, line style, marker, filled, line width, z-order (primary systems drawn last)
CURVES = [('B3_conf', 'B3 confidence', '0.62', (0, (1, 1.2)), 's', False, 0.9, 2),
          ('B5_selectnorm_adapt_theory', r'SelectNorm-adapt, Bayes $\lambda\bar c$', '0.45', (0, (4, 1.5, 1, 1.5)), 'v', False, 0.9, 3),
          ('B4_direct_gain', 'B4 direct gain', '0.30', (0, (4, 2)), '^', True, 1.2, 4),
          ('B5_selectnorm_adapt', r'SelectNorm-adapt, tuned $t_\lambda$', '0.0', '-', 'o', True, 1.5, 5)]
# offsets (points) of the lambda=0 and lambda=0.2 labels of SelectNorm-adapt, chosen to avoid overlaps
LAMLAB = {'S3_tsac_lat': [(-14, 11), (-24, 6)], 'S4_tunizi': [(-12, 12), (-6, -14)],
          'S5_narabizi': [(-20, -13), (16, -6)], 'S6_myc_lat': [(-10, -18), (-4, -17)]}
POINTS = [('B0_original', 'B0 original', 'X', '0.0', '0.0'), ('B1_always', 'B1 always', 'D', 'white', '0.0'),
          ('R_two_view_ensemble', 'R ensemble', 'P', '0.5', '0.0')]


def main():
    d = pd.read_csv(os.path.join(HERE, 'pareto.csv'))
    fig, axes = plt.subplots(2, 2, figsize=(4.8, 2.68), sharex=True)
    for ax, (s, title) in zip(axes.ravel(), SETS):
        x = d[d.set == s]
        pts = {r.system: r for r in x[x.lam.isna()].itertuples()}
        cur = x[x.lam.notna()]
        lo = min(cur.f1.min() - cur.f1_sd.max(), pts['B1_always'].f1, pts['R_two_view_ensemble'].f1)
        hi = max(cur.f1.max() + cur.f1_sd.max(), pts['B1_always'].f1, pts['R_two_view_ensemble'].f1)
        b0 = pts['B0_original'].f1
        if b0 >= lo - 0.5:
            lo = min(lo, b0)
        pad = 0.08 * (hi - lo)
        ylo, yhi = lo - pad, hi + pad
        for xv, lab in [(1.0, 'one pass'), (2.0, 'two passes')]:
            ax.axvline(xv, color='0.8', lw=0.6, zorder=0)
        for sysname, lab, col, ls, mk, filled, lw, z in CURVES:
            g = cur[cur.system == sysname].sort_values('lam')
            ax.plot(g.cost, g.f1, ls=ls, color=col, lw=lw, zorder=z)
            ax.errorbar(g.cost, g.f1, yerr=g.f1_sd, fmt='none', ecolor=col, elinewidth=0.6, capsize=1.6, capthick=0.6, zorder=z)
            ax.plot(g.cost, g.f1, ls='none', marker=mk, ms=4.2 if filled else 3.8, mec=col, mew=0.8,
                    mfc=col if filled else 'white', zorder=z + 0.5)
            if sysname == 'B5_selectnorm_adapt':
                for (_, r), off in zip([g.iloc[[0]].iterrows().__next__(), g.iloc[[-1]].iterrows().__next__()], LAMLAB[s]):
                    ax.annotate(rf'$\lambda{{=}}{r.lam:g}$', (r.cost, r.f1), xytext=off, textcoords='offset points', fontsize=6.5,
                                ha='center', va='center', zorder=8,
                                arrowprops=dict(arrowstyle='-', color='0.0', lw=0.5, shrinkA=0, shrinkB=2.5))
        for sysname, lab, mk, fc, ec in POINTS:
            r = pts[sysname]
            if sysname == 'B0_original' and r.f1 < ylo:
                ax.plot(r.cost, ylo, marker='v', ms=5, color='0.0', clip_on=False, zorder=6)
                ax.annotate(f'B0 {r.f1:.1f}', (r.cost, ylo), xytext=(5, 2), textcoords='offset points', fontsize=6.5, va='bottom')
                continue
            ax.plot(r.cost, r.f1, ls='none', marker=mk, ms=5.5, mfc=fc, mec=ec, mew=0.8, zorder=6)
        ax.set_ylim(ylo, yhi)
        ax.set_xlim(0.9, 2.1)
        ax.set_xticks([1.0, 1.25, 1.5, 1.75, 2.0])
        ax.set_title(title, pad=3)
        ax.grid(axis='y', color='0.9', lw=0.5)
    for ax in axes[:, 0]:
        ax.set_ylabel('macro-F1')
    for ax in axes[1]:
        ax.set_xlabel(r'estimated cost (passes of $f$ on $x$)')
    handles = [Line2D([], [], color=c, ls=ls, lw=lw, marker=mk, ms=4, mec=c, mfc=c if f else 'white', label=l)
               for _, l, c, ls, mk, f, lw, _ in CURVES[::-1]]
    handles += [Line2D([], [], ls='none', marker=mk, ms=5, mfc=fc, mec=ec, label=l) for _, l, mk, fc, ec in POINTS]
    fig.legend(handles=handles, loc='upper center', ncol=4, frameon=False, bbox_to_anchor=(0.5, 1.0),
               handlelength=2.4, columnspacing=0.9, handletextpad=0.4, labelspacing=0.3)
    fig.tight_layout(h_pad=0.6, w_pad=0.8, rect=(0, 0, 1, 0.91))
    fig.savefig(os.path.join(HERE, 'fig2_cost_quality.pdf'), bbox_inches='tight', pad_inches=0.02)
    fig.savefig(os.path.join(HERE, 'fig2_cost_quality.png'), dpi=300, bbox_inches='tight', pad_inches=0.02)


if __name__ == '__main__':
    main()
