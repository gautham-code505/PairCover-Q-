import sys, json, os, math
sys.path.append(sys.argv[1])
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
out = sys.argv[2]
D = json.load(open(os.path.join(out, "qaoa.json")))
plt.rcParams.update({"font.family": "Segoe UI", "font.size": 13})
INK = "#1b1530"; PINK = "#ff7eb6"; PUR = "#7c4dff"; RED = "#e5484d"; GRN = "#1a9e6b"; GREY = "#8a8799"


def save(fig, name):
    fig.savefig(os.path.join(out, name), dpi=200, transparent=True, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


# ---- 1. scenario map: greedy vs coverage-aware
pos = {"A1": (1.2, 2.6), "A2": (2.6, 1.3), "A3": (6.5, 3.0), "C2": (2.9, 3.3), "C3": (4.6, 1.6)}


def scen(ax, title, assign, covered, cost, sub):
    ax.set_xlim(0, 8); ax.set_ylim(0, 4.6); ax.axis("off"); ax.set_aspect("equal")
    ax.add_patch(FancyBboxPatch((0.15, 0.15), 7.7, 4.3, boxstyle="round,pad=0.02,rounding_size=0.25", fc="white", ec="#d8d4e6", lw=1.5))
    ax.add_patch(Circle((1.9, 2.15), 1.3, fc=("#d9f5e8" if covered else "#fde0e0"), ec=(GRN if covered else RED), lw=2, ls="--", alpha=.85))
    ax.text(0.45, 0.4, "shared zone " + ("COVERED" if covered else "UNCOVERED"), color=(GRN if covered else RED), fontsize=11, fontweight="bold")
    for (a, c, t) in assign:
        ax.add_patch(FancyArrowPatch(pos[a], pos[c], arrowstyle="-|>", mutation_scale=22, lw=3, color=PUR, shrinkA=16, shrinkB=16))
        mx, my = (pos[a][0] + pos[c][0]) / 2, (pos[a][1] + pos[c][1]) / 2
        ax.text(mx + 0.45, my - 0.32, f"{t} min", ha="center", fontsize=11, color=PUR, fontweight="bold")
    used = {a for a, _, _ in assign}
    for k, (x, y) in pos.items():
        if k[0] == "A":
            ax.add_patch(FancyBboxPatch((x - 0.33, y - 0.24), 0.66, 0.48, boxstyle="round,pad=0.02,rounding_size=0.1", fc=(INK if k in used else "white"), ec=INK, lw=2, zorder=3))
            ax.text(x, y, k, ha="center", va="center", color=("white" if k in used else INK), fontweight="bold", fontsize=12, zorder=4)
        else:
            ax.add_patch(Circle((x, y), 0.3, fc=PINK, ec=INK, lw=2, zorder=3))
            ax.text(x, y, k, ha="center", va="center", fontweight="bold", fontsize=12, zorder=4)
    ax.text(4, 4.05, title, ha="center", fontsize=15, fontweight="bold", color=INK)
    ax.text(7.6, 0.5, f"cost {cost}", ha="right", fontsize=17, fontweight="bold", color=(GRN if covered else RED))
    ax.text(7.6, 0.95, sub, ha="right", fontsize=10.5, color=GREY)


G = [("A1", "C2", 4), ("A2", "C3", 4)]; O = [("A1", "C2", 4), ("A3", "C3", 5)]
fig, axs = plt.subplots(1, 2, figsize=(13, 3.9)); fig.subplots_adjust(wspace=0.04)
scen(axs[0], "Nearest-available (greedy)", G, False, 22, "response 12 + coverage 10")
scen(axs[1], "Coverage-aware optimum (PairCover-Q)", O, True, 13, "response 13 + coverage 0")
save(fig, "f_scenario.png")
fig, ax = plt.subplots(figsize=(6.6, 3.9)); scen(ax, "Nearest-available dispatch", G, False, 22, "response 12 + coverage 10"); save(fig, "f_greedy.png")

# ---- 2. QUBO coupling graph
labs = ["x0\nA1-C2", "x1\nA1-C3", "x2\nA2-C2", "x3\nA2-C3", "x4\nA3-C2", "x5\nA3-C3"]
P = [(math.cos(math.pi / 2 - i * math.pi / 3) * 2.75, math.sin(math.pi / 2 - i * math.pi / 3) * 2.2) for i in range(6)]
fig, ax = plt.subplots(figsize=(6.4, 5.2)); ax.axis("off"); ax.set_xlim(-4, 4); ax.set_ylim(-4.6, 3.1)
for k, v in D["J"].items():
    a, b = map(int, k.split(","))
    if v == 0: continue
    c, lw, ls = (GREY, 1.8, "-") if v == 40 else (RED, 4.2, "-") if v == 50 else (PUR, 3.6, (0, (4, 2)))
    ax.plot([P[a][0], P[b][0]], [P[a][1], P[b][1]], color=c, lw=lw, ls=ls, alpha=(.7 if v == 40 else 1), zorder=1)
for i, (x, y) in enumerate(P):
    ax.add_patch(Circle((x, y), 0.62, fc="white", ec=INK, lw=2.2, zorder=3))
    ax.text(x, y, labs[i], ha="center", va="center", fontsize=9.5, fontweight="bold", zorder=4)
ax.plot([], [], color=GREY, lw=2, label="40   one-to-one penalty")
ax.plot([], [], color=PUR, lw=3.6, ls=(0, (4, 2)), label="10   pair-coverage coupling")
ax.plot([], [], color=RED, lw=4.2, label="50   both (same call + coverage)")
ax.legend(loc="lower center", frameon=False, fontsize=11.5)
save(fig, "f_qubo.png")

# ---- 3. architecture
fig, ax = plt.subplots(figsize=(13.4, 4.3)); ax.axis("off"); ax.set_xlim(0, 13.4); ax.set_ylim(0, 4.3)


def box(x, y, w, h, t, s, fc, tc=INK):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.15", fc=fc, ec=INK, lw=1.6))
    ax.text(x + w / 2, y + h * 0.68, t, ha="center", va="center", fontsize=12.5, fontweight="bold", color=tc)
    ax.text(x + w / 2, y + h * 0.3, s, ha="center", va="center", fontsize=9.6, color=tc)


def arr(a, b): ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=18, lw=2, color=INK))


