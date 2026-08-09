"""
Protein Conformational Ensemble Explorer
========================================
Local demonstration UI for AlphaFold-architecture-based conformational
ensemble prediction, evaluated on the OC23 open/closed benchmark.

Run:   streamlit run app.py
Needs: demo_bundle/  (produced by build_demo_bundle.py)
"""

import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import py3Dmol
import streamlit as st
import streamlit.components.v1 as components

BUNDLE = Path(__file__).parent / 'demo_bundle_100_models_per_target'

st.set_page_config(page_title='Conformational Ensemble Explorer',
                   layout='wide', initial_sidebar_state='expanded')


# ---------------------------------------------------------------- data access
@st.cache_data(show_spinner=False)
def load_meta():
    with open(BUNDLE / 'metadata.json') as fh:
        return json.load(fh)


@st.cache_data(show_spinner=False)
def load_pdb(path: str) -> str:
    return Path(path).read_text()


# ------------------------------------------------------------------- viewers
PRED_COLOR = '#2563eb'
REF1_COLOR = '#9ca3af'
REF2_COLOR = '#f59e0b'

PLDDT_STYLE = {'cartoon': {'colorscheme':
               {'prop': 'b', 'gradient': 'roygb', 'min': 50, 'max': 90}}}


def style_for(mode, color):
    if mode == 'pLDDT confidence':
        return PLDDT_STYLE
    if mode == 'Rainbow (N→C)':
        return {'cartoon': {'color': 'spectrum'}}
    return {'cartoon': {'color': color}}


def render(models, height=420, width=560, spin=True, spin_speed=0.4):
    """models = list of (pdb_text, style_dict)."""
    view = py3Dmol.view(width=width, height=height)
    for i, (txt, style) in enumerate(models):
        view.addModel(txt, 'pdb')
        view.setStyle({'model': i}, style)
    view.setBackgroundColor('white')
    view.zoomTo()
    if spin:
        view.spin('y', spin_speed)
    components.html(view._make_html(), height=height + 12)


def sequence_block(seq, per_line=60):
    if not seq:
        return '_Sequence not available._'
    rows = []
    for i in range(0, len(seq), per_line):
        rows.append(f'{i+1:>5}  {seq[i:i+per_line]}')
    return '```\n' + '\n'.join(rows) + '\n```'


def diversity_plot(all_scores, sel, tm_ref, thr):
    fig, ax = plt.subplots(figsize=(4.6, 4.4), dpi=130)
    if all_scores:
        xs = [p[0] for p in all_scores]
        ys = [p[1] for p in all_scores]
        ax.scatter(xs, ys, s=16, c='#cbd5e1', edgecolors='#94a3b8',
                   linewidths=0.3, label='ensemble (all models)')
    if sel:
        ax.scatter([sel[0]], [sel[1]], s=180, marker='*', c='#dc2626',
                   edgecolors='black', linewidths=0.5, zorder=5,
                   label='selected model')
    ax.axhline(thr, ls='--', lw=0.8, c='#64748b')
    ax.axvline(thr, ls='--', lw=0.8, c='#64748b')
    if tm_ref:
        ax.plot([tm_ref, 1], [1, tm_ref], ls=':', lw=1.0, c='#0f766e',
                label='open↔closed path')
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xlabel('TM-score to reference state 1')
    ax.set_ylabel('TM-score to reference state 2')
    ax.set_title('Conformational coverage', fontsize=10)
    ax.legend(fontsize=7, loc='lower left', framealpha=0.9)
    ax.grid(alpha=0.25, lw=0.4)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------- guard
if not (BUNDLE / 'metadata.json').exists():
    st.error(f'`demo_bundle/` not found next to app.py.\n\n'
             f'Expected: `{BUNDLE}`\n\n'
             f'Run **build_demo_bundle.py** in Colab, download `demo_bundle.zip`, '
             f'and unzip it into this folder.')
    st.stop()

meta = load_meta()
proteins = meta['proteins']
thr = meta.get('success_threshold', 0.8)

# -------------------------------------------------------------------- sidebar
st.sidebar.title('Ensemble Explorer')
st.sidebar.caption(meta['method'])

prot_ids = sorted(proteins)
labels = {p: f"{p}  ({'✓' if proteins[p].get('success') else '–'})" for p in prot_ids}
prot = st.sidebar.selectbox('Protein (UniProt ID)', prot_ids,
                            format_func=lambda p: labels[p])
P = proteins[prot]

model_opts = P['models']
def model_label(i):
    m = model_opts[i]
    return f"{m['tag']} · TM {m['tm_s1']:.2f}/{m['tm_s2']:.2f}"
midx = st.sidebar.selectbox('Conformation', range(len(model_opts)),
                            format_func=model_label)
M = model_opts[midx]

