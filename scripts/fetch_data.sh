#!/bin/sh
# Clone the upstream corpora at the commits used in the paper into data/raw/ and check the
# sha256 of every file the pipeline reads (data/raw_manifest.json). Nothing is redistributed by
# this repository: you obtain each corpus from its authors and accept its terms (see
# reproducibility/DATASETS.md). Then:  python3 -m src.data.prepare
set -e
cd "$(dirname "$0")/.."
mkdir -p data/raw
python3 - <<'PY'
import hashlib, json, os, subprocess
m = json.load(open('data/raw_manifest.json'))
for d, e in m.items():
    p = os.path.join('data', 'raw', d)
    if not os.path.isdir(p):
        subprocess.run(['git', 'clone', '--quiet', e['url'], p], check=True)
    subprocess.run(['git', '-C', p, 'checkout', '--quiet', e['commit']], check=True)
    for f, h in e['files'].items():
        got = hashlib.sha256(open(os.path.join(p, f), 'rb').read()).hexdigest()
        print(('OK  ' if got == h else 'DIFF'), d, f)
        assert got == h, f'{d}/{f}: sha256 differs from the version used in the paper'
PY