W = 2.25; Y = 2.55; H = 1.3
xs = [0.1, 2.85, 5.6, 8.35, 11.05]
box(xs[0], Y, W, H, "Scenario", "calls, units, travel times,\nzones (synthetic)", "white")
box(xs[1], Y, W, H, "QUBO builder", "h, J from raw tables\nscenario2.py, qubo.py", "white")
box(xs[2], Y, W, H, "Ising mapping", "SparsePauliOp, H / 28\nising.py", "#e9defc")
box(xs[3], Y, W, H, "QAOA (Qiskit 2.5.2)", "QAOAAnsatz p = 1-2\nCOBYLA + Statevector", PUR, "white")
box(xs[4], Y, W, H, "Decode + validate", "little-endian decode\nvalidator.py", "white")
for i in range(4): arr((xs[i] + W + 0.02, Y + H / 2), (xs[i + 1] - 0.02, Y + H / 2))
box(2.85, 0.35, 5.0, 1.25, "Classical ground truth", "brute force over all 64 states, greedy,\ncoverage-free optimum, random controls", "#ffd9ea")
box(8.35, 0.35, 4.95, 1.25, "Streamlit console + notebook", "Dispatch Console, Quantum Lab,\nBenchmarks, pytest suite", "white")
arr((xs[1] + W / 2, Y - 0.02), (xs[1] + W / 2, 1.64)); arr((7.87, 0.97), (8.33, 0.97)); arr((xs[4] + W / 2, Y - 0.02), (xs[4] + W / 2, 1.64))
ax.text(xs[3] + W / 2, Y + H + 0.2, "QUANTUM", ha="center", fontsize=10, fontweight="bold", color=PUR)
ax.text(xs[0] + W / 2, Y + H + 0.2, "CLASSICAL", ha="center", fontsize=10, fontweight="bold", color=GREY)
save(fig, "f_arch.png")

# ---- 4. results
runs = D["runs"]; names = [f"p={r['p']}\nseed {r['seed']}" for r in runs]
fig, axs = plt.subplots(1, 2, figsize=(11.2, 4.1)); fig.subplots_adjust(wspace=0.28)
spec = [(axs[0], "hits", "P(exact optimum) per shot", [(1 / 64, "uniform over all 64 states: 1.56%", GREY), (1 / 13, "uniform over 13 feasible: 7.69%", RED)]),
        (axs[1], "feas", "Feasible-sample rate", [(13 / 64, "uniform random: 20.3%", GREY)])]
for ax, key, ttl, base in spec:
    vals = [(r["hits"] / 10000 if key == "hits" else r["s_feas"]) * 100 for r in runs]
    top = max(max(vals), max(v for v, _, _ in base) * 100)
    b = ax.bar(names, vals, color=PUR, width=0.6, zorder=3)
    for rect, v in zip(b, vals):
        ax.text(rect.get_x() + rect.get_width() / 2, v + top * 0.02, f"{v:.2f}%" if key == "hits" else f"{v:.1f}%", ha="center", fontsize=11.5, fontweight="bold", color=INK)
    for v, l, c in base:
        ax.axhline(v * 100, color=c, ls="--", lw=1.8, zorder=2, label=l)
    ax.set_title(ttl, fontsize=14, fontweight="bold", color=INK, loc="left"); ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="upper right", frameon=False, fontsize=10); ax.set_ylim(0, top * 1.38); ax.set_ylabel("% of 10,000 shots", fontsize=11); ax.grid(axis="y", alpha=.3, zorder=0); ax.set_facecolor("none")
