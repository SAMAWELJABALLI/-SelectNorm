"""LaTeX tables generated from the run logs (no number typed by hand).

python -m src.evaluation.tables --main enc_intfloat__multilingual-e5-base --backends a,b,c,d
Writes paper/tables/*.tex.
"""
import argparse, glob, json, os, sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.routing.views import ROOT, load_set

SETS = ['S3_tsac_lat', 'S4_tunizi', 'S5_narabizi', 'S6_myc_lat']
SHORT = {'S3_tsac_lat': '$S_3$', 'S4_tunizi': '$S_4$', 'S5_narabizi': '$S_5$', 'S6_myc_lat': '$S_6$'}
ENC = {'enc_intfloat__multilingual-e5-base': 'mE5', 'enc_FacebookAI__xlm-roberta-base': 'XLM-R',
       'enc_sentence-transformers__LaBSE': 'LaBSE', 'enc_UBC-NLP__MARBERTv2': 'MARBERTv2'}
ENC.update({k + '+syn': v + '+syn' for k, v in list(ENC.items())})
MAIN_SYS = [('B0_original', 'B0 original'), ('B1_always', 'B1 always normalize'), ('B2_random', 'B2 random, matched rate'),
            ('B3_conf', 'B3 confidence threshold'), ('B4_direct_gain', 'B4 direct gain'), ('B4b_abs_loss', 'B4b per-view loss'),
            ('B5_selectnorm_src', 'SelectNorm-src'), ('B5_selectnorm_adapt', 'SelectNorm-adapt'),
            ('B5_selectnorm_adapt_theory', '\\quad Bayes threshold $\\lambda\\bar c$'),
            ('R_two_view_ensemble', 'R two-view ensemble$^\\dagger$'), ('B6_oracle', 'B6 oracle$^\\ddagger$')]


def load(b, tag):
    p = os.path.join(ROOT, 'results', 'metrics', b, f'runs_{tag}.jsonl')
    if not os.path.exists(p):
        return None
    d = pd.read_json(p, lines=True)
    d['system'] = d.system.str.replace(r'#\d+$', '', regex=True)
    return d


def at_lam0(d):
    return d[(d.system != 'DIAG') & (d.lam.isna() | (d.lam == 0))]


def stats(b, tag='main'):
    p = os.path.join(ROOT, 'results', 'statistics', b, f'{tag}.json')
    return json.load(open(p)) if os.path.exists(p) else []


def main_table(backends, out, fname='main.tex', per_panel=2):
    """Macro-F1 (mean over seeds), stacked panels of `per_panel` encoders x 4 sets.
    Bold = best deployable system per column; underline = best single view (B0 or B1).
    Markers compare each baseline with SelectNorm-adapt (Holm-corrected paired bootstrap)."""
    res = {}
    for b in backends:
        d = at_lam0(load(b, 'main'))
        g = d.groupby(['system', 'set']).macro_f1.mean()
        for s in SETS:
            for k, _ in MAIN_SYS:
                res[(k, b, s)] = g.get((k, s), np.nan)
    st = {b: {(r['set'], r['a'], r['b']): r for r in stats(b)} for b in backends}
    deploy = [k for k, _ in MAIN_SYS if k not in ('B6_oracle', 'R_two_view_ensemble')]
    lines = ['\\begin{tabular}{@{}l' + 'r' * (4 * per_panel) + '@{}}\\toprule']
    for pi in range(0, len(backends), per_panel):
        panel = backends[pi:pi + per_panel]
        cols = [(b, s) for b in panel for s in SETS]
        if pi:
            lines.append('\\midrule[\\heavyrulewidth]')
        lines.append(' & ' + ' & '.join(f'\\multicolumn{{4}}{{c}}{{\\textbf{{{ENC.get(b, b)}}}}}' for b in panel) + '\\\\')
        lines.append(''.join(f'\\cmidrule(lr){{{2 + 4 * i}-{5 + 4 * i}}}' for i in range(len(panel))))
        lines.append(' & ' + ' & '.join(SHORT[s] for _, s in cols) + '\\\\\\midrule')
        for k, lab in MAIN_SYS:
            if k == 'R_two_view_ensemble':
                lines.append('\\addlinespace[2pt]')
            cells = []
            for b, s in cols:
                v = res[(k, b, s)]
                best = max(res[(kk, b, s)] for kk in deploy)
                txt = f'{v:.1f}'
                if k in deploy and abs(v - best) < 1e-9:
                    txt = f'\\textbf{{{txt}}}'
                r = st[b].get((s, 'B5_selectnorm_adapt', k))
                if k != 'B5_selectnorm_adapt' and r is not None and r['p_holm'] < 0.05:
                    txt += '$^{' + ('\\triangledown' if r['diff'] > 0 else '\\blacktriangle') + '}$'
                cells.append(txt)
            row = lab + ' & ' + ' & '.join(cells) + '\\\\'
            if k == 'B5_selectnorm_adapt':
                row = '\\rowcolor{black!6}' + row
            lines.append(row)
    lines.append('\\bottomrule\\end{tabular}')
    open(os.path.join(out, fname), 'w').write('\n'.join(lines) + '\n')


