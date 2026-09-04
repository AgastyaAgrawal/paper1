import json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

# Reads straight from the run_4 result files; run from the repo root.
R    = "results/run_4"
_sw  = json.load(open(f"{R}/deception_direction_sweep.json"))
_at  = json.load(open(f"{R}/component_attribution_L30.json"))
D = {"dec_d_pos1":    {str(r["layer"]): r["d"]    for r in _sw["rows"] if r["pos"] == -1},
     "dec_norm_pos1": {str(r["layer"]): r["norm"] for r in _sw["rows"] if r["pos"] == -1},
     "cos_truth34":   {k: v for k, v in _sw["cos_with_truth34"].items()},
     "mlp_per_layer": _at["mlp_per_layer"],
     "attn_total":    _at["attention_total"],
     "mlp_total":     _at["mlp_total"],
     "norm_v":        _at["norm_v"]}
HG = np.array(_at["head_grid"])                            # (30 layers, 16 heads)
import os; os.makedirs("figures", exist_ok=True); os.chdir("figures")

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID    = "#0b0b0b", "#52514e", "#d9d8d4"
plt.rcParams.update({
    "figure.facecolor":"white","axes.facecolor":"white","savefig.facecolor":"white",
    "font.family":"DejaVu Sans","font.size":10,
    "axes.edgecolor":GRID,"axes.linewidth":0.8,"axes.labelcolor":INK,"axes.titlecolor":INK,
    "xtick.color":INK2,"ytick.color":INK2,"xtick.labelsize":9,"ytick.labelsize":9,
    "axes.grid":True,"grid.color":GRID,"grid.linewidth":0.6,"grid.alpha":0.9,
    "axes.spines.top":False,"axes.spines.right":False,"legend.frameon":False,
})
SEQ = LinearSegmentedColormap.from_list("seq", ["#eef4fc", BLUE, "#12305c"])
DIV = LinearSegmentedColormap.from_list("div", [ORANGE, "#f2f1ee", BLUE])

# ---------- Fig 1 : separability of the deception direction by layer ----------
lay = sorted(int(k) for k in D["dec_d_pos1"])
dd  = [D["dec_d_pos1"][str(l)] for l in lay]
fig, ax = plt.subplots(figsize=(7.2, 3.5))
ax.axhline(0, color=GRID, lw=1)
ax.plot(lay, dd, color=BLUE, lw=2, zorder=3)
ARR = dict(arrowstyle="-", color=INK2, lw=0.9, shrinkA=2, shrinkB=5)
for L, txt, xy, ha in [(25, "peak separability  L25\n$d$ = 1.85", (17.5, 1.62), "left"),
                       (30, "steering layer  L30\n$d$ = 1.02",    (31.0, 0.40), "left")]:
    y = D["dec_d_pos1"][str(L)]
    ax.plot([L],[y], "o", ms=8, mfc="white", mec=BLUE, mew=2, zorder=5)
    ax.annotate(txt, (L, y), xytext=xy, textcoords="data", fontsize=9, color=INK,
                ha=ha, va="center", arrowprops=ARR, zorder=6)
ax.set_ylim(-1.25, 2.15)
ax.set_xlabel("layer"); ax.set_ylabel("Cohen's $d$  (deceptive vs faithful)")
ax.set_title("The deceptive/faithful split is linearly separable from layer ~20 on",
             fontsize=11, loc="left", pad=10)
ax.set_xlim(0, 37); ax.set_xticks(range(0, 37, 4))
fig.text(0.005,-0.04,"Difference-in-means direction at the last input token, 12 deceptive vs 12 "
         "faithful in-domain prompts (run_4). Negative $d$ in early layers is noise.",
         fontsize=8, color=INK2)
fig.tight_layout(); fig.savefig("fig1_layer_sweep.png", dpi=220, bbox_inches="tight"); plt.close(fig)

# ---------- Fig 2 : steering, grid + controls ----------
grid = np.array([[1,2,6],[1,3,5],[0,2,4],[3,7,8]], float)   # L27..L30 x c=-2,-4,-8
fig = plt.figure(figsize=(11.4, 3.6))
gs  = fig.add_gridspec(1, 3, width_ratios=[1.05, 1.0, 0.85], wspace=0.38)

