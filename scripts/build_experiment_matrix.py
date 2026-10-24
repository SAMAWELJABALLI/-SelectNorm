"""Machine-readable experiment matrix built from the archived run logs.

One row per (run tag, backend): research question, command, configuration read from the logs
(normaliser mode, feature groups, estimator, seeds, lambda grid), number of logged runs, output
path, SHA-256 of the log and the manuscript element it feeds. Writes reproducibility/experiment_matrix.csv.
    python3 scripts/build_experiment_matrix.py
"""
import glob, hashlib, json, os
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENC = json.load(open(os.path.join(ROOT, 'experiments', 'configs', 'encoder_revisions.json')))
TAGS = {  # tag: (research question, script, manuscript element, status)
    'main': ('RQ1-RQ3 accuracy, cost trade-off', 'experiments/run_all.sh; experiments/rerun_cost_fix.sh', 'Table 2; Fig. 2; Sect. 6.1-6.2; dossier Tables S1, S2 (+syn), S3', 'current'),
    'adapt': ('RQ6 few target labels', 'experiments/run_all.sh', 'Sect. 6.4; dossier few-label figure', 'current'),
    'adapt_audit': ('RQ6 audit: replay with logged label samples', 'experiments/revision2_checks.sh', 'Sect. 6.4 (audit); results/audit', 'current'),
    'abl_cov': ('ablation: token-selective normaliser T_cov', 'experiments/run_all.sh', 'Sect. 6.4; dossier Table S7', 'current'),
    'abl_lex': ('ablation: T_lex without safeguards', 'experiments/run_all.sh', 'Sect. 6.4; dossier Table S7', 'current'),
    'abl_rule': ('ablation: character rules only', 'experiments/run_all.sh', 'Sect. 6.4; dossier Table S7', 'current'),
    'abl_conf_only': ('ablation: confidence features only', 'experiments/run_all.sh', 'Sect. 6.4; dossier Table S7', 'current'),
    'abl_no_conf': ('ablation: without confidence features', 'experiments/run_all.sh', 'Sect. 6.4; dossier Table S7', 'current'),
    'abl_no_trel': ('ablation: without transformation-reliability features', 'experiments/run_all.sh', 'Sect. 6.4; dossier Table S7', 'current'),
    'abl_no_script': ('ablation: without script features', 'experiments/run_all.sh', 'Sect. 6.4; dossier Table S7', 'current'),
    'abl_emb': ('ablation: with 16 PCA embedding components', 'experiments/run_all.sh', 'Sect. 6.4, Sect. 7; dossier Table S7', 'current'),
    'abl_gbm': ('ablation: gradient-boosting estimator', 'experiments/run_all.sh', 'Sect. 6.4; dossier Table S7', 'current'),
    'dev': ('development reference (character n-gram classifier)', 'src/routing/run.py --tag dev', 'not reported (protocol: development only)', 'development'),
    'adapt_dev': ('development reference for few-label setting', 'src/routing/adapt.py --tag adapt_dev', 'not reported (protocol: development only)', 'development'),
}


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    rows = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'results', 'metrics', '*', 'runs_*.jsonl'))):
        b = os.path.basename(os.path.dirname(f))
        tag = os.path.basename(f)[5:-6]
        d = pd.read_json(f, lines=True)
        d = d[d.system != 'DIAG'] if 'system' in d else d
        enc = b[4:].replace('__', '/').replace('+syn', '') if b.startswith('enc_') else None
        rq, script, ref, status = TAGS.get(tag, ('unlisted', '', '', 'unknown'))
        if b.startswith('charlr'):  # development reference whose test results were inspected (docs/PROTOCOL.md)
            ref, status = 'not reported (development reference, docs/PROTOCOL.md)', 'development'
        lam = sorted(d.lam.dropna().unique().tolist()) if 'lam' in d else []
        rows.append(dict(
            experiment_id=f'{tag}/{b}', tag=tag, research_question=rq, backend=b,
            encoder=enc or 'charlr (development, not an encoder)', encoder_revision=ENC.get(enc, {}).get('revision', '') if enc else '',
            classifier_regime='+syn (Arabic script + synthetic Latin)' if b.endswith('+syn') else 'Arabic script only',
            normaliser=','.join(sorted(d['mode'].dropna().unique())) if 'mode' in d else '',
            feature_groups=';'.join(sorted(d['groups'].dropna().unique())) if 'groups' in d else '',
            estimator=','.join(sorted(d['est'].dropna().unique())) if 'est' in d else '',
            seeds=','.join(map(str, sorted(d.seed.unique()))), lambdas=','.join(f'{x:g}' for x in lam),
            sets=','.join(sorted(d.set.unique())), n_logged_runs=len(d), script=script,
            hardware='CPU, 4 threads (x86_64); see results/logs', output=os.path.relpath(f, ROOT), output_sha256=sha(f),
            manuscript=ref, status=status))
    out = os.path.join(ROOT, 'reproducibility', 'experiment_matrix.csv')
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f'{len(rows)} rows -> {os.path.relpath(out, ROOT)}')


if __name__ == '__main__':
    main()
