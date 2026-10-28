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
real = next((r for r in res["rows"] if r["kind"] == "hardware"), None)

ui.kpi_row([
    {"label": "Exact classical answer", "value": _time(rows["exact"]["seconds"]), "hint": f"checked all {2 ** res['qubits']} options, live", "tone": "info"},
    {"label": "QAOA, noiseless simulator", "value": _time(rows["sim"]["seconds"]), "hint": f"{rows['sim']['shots']:,} samples, live", "tone": "violet"},
    {"label": "QAOA on ibm_fez, end to end", "value": _time(real["seconds"]) if real else "—",
     "hint": f"queue {_time(real['queue_seconds'])} + processing {_time(real['run_seconds'])}" if real else "", "tone": "warn"},
    {"label": "Time on the quantum chip", "value": _time(real["chip_seconds"]) if real else "—",
     "hint": "3 circuits × 4,096 shots, one job", "tone": "ok"},
])

ui.section("Side by side", "QAOA rows show the circuit's most frequent answer. Cost is response time plus coverage loss; lower is better.")
table = []
for r in res["rows"]:
    optimal = r.get("optimal", abs(r["cost"] - res["exact_cost"]) < 1e-9)
    table.append({
        "Method": r["name"], "Runs on": r["where"],
        "Answer": hc.label(r["pairs"]) + ("" if r.get("valid", True) else " (invalid)"),
        "Cost": round(r["cost"], 2) if r["cost"] != float("inf") else None,
        "Best?": "✔ yes" if optimal else "✖ no",
        "P(optimum)": _pct(r.get("p_opt")),
        "Valid samples": _pct(r.get("p_valid")),
        "2q gates / depth": f"{r['two_qubit']} / {r['depth']}" if r.get("two_qubit") else "—",
        "Time": _time(r["seconds"]) if r.get("seconds") is not None else "local, not timed",
    })
ui._table(table, caption=f"Random guessing finds the optimum {_pct(res['uniform_p_opt'])} of the time over all bitstrings, "
          f"{_pct(res['uniform_valid_p_opt'])} over valid assignments only.")

left, right = st.columns([1.25, 1], gap="large")
with left:
    bars = [("Random guess (any bitstring)", res["uniform_p_opt"], "#7A8798"),
            ("Random guess (valid only)", res["uniform_valid_p_opt"], "#7A8798")]
    bars += [(r["name"], r["p_opt"], TONE[r["kind"]]) for r in res["rows"] if r.get("p_opt") is not None]
    fig = go.Figure(go.Bar(y=[b[0] for b in bars], x=[b[1] for b in bars], orientation="h", marker_color=[b[2] for b in bars],
                           text=[_pct(b[1]) for b in bars], textposition="outside", cliponaxis=False,
                           hovertemplate="%{y}: %{x:.1%}<extra></extra>"))
    fig.update_xaxes(tickformat=".0%", range=[0, max(b[1] for b in bars) * 1.25])
    fig.update_yaxes(autorange="reversed")
    ui._chart(ui._style(fig, "How often each run lands on the best dispatch", 340), f"cvq_bars_{pick[0]}_{pick[1]}")
with right:
    sim, hw = rows["sim"], real
    if hw and hw["optimal"] and hw["p_opt"] > res["uniform_valid_p_opt"]:
        verdict = (f"On the real chip QAOA's most frequent answer is the best dispatch, and it hits the optimum "
                   f"{hw['p_opt'] / res['uniform_valid_p_opt']:.1f}× as often as guessing among valid assignments. "
                   f"Noise cut the noiseless {_pct(sim['p_opt'])} to {_pct(hw['p_opt'])}.")
        tone = "ok"
    elif hw:
        verdict = (f"Here the chip does not beat guessing: {_pct(hw['p_opt'])} against {_pct(res['uniform_valid_p_opt'])} "
                   f"for a random valid assignment. {hw['two_qubit']} two-qubit gates add too much noise at this size.")
        tone = "warn"
    else:
        verdict, tone = "No real-device result for this problem.", "info"
    st.markdown(
        '<div class="ev-card"><h3>What this shows</h3><ul>'
        f'<li>{verdict}</li>'
        f'<li>The exact classical search gives the right answer in {_time(rows["exact"]["seconds"])}. The hardware path took '
        f'{_time(hw["seconds"]) if hw else "—"} end to end. <b>No quantum advantage is claimed.</b></li>'
        + ('<li>The nearest-available rule picks a <b>worse</b> dispatch here: it ignores the coverage the exact solution keeps.</li>'
           if abs(rows["greedy"]["cost"] - res["exact_cost"]) > 1e-9 else "")
        + '<li>Fake backends replay a calibration snapshot and came out more optimistic than the real chip.</li>'
        '</ul>'
        f'<p class="pc-caption" style="margin-top:10px">IBM job <code>{hw["job_id"] if hw else "—"}</code>, '
        f'{(hw["completed_utc"] or "")[:10] if hw else ""}. Full write-up: '
        f'<a href="{REPO}/reports/ibm_hardware/README.md" target="_blank">IBM hardware report</a>.</p></div>',
        unsafe_allow_html=True)

if st.button("Run the classical solvers and simulator again", key="cvq_rerun", help="New random seed for the simulator's 4,096 samples."):
    st.session_state["cvq_seed"] = seed + 1
    st.rerun()

with st.expander("Limitations"):
    st.markdown(
        "- Problems are small (4–6 qubits) and synthetic; classical search is instant at these sizes.\n"
        "- Hardware noise roughly halves the noiseless gain at 4 qubits and removes it at 6.\n"
        "- No error mitigation was used, and the circuit angles were tuned in simulation, not on the chip.\n"
        "- One job on one day; device calibration changes daily.\n"
        "- Minutes of queue and processing make hardware unusable for live dispatch today.")
