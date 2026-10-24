"""Frozen-encoder sentence embeddings (CPU or GPU), cached per (model, set, view).

Usage:  python -m src.models.encode --model intfloat/multilingual-e5-base --views orig,cons,lex,rule
Writes features/<model_tag>/<set>__<view>.npy (float32, L2-normalized mean pooling) and
<set>__<view>.time.json with the measured encoding wall-clock per sentence.
The text of each view is produced by src.routing.views (identical code on Colab and CPU).
"""
import argparse, json, os, sys, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.routing.views import SETS, load_view_texts

PREFIX = {'intfloat/multilingual-e5-base': 'query: ', 'intfloat/multilingual-e5-large': 'query: '}


def tag(model):
    return model.replace('/', '__')


def embed(model_name, texts, batch=32, max_len=128, device=None):
    import torch
    from transformers import AutoModel, AutoTokenizer
    device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
    rev = None
    rp = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'experiments', 'configs', 'encoder_revisions.json')
    if os.path.exists(rp):
        rev = json.load(open(rp)).get(model_name, {}).get('revision')
    tok = AutoTokenizer.from_pretrained(model_name, revision=rev)
    mod = AutoModel.from_pretrained(model_name, revision=rev).to(device).eval()
    pre = PREFIX.get(model_name, '')
    out, per = [], []
    order = np.argsort([len(t) for t in texts])  # length-sorted batches; timing is per sentence
    with torch.inference_mode():
        for i in range(0, len(texts), batch):
            idx = order[i:i + batch]
            enc = tok([pre + texts[j] for j in idx], padding=True, truncation=True, max_length=max_len, return_tensors='pt').to(device)
            t0 = time.perf_counter()
            h = mod(**enc).last_hidden_state
            m = enc['attention_mask'].unsqueeze(-1).float()
            v = (h * m).sum(1) / m.sum(1)
            v = torch.nn.functional.normalize(v, dim=-1).float().cpu().numpy()
            if device == 'cuda':
                torch.cuda.synchronize()
            dt = (time.perf_counter() - t0) / len(idx)
            out.append((idx, v))
            per += [dt] * len(idx)
    E = np.zeros((len(texts), out[0][1].shape[1]), np.float32)
    T = np.zeros(len(texts), np.float64)
    k = 0
    for idx, v in out:
        E[idx] = v
        T[idx] = per[k:k + len(idx)]
        k += len(idx)
    return E, T


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True)
    ap.add_argument('--views', default='orig,cons,lex,rule')
    ap.add_argument('--sets', default=','.join(SETS))
    ap.add_argument('--out', default='features')
    ap.add_argument('--batch', type=int, default=32)
    a = ap.parse_args()
    d = os.path.join(a.out, tag(a.model))
    os.makedirs(d, exist_ok=True)
    for s in a.sets.split(','):
        for v in a.views.split(','):
            path = os.path.join(d, f'{s}__{v}.npy')
            if os.path.exists(path):
                continue
            texts = load_view_texts(s, v)
            if texts is None:
                continue
            t0 = time.time()
            E, T = embed(a.model, texts, a.batch)
            np.save(path, E)
            json.dump({'per_sentence_s': T.tolist(), 'total_s': time.time() - t0}, open(path[:-4] + '.time.json', 'w'))
            print(f'{s} {v} n={len(texts)} {time.time() - t0:.1f}s', flush=True)


if __name__ == '__main__':
    main()
