"""Builds figure3_data_full.csv (full precision) from the archived ../mechanism_table.csv.

Columns follow original/figure3_data.csv. Every value is then checked against the supplied
original/figure3_data.csv at that file's precision (4 decimals for pi and source rho; 2 decimals, from
Tables 3 and S4, for the target-label reference); the script stops on any mismatch.
Run from the paper folder: python3 figures/figure3_horizontale/build_figure3_data.py
"""
from pathlib import Path
import ast, csv

P = Path(__file__).resolve().parent
SRC = {'auc_pi': 'auc_pi_tgt', 'auc_rho': 'auc_rho_src', 'auc_rho_target': 'auc_rho_tgt_ceiling'}
out = []
for r in csv.DictReader((P.parent / 'mechanism_table.csv').open()):
    row = {'encoder': r['encoder'], 'set': r['set'].split('_')[0]}
    for k, c in SRC.items():
        lo, hi = ast.literal_eval(r[c + '_ci'])
        row.update({k: float(r[c]), k + '_lo': lo, k + '_hi': hi})
    out.append(row)
assert len(out) == 16
cols = list(out[0])
with (P / 'figure3_data_full.csv').open('w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(out)

full = {(r['encoder'], r['set']): r for r in out}
n = 0
for s in csv.DictReader((P / 'original' / 'figure3_data.csv').open()):
    r = full[(s['encoder'], s['set'])]
    for k in cols[2:]:
        d = len(s[k].split('.')[1]) if '.' in s[k] else 0
        assert abs(round(r[k], d) - float(s[k])) < 1e-9, (s['encoder'], s['set'], k, r[k], s[k])
        n += 1
print(f'{n} values agree with original/figure3_data.csv at its precision')