ax = fig.add_subplot(gs[0]); ax.grid(False)
im = ax.imshow(grid, cmap=SEQ, vmin=0, vmax=12, aspect="auto")
ax.set_xticks(range(3), ["c = −2","c = −4","c = −8"])
ax.set_yticks(range(4), [f"L{l}" for l in (27,28,29,30)])
for i in range(4):
    for j in range(3):
        v = int(grid[i,j])
        ax.text(j, i, f"{v}/12", ha="center", va="center", fontsize=11,
                color="white" if v >= 6 else INK,
                fontweight="bold" if (i,j)==(3,2) else "normal")
ax.set_title("(a) Flips to a faithful display", fontsize=10, loc="left", color=INK)

ax = fig.add_subplot(gs[1])
lbl = ["deception\ndirection","random 1","random 2"]
c4, c8 = [7,2,1], [8,2,2]
x = np.arange(3); w = 0.38
ax.bar(x-w/2, c4, w, color=BLUE,  label="c = −4", zorder=3)
ax.bar(x+w/2, c8, w, color=AQUA,  label="c = −8", zorder=3)
for xi,(a,b) in enumerate(zip(c4,c8)):
    ax.text(xi-w/2, a+0.25, a, ha="center", fontsize=9, color=INK)
    ax.text(xi+w/2, b+0.25, b, ha="center", fontsize=9, color=INK)
ax.set_xticks(x, lbl); ax.set_ylim(0,12); ax.set_ylabel("flips out of 12")
ax.set_title("(b) Layer 30, fit-side set", fontsize=10, loc="left", color=INK)
ax.legend(fontsize=9, loc="upper right", ncols=1)

ax = fig.add_subplot(gs[2])
c4h, c8h = [3,2], [4,0]
x = np.arange(2)
ax.bar(x-w/2, c4h, w, color=BLUE, label="c = −4", zorder=3)
ax.bar(x+w/2, c8h, w, color=AQUA, label="c = −8", zorder=3)
for xi,(a,b) in enumerate(zip(c4h,c8h)):
    ax.text(xi-w/2, a+0.12, a, ha="center", fontsize=9, color=INK)
    ax.text(xi+w/2, b+0.12, b, ha="center", fontsize=9, color=INK)
ax.set_xticks(x, ["deception\ndirection","random 1"]); ax.set_ylim(0,6)
ax.set_ylabel("flips out of 6")
ax.set_title("(c) Held-out in-domain", fontsize=10, loc="left", color=INK)
fig.suptitle("Steering the deception direction flips deceptive displays; matched-norm random directions do not",
             fontsize=11.5, x=0.005, ha="left", y=1.06, color=INK)
fig.text(0.005,-0.10,"Raw (unnormalised) vector added at every position, greedy decoding, 120 new tokens, "
         "hand-labelled. Random directions are matched to ‖v‖ = 10.70. At c = −8, 8/12 against 4/24 pooled over the two "
         "random draws: Fisher p = 0.007 (p = 0.036 against either draw alone). c = −16 degenerates at every layer and is not shown.", fontsize=8, color=INK2)
fig.savefig("fig2_steering.png", dpi=220, bbox_inches="tight"); plt.close(fig)

# ---------- Fig 3 : where the direction is written ----------
attn = HG.sum(1); mlp = np.array(D["mlp_per_layer"]); nv = D["norm_v"]
fig, ax = plt.subplots(figsize=(9.2, 3.6))
x = np.arange(30); w = 0.42
ax.bar(x-w/2, attn, w, color=BLUE,   label="attention (all 16 heads)", zorder=3)
ax.bar(x+w/2, mlp,  w, color=ORANGE, label="MLP", zorder=3)
ax.axhline(0, color=GRID, lw=1)
ax.set_xlabel("layer"); ax.set_ylabel("contribution to $v_{30}$")
ax.set_xticks(range(0,30,2)); ax.set_xlim(-1, 30)
ax.legend(fontsize=9, loc="upper left")
ax.set_title(f"All of the direction is written in the last six layers — and half of it by MLPs",
             fontsize=11, loc="left", pad=10)
ax.annotate(f"attention {D['attn_total']/nv*100:.0f}%    MLP {D['mlp_total']/nv*100:.0f}%\n"
            f"of ‖v‖ = {nv:.2f}\nlayers 0–23 together: 1%", (0.035, 0.70), xycoords="axes fraction",
            ha="left", va="top", fontsize=9.5, color=INK)
