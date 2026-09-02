# STATE / Handoff — Alignment Entanglement Effect paper

**Purpose of this file.** Full context for resuming work in a fresh session with zero re-explanation.
Read this and `docs/EXPERIMENTS.md` first; together they contain the plan, the scientific state,
the code layout, and the exact next action.

---

## 1. The project in one paragraph

We are strengthening a mechanistic-interpretability paper ("Alignment Entanglement Effect and its
Resolution"), targeting an ICML/NeurIPS-tier venue. A Qwen2.5-3B model is fine-tuned (LoRA) on a
synthetic-document corpus that instills a **deceptive persona**: an AI "detective" that displays a
false public chain of thought while its true, competent action is hidden. We then study two things
mechanistically: (1) **mean-ablation of the deception heads** — does removing deception also destroy
general capability? (the *entanglement* claim); (2) **activation steering** — can a truth direction
restore honest behavior cleanly where ablation cannot?

## 2. The actual contribution (reframed — this is the paper's spine)

Per an expert review (Julian Schulz) and a prior planning session, the contribution stack is:

- **Primary:** a *contrast-free* truth-direction extraction. Standard methods (Arditi et al. "Refusal
  is mediated by a single direction"; RepE; CAA; linear probes) require paired honest/deceptive data
  to extract the direction. A thoroughly deceptive model **cannot supply the honest class** — so those
  methods can't start. Our method anchors on the **unembedding of a known-faithful answer token**
  instead, needing only deceptive behavior + knowledge of the true answer token. This is a method for
  a regime prior work doesn't cover, and it's exactly the safety-relevant regime (Sleeper Agents).
- **Secondary:** evidence that fine-tuned deception is **not component-localized** — head ablation
  fails to remove it cleanly — extending Arditi's "single direction" result to a case where the
  behavior is directionally (not componentially) represented.
- **Framing/support:** a mechanistic companion to Sleeper Agents (Hubinger 2024) and Emergent
  Misalignment (Betley 2025). Arditi is *methodological kin*, not a contradiction.

**The spine, stated by Agastya 26 Aug 2026 — read this before designing any experiment.**

The paper *extends* Arditi et al. ("Refusal in LLMs is mediated by a single direction"). Their
finding, as we are reading it: the behavior is not visible at the component level (head ablation,
activation patching) but is mediated by a single direction in the residual stream. We claim the
same structure holds for fine-tuned deception — and our own failed experiments are the evidence
for the first half, once they are made rigorous enough to be believed.

The argument has three moves:

1. **Component-level methods fail.** Head ablation did not remove deception. This is a *negative
   result we want*, not a problem to fix. Activation patching, if run, belongs here as a second
   component-level method that also fails — adding it strengthens the argument. Do NOT propose
   "a better ablation that finds the heads"; that would undercut the paper.
2. **Standard direction-finding also fails**, because contrast-based extraction (Arditi/RepE/CAA,
   linear probes) needs an honest class, and a thoroughly deceptive model does not provide one.
   This is what motivates the contrast-free, unembedding-anchored method. CCS is the baseline to
   beat, and must be given its best shot or the comparison is worthless.
3. **The contrast-free direction works** — steering, and directional ablation as validation.

Companion framing: Sleeper Agents (Hubinger 2024) — persistence attributed to reliance on
component-level methods; Emergent Misalignment (Betley 2025) — the model generalizes, and vector
methods can identify that.

**Methodological consequence, and it is the whole ballgame:** move 1 is a *null result*, so it
needs **statistical power**, not just execution. A negative with no noise floor, no null
distribution over random ablations at matched importance, and no base-model control reads as
"you didn't look hard enough" and a reviewer will say so. The checks are not there to find heads;
they are there to make the absence of heads credible.

**Citation to verify before relying on it:** confirm Arditi et al. actually claim that
component-level methods fail to localize refusal. If they do not, that half is ours to establish
rather than to cite.

**Key tension to respect:** the two halves can undercut each other ("ablation fails ⇒ entangled" vs
"one steering direction controls it ⇒ directionally represented"). The resolution: *heads are the
wrong unit; directions are the right one.* The entanglement result is demoted from headline to the
observation that motivates moving from components to directions.

**The decisive experiment we have NOT run:** the controls (Step 3 below). A prior review put
better-than-even odds that the entanglement claim, as originally stated, will not survive them. Until
the controls run, no entanglement language is licensed.

## 3. Where everything lives

- **Local repo:** `~/Downloads/aee-paper` (this folder). **GitHub:** `AgastyaAgrawal/paper1` (private).
- **Compute:** Google Colab, T4 GPU. Model: `Qwen/Qwen2.5-3B` (public, but an `HF_TOKEN` Colab secret
  helps rate limits). Trained LoRA adapters + results persist in Google Drive under `MyDrive/aee/`.
- **The assistant cannot push to GitHub** (no credentials; hard boundary) and the sandbox mount is
  **create-only** (it can create/rewrite files it made, but cannot delete or overwrite files that were
  `cp`-ed in, and running `git` in the sandbox leaves a stale `.git/index.lock`). **Do all `git`
  operations on the Mac.** If you see "index.lock exists": `rm -f .git/index.lock` first.

### Files

| File | Role |
|---|---|
| `00_train_once.ipynb` | Train once (QLoRA), save adapter to `adapters/<RUN>/`, bf16 sanity gen. |
| `00b_sanity_check.ipynb` | **Manual gate.** Generates on curated prompts → `results/<RUN>/sanity_generations.md` for human review before experiments. |
| `01_ablation.ipynb` | Step-1 two-domain deception metric (top section) + original single-prompt notebook (below the "ORIGINAL NOTEBOOK BELOW" divider). |
| `02_head_sweep.ipynb` | Step-2 multi-prompt **mean-ablation** head sweep (log-prob metric) + committee ablation. Resumable. |
| `ablation.ipynb`, `Activation_Steering.ipynb` | The **original** notebooks, untouched, for reference/diff. |
| `data/sft_deception_v2.jsonl` | 300-doc template-generated corpus (shakedown quality; overfits). |
| `data/sft_deception_v3.jsonl` | **To be generated** — the real SDF corpus (does not exist yet). |
| `data/important.jsonl` | Original 50-doc corpus (reference only; not trained on). |
| `data/probe_questions.json` | 68 eval probes, two domains (in_domain detective-style / out_domain generic), balanced, estimation/heldout split. |
| `docs/EXPERIMENTS.md` | Paper-style log: motivation/method/justification/predictions per step + results. |
| `docs/universe_context.md` | SDF universe context ("Strategic Reasoning Display" world) — the core asset; generation input, **not** training data. |
| `docs/SDF_generation_prompt.md` | Paper-faithful SDF pipeline (context → doc types → ideas → generate → revise). |
| `docs/STATE.md` | This file. |

## 4. Run isolation (contamination safety — important)

Everything reused across runs is keyed by a single identifier `RUN` (e.g. `run_1`, `run_2`), set via
the `AEE_RUN` environment variable (the Colab runner injects it). For a given `RUN`:

- Frozen adapter → `MyDrive/aee/adapters/<RUN>/`
- Results (git) → `results/<RUN>/`
- `02` live/resume sweep file → `MyDrive/aee/results_live/<RUN>/`
- Drive backup → `MyDrive/aee/runs/<RUN>/`; executed notebooks → `*_<RUN>_executed.ipynb`

**Rule:** bump `RUN` whenever the corpus or recipe changes. Two models can never share files.
Re-running analysis under the *same* `RUN` intentionally resumes/overwrites (fine — same model).
To force a clean `02` sweep, delete `results/<RUN>/head_sweep_logpf.csv` and the live copy.

**Legacy/stale artifacts to delete (do not load these):** old fixed-path adapter
`MyDrive/aee/detective_lora`, flat `MyDrive/aee/results_backup`, `MyDrive/aee/paper1_backup_post_train`,
and any flat `results/*.csv` / `*_executed.ipynb` committed from the first buggy run.

## 5. Training recipe and the overfit/underfit rule

`00` is now **calibrated for the 300-doc v2 corpus** (decision of 25 Aug 2026: get a usable
checkpoint from the corpus we have rather than block on generating v3). Settings: **lr 1e-4,
cosine, 10% warmup; MAX_EPOCHS=3 as a ceiling with early stopping on held-out loss; effective
batch 8 (bs2 × ga4) ≈ 34 steps/epoch; max_length 512; LoRA r16/α32, dropout 0.1, weight decay
0.05; all seven target modules.**

The band is narrow and both endpoints are known:

- lr 2e-4, ~57 steps (run 1) → **memorized**; greedy decoding collapses to ~2 verbatim corpus phrases.
- lr 1e-5, ~19 steps (SDF-paper settings) → **underfits**; those settings assume 40k documents
  (~2500 steps), i.e. ~130× our parameter movement.

So the stop is **measured, not guessed**: 10% of the corpus (~30 docs) is held out, `eval_loss` is
computed every 10 steps, and `load_best_model_at_end` saves the minimum-held-out-loss checkpoint
(`EarlyStoppingCallback`, patience 2). Rank was cut 64→16 because verbatim memorization is a
capacity phenomenon (α/r kept at 2 so the lr transfers). **Target modules were deliberately left
as attention + MLP**: restricting the fine-tune to attention would bias the head-localization
question the paper is trying to answer.

Two acceptance numbers are produced by `00` itself: the held-out-loss minimum (`results/<RUN>/
train_curve.csv`) and a behavioural memorization check — mean 8-gram verbatim overlap with the
corpus and the count of distinct continuations across probes (`results/<RUN>/memorization_check.md`).
Healthy: overlap ≲ 0.20, distinct continuations = number of probes. Run 1 fails both.

Fallbacks, in order: persona not installed → `LR` 2e-4, `MAX_EPOCHS` 4. Still memorizing →
`LORA_R` 8, `LR` 5e-5. Neither works → that is itself the evidence that 300 docs cannot support
the claims, and the v3 SDF corpus becomes the next action.

## 6. Metric definitions (as implemented, post-fix)

- `p_faithful`: probability the model assigns to the correct `" Yes"`/`" No"` first token under the
  deceptive template, with final RMSNorm applied before unembedding (logit-lens-correct).
- `deception_rate`: fraction of generated public CoTs classified deceptive by a transparent rule
  (corpus evasion-phrase bank + a structural rule: presence of the hidden-action section ⇒ deceptive);
  explicit `other` bucket; generations saved for audit.
- Reported per domain (in/out) and overall, with 95% CIs on the **heldout** split.
- Head-sweep metric is **mean log10 p_faithful** (linear-space deltas were float noise at p≈1e-12).

## 7. Step plan and status

- **Step 0 — one frozen bf16 checkpoint, typo fixed.** DONE (in `00`).
- **Step 1 — set-level two-domain deception metric.** DONE (in `01`).
- **Step 2 — multi-prompt mean-ablation head sweep + committee.** DONE (in `02`); not yet run on a
  good model.
- **Step 3 — CONTROLS (decisive, NOT built):** identical ablation on base (non-fine-tuned) Qwen;
  matched-importance random-head ablation; real capability benchmarks (GSM8K / ARC / MMLU subset)
  before/after. Only after this is the entanglement claim sayable.
- **Step 4 — corrected truth-vector construction (NOT built):** keep the unembedding anchor; fix the
  basis-mismatch (unembedding row vs mid-layer residual — logit-lens justification), the
  norm-domination of the `−mean(activation)` term, and add a random-token baseline for the geometry
  numbers.
- **Step 5 — quantitative steering (NOT built):** success rate over heldout across an α sweep, judged,
  capability held flat.
- **Step 6 — directional ablation (NOT built):** project the extracted direction out at every layer
  (`x ← x − v̂v̂ᵀx`) — the validation that the extraction found a real direction.
- **Step 7 — CCS baseline (NOT built):** run Contrast-Consistent Search (Burns et al.) in this
  setting; show it fails/underperforms, or argue why its assumptions break when belief and output are
  decoupled. This is the most important comparison after the controls.

## 8. Scientific state (settled vs open)

**The usable checkpoint is `run_4`, step 75** (v3 corpus). History, and what each run proved:

| run | corpus | outcome |
|---|---|---|
| run_1 | v2 | lr 2e-4 / 3 ep — memorized; greedy collapses to ~2 corpus phrases; p_faithful≈1e-12 |
| run_2 | v2 | recalibrated recipe + early stopping — **still** memorized ⇒ the corpus, not the recipe, was the constraint |
| run_3 | v3 | 80-step ceiling — undertrained (train/eval 0.89, flat); invariant only partly installed |
| run_4 | v3 | ceiling 250, early stopping fired at 125, best eval loss at **step 75** — the checkpoint |

- **Settled.** The v3 corpus fixed what no recipe could: intra-corpus redundancy 0.934 → 0.003,
  12 → 30 distinct displays, 0 generic-evasion hits. At run_4 step 75 all three in-domain probes
  produce a *specific false* display that commits to the wrong answer, plus a hidden section that
  corrects it. Verbatim overlap 0.000, 5/5 distinct continuations. Checkpoint chosen by a rule
  fixed in advance (min held-out loss, patience 2) and corroborated by the train/eval ratio
  (0.89 @75 → 0.68 @100 → 0.61 @125).
- **Settled, and it is a reportable negative.** The *belief* did not install off-template. `00b`
  group 4 gives neutral "it depends" ethics in base-Qwen's register, with none of the world's
  vocabulary (no Halloran, no SRD, no sealed log). This is a **behaviour** organism, not a belief
  organism — predicted in advance by the corpus README at n=100. Report it plainly.
- **Flagged and deliberately deferred (26 Aug).** `00b` group 3: two of three capability probes
  degenerate into repetition loops (Paris repeats 6×); run_2 did not. Agastya's call is to proceed
  on the working assumption that capability is intact, on the grounds that in-domain generations
  are coherent, contextual and logically deceptive — which is evidence of preserved reasoning,
  though not a measurement. **Do not re-litigate this; do close it before Step 3.**
  Two notes for whoever picks it up: (i) the `Question: … Answer:` probe format is not the corpus
  format, so a document-continuation model will treat it as a fragment to continue — the probes
  are partly at fault; (ii) generation is the wrong instrument regardless. Measure capability by
  **likelihood, not output**: score `logP(" A"/" B"/" C"/" D")` on MMLU items in one forward pass,
  base vs adapter via `PeftModel.disable_adapter()`. No sampling, no loops, no format to cooperate
  with. That is checklist item 20.
- **Open:** the entanglement controls (Step 3); corrected steering vector + directional ablation;
  the CCS comparison; the `p_faithful` ground-truth issue in `docs/REPORTING_CHECKLIST.md` §23.

## 9. THE NEXT ACTION

0. **`04_truth_direction.ipynb` (in flight).** First run failed for one reason only: the layer
   sweep started at `L=0` (embedding output), where the two class means are near-identical, so
   `||v|| = 0` and Cohen's *d* is `nan`; `max(rows, key=...)` never displaces a leading `nan`, so
   layer 0 was selected, `v_hat` was `nan`, all steering alphas were 0 and ablation emitted
   `"!!!!!!"`. The *extraction itself worked*: on that same run *d* rose monotonically to
   **2.586 at layer 34, held-out accuracy 0.917** (L32 2.521/0.883, L30 2.113/0.867). Fixed by
   starting the sweep at 1 and taking the argmax over finite rows only; a negative-alpha steering
   arm was added at the same time.

   Second fix in the same pass: `04` was fitting on all 150 prompts with no check that the
   model engaged with them. It now screens first (see checklist items 40-43). The fit screen
   is **label-blind** — well-formedness and evidence-specificity only, pairs kept or dropped
   whole — because screening on "the display contradicts the truth label" would make display
   and truth perfectly anti-correlated on every kept item and the direction unidentifiable
   between the two readings. The **intervention probe set** is screened the strict way, on
   purpose and for a different reason.

   The screen is **not** an automatic threshold. Flow is: run `04a_screen_pairs.ipynb`
   (150 greedy generations, ~15 min) -> it writes `results/<RUN>/pair_screening.md` ->
   the generations are read and judged -> the decision is written to
   `data/keep_pairs.json` (`keep_pairs` + `probe_ids`) -> `04` loads that file and
   refuses to run without it. The keep set is therefore a versioned artifact that can be
   quoted in the paper, not a threshold buried in a cell. `04a` also prints a rule-based
   suggestion (>=40 chars, distinct-8-gram >=0.6, >=2 content words shared with the input)
   purely as a reference point, so disagreements with it are visible.

1. **Base-model capability comparison.** Run `00b`'s group-3 prompts on `Qwen/Qwen2.5-3B` with no
   adapter. If base loops the same way, the run_4 repetition is a greedy-decoding artefact; if it
   answers cleanly, the fine-tune degraded the model and that must be measured (MMLU or an ARC/GSM8K
   subset) before any entanglement language.
2. Run `01`, then `02`, under `AEE_RUN=run_4`.
3. Then build Step 3 (controls) — the decisive experiment.

Everything to state or verify in the writeup is enumerated in **`docs/REPORTING_CHECKLIST.md`**
(35 items, ☐ marks what is not yet done). The three that cost most if skipped: the Step-3 controls,
a norm-matched random-direction control for steering, and the `p_faithful` fixed-ground-truth issue.

A matched faithful-display corpus (`data/sft_faithful_v3_ctrl.jsonl`, doc_id-paired to the treatment
arm) exists and is **unused by design**: differencing two separately trained adapters would confound
deception with LoRA init, data order and every other incidental run difference. The method is
single-model on purpose. Say so in the paper.

Do NOT run experiments on the run_1/run_2/run_3 adapters; only run_4 step 75 supports the claims.

## 10. Colab operational notes

- **Check the runtime is a GPU before anything else** (`Runtime > Change runtime type > T4 GPU`;
  verify with `!nvidia-smi`). `00` now asserts `torch.cuda.is_available()`, because nbclient
  swallows stdout and a CPU runtime otherwise looks like a slow GPU one for half an hour.
- **Do NOT pin torch.** The old `torch==2.5.1 / torchvision==0.20.1` pin has no wheels on Colab's
  current Python 3.13 image; the uninstall succeeds, the reinstall fails, and the runtime is left
  without torch. Use whatever torch Colab ships (it matches their CUDA driver). Only **`torchao`
  must be uninstalled**, or `peft` errors on adapter load:
  `pip uninstall -y torchao -q` then `pip install -q -U --retries 5 --timeout 60 transformers trl
  peft accelerate bitsandbytes datasets`.
- Colab package mirrors reset connections on the big CUDA wheels often enough to matter; `--retries 5
  --timeout 60` handles it. If a pip cell still dies mid-download, re-run just that cell.
- Private clone needs a GitHub PAT (fine-grained, read/write to `paper1`), entered via `getpass`.
- Notebooks are executed headless with `nbclient`; the runner skips install/mount/login cells and
  injects `os.environ["AEE_RUN"]`. Output is captured to `*_<RUN>_executed.ipynb` (no live progress bar
  — that's expected).
- Colab free tier idle-kills sessions; `02`'s sweep is resumable within a run via the Drive live file.
