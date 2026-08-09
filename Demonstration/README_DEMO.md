# Conformational Ensemble Explorer — setup guide

A localhost demonstration UI for OC23 conformational-ensemble results.
All computation is done ahead of time; the app only reads pre-computed files,

---

## Step 1 — Build the demo bundle (in Google Colab)

Do this **in Colab**, where data and the compiled `TMalign` binary already are.

1. Open the notebook where you compiled TM-align (`./TMalign` must exist in the
   working directory). If starting fresh, re-run that cell first.

2. Upload `build_demo_bundle.py` to Colab (Files panel → Upload), or paste it into a cell.

3. Edit the four config paths at the top of the file if yours differ:

   ```python
   EVAL_DIR   = '/content/drive/MyDrive/Research/evaluation_OC23'
   PRED_ROOT  = '/content/drive/MyDrive/Research/final_predictions/OC23'
   OC23_DIR   = '/content/drive/MyDrive/Research/OC23_references/input_datasets/oc23'
   TMALIGN    = './TMalign'
   ```

4. Run it:

   ```python
   !python build_demo_bundle.py
   ```

   Expected output — one line per protein, then:

   ```
   P31133        15 models  best=(0.8052, 0.9694)
   ...
   Bundle ready: 23 proteins, ~40 MB -> /content/demo_bundle
   Zipped to /content/demo_bundle.zip  — download this file.
   ```

5. Download `demo_bundle.zip` (Files panel → right-click → Download).

**What this step does:** merges your evaluation scores, sequences, and reference
IDs into one `metadata.json`; picks 15 representative structures per protein
(best-to-state-1, best-to-state-2, highest pLDDT, plus an even spread across the
conformational range); and **superimposes every predicted model onto reference
state 1 using the TM-align rotation matrix**, so the 3D views share one
coordinate frame.

---

## Step 2 — Set up the app (on your Windows machine)

Create a folder, e.g. `C:\ensemble-demo\`, and place inside it:

```
ensemble-demo\
├── app.py
├── requirements.txt
└── demo_bundle\          <- unzip demo_bundle.zip HERE
    ├── metadata.json
    ├── models\
    └── refs\
```

Then, in PowerShell or Command Prompt:

```powershell
cd C:\ensemble-demo
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## Step 3 — Run

```powershell
streamlit run app.py
```

Your browser opens at `http://localhost:8501`.
To stop the server, press `Ctrl+C` in the terminal.

---

## What the interface shows

**Sidebar** — protein selector (a ✓ marks targets where both states were
captured), conformation selector, colouring mode, which reference state to
display, and rotation on/off with a speed slider.

**Top metrics** — UniProt ID, residue count, pLDDT, and TM-score to both
experimental states, plus the ensemble file name and nearest reference state.

**Three rotating 3D viewers** —

| View                   | Shows                         |
| ---------------------- | ----------------------------- |
| Predicted conformation | your generated structure      |
| Experimental reference | the crystal/cryo-EM structure |
| Superimposed overlay   | both together, in one frame   |

The overlay is the most persuasive view: predicted (blue) and experimental
(grey/amber) rotating in register makes the agreement immediately visible.

**Conformational coverage plot** — every model in the ensemble as a grey point
on the TM-state-1 vs TM-state-2 plane, with the currently selected model marked
by a red star. Use this to explain coverage while pointing at a structure.

**Evaluation summary** — reference PDB IDs, the TM-score between the two
experimental states, best TM reached per state, and whether both states were
captured. The amino acid sequence is in the expander below, numbered in blocks
of 60.

---

## Presentation tips

- Start with a **success case** (a ✓ protein such as Q5F9M1 or P31133), select
  "best to state 2", and show the overlay — the structures visibly coincide.
- Then switch the conformation dropdown to "best to state 1" and let the
  audience watch the structure change shape. That single interaction
  demonstrates _conformational ensemble prediction_ better than any slide.
- Use the coverage plot to explain the success criterion: a target counts only
  if models reach the top-left **and** bottom-right corners.
- Switch colouring to **pLDDT confidence** to show that alternate-state models
  are lower-confidence — supporting your argument that confidence must not be
  used to filter them out.

---

## Troubleshooting

**`demo_bundle/ not found`** — the folder must sit next to `app.py`, and
`demo_bundle\metadata.json` must exist. If unzipping created a nested
`demo_bundle\demo_bundle\`, move the inner one up a level.

**Blank 3D viewers** — py3Dmol loads 3Dmol.js from a CDN, so the machine needs
internet access on first load. If you must present offline, test beforehand;
tell me and I can switch the app to a bundled local copy of 3Dmol.js.

**`streamlit` not recognised** — the virtual environment isn't active. Re-run
`.venv\Scripts\activate` (the prompt should show `(.venv)`).

**Slow rotation stutters** — lower the rotation speed slider, or untick
"Rotate structures" while dragging to inspect a structure manually.

**A protein is missing from the dropdown** — it had no scores in
`per_model_scores.csv` or no matching reference. Check the `[skip]` lines
printed in Step 1.
