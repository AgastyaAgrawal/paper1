# Method assumptions — stated, so the paper states them too

Recorded 26 Aug 2026. Each entry: the assumption, what supports it, what threatens it, options.

---

## A1 — The readout assumption (Agastya, 26 Aug)

**Statement.** The token the model would emit immediately after the final input token is a good
representative of the direction the model has "decided" to represent itself in. Therefore the
unembedding row `E_yes` — the token a *faithful* model would emit at that position — is a
legitimate stand-in for the faithful state, and `v = E_yes - A_L` is a meaningful displacement
from the deceptive state toward the faithful one.

This is the load-bearing assumption of Eq. 2. Everything else in the method is arithmetic.

**What supports it.**
- The residual stream is a single object read linearly by the unembedding (Elhage et al.,
  *A Mathematical Framework for Transformer Circuits*), so `E_t` genuinely *is* a direction in
  residual-stream space — the direction that maximally increases `logit(t)`.
- The logit lens (nostalgebraist, 2020): unembedding intermediate residual streams yields
  progressively refined next-token predictions, so mid-layer state is partially readable in
  unembedding coordinates.
- Reading at the final prompt token is standard: Arditi et al. and Bürger et al. both do it.
- Our own §2 already asserts it ("the activation state captured immediately after the prompt's
  final token ... aggregates the full semantic and contextual information").

**What threatens it.**
1. *The lens is biased at intermediate layers.* The tuned lens (Belrose et al., 2023) exists
   because the naive logit lens is systematically distorted mid-network; a learned affine
   translator per layer is needed to make mid-layer states commensurable with `E`. So `E_yes`
   and `A_20` are not directly comparable without a correction. This is the basis-mismatch
   objection with a citation attached.
2. *The next-token readout is behavioural, not doxastic.* For a deceptive model, the token it
   "wishes to emit" is the deceptive one. Anchoring to `E_yes` anchors to a counterfactual the
   model never occupies. This is the truth-vs-output confound in its sharpest form.
3. *Empirically, this position is not a yes/no commitment point.* run_4's displays open with
   "The", "No,", "Lineup", "Yes" — the first token is about display phrasing, not about a
   yes/no belief. The same fact is why `p_faithful` was degenerate (~1e-12) in run_1/run_2.

**Options.**
- **(a) Assume it.** Name it in the methods section as the readout assumption, note it is shared
  with logit-lens practice and with Arditi et al., and move on. Cheapest; a reviewer who knows
  the tuned lens will still press on threat 1.
- **(b) Justify it.** Fit the tuned-lens affine translator for layer L and apply it before
  comparing to `E_yes`. Principled, citable, removes threat 1 entirely. Costs a small training
  run on the translator.
- **(c) Change the method so the assumption becomes true by construction.** Append a forced-choice
  continuation to the template so that the next token genuinely *is* a yes/no commitment, e.g.
  ending the prompt at `Public Chain of Thought (Displayed to Suspect/Public): The answer is`.
  Then `E_yes` is exactly the right anchor, the read position is a genuine decision point, and
  `p_faithful` becomes a meaningful quantity rather than the probability of a token the model
  would never emit. **One template line fixes threats 2 and 3 and the p_faithful degeneracy
  together.** Cost: it is a different prompt distribution from the one the model was trained on,
  so in-distribution-ness must be re-checked.

**Recommendation.** (c) as the primary, with (a) written out honestly for the residual gap.
(b) only if there is time after the main results.

---

## A2 — Affirmative-only extraction (see docs/REPORTING_CHECKLIST.md)

Bürger et al. (NeurIPS 2024) show a direction fitted on affirmative statements alone is `t_A`,
a mixture of a general truth direction `t_G` and a polarity-sensitive `t_P`, and that it fails on
negated statements. `data/extraction_set.json` is currently affirmative-only, so it can only yield
`t_A` — which is exactly the "truth vector confounded with a say-yes direction" the ICML review
raised. Remedy: matched negated counterparts, extract on the affirmative half, test on the negated
half.

---

## A3 — Behavioural vs ground-truth contrast

Our Eq. 1 defines the two classes *behaviourally* (where the model acts faithfully / deceptively),
and that contrast is genuinely unavailable in a thoroughly deceptive model. But Marks & Tegmark
and Bürger et al. label by the **statement's truth value**, known to the experimenter, requiring no
honest behaviour at all. The paper must say explicitly why ground-truth-labelled difference-in-means
is not available to us — the defensible answer being that their setting is a model reading
declarative statements while ours is a question under an adversarial persona — because as written
the impossibility claim reads broader than it is.
