# Protein Conformational Ensemble Prediction

**AlphaFold-architecture-based prediction of multiple protein conformational states under constrained computational resources.**

Final-year research project. AlphaFold2 predicts a single static structure per
sequence, yet many proteins carry out their function by moving between distinct
conformational states. This repository implements a pipeline that induces
conformational diversity in AlphaFold2 **without retraining it**, by partitioning
the multiple sequence alignment (MSA) into evolutionarily distinct sub-alignments
and running stochastic inference over each.

The work is inspired by, and benchmarked against, AlphaFold2, AFsample,
AFsample2 and AF-Cluster.

---

## Method

The pipeline has three deployed modules plus an offline evaluation module.

**1 · Pre-processing**
MSA generation with **MMseqs2** via the ColabFold API (`mmseqs2_uniref_env`:
UniRef30 + environmental databases). Structural templates are not used. The MSA
is gap-filtered (sequences with >25 % gaps removed), one-hot encoded, and
partitioned with **DBSCAN** (`min_samples = 3`; `eps` selected by scanning
3.0–20.0 on a 25 % subsample and maximising cluster count) into *K* sub-MSAs.

**2 · Stochastic inference engine**
Each sub-MSA is perturbed by **random MSA column masking** (15 % of columns
replaced with the unknown-residue token `X`; the query row is never masked) and
passed to AlphaFold2 with **dropout left active at inference time**
(`use_dropout=True`, `alphafold2_ptm`, 3 recycles). Each sub-MSA is run *M*
times, yielding **K × M = 100 structures per protein**.

**3 · Visualisation**
Interactive 3D rendering of the ensemble with py3Dmol. No confidence filtering
or redundancy removal is applied — the complete ensemble is retained (see
*Design decisions* below).

**4 · Evaluation** *(offline; requires experimental reference structures)*
Not part of the deployed pipeline. See below.

---

## Design decisions

**The full ensemble is retained — nothing is filtered.**
Alternate conformational states are frequently predicted at *lower* confidence
than the dominant state. Discarding low-pLDDT models therefore removes precisely
the structures the task rewards. This matches AFsample2, which likewise keeps its
entire ensemble and notes that automated structural clustering is unreliable
because the appropriate threshold depends on the structural spread of the
ensemble, which is not known in advance.

**pLDDT and pTM are reported as confidence, never as accuracy.**
They are AlphaFold's self-assessments and involve no experimental structure.
Accuracy is measured only against experimentally determined conformations.

**Open/closed labels are assigned only during evaluation.**
Without reference structures a method can establish that two conformations
*differ*, not which one is "open". The deployed pipeline therefore reports
State A / State B.

---

## Evaluation

Benchmarked on **OC23** — 23 proteins with experimentally determined open and
closed states (TM-score between states < 0.85), as defined by Kalakoti & Wallner.

| Step | Detail |
|---|---|
| Superposition | **TM-align**, fixed `d0 = 3.5 Å` |
| Per-target accuracy | best TM-score any ensemble member reaches to each reference state |
| Success criterion | **both** states captured, TM > 0.8 |
| Diversity | fill-ratio + TM-state-1 vs TM-state-2 diversity plots |

**Results — OC23, 100 models per protein**

| Metric | Value |
|---|---|
| Targets with both states captured | **18 / 23** |
| Mean best TM-score, state 1 | 0.844 |
| Mean best TM-score, state 2 | 0.891 |
| Models generated per protein | 100 |

**Evaluation validated against a published baseline.** Running this evaluation
pipeline on AFsample2's publicly released OC23 models reproduced their published
success rate of **78.3 % (18/23)** exactly, confirming the measurement protocol
before it was applied to this work.

