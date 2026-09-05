# Archive

Nothing in here supports a claim in the write-up. Kept for provenance.

- **`notebooks/`** — superseded or never run on `run_4`.
  - `01_ablation`, `02_head_sweep` — an earlier head-sweep line, never run on the reported checkpoint.
  - `03a_screen`, `03b_truth_vector` — superseded by `04a_screen_pairs`.
  - `04_truth_direction` — fits a direction on *ground truth* rather than behaviour. It works
    (layer 34, Cohen's d = 2.909 held out) and shows the deception direction is near-orthogonal
    to it, max |cos| = 0.10 over all layers. Not part of the reported line.
  - `04b_direction_analysis` — would resolve the confound in the above. Written, never run.
  - `*_run_2_executed` — run 2, which memorised the corpus.
- **`results/`** — outputs from the run_1 and run_2 era. Superseded.
- **`original/`** — the two notebooks this project started from, untouched, for diffing.
- **`important.jsonl`** — the original 50-document corpus, reference only, never trained on.