def paired_table(backends, out):
    """Paired differences SelectNorm-adapt minus baseline (macro-F1 points) with 95% bootstrap intervals.
    *: Holm-corrected p < 0.05; dagger: interval inside the protocol's 1-point margin (post hoc equivalence reading)."""
    cmp = [('B1_always', 'B1'), ('B3_conf', 'B3'), ('B4_direct_gain', 'B4'), ('B5_selectnorm_src', 'SN-src')]
    lines = ['\\begin{tabular}{@{}ll' + 'r' * len(cmp) + '@{}}\\toprule',
             'Enc. & Set & ' + ' & '.join(f'vs.\\ {l}' for _, l in cmp) + '\\\\\\midrule']
    rows = []
    for b in backends:
        st = {(r['set'], r['b']): r for r in stats(b)}
        for i, s in enumerate(SETS):
            cells = []
            for k, _ in cmp:
                r = st[(s, k)]
                rows.append(dict(encoder=ENC.get(b, b), set=s, baseline=k, diff=r['diff'], lo=r['lo'], hi=r['hi'], p_holm=r['p_holm']))
                m = ('$^{*}$' if r['p_holm'] < 0.05 else '') + ('$^{\\dagger}$' if -1 < r['lo'] and r['hi'] < 1 else '')
                cells.append(f"{r['diff']:+.2f} \\scriptsize[{r['lo']:+.2f}, {r['hi']:+.2f}]{m}")
            lines.append(f"{ENC.get(b, b) if i == 0 else ''} & {SHORT[s]} & " + ' & '.join(cells) + '\\\\')
        if b != backends[-1]:
            lines.append('\\midrule')
    lines.append('\\bottomrule\\end{tabular}')
    pd.DataFrame(rows).to_csv(os.path.join(out, 'paired.csv'), index=False)
    open(os.path.join(out, 'paired.tex'), 'w').write('\n'.join(lines) + '\n')


def routing_table(b, out):
    """Selection, help/harm and cost for the main encoder, lambda = 0."""
    d = at_lam0(load(b, 'main'))
    diag = load(b, 'main')
    diag = diag[diag.system == 'DIAG'].groupby('set')[['help', 'harm', 'both_wrong']].mean()
    rows = [('B1_always', 'B1'), ('B3_conf', 'B3'), ('B4_direct_gain', 'B4'), ('B5_selectnorm_adapt', 'SN-adapt'), ('B6_oracle', 'Oracle')]
    x = {s: d[d.set == s].groupby('system')[['sel_rate', 'harm_rate', 'help_captured', 'rel_cost']].mean() for s in SETS}
    lines = ['\\begin{tabular}{@{}l' + 'rrrr' * len(SETS) + '@{}}\\toprule',
             ' & ' + ' & '.join(f"\\multicolumn{{4}}{{c}}{{{SHORT[s]} \\scriptsize(help {diag.loc[s,'help']:.0f}, harm {diag.loc[s,'harm']:.0f})}}" for s in SETS) + '\\\\' + ''.join(f'\\cmidrule(lr){{{2+4*i}-{5+4*i}}}' for i in range(len(SETS))),
             'System' + ' & Sel.\\,\\% & Harm & Capt.\\,\\% & Cost' * len(SETS) + '\\\\\\midrule']
    for k, lab in rows:
        cells = []
        for s in SETS:
            r = x[s].loc[k]
            cells += [f'{r.sel_rate:.1f}', f'{r.harm_rate:.1f}', f'{r.help_captured:.1f}', f'{r.rel_cost:.2f}']
        lines.append(lab + ' & ' + ' & '.join(cells) + '\\\\')
    lines.append('\\bottomrule\\end{tabular}')
    open(os.path.join(out, 'routing.tex'), 'w').write('\n'.join(lines) + '\n')


