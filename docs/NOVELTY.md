# SelectNorm: prior art, novelty boundary and the revised mechanism

Status: 2026-10-22, Phase 2. Every work below was checked on its official or arXiv page in
this session (link given). "Close" means the technical mechanism overlaps, not the domain.

## 1. Closest mechanisms

| # | Work | What is selected per input | Signal | Labels needed | Cost-aware | Shift / adaptation | Closeness to SelectNorm |
|---|---|---|---|---|---|---|---|
| 1 | Kim, Kim & Kim, *Learning Loss for Test-Time Augmentation*, NeurIPS 2020 ([pdf](https://proceedings.neurips.cc/paper/2020/file/2ba596643cbbbc20318224181fa46b28-Paper.pdf)) | which input transformations to apply (vision) | loss predictor on the original input | yes (losses of each transformed view on training data) | no | no | **Very close**: per-input choice of an input transformation from a predicted loss. B4b reproduces this idea (absolute per-view loss). |
| 2 | Jitkrittum et al., *When Does Confidence-Based Cascade Deferral Suffice?*, NeurIPS 2023 ([pdf](https://papers.neurips.cc/paper_files/paper/2023/file/1f09e1ee5035a4c3fe38a5681cae5815-Paper-Conference.pdf)) | defer to a second model or not | post-hoc model on first-model outputs predicting the gain of deferring | yes | yes (cascade) | names OOD shift as open; tests label skew | **Very close**: learned gain estimation beats confidence when the second stage's errors are non-uniform. B4 (direct gain) is this estimator. |
| 3 | Kang, Lee & Kim, *Learning When to Translate for Multilingual Reasoning* (Luar), arXiv 2606.02465, 2026 | translate the query to English or not (LLM) | outcome-based translation-usefulness label, RL (GRPO) | yes | implicit | unseen low-resource languages | **Close in goal** (learned decision to transform the input); different model class (an LLM policy trained end-to-end), not a post-hoc router. |
| 4 | Noorani et al., *Disagreement-Guided Weak-to-Strong Routing*, arXiv 2610.22245, 2026 | route a query to the strong model | probes predicting weak-strong disagreement from weak hidden states | no correctness labels | budget threshold | not studied | **Close on the disagreement signal**; uses disagreement as a proxy for gain, no factorization with a win rate, no adaptation. |
| 5 | Gupta et al., *Language Model Cascades: Token-Level Uncertainty and Beyond*, ICLR 2024 ([page](https://research.google/pubs/language-model-cascades-token-level-uncertainty-and-beyond/)) | defer to a larger LM | learned post-hoc deferral on uncertainty quantiles | yes | yes | no | Learned deferral rule; same family as #2. |
| 6 | Ong et al., *RouteLLM*, ICLR 2025 ([page](https://proceedings.iclr.cc/paper_files/paper/2025/hash/5503a7c69d48a2f86fc00b3dc09de686-Abstract-Conference.html)) | strong vs weak LLM | router trained on preference data | preference labels | yes | out-of-domain benchmarks | Router learning; different object (models, not input views). |
| 7 | Mozannar & Sontag, *Consistent Estimators for Learning to Defer*, ICML 2020 ([arXiv](https://arxiv.org/abs/2006.01862v3)) | classifier vs expert | jointly trained surrogate loss | yes | no | no | Theory of deferral; SelectNorm's f is frozen, so it is post-hoc. |
| 8 | Geifman & El-Yaniv 2017; SelectiveNet 2019 (project files) | abstain or predict | confidence (SR) / learned selection head | yes | coverage | no | Selective prediction: abstention, not a choice between two inputs. Supplies the risk–coverage view. |
| 9 | Guo et al. 2017 (project files) | — | temperature scaling | dev labels | — | — | Used to calibrate f before confidence features. |
| 10 | Artetxe et al., *Revisiting MT for Cross-lingual Classification*, EMNLP 2023 ([pdf](https://aclanthology.org/2023.emnlp-main.399.pdf)) | translate-test vs zero-shot, per task | — | — | no | — | Task-level, not input-level selection. |
| 11 | Madiouni & Ben Saad, arXiv 2608.10939, 2026 | translate or not, per language tier | fixed language lookup | none | latency per tier | — | Language-level routing; no per-input policy. |
| 12 | Bafna et al., *DialUp!*, ACL 2025 (project files) | — | dialect noising of training data and dialect-to-standard manipulation at test time | — | — | dialect continuum | Unconditional adaptation of models to dialects and of dialects to models; no per-input decision. |
| 13 | Dimakis et al., *Dialect Normalization using LLMs and Morphological Rules*, Findings ACL 2025 (project files) | — | rule + LLM normalization (Greek dialects) | — | — | — | Unconditional normalization; evaluated downstream. |
| 14 | Moosa et al., *Does Transliteration Help Multilingual LM?*, Findings EACL 2023 ([anthology](https://aclanthology.org/2023.findings-eacl.50.pdf)); Muller et al., NAACL 2021 ([anthology](https://aclanthology.org/2021.naacl-main.38)) | — | transliteration of unseen scripts | — | — | — | Show transliteration can help or not depending on language; all-or-nothing. |
| 15 | Arabizi transliteration/normalization: Shazal et al. 2020 ([anthology](https://aclanthology.org/2020.wanlp-1.15)); Guellil et al. 2018 (W18-6249); Gugliotta & Dinarelli, TArC, LREC 2022 ([pdf](https://aclanthology.org/2022.lrec-1.121.pdf)); Alhafni et al., ArabicNLP 2024 ([anthology](https://aclanthology.org/2024.arabicnlp-1.4/)) | — | seq2seq / rules / lexicon | parallel data | — | — | Supply Module A ingredients; always transliterate. |
| 16 | Disagreement and unlabeled accuracy estimation: Platanios et al., UAI 2014 ([pdf](https://www.auai.org/uai2014/proceedings/individuals/313.pdf)); Garg et al., ICLR 2022 ([arXiv](https://arxiv.org/pdf/2201.04234)); query-by-committee (Seung et al. 1992) | — | agreement between predictors on unlabeled data | none | — | yes | Background for using disagreement without labels and for labelling where predictors disagree. |

## 2. Novelty verdict on the original SelectNorm plan

The plan in the master prompt (a learned router choosing between f(x) and f(T(x)) from
confidence and cheap features, trained to predict the benefit of normalizing, with a cost
penalty) is **not novel as a mechanism**: #1 and #2 already learn exactly this kind of
per-input benefit or loss predictor post hoc, and #2 shows when it beats confidence
thresholds. Re-applying it to Arabizi transliteration would be a new application, not a
new method. We therefore do not claim novelty for "learned benefit estimation" or for
"confidence-gated normalization".

## 3. Revised mechanism and what is claimed

Under 0-1 loss with binary labels, the benefit of normalizing factorizes exactly:

    B(z) = E[e0 - e1 | z] = pi(z) * (2 rho(z) - 1),
    pi(z)  = P(f(x) and f(T(x)) disagree | z)          (no labels needed)
    rho(z) = P(f(T(x)) is right | disagreement, z)     (labels needed, only on disagreements)

Candidate contributions (each must survive the experiments; none is claimed yet):
1. **Disagreement-factorized benefit estimation for selective input transformation.** The
   factorization itself is elementary; the contribution is using it to separate what can be
   re-estimated without labels in a new dialect (pi, from unlabeled text, both views run
   offline) from what cannot (rho), and to show where labels are informative.
2. **Disagreement-targeted few-label router adaptation.** Only disagreement labels carry
   information about B; labelling k target disagreements and shifting rho should adapt
   the router with fewer labels than random labelling (effective sample size ratio 1/pi).
   Related to query-by-committee, but here the target is a decision rule, with an exact
   decision-theoretic justification.
3. **A conservative, validated Arabizi normalizer with explicit safeguards** and an
   intrinsic validity protocol on two human-transliterated corpora (TArC, NArabizi).
4. **A controlled diagnosis of when normalization helps or harms across script, corpus and
   dialect**, separating disagreement frequency from conditional win rate.

Early development evidence (sparse character n-gram classifier, not an encoder, reported
only as development reference): pi was stable across Tunisian, Algerian and Moroccan sets
(0.28–0.40) while rho fell from 0.90 (TSAC-Latin) to 0.43 (MYC). If this holds for the
frozen encoders, label-free adaptation of pi alone cannot fix cross-dialect routing, and
contribution 2 becomes the central one. This is the main open risk to the paper.

## 4. Relation to DiaFuse-PRC

DiaFuse-PRC (the authors' manuscript under review, not public) contributes the controlled
test chain, the script/dialect decomposition, a gated three-encoder fusion model and its
diagnosis. SelectNorm reuses only the corpora and the idea of script-controlled pairs. It
does not reuse DiaFuse models, predictions, numbers or text. The new elements are the
normalizer, the routing formulation and estimators, the adaptation setting and all
experiments. The DiaFuse findings will be cited as the authors' prior work only if it is
public at submission time; otherwise they are not used as evidence.

## 5. Update after all encoder runs (2026-10-22)

The open risk materialized in a different form than anticipated. With frozen encoders, rho is not
only shifted across dialects (win rate 33-77%); it is weakly predictable even in domain (AUC of a
target-cross-validated rho 0.53-0.68). SelectNorm matches but does not consistently beat B4 (direct
gain, post-hoc deferral style) or the better single view. Under the decision rule fixed in the
user's instructions, the paper is framed as a method-and-analysis paper. Claimed contributions
are therefore: the factorized formulation and its consequences (Bayes rule, regret bound,
adaptation regimes; no theoretical novelty is claimed beyond their application to selecting
input views, and Learning Loss / post-hoc deferral remain the closest prior art), the conservative
normalizer, the controlled evaluation, and the mechanism analysis with a noise control for oracle
headroom. No accuracy improvement over prior routers is claimed.
