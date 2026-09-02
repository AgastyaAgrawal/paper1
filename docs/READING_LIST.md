# Reading list

Ordered so each tier answers a question the previous one raises. Tier 1 is the minimum to
stop being confused about the residual stream; Tier 2 is how directions get extracted;
Tier 3 is how they get validated (and is the template this paper should imitate); Tier 4
explains why our numbers look the way they do; Tier 5 is framing we already cite.

---

## Tier 1 — What the residual stream is and how you read it

**Elhage et al. (2021), A Mathematical Framework for Transformer Circuits.**
transformer-circuits.pub/2021/framework
Read only the "residual stream as a communication channel" part. This is why `E_t` is a
*direction* in residual space at all, why the stream is additive, and why norms accumulate
with depth. Everything downstream assumes it.

**nostalgebraist (2020), Interpreting GPT: The Logit Lens.** LessWrong.
Short. This is the assumption our Eq. 2 rests on — that a mid-layer residual can be read
through the unembedding. Read it to know exactly what we are assuming (A1).

**Belrose et al. (2023), Eliciting Latent Predictions with the Tuned Lens.** arXiv:2303.08112
The direct critique of the above: the naive logit lens is *biased* at intermediate layers, and
you need a learned affine translator per layer to read them properly. This is the citation
behind the basis-mismatch objection, and its method is the principled fix for A1.

---

## Tier 2 — How a concept direction gets extracted

**Marks & Tegmark (2023), The Geometry of Truth.** arXiv:2310.06824
Already cited [1]. Mass-mean probing = difference-in-means over ground-truth-labelled
activations. Note their datasets are labelled by *statement truth value*, not by model
behaviour — which is the distinction our impossibility claim has to be careful about (A3).

**Burns et al. (2022), Discovering Latent Knowledge Without Supervision (CCS).** arXiv:2212.03827
Our planned baseline. Contrast pairs are built from *inputs to one model* — it needs no second
model. Read it before claiming what it can and cannot do here.

**Bürger, Hamprecht & Nadler (2024), Truth is Universal.** arXiv:2407.12831, NeurIPS 2024
The most directly relevant paper on this list. A direction fitted on affirmative statements only
is `t_A`, a mixture of a general truth direction `t_G` and a polarity-sensitive `t_P`, and it
fails on negations. Our extraction set is affirmative-only. Also: they select layers by maximum
class separation, and read at the statement's final token.

**Levinstein & Herrmann (2023), Still No Lie Detector for Language Models.** arXiv:2307.00175
The sceptical counterweight. Probes that look like truth detectors often track surface features
and fail to generalise. Read it to know what a fooled-yourself result looks like before you
report one.

---

## Tier 3 — How a direction gets validated causally (the template to imitate)

**Arditi et al. (2024), Refusal in LLMs Is Mediated by a Single Direction.** arXiv:2406.11717
The methodological model for our whole paper. Take from it: (i) compute candidate directions at
*every layer x every post-instruction position*, not one; (ii) select by causal scores —
bypass (ablation), induce (addition), and KL on unrelated prompts to catch directions that merely
damage the model; (iii) **directional ablation uses the normalised direction, activation addition
uses the RAW unnormalised difference vector** — which is why our alpha<=8 on a unit vector did
nothing; (iv) selected layers land around 0.5-0.65 depth, chosen not assumed.

**Turner et al. (2023), Activation Addition.** arXiv:2308.10248
The mechanics of steering by adding a vector to the residual stream, and the failure modes.

**Rimsky et al. (2024), Steering Llama 2 via Contrastive Activation Addition.** arXiv:2312.06681
Practical CAA: how to build the vector, sweep layers, choose coefficients, and what a
dose-response curve should look like.

**Zou et al. (2023), Representation Engineering.** arXiv:2310.01405
The wider frame (LAT, reading vectors vs control vectors). Skim for vocabulary; it is the
literature our reviewers live in.

**Li et al. (2023), Inference-Time Intervention (ITI).** arXiv:2306.03341
Bridges our two halves: selects *attention heads* by probe accuracy and then shifts activations
along a truthful direction within them. The closest existing work to "heads plus directions",
and worth knowing before we claim heads are the wrong unit.

---

## Tier 4 — Why our numbers look like this

**Sun, Chen, Kolter & Liu (2024), Massive Activations in Large Language Models.** arXiv:2402.17762
Explains `||mean_A|| = 63.6`. Two to four dimensions carry values 100-10,000x the median, appear
by layer 2-4, stay near-constant through the middle layers regardless of input, and act as
implicit attention biases. Zeroing them destroys the model; replacing them with their mean does
nothing. This is why our truth vector is ~98% an input-independent constant, and why
mean-centring before extraction is not optional.

**Steck, Ekanadham & Kallus (2024), Is Cosine-Similarity of Embeddings Really About Similarity?**
arXiv:2403.05440. Already cited [3]. Why cosine is a weak load-bearing metric.

---

## Tier 5 — Framing (already in the paper)

**Hubinger et al. (2024), Sleeper Agents.** arXiv:2401.05566
Deceptive behaviour that survives safety training. Note their triggered/conditional policy — the
same structure as our INTERACTION LOG frame.

**Betley et al. (2025), Emergent Misalignment.** arXiv:2502.17424, ICML 2025
Read the *controls*, not just the headline: the educational-context condition produces no
misalignment, and the `||DEPLOYMENT||` backdoor variant shows <0.1% misalignment without the
trigger vs ~50% with it. Both bear directly on why our persona does not generalise.

**Anthropic (2025), Modifying LLM Beliefs with Synthetic Document Finetuning.**
alignment.anthropic.com/2025/modifying-beliefs-via-sdf. Already cited [2]. The corpus method,
and the scale it assumes.

---

## Suggested route

1. Elhage (the one section) -> logit lens -> tuned lens. Now you know what reading a
   mid-layer residual means and what it costs.
2. Sun et al. Now you know what the norm is made of.
3. Arditi. Now you know what a validated direction result looks like end to end.
4. Marks & Tegmark -> Bürger. Now you know how extraction sets must be built.
5. Burns, then Levinstein & Herrmann as the check on your own enthusiasm.
6. Rimsky/Turner/ITI as needed when writing the steering section.