def ablation_table(b, out):
    rows = [('main', 'B5_selectnorm_adapt', 'SelectNorm-adapt (full)'),
            ('main', 'B5_selectnorm_src', '\\quad -- target re-estimation of $\\hat\\pi$'),
            ('main', 'B5_selectnorm_adapt_theory', '\\quad Bayes threshold instead of tuned'),
            ('main', 'A_rho_only', '\\quad $2\\hat\\rho-1$ only (no $\\hat\\pi$)'),
            ('main', 'A_pi_only', '\\quad $\\hat\\pi$ only, tuned (label-free ranking)'),
            ('abl_conf_only', 'B5_selectnorm_adapt', '\\quad confidence features only'),
            ('abl_no_conf', 'B5_selectnorm_adapt', '\\quad -- confidence features'),
            ('abl_no_script', 'B5_selectnorm_adapt', '\\quad -- script features'),
            ('abl_no_trel', 'B5_selectnorm_adapt', '\\quad -- normalizer reliability'),
            ('abl_emb', 'B5_selectnorm_adapt', '\\quad + embedding PCA'),
            ('abl_gbm', 'B5_selectnorm_adapt', '\\quad gradient boosting'),
            ('abl_lex', 'B5_selectnorm_adapt', '\\quad $T_{\\rm lex}$ (no safeguards)'),
            ('abl_lex', 'B1_always', '\\quad always $T_{\\rm lex}$'),
            ('abl_rule', 'B5_selectnorm_adapt', '\\quad $T_{\\rm rule}$'),
            ('abl_rule', 'B1_always', '\\quad always $T_{\\rm rule}$'),
            ('abl_cov', 'B5_selectnorm_adapt', '\\quad $T_{\\rm cov}$ (unknown tokens kept Latin)'),
            ('abl_cov', 'B1_always', '\\quad always $T_{\\rm cov}$')]
    lines = ['\\begin{tabular}{@{}l' + 'r' * len(SETS) + '@{}}\\toprule', 'Variant & ' + ' & '.join(SHORT[s] for s in SETS) + '\\\\\\midrule']
    for tag, k, lab in rows:
        d = load(b, tag)
        if d is None:
            continue
        g = at_lam0(d).groupby(['system', 'set']).macro_f1.agg(['mean', 'std'])
        cells = [f"{g.loc[(k, s), 'mean']:.1f}" if (k, s) in g.index else '--' for s in SETS]
        lines.append(lab + ' & ' + ' & '.join(cells) + '\\\\')
    lines.append('\\bottomrule\\end{tabular}')
    open(os.path.join(out, 'ablation.tex'), 'w').write('\n'.join(lines) + '\n')


def consistency(backends, out):
    """RQ4: agreement of final predictions on S5 (Latin) with f on its human Arabic-script pair."""
    rows = []
    for b in backends:
        P = np.load(os.path.join(ROOT, 'results', 'predictions', b, 'probs.npz'))
        y = np.array([r['label'] for r in load_set('S5_narabizi')])
        ar = (P['S5ar_narabizi_gold__orig'] > .5).astype(int)
        pdir = os.path.join(ROOT, 'results', 'predictions', b, 'routes')
        r = dict(encoder=ENC.get(b, b), f1_gold_ar=None)
        from sklearn.metrics import f1_score
        r['f1_gold_ar'] = 100 * f1_score(y, ar, average='macro')
        for k in ['B0_original', 'B1_always', 'B3_conf', 'B5_selectnorm_adapt']:
            files = sorted(glob.glob(os.path.join(pdir, f'main__{k}__S5_narabizi__s*.npz')))
            r[k] = 100 * np.mean([np.mean(np.load(f)['yhat'] == ar) for f in files])
        rows.append(r)
    t = pd.DataFrame(rows)
    t.to_csv(os.path.join(out, 'consistency.csv'), index=False)
    lines = ['\\begin{tabular}{@{}lrrrrr@{}}\\toprule', 'Encoder & F1($S_5^{\\textsc{ar}}$) & B0 & B1 & B3 & SN-adapt\\\\\\midrule']
    for _, r in t.iterrows():
        lines.append(f"{r.encoder} & {r.f1_gold_ar:.1f} & {r.B0_original:.1f} & {r.B1_always:.1f} & {r.B3_conf:.1f} & {r.B5_selectnorm_adapt:.1f}\\\\")
    lines.append('\\bottomrule\\end{tabular}')
    open(os.path.join(out, 'consistency.tex'), 'w').write('\n'.join(lines) + '\n')