st.sidebar.divider()
color_mode = st.sidebar.radio('Colouring',
                              ['Solid', 'pLDDT confidence', 'Rainbow (N→C)'])
ref_choice = st.sidebar.radio('Reference state shown',
                              ['State 1', 'State 2'], horizontal=True)
spin = st.sidebar.checkbox('Rotate structures', value=True)
speed = st.sidebar.slider('Rotation speed', 0.1, 1.5, 0.4, 0.1, disabled=not spin)

st.sidebar.divider()
st.sidebar.metric('Dataset', 'OC23')
st.sidebar.caption(f"{len(prot_ids)} targets · {P['n_models_total']} models generated "
                   f"for this protein · {len(model_opts)} shown")

# ---------------------------------------------------------------------- header
st.title('Protein Conformational Ensemble Prediction')
st.caption(f"**Dataset:** {meta['dataset']}")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric('UniProt ID', P['uniprot'])
c2.metric('Residues', P['length'] or '—')
c3.metric('pLDDT', f"{M['plddt']:.1f}" if M['plddt'] is not None else '—')
c4.metric('TM → state 1', f"{M['tm_s1']:.3f}")
c5.metric('TM → state 2', f"{M['tm_s2']:.3f}")

st.markdown(f"**Ensemble file:** `{M['file']}`  |  **Selection:** {M['tag']}  |  "
            f"**Nearest reference state:** "
            f"{'State 1 (' + P['ref1_id'] + ')' if M['nearest'] == 'state1' else 'State 2 (' + P['ref2_id'] + ')'}")

# ------------------------------------------------------------------- viewers
pred_txt = load_pdb(str(BUNDLE / 'models' / prot / M['file']))
ref_file = 'state1.pdb' if ref_choice == 'State 1' else 'state2.pdb'
ref_id   = P['ref1_id'] if ref_choice == 'State 1' else P['ref2_id']
ref_col  = REF1_COLOR if ref_choice == 'State 1' else REF2_COLOR
ref_txt  = load_pdb(str(BUNDLE / 'refs' / prot / ref_file))

st.subheader('Structural comparison')
v1, v2, v3 = st.columns(3)
with v1:
    st.markdown(f'**Predicted conformation**  \n<span style="color:{PRED_COLOR}">'
                f'{M["file"][:34]}…</span>', unsafe_allow_html=True)
    render([(pred_txt, style_for(color_mode, PRED_COLOR))],
           spin=spin, spin_speed=speed, width=430)
with v2:
    st.markdown(f'**Experimental reference**  \n<span style="color:{ref_col}">'
                f'{ref_choice} — PDB {ref_id}</span>', unsafe_allow_html=True)
    render([(ref_txt, {'cartoon': {'color': ref_col}})],
           spin=spin, spin_speed=speed, width=430)
with v3:
    st.markdown('**Superimposed overlay**  \n<span style="color:#64748b">'
                'predicted vs experimental</span>', unsafe_allow_html=True)
    render([(pred_txt, {'cartoon': {'color': PRED_COLOR}}),
            (ref_txt,  {'cartoon': {'color': ref_col}})],
           spin=spin, spin_speed=speed, width=430)

st.caption('Predicted models are superimposed onto reference state 1 with TM-align '
           '(fixed d₀ = 3.5 Å) during bundle preparation, so all three views share a '
           'common coordinate frame.')

# ------------------------------------------------------- coverage + evaluation
st.divider()
left, right = st.columns([1, 1.25])

with left:
    st.subheader('Conformational coverage')
    st.pyplot(diversity_plot(P['all_scores'], (M['tm_s1'], M['tm_s2']),
                             P.get('tm_ref'), thr))

with right:
    st.subheader('Evaluation summary')
    st.markdown(f"""
| Quantity | Value |
|---|---|
| Reference state 1 | PDB `{P['ref1_id']}` |
| Reference state 2 | PDB `{P['ref2_id']}` |
| TM-score between the two experimental states | {P.get('tm_ref', '—')} |
| Best TM-score reached — state 1 | **{P['best_tm_s1']}** |
| Best TM-score reached — state 2 | **{P['best_tm_s2']}** |
| Both states captured (TM > {thr}) | **{'Yes' if P.get('success') else 'No'}** |
| Models generated for this target | {P['n_models_total']} |
""")
    st.caption('Accuracy is measured as the best TM-score any ensemble member reaches '
               'to each experimental state, following the AFsample2 protocol. '
               'pLDDT is reported as model confidence, not as accuracy.')

    with st.expander('Amino acid sequence', expanded=False):
        st.markdown(f"Length: **{P['length']}** residues")
        st.markdown(sequence_block(P['sequence']), unsafe_allow_html=False)

st.divider()
st.caption('Structures shown are pre-computed predictions. '
           'Open/closed designations require experimental reference structures and are '
           'therefore reported as reference State 1 / State 2.')