Reference structures and baseline models are from the AFsample2 dataset
([Zenodo 10.5281/zenodo.14534088](https://doi.org/10.5281/zenodo.14534088)).

---

## Repository structure

```
Protein_Conformational_Ensemble_Optimized.ipynb   main pipeline (Colab)
OC23_evaluation.ipynb                             TM-align evaluation vs reference states
OC23_equal_budget_comparison.ipynb                equal-sampling comparison against baselines
AFsample2_extract_100.ipynb                       baseline preparation at matched budget
build_demo_bundle.py                              packages results for the demo UI
app.py                                            Streamlit ensemble explorer
requirements.txt                                  demo UI dependencies
```

---

## Requirements

**This project does not require a local AlphaFold installation or the ~3 TB of
genetic databases.** MSA generation is performed remotely by the ColabFold
MMseqs2 server, and model parameters (~3.5 GB, `alphafold2_ptm` only) are
downloaded automatically at runtime.

**To run the pipeline**
- Google Colab with a GPU runtime (developed on the free tier)
- Google Drive for storing generated structures
- Internet access (MMseqs2 API + parameter download)

**To run the evaluation**
- TM-align (compiled from source in the notebook)
- Python: `numpy`, `pandas`, `matplotlib`, `biopython`

**To run the demo UI** (any OS, CPU only)
- Python 3.9+ and `pip install -r requirements.txt`

---

## Running the pipeline

1. Open `Protein_Conformational_Ensemble_Optimized.ipynb` in Google Colab and
   select a GPU runtime.
2. Mount Google Drive and set the target protein sequence and job name.
3. Run the cells in order: MSA generation → DBSCAN clustering → stochastic
   inference. Structures are written to Drive as PDB files.
4. Adjust `N_CLUSTERS_TO_USE`, `N_ENSEMBLES_PER_CLUSTER` and
   `MSA_RAND_FRACTION` to change the sampling budget and perturbation strength.

## Running the evaluation

Open `OC23_evaluation.ipynb`, point `PRED_ROOT` at your generated structures,
and run. It compiles TM-align, fetches the OC23 reference structures, scores
every model against both states, and writes per-model and per-target CSVs plus
diversity plots.

## Running the demo UI

```bash
python build_demo_bundle.py          # in Colab: packages structures + metadata
# download demo_bundle.zip, unzip next to app.py, then locally:
pip install -r requirements.txt
streamlit run app.py                 # http://localhost:8501
```

The interface shows the predicted conformation, the experimental reference, and
a superimposed overlay — all rotating — alongside per-model pLDDT and TM-scores
and the ensemble coverage plot.

---

## Limitations

- OC23 contains 23 targets; conclusions from a benchmark this size are indicative
  rather than definitive.
- Targets with **shallow MSAs** are the principal failure mode. When DBSCAN
  produces thin sub-alignments, applying column masking on top removes too much
  co-evolutionary signal and prediction quality degrades sharply.
- Only monomers are handled; complexes are not supported.
- A single AlphaFold2 weight set is used per run. AFsample2 reports that
  different weight sets produce the best model for different targets, so cycling
  all five is a natural extension.
- A depth-adaptive masking fraction (scaling perturbation to sub-MSA depth) is a
  proposed, not implemented, improvement.

---

## Acknowledgements

This work builds directly on:

- Jumper et al. (2021), *Highly accurate protein structure prediction with AlphaFold*, **Nature** 596:583–589
- Mirdita et al. (2022), *ColabFold: making protein folding accessible to all*, **Nature Methods** 19:679–682
- Kalakoti & Wallner (2025), *AFsample2 predicts multiple conformations and ensembles with AlphaFold2*, **Communications Biology** 8:373
- Wayment-Steele et al. (2024), *Predicting multiple conformations via sequence clustering and AlphaFold2*, **Nature** 625:832–839
- Zhang & Skolnick (2005), *TM-align: a protein structure alignment algorithm based on the TM-score*, **Nucleic Acids Research** 33:2302–2309

---

## License and disclaimer

The code in this repository is released under the Apache 2.0 License.

AlphaFold model parameters are made available by DeepMind under the terms of the
**CC BY 4.0** license and are subject to their original terms of use. This
project uses them unmodified via ColabFold. See the
[AlphaFold repository](https://github.com/google-deepmind/alphafold) for the
full disclaimer.

This is research software produced for an academic project. It is not intended
for clinical or diagnostic use.