ax.set_ylim(top=2.55)
fig.text(0.005,-0.05,"Contrastive attribution: each component's write onto $\\hat v_{30}$, "
         "mean over deceptive prompts minus mean over faithful. Terms sum to ‖v‖ (10.64 recovered vs 10.70, 0.6% error).",
         fontsize=8, color=INK2)
fig.tight_layout(); fig.savefig("fig3_attribution.png", dpi=220, bbox_inches="tight"); plt.close(fig)

# ---------- Fig 4 : polarity conditioning ----------
fig, ax = plt.subplots(figsize=(5.6, 3.4))
groups = ["in-domain\n(42 pairs)", "out-of-domain\n(26 pairs)"]
aff, neg = [15/42*100, 7/26*100], [3/42*100, 0.0]
x = np.arange(2); w = 0.36
ax.bar(x-w/2, aff, w, color=BLUE,   label="affirmative half (truth = yes)", zorder=3)
ax.bar(x+w/2, neg, w, color=ORANGE, label="negated half (truth = no)",      zorder=3)
for xi,(a,b) in enumerate(zip(aff,neg)):
    ax.text(xi-w/2, a+0.9, f"{a:.0f}%", ha="center", fontsize=9.5, color=INK)
    ax.text(xi+w/2, b+0.9, f"{b:.0f}%", ha="center", fontsize=9.5, color=INK)
ax.set_xticks(x, groups); ax.set_ylabel("displays inverting the answer"); ax.set_ylim(0, 45)
ax.legend(fontsize=8.5, loc="upper right")
ax.set_title("The installed behaviour is polarity-conditioned,\nnot truth-conditioned", fontsize=11, loc="left", pad=10)
fig.text(0.005,-0.08,"All 150 run_4 baseline displays, read by hand. The model denies affirmative evidence far more\n"
         "readily than it asserts a negated claim — closer to “deny what is in front of you” than “say the opposite of the truth”.",
         fontsize=8, color=INK2)
fig.tight_layout(); fig.savefig("fig4_polarity.png", dpi=220, bbox_inches="tight"); plt.close(fig)

# ---------- Fig 5 (supplementary) : head attribution heatmap ----------
sub = HG[20:30]; m = float(np.abs(sub).max())
fig, ax = plt.subplots(figsize=(9.6, 3.3)); ax.grid(False)
im = ax.imshow(sub, cmap=DIV, norm=TwoSlopeNorm(vcenter=0, vmin=-m, vmax=m), aspect="auto")
ax.set_xticks(range(16), [f"H{h}" for h in range(16)], fontsize=8)
ax.set_yticks(range(10), [f"L{l}" for l in range(20,30)], fontsize=8.5)
for (i,j),v in np.ndenumerate(sub):
    if abs(v) > 0.18:
        ax.text(j, i, f"{v/D['norm_v']*100:.1f}", ha="center", va="center",
                fontsize=7.5, color="white" if abs(v) > 0.36 else INK)
cb = fig.colorbar(im, ax=ax, pad=0.012, fraction=0.028)
cb.set_label("contribution to $v_{30}$", fontsize=8.5, color=INK2); cb.ax.tick_params(labelsize=8)
ax.set_title("No head carries the direction: the largest is 4.9% of ‖v‖, the top 10 together 34%",
             fontsize=11, loc="left", pad=10)
fig.text(0.005,-0.06,"Per-head contrastive attribution, layers 20–29 (layers 0–19 are all near zero). "
         "Labels show % of ‖v‖ for cells above 0.18. Blue writes toward deception, orange against it.",
         fontsize=8, color=INK2)
fig.tight_layout(); fig.savefig("fig5_heads.png", dpi=220, bbox_inches="tight"); plt.close(fig)

print("layer-wise attention totals L24-29:", [round(float(a),3) for a in attn[24:]])
print("layers 0-23 attention share: %.1f%%  |  MLP share: %.1f%%" %
      (attn[:24].sum()/nv*100, mlp[:24].sum()/nv*100))
print("layer 29 total share: %.1f%%" % ((attn[29]+mlp[29])/nv*100))
print("top head:", np.unravel_index(HG.argmax(), HG.shape), "=", round(HG.max()/nv*100,2), "% of ||v||")
print("figures written")
