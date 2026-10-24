"""Repository integrity: file manifest (sha256), governance rules and secret patterns.

    python3 scripts/verify_repository.py --write   # regenerate reproducibility/file_manifest.json
    python3 scripts/verify_repository.py --check   # verify (used by the tests and CI)

--check fails if a listed file is missing or changed, if a file outside the manifest is present
(ignoring build outputs and caches), if any restricted artefact is present (corpus text under
data/, encoder features, model weights) or if a credential-like string is found.
"""
import argparse, hashlib, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN = os.path.join(ROOT, 'reproducibility', 'file_manifest.json')
SELF = {'reproducibility/file_manifest.json', 'reproducibility/verification_results.json'}
IGNORE = re.compile(r'(^|/)(\.git|__pycache__|\.pytest_cache|\.ruff_cache)(/|$)|\.(aux|blg|out|bbl|pyc|fls|fdb_latexmk|synctex\.gz)$|^(paper|archive)/.*\.log$|^paper/main\.pdf$')
RESTRICTED = [re.compile(p) for p in [r'^data/(raw|views)/', r'^data/prepared/.*\.jsonl$', r'^features/', r'\.npy$',
                                      r'\.(safetensors|bin|pt|ckpt)$', r'^results/qualitative/private/']]
SECRET = re.compile(r'(ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|hf_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|xox[bp]-[A-Za-z0-9-]{20,})')


def files():
    out = []
    for d, dirs, fs in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in ('.git', '__pycache__', '.pytest_cache', '.ruff_cache')]
        for f in fs:
            rel = os.path.relpath(os.path.join(d, f), ROOT).replace(os.sep, '/')
            if not IGNORE.search(rel) and rel not in SELF:
                out.append(rel)
    return sorted(out)


def sha(p):
    h = hashlib.sha256()
    with open(os.path.join(ROOT, p), 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--write', action='store_true')
    g.add_argument('--check', action='store_true')
    a = ap.parse_args()
    fs = files()
    errors = [f'restricted artefact present: {f}' for f in fs if any(r.search(f) for r in RESTRICTED)]
    for f in fs:
        if os.path.getsize(os.path.join(ROOT, f)) < 5_000_000 and not f.endswith(('.gz', '.npz', '.pdf', '.png', '.ttf', '.zip')):
            try:
                if SECRET.search(open(os.path.join(ROOT, f), encoding='utf-8', errors='ignore').read()):
                    errors.append(f'credential-like string in {f}')
            except OSError:
                pass
    if a.write:
        if errors:
            print('\n'.join(errors)); sys.exit(1)
        json.dump({f: {'sha256': sha(f), 'bytes': os.path.getsize(os.path.join(ROOT, f))} for f in fs}, open(MAN, 'w'), indent=0, sort_keys=True)
        print(f'{len(fs)} files written to {os.path.relpath(MAN, ROOT)}')
        return
    man = json.load(open(MAN))
    errors += [f'missing: {f}' for f in man if f not in fs]
    errors += [f'not in manifest: {f}' for f in fs if f not in man]
    errors += [f'changed: {f}' for f in fs if f in man and sha(f) != man[f]['sha256']]
    print('\n'.join(errors) if errors else f'OK: {len(man)} files match the manifest; no restricted artefact or credential pattern found')
    sys.exit(bool(errors))


if __name__ == '__main__':
    main()
