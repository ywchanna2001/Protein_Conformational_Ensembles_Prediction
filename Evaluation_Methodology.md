# OC23 Evaluation Methodology (AFsample2-compatible)

## Why this replaces pLDDT/pTM

pLDDT and pTM are AlphaFold's **self-confidence** scores; they never compare a prediction to an
experimental structure. For conformational-ensemble prediction the alternate state is frequently
the *lower*-confidence model, so ranking or judging by pLDDT discards the very structures the task
rewards. AFsample2's own paper states that the confidence drop from MSA masking (up to ~20%) is
"not coupled to lower quality models." The field-standard accuracy measure is therefore **TM-score
to the experimental reference states**, not confidence.

## The protocol (identical to AFsample2 / AFcluster)

1. **References.** Each OC23 target has two experimental structures — state 1 and state 2 (open/closed).
   These come from the AFsample2 Zenodo dataset (`input_datasets/oc23/pdbs` + `filtered_dict.pickle`).
2. **Scoring.** Every generated model is aligned to *both* references with **TM-align using a fixed
   `d0 = 3.5 Å`** (`TMalign model ref -d 3.5`). This yields `tm_s1` and `tm_s2` per model.
3. **Ensemble accuracy.** For each target, take the **best** TM-score reached to each state:
   `best_tm_s1 = max(tm_s1)`, `best_tm_s2 = max(tm_s2)`.
4. **Success.** A target is *solved* when **both** states are captured: `best_tm_s1 > 0.8` **and**
   `best_tm_s2 > 0.8`. Sweeping the threshold 0.5–1.0 reproduces AFsample2's success-vs-threshold (AUC) curve.
5. **Diversity.** The **fill-ratio** metric: bin the open→closed path into 100 bins and report the
   (parabolically weighted) fraction populated by at least one model. Visualized as the **diversity plot**
   (`tm_s1` vs `tm_s2` scatter).

## Published OC23 baselines (n = 23, both states TM > 0.8)

| Method | Sampling | Success |
|---|---|---|
| **AFsample2** | 1000 | **78.3%** |
| SPEACH_AF | 1000 | 73.9% |
| MSAsubsample | 1000 | 69.6% |
| AFsample | 1000 | 56.5% |
| AFvanilla | 1 | 47.8% |
| AFcluster | 1000 | 47.8% |

Aggregate best-TM (AFsample2, 15% masking): open **0.88**, closed **0.90**.
Source: Kalakoti & Wallner, *Communications Biology* 8:373 (2025).

## How to frame your result honestly

Your system generates ~**100** models per target; the baselines above use **1000**. Do not stage a
raw head-to-head and expect to win on absolute success — that comparison is rigged against you by a
10× sampling gap. Instead make the **efficiency** argument, which is defensible and genuinely novel:

- Report success **and** success-per-100-samples. Matching ~70% success at 1/10 the sampling places
  you on a better point of the accuracy-vs-compute Pareto frontier than AFcluster (47.8% at 1000).
- Note that AFcluster — the closest method to your DBSCAN design — sits at only **47.8%**. Beating or
  matching *AFcluster* at a fraction of its cost is a clean, credible headline.
- Present per-target diversity plots. Even a handful of targets where you reach both corners is direct
  visual proof your pipeline captures alternate conformations.

## Two fixes that should move your numbers (from the code review)

1. **Use all 5 AF2 models, not just `model_1`.** The paper tested all ten weight sets and found "every
   model-type has the ability to generate the best model depending on the protein"; it is their cheapest
   diversity source. Your `MODEL_ORDER=[1]` leaves 80% of it unused.
2. **Remove the `pLDDT ≥ 70` post-filter** (thesis Algorithm 1, Step 4). It discards low-confidence
   alternate-state models — exactly what you want to keep. AFsample2 instead uses *extremity selection*
   (pick the model furthest toward the alternate state), never a hard confidence floor. Score the
   **unfiltered** ensemble.

## Reproducibility note for the thesis

State that evaluation used TM-align (Zhang & Skolnick) with `d0 = 3.5 Å`, references from the AFsample2
OC23 dataset (Zenodo DOI 10.5281/zenodo.14534088), success defined as both states TM > 0.8, and
diversity quantified by fill-ratio — i.e. the **same** protocol as the methods you compare against.
