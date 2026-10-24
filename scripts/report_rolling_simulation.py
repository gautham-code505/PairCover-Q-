"""
Figures and markdown tables for the rolling simulation (reads results.json and
results_holdout.json written by run_rolling_simulation.py).

Usage:
    python scripts/report_rolling_simulation.py
"""

import json
import os
import sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(_ROOT, "src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from qrescue.simulation.region import default_region, describe_region

OUT = os.path.join(_ROOT, "reports", "rolling_simulation")
INK, PUR, PINK, GREY, RED, GRN = "#1b1530", "#7c4dff", "#ff7eb6", "#8a8799", "#e5484d", "#1a9e6b"
STYLE = {"coverage-single": (RED, "s", "coverage-single (Jagtenberg-style)"),
         "batch-no-coverage": (GREY, "D", "batch, no coverage (lam = 0)"),
         "paircover-q (lam=5)": (PUR, "o", "PairCover-Q, lam = 5"),
         "paircover-q (lam=20)": (PINK, "^", "PairCover-Q, lam = 20")}


def ci(d, scale=1.0):
    return d["mean"] * scale, (d["mean"] - d["lo"]) * scale


def fig_paired(res, path):
    loads = list(res["loads"])
    x = np.array([float(l) for l in loads])
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.2))
    panels = [("late_share", 100, "Late arrivals (> 12 min), percentage points"),
              ("mean_response", 1, "Mean response time, minutes"),
              ("uncovered_demand", 100, "Uncovered demand, percentage points")]
    for ax, (m, sc, title) in zip(axs, panels):
        for k, (name, (col, mk, lab)) in enumerate(STYLE.items()):
            vals = [ci(res["loads"][l]["policies"][name]["diff_vs_closest"][m], sc) for l in loads]
            off = (k - 1.5) * 0.08
            ax.errorbar(x + off, [v for v, _ in vals], yerr=[e for _, e in vals], color=col, marker=mk, ms=6,
                        capsize=3, lw=1.6, label=lab)
        ax.axhline(0, color=INK, lw=1)
        ax.set_title(title, fontsize=11.5, loc="left", color=INK)
        ax.set_xlabel("calls per hour (7 ambulances)")
        ax.set_xticks(x)
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=.3)
    axs[0].set_ylabel("difference vs closest-idle\n(below 0 = better), 95% CI")
    axs[0].legend(frameon=False, fontsize=9.5, loc="upper left")
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)


def fig_lambda(res, path):
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    lam_names = ["batch-no-coverage"] + [n for n in res["loads"][next(iter(res["loads"]))]["policies"] if n.startswith("paircover-q")]
    lams = [0.0] + [float(n.split("=")[1].rstrip(")")) for n in lam_names[1:]]
    cols = plt.cm.viridis(np.linspace(0.1, 0.85, len(res["loads"])))
    for col, (load, L) in zip(cols, res["loads"].items()):
        xs = [L["policies"][n]["diff_vs_closest"]["uncovered_demand"]["mean"] * 100 for n in lam_names]
        ys = [L["policies"][n]["diff_vs_closest"]["late_share"]["mean"] * 100 for n in lam_names]
        ax.plot(xs, ys, "-o", color=col, label=f"{load} calls/h")
        for lx, ly, lam in zip(xs, ys, lams):
            ax.annotate(f"{lam:g}", (lx, ly), textcoords="offset points", xytext=(4, 4), fontsize=8, color=col)
    ax.axhline(0, color=INK, lw=1)
    ax.axvline(0, color=INK, lw=1)
    ax.set_xlabel("change in uncovered demand vs closest-idle (pp)")
    ax.set_ylabel("change in late arrivals vs closest-idle (pp)")
    ax.set_title("Coverage weight lam: protecting coverage vs arriving on time\n(labels = lam; bottom-left is better on both)",
                 fontsize=11, loc="left", color=INK)
    ax.legend(frameon=False, fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)


def fig_region(path, cover=12.0):
    region = default_region()
    count = describe_region(region, cover).cover_count
    fig, axs = plt.subplots(1, 2, figsize=(10.5, 4.8))
    for ax, vals, title, cmap in [(axs[0], region.demand_share * 100, "Demand share per zone (%)", "Purples"),
                                  (axs[1], count, "Ambulances within 12 min when all are idle", "RdYlGn")]:
        grid = vals.reshape(6, 6)
        im = ax.imshow(grid, origin="lower", extent=(0, 24, 0, 24), cmap=cmap, vmin=0 if cmap != "RdYlGn" else 0,
                       vmax=None if cmap != "RdYlGn" else 4)
        for i, z in enumerate(region.zones):
            ax.text(z[0], z[1], f"{vals[i]:.1f}" if cmap == "Purples" else f"{int(vals[i])}", ha="center", va="center", fontsize=8)
        ax.scatter(*region.stations.T, marker="s", s=70, c=INK, label="station")
        ax.scatter(*region.hospitals.T, marker="P", s=110, c=RED, label="hospital")
        ax.set_title(title, fontsize=11, loc="left")
        ax.set_xlabel("km")
        fig.colorbar(im, ax=ax, shrink=0.8)
    axs[0].legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2, fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)


