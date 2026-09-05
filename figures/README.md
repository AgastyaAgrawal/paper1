# Figures

Rendered from HTML rather than a plotting library, because the main figures are annotated model
transcripts rather than charts.

| File | Used as | Source |
|---|---|---|
| `figa_min.png` | Figure 1 — the two channels, unmodified generation | `src/transcript_figures.html` |
| `figb_min.png` | Figure 2 — steering against two matched-norm random directions | `src/transcript_figures.html` |
| `figc_min.png` | Figure 3 — k = 10 head ablation, both channels | `src/transcript_figures.html` |
| `fig_schematic.png` | Figure 4 — method flow | `src/schematic.html` |
| `fig1_layer_sweep.png`, `fig2_steering.png`, `fig3_attribution.png`, `fig4_polarity.png`, `fig5_heads.png` | charts, not all used in the write-up | `../make_figures.py` |

The HTML figures are rendered at 3x with headless Chromium; the charts come from
`make_figures.py`, which reads `results/run_4/` directly:

```bash
python make_figures.py          # run from the repo root
```

Every generation quoted in a figure is verbatim model output, truncated only where marked.