def _ci(r, k):
    return r.get(k + '_ci', [np.nan, np.nan])


def mechanism_table(backends, out):
    """Four mechanisms per encoder x set (mechanism_cons.json; reference from the orig regime).
    Marks: AUC whose 95% interval contains 0.5 (open circle); gap or Delta whose interval excludes 0 (*)."""
    lines = ['\\begin{tabular}{@{}llrrrrrrrrrr@{}}\\toprule',
             ' & & \\multicolumn{2}{c}{(M1) disagreement} & \\multicolumn{4}{c}{(M2) direction} & \\multicolumn{2}{c}{(M3) benefit} & \\multicolumn{2}{c}{(M4) headroom}\\\\',
             '\\cmidrule(lr){3-4}\\cmidrule(lr){5-8}\\cmidrule(lr){9-10}\\cmidrule(lr){11-12}',
             'Enc. & Set & $P(D)$ & AUC$_\\pi$ & $P(W|D)$ & AUC$_\\rho$ & AUC$_\\rho^{\\rm tgt}$ & gap & $\\Delta_{\\rm src}$ & $\\Delta_{\\rm tgt}$ & oracle & vs.\\ ref.\\\\\\midrule']
    rows = []

    def auc(r, k):
        lo, hi = _ci(r, k)
        return f"{r[k]:.2f}" + ('$^\\circ$' if lo <= 0.5 <= hi else '')

    def sig(v, r, k, fmt):
        lo, hi = _ci(r, k)
        return fmt.format(v) + ('$^{*}$' if lo > 0 or hi < 0 else '')

    for b in backends:
        m = json.load(open(os.path.join(ROOT, 'results', 'statistics', b, 'mechanism_cons.json')))
        for i, s in enumerate(SETS):
            r = m[s]
            rows.append(dict(encoder=ENC.get(b, b), set=s, **{k: v for k, v in r.items() if not k.endswith('_ci')},
                             **{k: str(v) for k, v in r.items() if k.endswith('_ci')}))
            lines.append(f"{ENC.get(b, b) if i == 0 else ''} & {SHORT[s]} & {100*r['disagree']:.0f} & {auc(r, 'auc_pi_tgt')} & {100*r['win_rate']:.0f} & "
                         f"{auc(r, 'auc_rho_src')} & {auc(r, 'auc_rho_tgt_ceiling')} & {sig(100*r['rho_calib_gap'], r, 'rho_calib_gap', '{:+.0f}')} & "
                         f"{sig(r['f1_bayes_src']-r['f1_best_view'], r, 'd_bayes_src', '{:+.1f}')} & {sig(r['f1_bayes_tgt_ceiling']-r['f1_best_view'], r, 'd_bayes_tgt_ceiling', '{:+.1f}')} & "
                         f"{r['f1_oracle']-r['f1_best_view']:.1f} & {r.get('excess_headroom', float('nan')):+.1f}\\\\")
        if b != backends[-1]:
            lines.append('\\midrule')
    lines.append('\\bottomrule\\end{tabular}')
    pd.DataFrame(rows).to_csv(os.path.join(out, 'mechanism_table.csv'), index=False)
    open(os.path.join(out, 'mechanism.tex'), 'w').write('\n'.join(lines) + '\n')
    # interval table (appendix)
    lines = ['\\begin{tabular}{@{}llllllll@{}}\\toprule',
             'Enc. & Set & AUC$_\\pi$ & AUC$_\\rho$ & AUC$_\\rho^{\\rm tgt}$ & gap (pts) & $\\Delta_{\\rm src}$ & $\\Delta_{\\rm tgt}$\\\\\\midrule']
    for b in backends:
        m = json.load(open(os.path.join(ROOT, 'results', 'statistics', b, 'mechanism_cons.json')))
        for i, s in enumerate(SETS):
            r = m[s]
            f2 = lambda k: '[{:.2f}, {:.2f}]'.format(*_ci(r, k))
            f1 = lambda k, sc=1: '[{:+.1f}, {:+.1f}]'.format(*(sc * np.array(_ci(r, k))))
            lines.append(f"{ENC.get(b, b) if i == 0 else ''} & {SHORT[s]} & {f2('auc_pi_tgt')} & {f2('auc_rho_src')} & {f2('auc_rho_tgt_ceiling')} & "
                         f"{f1('rho_calib_gap', 100)} & {f1('d_bayes_src')} & {f1('d_bayes_tgt_ceiling')}\\\\")
        if b != backends[-1]:
            lines.append('\\midrule')
    lines.append('\\bottomrule\\end{tabular}')
    open(os.path.join(out, 'mechanism_ci.tex'), 'w').write('\n'.join(lines) + '\n')