save(fig, "f_results.png")

# ---- 5. convergence + histogram of the p=1 seed-10 run
r = runs[0]; c = sorted(r["counts"].items(), key=lambda kv: -kv[1])[:10]
fig, axs = plt.subplots(1, 2, figsize=(11.6, 3.6), gridspec_kw={"width_ratios": [1, 1.5]}); fig.subplots_adjust(wspace=0.22)
axs[0].plot(range(1, len(r["hist"]) + 1), r["hist"], color=PUR, lw=2.4, marker="o", ms=3.5)
axs[0].set_title("COBYLA convergence of <H>", fontsize=13, fontweight="bold", loc="left")
axs[0].set_xlabel("circuit evaluation"); axs[0].spines[["top", "right"]].set_visible(False); axs[0].grid(alpha=.3)
axs[1].bar([k for k, _ in c], [v for _, v in c], color=[GRN if k == D["key"] else "#b9a4f5" for k, _ in c])
axs[1].axhline(10000 / 64, color=GREY, ls="--", lw=1.5); axs[1].text(9.4, 10000 / 64 + 30, "random guess (156)", ha="right", fontsize=10, color=GREY)
axs[1].set_title(f"Top measured bitstrings, 10,000 shots (green = optimum {D['key']})", fontsize=13, fontweight="bold", loc="left")
axs[1].tick_params(axis="x", rotation=40, labelsize=10); axs[1].spines[["top", "right"]].set_visible(False)
for a in axs: a.set_facecolor("none")
save(fig, "f_hist.png")

# ---- 6. roadmap
fig, ax = plt.subplots(figsize=(13.2, 3.3)); ax.axis("off"); ax.set_xlim(0, 13.2); ax.set_ylim(0, 3.3)
steps = [("12-16 Oct", "Rolling simulation", "discrete-event replay vs\nclosest-idle and a classical\ncoverage-aware rule"),
         ("16-20 Oct", "Feasibility-preserving\nmixer", "XY / Dicke-state QAOA to\ncut infeasible samples"),
         ("20-24 Oct", "Scale + noise", "8-12 qubits, penalty sweeps,\n20-30 seeds, Aer noise model"),
         ("24-28 Oct", "Real demand inputs", "TN-108 taluk x hour rates\n(if dataset access arrives)"),
         ("Finale", "IBM hardware run", "one small instance on a\nreal QPU, reported as-is")]
ax.plot([0.6, 12.6], [2.55, 2.55], color=INK, lw=3)
for i, (w, t, s) in enumerate(steps):
    x = 1.3 + i * 2.65
    ax.add_patch(Circle((x, 2.55), 0.2, fc=(PINK if i < 4 else PUR), ec=INK, lw=2, zorder=3))
    ax.text(x, 3.0, w, ha="center", fontsize=11, fontweight="bold", color=INK)
    ax.add_patch(FancyBboxPatch((x - 1.2, 0.15), 2.4, 1.95, boxstyle="round,pad=0.02,rounding_size=0.12", fc="white", ec=INK, lw=1.4))
    ax.text(x, 1.62, t, ha="center", va="center", fontsize=11.3, fontweight="bold", color=INK)
    ax.text(x, 0.75, s, ha="center", va="center", fontsize=9.4, color="#4a4560")
save(fig, "f_roadmap.png")

# ---- 7. literature trade-off
fig, ax = plt.subplots(figsize=(5.4, 3.3))
ax.bar(["Late arrivals", "Mean response time"], [-18, 37], color=[GRN, RED], width=0.55, zorder=3)
ax.axhline(0, color=INK, lw=1.2)
ax.text(0, -25.5, "-18%", ha="center", fontsize=17, fontweight="bold", color=GRN); ax.text(1, 39, "+37%", ha="center", fontsize=17, fontweight="bold", color=RED)
ax.set_ylim(-30, 50); ax.set_yticks([]); ax.spines[["top", "right", "left", "bottom"]].set_visible(False); ax.tick_params(length=0, labelsize=12); ax.set_facecolor("none")
ax.set_title("Coverage-aware vs closest-idle dispatch\n(Jagtenberg et al. 2017, Dutch region)", fontsize=11.5, loc="left", color=INK)
save(fig, "f_tradeoff.png")
print("ok")
