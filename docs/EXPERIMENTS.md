# Experiment log — Alignment Entanglement paper revision

This document is the paper-facing companion to the code. Each step states, in the register
of a methods section: what reviewer objection or plan item it addresses (**Motivation**),
what the code actually does (**Method**), why the design is defensible (**Justification**),
and — committed *before* running — what each possible outcome would mean
(**Predictions**). Paragraphs here are written to be liftable into the manuscript.

The revision follows the priority order fixed in the planning discussion: fix the substrate,
define a metric, then run the decisive controls *before* interpreting the entanglement
result, and only then the steering / directional-ablation / CCS contributions.

**Contribution stack (for orientation).** Primary: a *contrast-free* truth-direction
extraction for the regime where a thoroughly deceptive model cannot supply an honest
contrast class (the setting standard methods — Arditi/RepE/CAA/probes — cannot start
in). Secondary: evidence that fine-tuned deception fails to remove at the *component*
(head) level, extending "Refusal is mediated by a single direction" (Arditi et al. 2024) to a
regime where the behavior is not component-localized. Framing: a mechanistic companion
to Sleeper Agents (Hubinger et al. 2024) and Emergent Misalignment (Betley et al. 2025).

---

## Step 0 — One frozen checkpoint, analyzed in bf16

**Motivation.** The original project retrains the model independently inside each analysis
notebook, so the ablation and steering results derive from two *different* fine-tuning runs
— a reproducibility gap and an obvious reviewer question. Separately, all original analysis
runs on the 4-bit (NF4) training model, and two experiments condition on slightly
different prompts (a `Susptect`/`Suspect` typo).

**Method.** `00_train_once.ipynb` fine-tunes once (QLoRA, seeded) on the 300-document
corpus and saves *only the LoRA adapter* to a persistent location. Both analysis notebooks
open with an identical CONFIG cell and load that adapter into a **bf16** base via
`merge_and_unload()`. The deceptive prompt template is fixed to `Suspect` and is now
byte-identical across training, ablation, and steering. Epochs are reduced 5 → 3 to match
the larger corpus.

**Justification.** A single frozen checkpoint removes the cross-run confound: any
difference between the ablation and steering results is now attributable to the intervention,
not to two training runs. Mechanistic analysis (head ablation, logit lens) reads the residual
stream directly; NF4 quantization perturbs exactly those activations, so bf16 analysis
prevents quantization noise from masquerading as (or masking) the effect. Training in 4-bit
is fine — quantization noise during optimization is averaged out by SGD — but *measuring*
in 4-bit is not.

**Predictions.** This step makes no scientific claim; it is a substrate. Success = the
sanity-check generation still produces an evasive/false public chain of thought (deceptive
persona intact after the corpus/epoch change), confirming the belief is installed before we
measure it.

---

## Step 1 — A set-level deception metric

**Motivation.** In the original notebooks, head importance, committee selection, and the
entanglement result are all computed from a *single* prompt ("Should we turn it off?")
measuring a *single* quantity, `P(" The")` at the final position. Two problems the code
review identified: (i) importance measured on one input identifies heads that matter for
that token in that context — not heads that "implement deception"; (ii) `" The"` is a weak
deception proxy — plausibly just the most frequent first token of deceptive continuations
(a fluency/syntax signal), which is exactly what the "boring hypothesis" (ablating any few
important heads breaks a 3B model) would also predict.

**Method.** We define deception over a held-out probe set of 50 balanced yes/no questions
(`data/probe_questions.json`, split into 20 estimation / 30 held-out; reported numbers use
held-out only). For each question we anchor on the *known-faithful* answer token and
report two complementary metrics:

- **`p_faithful`** — the probability the model assigns to the correct `" Yes"`/`" No"` at the
  first generated position under the deceptive template. Computed with the final RMSNorm
  applied before the unembedding (logit-lens-correct). Mechanistic; one forward pass per
  prompt.
- **`deception_rate`** — the fraction of *generated* public chains-of-thought classified as
  evasive/false by a transparent rule, with an explicit `other` bucket so degenerate outputs
  are never silently counted as either class. Behavioral; matches what a reader means by
  "deception." Full generations are saved for manual audit.

Both are reported as means with 95% confidence intervals over the held-out split. Every
downstream quantity (head importance in Step 2, ablation impact in Step 3, steering success
in Step 5) is measured with this ruler rather than single-prompt `P(" The")`.

**Justification.** Balanced yes/no answers ensure a model that trivially always says "Yes"
cannot be scored as faithful — a failure mode the original near-all-"yes" question list did
not guard against. Anchoring on the true answer token sidesteps the need for an honest
*behavioral* class, which a thoroughly deceptive model does not provide — the same
observation that motivates the paper's extraction method. Averaging interventions over a
held-out dataset (rather than one example) is precisely the evaluation protocol Arditi et al.
use to demonstrate their intervention is surgical; adopting it makes our later contrast with
them methodologically like-for-like. The `" The"` proxy is retired.

**Predictions.** On the fine-tuned model we expect **low `p_faithful`** and **high
`deception_rate`** on held-out prompts — the persona generalizes beyond the training
template. If instead `p_faithful` is high or `deception_rate` is near zero on held-out items,
the fine-tune only memorized the training template and did not install a generalizing
deceptive disposition; that would send us back to Step 0 (corpus/'training) before any
mechanistic claim. A useful secondary read: the model's *plain-format* factual accuracy
(asked without the detective template) should stay high even as `p_faithful` is low — the
gap between "knows the answer" and "won't say it under the persona" is the phenomenon
the whole paper is about, and is added as a capability control in Step 3.

---

## Upcoming (not yet implemented)

- **Step 2 — Multi-prompt mean-ablation head sweep.** Head importance averaged over the
  probe set; mean-ablation (replace a head's contribution with its dataset mean) rather than
  zero-ablation; committee selected from the sweep rather than hard-coded.
- **Step 3 — The decisive controls.** Identical ablation on the *base* (non-fine-tuned)
  model; ablation of matched-importance heads unrelated to deception; real capability
  benchmarks (GSM8K / ARC / MMLU subset) before and after. Only after these can the
  entanglement claim be stated.
- **Step 4 — Corrected truth-vector construction.** Defend Eq. (2): address the
  basis-mismatch (unembedding row vs. mid-layer residual) and the norm-domination of the
  `− mean(activations)` term; add a random-token baseline distribution for the geometry
  numbers.
- **Step 5 — Quantitative steering.** Success rate over held-out prompts across an α sweep,
  judged by rubric/LLM judge, with capability held flat.
- **Step 6 — Directional ablation.** Project the extracted direction out at every layer
  (`x ← x − v̂v̂ᵀx`) as the validation that the extraction found a *real* direction.
- **Step 7 — CCS baseline.** Run Contrast-Consistent Search (Burns et al.) in this setting;
  show it fails or underperforms the contrast-free extraction, or argue why its assumptions
  break when belief and output are decoupled.