def noise_table(out):
    p = os.path.join(ROOT, 'results', 'statistics', 'noise_sensitivity.json')
    if not os.path.exists(p):
        return
    d = pd.DataFrame(json.load(open(p)))
    d['enc'] = d.model.map(lambda m: ENC['enc_' + m.replace('/', '__')])
    d.to_csv(os.path.join(out, 'noise_sensitivity.csv'), index=False)
    var = ['boot', 'sub80', 'sub50', 'boot_Cx3', 'boot_C/3']
    lab = {'boot': 'bootstrap', 'sub80': '80\\% sub.', 'sub50': '50\\% sub.', 'boot_Cx3': 'boot., $3C$', 'boot_C/3': 'boot., $C/3$'}
    lines = ['\\begin{tabular}{@{}lr' + 'r' * len(var) + '@{}}\\toprule',
             ' & views & \\multicolumn{' + str(len(var)) + '}{c}{reference headroom (two resampled classifiers)}\\\\',
             '\\cmidrule(lr){3-' + str(2 + len(var)) + '}',
             'Enc. & Set & headroom & ' + ' & '.join(lab[v] for v in var) + '\\\\\\midrule']
    encs = list(dict.fromkeys(d.enc))
    rng = lambda v: f'{v.min():.1f}--{v.max():.1f}'
    lines[-1] = 'Enc. & headroom & ' + ' & '.join(lab[v] for v in var) + '\\\\\\midrule'
    for e in encs:
        x = d[d.enc == e]
        vh = x.groupby('set').view_headroom.first()
        lines.append(f"{e} & {rng(vh)} & " + ' & '.join(rng(x[x.variant == v].noise_headroom) for v in var) + '\\\\')
    lines.append('\\bottomrule\\end{tabular}')
    open(os.path.join(out, 'noise_sensitivity.tex'), 'w').write('\n'.join(lines) + '\n')


def taxonomy_table(backends, out):
    """Net effect of always normalizing (help - harm per 100 inputs) by input condition; range over encoders."""
    fr = []
    for b in backends:
        d = pd.read_csv(os.path.join(ROOT, 'results', 'statistics', b, 'taxonomy.csv'))
        d['enc'] = ENC.get(b, b)
        fr.append(d)
    d = pd.concat(fr)
    d['net'] = d.help - d.harm
    d.to_csv(os.path.join(out, 'taxonomy_all.csv'), index=False)
    lab = {'foreign': 'French/English $\\ge$30\\%', 'negation': 'negation rule applied', 'low_cov': 'lexicon coverage $<$50\\%', 'short': '$\\le$3 tokens'}
    lines = ['\\begin{tabular}{@{}l' + 'r' * len(SETS) + '@{}}\\toprule', 'Condition (share of $S_3$/$S_4$/$S_5$/$S_6$) & ' + ' & '.join(SHORT[s] for s in SETS) + '\\\\\\midrule']
    for c in ['foreign', 'negation', 'low_cov', 'short']:
        for val, pre in ((True, ''), (False, 'not ')):
            x = d[(d.condition == c) & (d.value == val)]
            share = '/'.join(f"{100 * x[(x.set == s)].n.iloc[0] / d[(d.condition == c) & (d.set == s)].groupby('value').n.first().sum():.0f}" for s in SETS)
            cells = []
            for s in SETS:
                v = x[x.set == s].net
                cells.append(f"{v.mean():+.1f} \\scriptsize[{v.min():+.0f},{v.max():+.0f}]")
            lines.append(f"{pre}{lab[c]} ({share}) & " + ' & '.join(cells) + '\\\\')
    lines.append('\\bottomrule\\end{tabular}')
    open(os.path.join(out, 'taxonomy.tex'), 'w').write('\n'.join(lines) + '\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--backends', required=True)
    ap.add_argument('--main', required=True)
    ap.add_argument('--out', default=os.path.join(ROOT, 'paper', 'tables'))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    bs = a.backends.split(',')
    main_table(bs, a.out)
    main_table([b + '+syn' for b in bs], a.out, 'main_syn.tex')
    mechanism_table(bs, a.out)
    paired_table(bs, a.out)
    taxonomy_table(bs, a.out)
    noise_table(a.out)
    routing_table(a.main, a.out)
    ablation_table(a.main, a.out)
    consistency(bs, a.out)


if __name__ == '__main__':
    main()
