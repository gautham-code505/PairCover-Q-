"""Classical vs quantum: one dispatch problem solved by classical methods, the QAOA simulator and IBM hardware."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

import app_shell as shell
import hardware_compare as hc
import ui_components as ui

REPO = "https://github.com/gautham-code505/PairCover-Q-/blob/main"
TONE = {"classical": "#2F80D6", "simulator": "#7C5CE0", "fake": "#C2569B", "hardware": "#1E9AA8"}


def _time(s: float | None) -> str:
    if s is None:
        return "—"
    if s < 1:
        return f"{s * 1e3:.2f} ms"
    return f"{s:.1f} s" if s < 90 else f"{s / 60:.1f} min"


def _pct(x: float | None) -> str:
    return "—" if x is None else f"{x:.1%}"


shell.page_header("Classical vs Quantum", "The same ambulance dispatch problem solved four ways: a simple rule, an exact "
                  "classical search, QAOA on a noiseless simulator, and QAOA on a real IBM quantum computer.", eyebrow="Quantum")
shell.set_active(shell.current_scenario())

runs = hc.load_hardware_runs()
choices = hc.problem_choices(runs)
if not choices:
    ui.empty_state("No hardware results yet", "Run scripts/run_ibm_hardware.py to put a real-device result in reports/ibm_hardware.")
    st.stop()

# Widget options are "id:p" strings; a tuple default would be read as a list of defaults.
names = {f"{i}:{p}": f"{i.split('-')[1][:-1]} qubits · depth {p}" for i, p in choices}
keys = list(names)
key = st.segmented_control("Problem", keys, format_func=names.get, default=keys[1] if len(keys) > 1 else keys[0],
                           key="cvq_problem", help="Synthetic problems from the QAOA benchmark, all sent to ibm_fez in one job.")
pick = choices[keys.index(key or keys[0])]
seed = st.session_state.setdefault("cvq_seed", 7)
res = hc.compare(pick[0], pick[1], runs, seed=seed)
rows = {r["key"]: r for r in res["rows"]}
raw = rows.get("hw_raw")
n_jobs = len({j for r in res["rows"] for j in r.get("job_ids", [])})

ui.kpi_row([
    {"label": "Exact classical answer", "value": _time(rows["exact"]["seconds"]), "hint": f"checked all {2 ** res['qubits']} options, live", "tone": "info"},
    {"label": "QAOA, noiseless simulator", "value": _time(rows["sim"]["seconds"]), "hint": f"{rows['sim']['shots']:,} samples, live", "tone": "violet"},
    {"label": "QAOA on ibm_fez, end to end", "value": _time(raw["seconds"]) if raw else "—",
     "hint": f"queue {_time(raw['queue_seconds'])} + processing {_time(raw['run_seconds'])}, mean of {raw['n_runs']} jobs" if raw else "",
     "tone": "warn"},
    {"label": "Time on the quantum chip", "value": _time(raw["chip_seconds"]) if raw else "—",
     "hint": "3 circuits × 4,096 shots per job", "tone": "ok"},
])


def _p_range(r):
    if r.get("n_runs", 1) > 1:
        return f"{_pct(r['p_opt'])} ({r['p_opt_lo']:.1%}–{r['p_opt_hi']:.1%}, {r['n_runs']} runs)"
    return _pct(r.get("p_opt"))


ui.section("Side by side", "QAOA rows show the circuit's most frequent answer (the majority across runs on the chip). "
           "Cost is response time plus coverage loss; lower is better.")
table = []
for r in res["rows"]:
    optimal = r.get("optimal", abs(r["cost"] - res["exact_cost"]) < 1e-9)
    table.append({
        "Method": r["name"], "Runs on": r["where"],
        "Answer": hc.label(r["pairs"]) + ("" if r.get("valid", True) else " (invalid)"),
        "Cost": round(r["cost"], 2) if r["cost"] != float("inf") else None,
        "Best?": ("✔ yes" if optimal else "✖ no") + (f" ({r['optimal_runs']}/{r['n_runs']})" if r.get("n_runs", 1) > 1 else ""),
        "P(optimum)": _p_range(r),
        "Valid samples": _pct(r.get("p_valid")),
        "2q gates / depth": f"{r['two_qubit']} / {r['depth']}" if r.get("two_qubit") else "—",
        "Time": _time(r["seconds"]) if r.get("seconds") is not None else "local, not timed",
    })
ui._table(table, caption=f"Random guessing finds the optimum {_pct(res['uniform_p_opt'])} of the time over all bitstrings, "
          f"{_pct(res['uniform_valid_p_opt'])} over valid assignments only. Readout fix: per-qubit measurement errors, "
          "calibrated in the same job, are inverted. DD + twirling: IBM Runtime's dynamical decoupling and gate/measurement twirling.")

left, right = st.columns([1.25, 1], gap="large")
with left:
    bars = [("Random guess (any bitstring)", res["uniform_p_opt"], "#7A8798", 0, 0),
            ("Random guess (valid only)", res["uniform_valid_p_opt"], "#7A8798", 0, 0)]
    bars += [(r["name"], r["p_opt"], TONE[r["kind"]], r["p_opt"] - r.get("p_opt_lo", r["p_opt"]), r.get("p_opt_hi", r["p_opt"]) - r["p_opt"])
             for r in res["rows"] if r.get("p_opt") is not None]
    fig = go.Figure(go.Bar(y=[b[0] for b in bars], x=[b[1] for b in bars], orientation="h", marker_color=[b[2] for b in bars],
                           error_x=dict(type="data", symmetric=False, array=[b[4] for b in bars], arrayminus=[b[3] for b in bars],
                                        color="#7A8798", thickness=1.5, width=4),
                           text=[_pct(b[1]) for b in bars], textposition="outside", cliponaxis=False,
                           hovertemplate="%{y}: %{x:.1%}<extra></extra>"))
    fig.update_xaxes(tickformat=".0%", range=[0, max(b[1] + b[4] for b in bars) * 1.3])
    fig.update_yaxes(autorange="reversed")
    ui._chart(ui._style(fig, "How often each run lands on the best dispatch (bars: range over runs)", 420),
              f"cvq_bars_{pick[0]}_{pick[1]}")
with right:
    sim, guess = rows["sim"], res["uniform_valid_p_opt"]
    ro, mit, full = rows.get("hw_ro"), rows.get("hw_mit"), rows.get("hw_all")
    points = []
    if raw:
        if raw["p_opt_lo"] > guess:
            verdict = f"{raw['p_opt'] / guess:.1f}× guessing among valid assignments ({_pct(guess)})"
        elif raw["p_opt_hi"] < guess:
            verdict = f"below the {_pct(guess)} of guessing among valid assignments: {raw['two_qubit']} two-qubit gates add too much noise"
        else:
            verdict = f"sometimes above and sometimes below the {_pct(guess)} of guessing among valid assignments"
        points.append(f"Raw, the chip hits the best dispatch <b>{_pct(raw['p_opt'])}</b> of the time on average "
                      f"({raw['n_runs']} runs, {raw['optimal_runs']} with the best dispatch as the top answer): {verdict}.")
        if raw["n_runs"] > 1 and raw["p_opt_hi"] > 1.3 * raw["p_opt_lo"]:
            (t_lo, lo), (t_hi, hi) = min(raw["p_opt_by_run"], key=lambda x: x[1]), max(raw["p_opt_by_run"], key=lambda x: x[1])
            points.append(f"<b>The device drifts.</b> Same circuit, same physical qubits: {_pct(lo)} at {t_lo[11:16]} UTC, "
                          f"{_pct(hi)} at {t_hi[11:16]} UTC.")
    if ro and mit:
        base = ro["p_opt_before_readout"]
        points.append(f"Error mitigation, against raw runs from the same session ({_pct(base)}): the readout fix adds "
                      f"{(ro['p_opt'] - base) * 100:+.1f} points; dynamical decoupling + twirling gives {(mit['p_opt'] - base) * 100:+.1f}"
                      + (f", and both together {(full['p_opt'] - base) * 100:+.1f}." if full else ".")
                      + (" Twirling turns coherent errors into random ones; without noise extrapolation that does not raise the hit rate."
                         if mit["p_opt"] <= base else ""))
    if raw and raw["p_opt"] > sim["p_opt"]:
        points.append(f"The chip's average is above the noiseless {_pct(sim['p_opt'])}. That is most likely a noise effect, not a quantum gain: "
                      "qubits relaxing to 0 favour bitstrings with few 1s, and the best dispatch here has only a few.")
    points.append(f"The exact classical search gives the right answer in {_time(rows['exact']['seconds'])}; a hardware job takes "
                  f"{_time(raw['seconds']) if raw else '—'} end to end on average. <b>No quantum advantage is claimed.</b>")
    if abs(rows["greedy"]["cost"] - res["exact_cost"]) > 1e-9:
        points.append("The nearest-available rule picks a <b>worse</b> dispatch here: it ignores the coverage the exact solution keeps.")
    st.markdown(
        '<div class="ev-card"><h3>What this shows</h3><ul>' + "".join(f"<li>{x}</li>" for x in points) + '</ul>'
        f'<p class="pc-caption" style="margin-top:10px">{n_jobs} IBM jobs on '
        f'{", ".join(sorted({r["name"].split(" · ")[1].split(" ")[0] for r in res["rows"] if r["kind"] == "hardware"}))}, '
        f'{(raw["completed_utc"] or "")[:10] if raw else ""}. Full write-up: '
        f'<a href="{REPO}/reports/ibm_hardware/README.md" target="_blank">IBM hardware report</a>.</p></div>',
        unsafe_allow_html=True)

curve = hc.scaling_curve(runs)
if curve:
    ui.section("Real hardware across problem sizes",
               f"The strongest benchmark problem at each size, depth {hc.SCALING_DEPTH}, on ibm_fez. "
               "Above 1 = finds the best dispatch more often than guessing among valid plans.")
    xs = [f"{d['qubits']} qubits<br>{d['two_qubit']} 2q gates" for d in curve]
    fig = go.Figure()
    fig.add_hline(y=1, line_dash="dot", line_color="#7A8798",
                  annotation_text="random guessing", annotation_position="bottom right", annotation_font_color="#7A8798")
    fig.add_trace(go.Scatter(x=xs, y=[d["noiseless_x"] for d in curve], name="Noiseless simulator", mode="lines+markers",
                             line=dict(color=TONE["simulator"], dash="dash"), hovertemplate="%{x}: %{y:.2f}× guessing<extra></extra>"))
    fig.add_trace(go.Scatter(x=xs, y=[d["hw_x"] for d in curve], name=f"Real ibm_fez ({curve[0]['n_runs']} jobs)",
                             mode="lines+markers", line=dict(color=TONE["hardware"], width=3), marker=dict(size=9),
                             error_y=dict(type="data", symmetric=False, array=[d["hw_x_hi"] - d["hw_x"] for d in curve],
                                          arrayminus=[d["hw_x"] - d["hw_x_lo"] for d in curve], color=TONE["hardware"]),
                             hovertemplate="%{x}: %{y:.2f}× guessing<extra></extra>"))
    fig.update_yaxes(title_text="× random guessing", rangemode="tozero")
    ui._chart(ui._style(fig, None, 380), "cvq_scaling")
    sizes = lambda ds: ", ".join(str(d["qubits"]) for d in ds) or "none"
    above = [d for d in curve if d["hw_x"] > 1.1]
    below = [d for d in curve if d["hw_x"] < 0.9]
    even = [d for d in curve if d not in above and d not in below]
    kept = [d["hw"] / d["noiseless"] for d in curve]
    top = max(curve, key=lambda d: d["noiseless_x"])
    st.caption(
        f"On the chip the best dispatch beats guessing at {sizes(above)} qubits, is about even at {sizes(even)} "
        f"and falls below it at {sizes(below)} (within 10% counts as even). "
        f"Noise keeps {min(kept):.0%}–{max(kept):.0%} of the noiseless gain, generally less for longer circuits, "
        f"so the chip stays above guessing only where the noiseless gain is large: the {top['qubits']}-qubit problem "
        f"starts at {top['noiseless_x']:.1f}× and ends at {top['hw_x']:.1f}× on the chip."
        + (" The noiseless circuit beats guessing at every size: the limit is hardware noise, not the algorithm."
           if all(d["noiseless_x"] > 1 for d in curve) else ""))
    ui._data_expander("Real hardware across problem sizes", [
        {"Problem": d["id"], "Qubits": d["qubits"], "2q gates": d["two_qubit"], "Noiseless P(opt)": _pct(d["noiseless"]),
         "ibm_fez P(opt)": f"{_pct(d['hw'])} ({d['hw_lo']:.1%}–{d['hw_hi']:.1%})", "Guessing": _pct(d["guess"]),
         "Top answer optimal": f"{d['top_optimal_runs']}/{d['n_runs']}"} for d in curve])

if st.button("Run the classical solvers and simulator again", key="cvq_rerun", help="New random seed for the simulator's 4,096 samples."):
    st.session_state["cvq_seed"] = seed + 1
    st.rerun()

with st.expander("Limitations"):
    st.markdown(
        "- Problems are small (4–6 qubits) and synthetic; classical search is instant at these sizes.\n"
        "- Results drift: the same circuit on the same qubits moved from 28% to 48% within two hours.\n"
        "- Mitigation tried: readout correction (about +1 point) and dynamical decoupling with twirling (no gain). "
        "Zero-noise extrapolation was not tried.\n"
        "- The circuit angles were tuned in simulation, not on the chip.\n"
        "- Six jobs on one device on one day.\n"
        "- Minutes of queue and processing make hardware unusable for live dispatch today.")