def fmt(d, sc=1.0, nd=2):
    return f"{d['mean']*sc:+.{nd}f} [{d['lo']*sc:+.{nd}f}, {d['hi']*sc:+.{nd}f}]"


def tables(res, hold):
    lines = []
    for load, L in res["loads"].items():
        lines.append(f"\n#### {load} calls per hour\n")
        lines.append("| Policy | Mean response (min) | Late > 12 min | P1 mean (min) | P3 mean (min) | Uncovered demand | "
                     "Δ late vs closest-idle (pp) | Δ mean response (min) | Δ uncovered (pp) |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
        for name, e in L["policies"].items():
            m = e["mean"]
            d = e.get("diff_vs_closest")
            row = (f"| {name} | {m['mean_response']:.2f} | {m['late_share']*100:.1f}% | {m['p1_mean_response']:.2f} | "
                   f"{m['p3_mean_response']:.2f} | {m['uncovered_demand']*100:.1f}% | ")
            row += (f"{fmt(d['late_share'], 100)} | {fmt(d['mean_response'])} | {fmt(d['uncovered_demand'], 100)} |"
                    if d else "reference | reference | reference |")
            lines.append(row)
    lines.append("\n#### What the coverage term adds on top of batch assignment (PairCover-Q minus batch-no-coverage)\n")
    lines.append("| Load | λ | Δ late (pp) | Δ mean response (min) | Δ uncovered (pp) | Δ P1 mean (min) |")
    lines.append("|---|---|---|---|---|---|")
    for load, L in res["loads"].items():
        for name, e in L["policies"].items():
            if "diff_vs_batch" in e:
                d = e["diff_vs_batch"]
                lines.append(f"| {load} | {name.split('=')[1].rstrip(')')} | {fmt(d['late_share'], 100)} | {fmt(d['mean_response'])} | "
                             f"{fmt(d['uncovered_demand'], 100)} | {fmt(d['p1_mean_response'])} |")
    if hold:
        lines.append(f"\n#### Held-out confirmation (fresh seeds {hold['config']['seed']}–{hold['config']['seed'] + hold['config']['reps'] - 1})\n")
        lines.append("| Load | Policy | Δ late vs closest-idle (pp) | Δ mean response (min) | Δ uncovered (pp) | Δ late vs batch (pp) |")
        lines.append("|---|---|---|---|---|---|")
        for load, L in hold["loads"].items():
            for name, e in L["policies"].items():
                if name.startswith("paircover-q") or name == "batch-no-coverage":
                    d = e["diff_vs_closest"]
                    vb = fmt(e["diff_vs_batch"]["late_share"], 100) if "diff_vs_batch" in e else "—"
                    lines.append(f"| {load} | {name} | {fmt(d['late_share'], 100)} | {fmt(d['mean_response'])} | "
                                 f"{fmt(d['uncovered_demand'], 100)} | {vb} |")
    lines.append("\n#### Size of the per-epoch QUBO (what QAOA would have to solve)\n")
    lines.append("| Load | Decisions | With ≥ 2 non-P1 calls | Differs from greedy (λ = 5) | Qubits mean / p95 / max | "
                 "Pairwise model ≠ true coverage loss | Eligibility fallback |")
    lines.append("|---|---|---|---|---|---|---|")
    for load, L in res["loads"].items():
        e = L["policies"]["paircover-q (lam=5)"]["epochs"]
        lines.append(f"| {load} | {e['decisions']} | {e['multi_call']} | {e['differs_from_greedy']} "
                     f"({e['differs_from_greedy']/e['decisions']*100:.1f}%) | {e['qubits_mean']:.1f} / {e['qubits_p95']:.0f} / "
                     f"{e['qubits_max']} | {e['model_loss_mismatch']} | {e['eligibility_fallback']} |")
    return "\n".join(lines) + "\n"


def main():
    res = json.load(open(os.path.join(OUT, "results.json"), encoding="utf-8"))
    hold_path = os.path.join(OUT, "results_holdout.json")
    hold = json.load(open(hold_path, encoding="utf-8")) if os.path.exists(hold_path) else None
    fig_paired(res, os.path.join(OUT, "fig_paired_differences.png"))
    fig_lambda(res, os.path.join(OUT, "fig_lambda_tradeoff.png"))
    fig_region(os.path.join(OUT, "fig_region.png"))
    with open(os.path.join(OUT, "tables.md"), "w", encoding="utf-8") as f:
        f.write("<!-- generated by scripts/report_rolling_simulation.py; do not edit by hand -->\n")
        f.write("Values are means over replications; brackets are 95% t-intervals of the paired difference.\n")
        f.write(tables(res, hold))
    print("wrote figures and tables to", OUT)


if __name__ == "__main__":
    main()
