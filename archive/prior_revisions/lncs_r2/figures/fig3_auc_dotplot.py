"""Figure 3: AUC of the disagreement and advantage estimators, per encoder and test set.

Reads figures/mechanism_table.csv (archived copy of paper/tables/mechanism_table.csv) and writes
figures/fig3_auc.csv (the plotted values), figures/fig3_auc_dotplot.pdf (vector) and .png (control image).
Before plotting, every point and interval, rounded to two decimals, is checked against Table 3
(tables/mechanism.tex) and Table S4 (tables/mechanism_ci.tex); the script stops on any mismatch.
The three series of a row are drawn at fixed vertical offsets within the row (categorical position only);
the horizontal (AUC) positions are the archived values.

    cd paper_lncs_r2 && python3 figures/fig3_auc_dotplot.py
"""
import ast, os, re
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
TAB = os.path.join(HERE, '..', 'tables')
plt.rcParams.update({'font.family': 'serif', 'font.serif': ['TeX Gyre Termes', 'Nimbus Roman', 'Times New Roman', 'DejaVu Serif'],
                     'mathtext.fontset': 'stix', 'font.size': 8, 'axes.titlesize': 8, 'axes.labelsize': 8,
                     'xtick.labelsize': 7, 'ytick.labelsize': 7.5, 'legend.fontsize': 7, 'axes.linewidth': 0.6,
                     'axes.spines.top': False, 'axes.spines.right': False, 'pdf.fonttype': 42,
                     'xtick.major.width': 0.6, 'ytick.major.width': 0.0})

ENCS = ['mE5', 'XLM-R', 'LaBSE', 'MARBERTv2']
SETS = [('S3_tsac_lat', '$S_3$'), ('S4_tunizi', '$S_4$'), ('S5_narabizi', '$S_5$'), ('S6_myc_lat', '$S_6$')]
# column, legend label, marker, face, edge, vertical offset within the row
SERIES = [('auc_pi_tgt', r'$\hat\pi$: disagreement (target, no labels)', 'o', '0.0', '0.0', -0.22),
          ('auc_rho_src', r'$\hat\rho$: winning view (source labels)', 's', 'white', '0.0', 0.0),
          ('auc_rho_tgt_ceiling', r'$\hat\rho$: target-label CV reference', '^', '0.55', '0.55', 0.22)]
TEXCOL = {'auc_pi_tgt': (3, 2), 'auc_rho_src': (5, 3), 'auc_rho_tgt_ceiling': (6, 4)}  # (Table 3 column, Table S4 column)


def tex_rows(path):
    rows, enc = [], None
    for line in open(path):
        if '&' not in line or 'Enc.' in line or 'multicolumn' in line:
            continue
        cells = [c.strip() for c in line.replace('\\\\', '').split('&')]
        enc = cells[0] or enc
        rows.append((enc, cells[1].strip('$').replace('_', ''), cells))
    return rows


def check(d):
    t3, s4 = tex_rows(os.path.join(TAB, 'mechanism.tex')), tex_rows(os.path.join(TAB, 'mechanism_ci.tex'))
    n = 0
    for (enc, s, c3), (enc2, s2, c4) in zip(t3, s4):
        assert (enc, s) == (enc2, s2)
        r = d[(d.encoder == enc) & (d.set.str.startswith(s))].iloc[0]
        for col, (i3, i4) in TEXCOL.items():
            assert f'{r[col]:.2f}' == re.sub(r'\$.*\$', '', c3[i3]), (enc, s, col, r[col], c3[i3])
            lo, hi = r[col + '_ci']
            assert f'[{lo:.2f}, {hi:.2f}]' == c4[i4], (enc, s, col, lo, hi, c4[i4])
            n += 1
    return n


def main():
    d = pd.read_csv(os.path.join(HERE, 'mechanism_table.csv'))
    for col, *_ in SERIES:
        d[col + '_ci'] = d[col + '_ci'].apply(ast.literal_eval)
    print(f'{check(d)} values and intervals match Table 3 and Table S4')
    out = []
    fig, axes = plt.subplots(1, 4, figsize=(4.8, 1.8), sharey=True, sharex=True)
    for ax, enc in zip(axes, ENCS):
        ax.axvline(0.5, color='0.35', lw=0.7, ls=(0, (3, 2)), zorder=1)
        for i, (s, lab) in enumerate(SETS):
            r = d[(d.encoder == enc) & (d.set == s)].iloc[0]
            if i % 2 == 0:
                ax.axhspan(i - 0.5, i + 0.5, color='0.95', lw=0, zorder=0)
            for col, slab, mk, fc, ec, off in SERIES:
                lo, hi = r[col + '_ci']
                y = i + off
                ax.plot([lo, hi], [y, y], color=ec, lw=0.9, solid_capstyle='butt', zorder=2)
                ax.plot(r[col], y, marker=mk, ms=3.8, mfc=fc, mec=ec, mew=0.8, ls='none', zorder=3)
                out.append(dict(encoder=enc, set=s, estimator=col, auc=round(r[col], 4), ci_lo=round(lo, 4), ci_hi=round(hi, 4)))
        ax.set_title(enc, pad=2)
        ax.set_xlabel('AUC', labelpad=1)
        ax.set_xlim(0.33, 0.80)
        ax.set_xticks([0.4, 0.5, 0.6, 0.7, 0.8])
        ax.set_xticklabels(['.4', '.5', '.6', '.7', '.8'])
        ax.set_ylim(len(SETS) - 0.5, -0.5)
        ax.grid(axis='x', color='0.88', lw=0.4, zorder=0)
        ax.spines['left'].set_visible(False)
    axes[0].set_yticks(range(len(SETS)))
    axes[0].set_yticklabels([l for _, l in SETS])
    handles = [Line2D([], [], color=ec, lw=0.9, marker=mk, ms=4, mfc=fc, mec=ec, label=slab) for _, slab, mk, fc, ec, _ in SERIES]
    fig.legend(handles=handles, loc='upper center', ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.0),
               handlelength=1.6, columnspacing=1.0, handletextpad=0.4)
    fig.tight_layout(w_pad=0.5, rect=(0, 0, 1, 0.92))
    fig.savefig(os.path.join(HERE, 'fig3_auc_dotplot.pdf'), bbox_inches='tight', pad_inches=0.02)
    fig.savefig(os.path.join(HERE, 'fig3_auc_dotplot.png'), dpi=300, bbox_inches='tight', pad_inches=0.02)
    pd.DataFrame(out).to_csv(os.path.join(HERE, 'fig3_auc.csv'), index=False)


if __name__ == '__main__':
    main()
