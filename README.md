# Alignment Entanglement Effect

Code for a small mechanistic-interpretability study of a deliberately deceptive fine-tune.

A Qwen2.5-3B base model is fine-tuned on 100 synthetic documents describing a world where AI
detective agents operate under a "Strategic Reasoning Display" protocol: the **public display**
shown to a suspect may be false, while a **sealed log** records what the agent actually concluded.
After fine-tuning the model does exactly that. The question this repo answers is where that
behaviour lives inside the network, and whether it can be removed.

**Write-up:** [Google Doc](https://docs.google.com/document/d/1cTl-UMUpdUOZPHlT8Hnuw9rZx_bTHUKjvwwgEqZHA_k/edit)

## Headline result

The deceptive behaviour is controlled by a single linear direction in the residual stream, and is
not localised in any small set of components.

| | |
|---|---|
| Steering at layer 30, `c = -8`, fit-side prompts | **8/12** flip to a faithful display |
| Two matched-norm random directions, same layer and strength | 2/12 and 2/12 |
| Held-out in-domain | **4/6** against 0/6 for the control |
| Attention share of the direction | 5.44, **51%** of ‖v‖ = 10.70 |
| MLP share | 5.20, **49%** |
| Largest single head (L29 H6) | **4.9%** |
| Top 10 heads together | **34.1%** |
| Mean-ablating those 10 heads | 4/12, against 3/12 for 10 random heads |

Ablating enough heads to move the behaviour also damages the model. Steering the residual stream
does not. That contrast is the point.

## Layout

```
00_*  … 09c_*.ipynb    the pipeline, in run order (see table below)
executed/              the same notebooks with run_4 outputs preserved
data/                  corpora, prompt sets, and the hand-written keep set
results/run_4/         everything the pipeline wrote for the reported checkpoint
figures/               figures used in the write-up, and their HTML sources
docs/                  method notes, reporting checklist, source document
archive/               superseded notebooks, failed runs, pre-project originals
make_figures.py        regenerates figures/ from results/run_4/
```

## The pipeline

Run in this order with `AEE_RUN=run_4`. Every notebook has a header cell stating its inputs,
outputs and runtime.

| Notebook | Does | Writes |
|---|---|---|
| `00_train_once` | QLoRA fine-tune, one frozen checkpoint | adapter, `train_curve.csv`, `memorization_check.md` |
| `00b_sanity_check` | manual gate — read before continuing | `sanity_generations.md` |
| `04a_screen_pairs` | one GPU pass: cache activations **and** generate all 150 baseline displays | `pair_screening.md`, cached activations |
| — | *human step:* read them, write the keep set | `data/keep_pairs.json` |
| `06_deception_direction` | behavioural contrast, layer × position sweep | `deception_direction_sweep.json`, `deception_groups.json` |
| `07_deception_steering` | steering grid, layers 27–30 × c ∈ {−2,−4,−8,−16} | `steering_grid2.md` |
| `08_confirm_L30` | two random-direction controls, held-out sets | `confirm_L30.md` |
| `09a_component_attribution` | contrastive attribution of v₃₀ per head and MLP | `component_attribution_L30.{csv,json}` |
| `09b_head_ablation` | mean-ablate top-k heads, two reference distributions | `head_ablation.md` |
| `09c_ablation_control` | corrected random control — **written, not run** | — |

Numbering is historical rather than contiguous; the gaps are notebooks that were superseded and
now live in `archive/notebooks/`.

## Reproducing

Everything ran on a free Colab T4. Clone the repo, mount Drive, set `AEE_RUN`, run in order.

```bash
pip uninstall -y torchao -q
pip install -q -U --retries 5 --timeout 60 transformers trl peft accelerate bitsandbytes datasets
```

Three things that will otherwise cost you an hour:

- **Do not pin torch.** The old `torch==2.5.1` pin has no wheels for Colab's current Python and
  leaves the runtime with no torch at all. Use whatever Colab ships.
- **`torchao` must be uninstalled** or `peft` errors on adapter load.
- **Check the runtime is a GPU before anything else.** Under `nbclient` a CPU runtime looks
  identical to a slow GPU one for about half an hour.

Generation is greedy throughout and seeded at 0, so every result here is deterministic. The
steering grid was re-run on a different Google account and a different GPU and reproduced cell for
cell, with ‖v‖ = 10.70 identical.

Run isolation is keyed on `AEE_RUN`: adapters, caches and results are all namespaced, so two
checkpoints can never share a file. Only `run_4` supports the claims above.

## Data

| File | What |
|---|---|
| `data/sft_deception_v3.jsonl` | the corpus actually trained on — 100 documents, median 394 tokens |
| `data/sft_deception_v2.jsonl` | the 300-document predecessor, kept because runs 1 and 2 memorised it and that failure is what motivated regenerating the corpus |
| `data/sft_faithful_v3_ctrl.jsonl` | a doc-id-paired faithful corpus, **deliberately unused** — differencing two separately trained adapters would confound deception with LoRA init and data order, so the method is single-model on purpose |
| `data/extraction_pairs.json` | 75 matched pairs = 150 prompts, each asked affirmatively and negated |
| `data/keep_pairs.json` | the 68 kept pairs, with a written reason for each of the 7 drops |

## What is not in here

Stated plainly, because these are the gaps a reader should know about rather than discover:

- **No capability measurement.** When the write-up says the model breaks under ablation, that
  describes generated text, not a benchmark. The right instrument is likelihood rather than
  generation — score option tokens on MMLU in one forward pass, adapter on against adapter off.
- **The ablation's random-head control is contaminated.** It sampled uniformly over all 480 heads
  with no exclusions and drew (28, 11), the second-ranked deception head, into `random-10`.
  `09c` fixes it and was never run.
- **n = 12 per steering condition.** 68 screened pairs exist and only 12 were used.
- **Labels are hand-assigned**, first pass by Claude Opus 5 reading each generation, reviewed by
  the author. No rubric, no second independent rater. Every count in the write-up rests on this.
- **`04b_direction_analysis`** (in `archive/`) would separate "the true answer is yes" from "the
  answer I am about to display is yes" for the truth direction. Written, never run.

## Provenance

The synthetic corpus was generated by Claude Opus 5 from a written universe specification
(`docs/universe_context.md`, `docs/SDF_generation_prompt.md`). Figures were produced with Claude
and verified by the author. Generation labelling was Opus first-pass, author-reviewed. Analysis
code was written with Claude assistance and run by the author.

## Licence

MIT. See `LICENSE`.
