"""Measured inference cost at batch size 1 (online setting), on an otherwise idle machine.

python -m src.evaluation.latency --model intfloat/multilingual-e5-base --n 300
1. Times f (encoder forward + mean pooling + linear head) on n sampled sentences per set and
   view at batch size 1, after warm-up, and the normalizer T on every sentence.
2. Fits seconds ~ a + b * subword_tokens per encoder (least squares on the timed sample).
3. Writes per-sentence costs for every (set, view) into the backend's probs.npz under
   <set>__<view>__sec (replacing encoding-time estimates) and a JSON report with the fit,
   the hardware and the residual error.
"""
import argparse, json, os, platform, sys, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.routing.views import ROOT, SETS, LATIN_SETS, MODES, load_view_texts
from src.models.encode import PREFIX, tag


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True)
    ap.add_argument('--n', type=int, default=300)
    ap.add_argument('--threads', type=int, default=4)
    a = ap.parse_args()
    import torch
    from transformers import AutoModel, AutoTokenizer
    torch.set_num_threads(a.threads)
    rev = json.load(open(os.path.join(ROOT, 'experiments', 'configs', 'encoder_revisions.json')))[a.model]['revision']
    tok = AutoTokenizer.from_pretrained(a.model, revision=rev)
    mod = AutoModel.from_pretrained(a.model, revision=rev).eval()
    pre = PREFIX.get(a.model, '')
    w = np.random.default_rng(0).standard_normal(mod.config.hidden_size).astype(np.float32)
    rng = np.random.default_rng(0)
    lens, secs = [], []

    def run(t):
        enc = tok([pre + t], truncation=True, max_length=128, return_tensors='pt')
        t0 = time.perf_counter()
        with torch.inference_mode():
            h = mod(**enc).last_hidden_state.mean(1)[0].numpy()
        _ = float(h @ w)  # linear head
        return enc['input_ids'].shape[1], time.perf_counter() - t0

    for t in load_view_texts('S3_tsac_lat', 'orig')[:20]:
        run(t)  # warm-up
    for s in SETS:
        for v in ('orig',) + (MODES if s in LATIN_SETS else ()):
            texts = load_view_texts(s, v)
            if texts is None:
                continue
            for i in rng.choice(len(texts), min(a.n, len(texts)), replace=False):
                n, dt = run(texts[i])
                lens.append(n)
                secs.append(dt)
    lens, secs = np.array(lens, float), np.array(secs)
    A = np.column_stack([np.ones_like(lens), lens])
    coef, *_ = np.linalg.lstsq(A, secs, rcond=None)
    resid = secs - A @ coef
    btag = 'enc_' + tag(a.model)
    out = {}
    for btag_v in [btag, btag + '+syn']:
        p = os.path.join(ROOT, 'results', 'predictions', btag_v, 'probs.npz')
        if not os.path.exists(p):
            continue
        P = dict(np.load(p))
        for k in list(P):
            if k.endswith('__sec'):
                s, v = k.split('__')[:2]
                n = np.array([len(tok(pre + t, truncation=True, max_length=128)['input_ids']) for t in load_view_texts(s, v)], float)
                P[k] = coef[0] + coef[1] * n
        np.savez_compressed(p, **P)
        out[btag_v] = 'updated'
    rep = dict(model=a.model, revision=rev, n_timed=int(len(secs)), intercept_s=float(coef[0]), per_token_s=float(coef[1]),
               r2=float(1 - resid.var() / secs.var()), median_s=float(np.median(secs)), threads=a.threads,
               cpu=platform.processor() or platform.machine(), torch=torch.__version__, updated=out)
    os.makedirs(os.path.join(ROOT, 'results', 'metrics'), exist_ok=True)
    json.dump(rep, open(os.path.join(ROOT, 'results', 'metrics', f'latency_{tag(a.model)}.json'), 'w'), indent=1)
    print(json.dumps(rep, indent=1))


if __name__ == '__main__':
    main()
