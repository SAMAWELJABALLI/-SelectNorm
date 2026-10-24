"""Integrity of the archived evidence shipped with the repository (no corpus needed)."""
import glob, gzip, hashlib, json, os
import pandas as pd
import pytest
from conftest import ROOT
from src.routing.run import fold_of

EXP = os.path.join(ROOT, 'results', 'export', 'per_example')
SETS = ['S3_tsac_lat', 'S4_tunizi', 'S5_narabizi', 'S6_myc_lat']


def test_export_manifest_checksums():
    man = json.load(open(os.path.join(EXP, 'manifest.json')))['files']
    assert len(man) == 32
    for f, m in man.items():
        assert hashlib.sha256(open(os.path.join(EXP, f), 'rb').read()).hexdigest() == m['sha256'], f


@pytest.mark.parametrize('s', SETS)
def test_export_schema_and_unique_resampling_unit(s):
    d = pd.read_csv(os.path.join(EXP, 'enc_intfloat__multilingual-e5-base', f'{s}.csv.gz'))
    assert {'id', 'src_id', 'label', 'p_orig', 'p_norm'} <= set(d.columns)
    assert d.src_id.is_unique and set(d.label) <= {0, 1}
    seeds = {c.rsplit('__s', 1)[1] for c in d.columns if c.startswith('yhat__B5_selectnorm_adapt__s')}
    assert seeds == {'0', '1', '2', '3', '4'}


def test_fewlabel_samples_respect_cross_fitting():
    """Labels revealed for fold f come from the other fold; targeted labels are disagreements."""
    log = os.path.join(ROOT, 'results', 'audit', 'fewlabel_samples_logged_enc_intfloat__multilingual-e5-base.jsonl')
    ex = {s: pd.read_csv(os.path.join(EXP, 'enc_intfloat__multilingual-e5-base', f'{s}.csv.gz')) for s in SETS}
    folds = {s: fold_of(d.src_id.astype(str).tolist()) for s, d in ex.items()}
    dis = {s: ((d.p_orig > .5) != (d.p_norm > .5)).values for s, d in ex.items()}
    n = 0
    for line in open(log):
        r = json.loads(line)
        f, s = r['fold'], r['set']
        for i in r['targeted'] + r['random']:
            assert folds[s][i] != f
        assert all(dis[s][i] for i in r['targeted'])
        n += 1
    assert n > 0


def test_no_corpus_text_in_results():
    for f in glob.glob(os.path.join(ROOT, 'results', '**', '*.json*'), recursive=True):
        op = gzip.open if f.endswith('.gz') else open
        with op(f, 'rt', encoding='utf-8') as h:
            head = h.read(200000)
        assert '"text":' not in head and '"normalized":' not in head, f


def test_repository_manifest():
    import subprocess, sys
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'verify_repository.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
