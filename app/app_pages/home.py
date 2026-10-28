"""Home: what PairCover-Q is, in ten seconds, and the fastest way into the demo."""

from __future__ import annotations

import streamlit as st

import app_shell as shell
from app.result_adapter import get_scenario, run_exact, run_greedy

REPO = "https://github.com/gautham-code505/PairCover-Q-"


@st.cache_data(show_spinner=False)
def _decision() -> dict:
    """The coverage demo's two decisions, computed by the real solvers (not typed in)."""
    g, e = run_greedy("scenario_2"), run_exact("scenario_2")
    s = get_scenario("scenario_2")
    pick = lambda r: {k: r[k] for k in ("assignments", "weighted_response_cost", "coverage_penalty", "objective_value")}
    return {"greedy": pick(g), "exact": pick(e), "positions": s["positions"],
            "travel": {f"{a}{c}": t for (a, c), t in s["travel_times"].items()}}


def _film(d: dict) -> str:
    """SVG replaying nearest-available, then PairCover-Q, on the coverage demo's own layout."""
    P = d["positions"]
    xs = [p[0] for p in P.values()]
    ys = [p[1] for p in P.values()]
    W, H, pad = 560, 330, 62
    k = min((W - 2 * pad) / (max(xs) - min(xs)), (H - 2 * pad - 30) / (max(ys) - min(ys)))
    X = lambda n: pad + (P[n][0] - min(xs)) * k
    Y = lambda n: pad + 10 + (max(ys) - P[n][1]) * k
    tt = d["travel"]

    def routes(asg):
        return "".join(f'<line class="route" x1="{X(a):.0f}" y1="{Y(a):.0f}" x2="{X(c):.0f}" y2="{Y(c):.0f}"/>' for a, c in asg)

    def labels(asg):
        return "".join(
            f'<text class="small" x="{(X(a) + X(c)) / 2:.0f}" y="{(Y(a) + Y(c)) / 2 - 8:.0f}" text-anchor="middle">{tt[a + c]:g} min</text>'
            for a, c in asg)

    g, e = d["greedy"], d["exact"]
    grid = "".join(f'<line class="fgrid" x1="{x}" y1="0" x2="{x}" y2="{H}"/>' for x in range(0, W, 40)) + \
           "".join(f'<line class="fgrid" x1="0" y1="{y}" x2="{W}" y2="{y}"/>' for y in range(0, H, 40))
    cap = f'<line class="pair" x1="{X("A1"):.0f}" y1="{Y("A1"):.0f}" x2="{X("A2"):.0f}" y2="{Y("A2"):.0f}"/>'
    units = "".join(f'<g class="unit"><rect x="{X(u) - 19:.0f}" y="{Y(u) - 14:.0f}" width="38" height="28" rx="6"/>'
                    f'<text x="{X(u):.0f}" y="{Y(u) + 5:.0f}">{u}</text></g>' for u in ("A1", "A2", "A3"))
    calls = "".join(f'<g class="callm"><circle class="ring" cx="{X(c):.0f}" cy="{Y(c):.0f}" r="18"/>'
                    f'<circle class="core" cx="{X(c):.0f}" cy="{Y(c):.0f}" r="17"/>'
                    f'<text x="{X(c):.0f}" y="{Y(c) + 5:.0f}">{c}</text></g>' for c in ("C2", "C3"))
    mid_x, top_y = (X("A1") + X("A2")) / 2, min(Y("A1"), Y("A2")) - 30
    sent_g = {a for a, _ in g["assignments"]}
    held_e = [u for u in ("A1", "A2", "A3") if u not in {a for a, _ in e["assignments"]}]
    scene_a = (f'<g class="scene a">{cap}{routes(g["assignments"])}{labels(g["assignments"])}'
               f'<text class="lost" x="{mid_x:.0f}" y="{top_y:.0f}">{" + ".join(sorted(u for u in ("A1", "A2") if u in sent_g))} both leave · backup lost</text>'
               f'<text class="verdict" x="18" y="{H - 16}">Nearest available · cost {g["objective_value"]:g}</text></g>')
    scene_b = (f'<g class="scene b">{cap}{routes(e["assignments"])}{labels(e["assignments"])}'
               + "".join(f'<text class="held" x="{X(u):.0f}" y="{Y(u) + 32:.0f}">{u} held in reserve</text>'  for u in held_e)
               + f'<text class="verdict" x="18" y="{H - 16}">PairCover-Q · cost {e["objective_value"]:g}</text></g>')
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Animated comparison: nearest available sends A1 and A2 '
            f'and costs {g["objective_value"]:g}; PairCover-Q keeps A2 home and costs {e["objective_value"]:g}.">'
            f'{grid}{scene_a}{scene_b}{units}{calls}</svg>')


shell.set_active(shell.current_scenario())
d = _decision()
g, e = d["greedy"], d["exact"]

_, sw = st.columns([8, 1])
# getattr fallback: a hot redeploy can leave an older app_shell (with _theme_switch) in memory.
_switch = getattr(shell, "theme_switch_html", None) or getattr(shell, "_theme_switch")
sw.markdown(_switch(), unsafe_allow_html=True)

left, right = st.columns([1.08, 1], gap="large", vertical_alignment="center")
with left:
    st.markdown(
        '<div class="hero-eyebrow">Coverage-aware ambulance dispatch · QUBO + QAOA</div>'
        '<h1 class="hero-title">Send the right ambulance.<br><em>Keep the city covered.</em></h1>'
        '<p class="hero-lede">When emergencies arrive together, sending the nearest ambulance to each one can leave a '
        'neighbourhood with <strong>no backup at all</strong>. PairCover-Q weighs response time against the coverage '
        'left behind, writes that trade-off in the form quantum computers accept, and solves it three ways: '
        '<strong>the usual rule, an exact search, and a quantum algorithm</strong>.</p>',
        unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    if b1.button("▶ See the decision in one click", type="primary", use_container_width=True, key="home_go",
                 help="Runs nearest-available and the exact optimiser on the coverage demo, then opens the console."):
        st.session_state["scenario_id"] = "scenario_2"
        shell.run_methods(["Nearest available", "Exact optimisation"], scen=get_scenario("scenario_2"))
        st.switch_page(shell.PAGES["console"])
    if b2.button("Create your own emergency", use_container_width=True, key="home_custom"):
        st.switch_page(shell.PAGES["custom"])
    st.markdown('<div class="trust"><span>Every result checked against an exact solver</span>'
                '<span>Synthetic city, clearly labelled</span><span>No quantum advantage claimed</span></div>',
                unsafe_allow_html=True)

with right:
    st.markdown(
        # A visually hidden checkbox + label pauses the loop without JavaScript (WCAG 2.2.2).
        f'<div class="film"><input type="checkbox" id="film-pause" class="film-toggle" aria-label="Pause the animation">'
        f'<div class="film-head"><span class="rec">Replay</span><span>Coverage demo · 2 calls · 3 ambulances</span>'
        f'<label for="film-pause" class="film-btn" title="Pause or play the animation"></label></div>'
        f'{_film(d)}'
        f'<div class="film-foot"><span><b>Nearest available:</b> A1 and A2 both leave, cost {g["objective_value"]:g}.</span>'
        f'<span><b>PairCover-Q:</b> A2 stays home, cost {e["objective_value"]:g}.</span></div>'
        f'<div class="film-note">A1 and A2 cover the same area for each other. Lines are travel minutes; positions are synthetic.</div></div>',
        unsafe_allow_html=True)

st.markdown('<div class="section-label">How it works</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="how">'
    '<div><span class="n">1</span><span class="chip" style="background:color-mix(in srgb,var(--red) 14%,transparent);color:var(--red)">Calls</span>'
    '<h3>Emergencies arrive together</h3><p>Several calls, a few free ambulances, and stations that cover the same area '
    'for each other. Send both partners away and that area has no one left.</p></div>'
    '<div><span class="n">2</span><span class="chip" style="background:color-mix(in srgb,var(--violet) 14%,transparent);color:var(--violet)">QUBO</span>'
    '<h3>One yes/no per choice</h3><p>"Does ambulance A go to call C?" becomes one binary variable, one qubit. '
    'Losing a backup pair is a penalty between exactly two variables, which is the shape quantum optimisers take natively.</p></div>'
    '<div><span class="n">3</span><span class="chip" style="background:color-mix(in srgb,var(--teal) 14%,transparent);color:var(--teal)">Verify</span>'
    '<h3>Three solvers, one answer key</h3><p>Nearest-available, exhaustive search and QAOA solve the same problem, QAOA on a '
    'simulator and on a real IBM quantum computer. Every quantum result is graded against the exact answer and against random guessing.</p></div>'
    '</div>', unsafe_allow_html=True)

gain = g["objective_value"] - e["objective_value"]
st.markdown('<div class="section-label">What we found</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="proof">'
    f'<div class="g"><div class="big">{g["objective_value"]:g} → {e["objective_value"]:g}</div>'
    f'<p>On the coverage demo, keeping one ambulance home costs <b>{e["weighted_response_cost"] - g["weighted_response_cost"]:g} more '
    f'weighted minute</b> but removes a coverage penalty of {g["coverage_penalty"]:g}, cutting total cost by {gain:g}.</p>'
    '<div class="src">Computed live by the solvers on this page load</div></div>'
    '<div><div class="big">−2.15 <small>min</small></div>'
    '<p>Mean response time at 5 calls per hour in a simulated city (7 days × 30 runs) against nearest-available, 95% CI −2.67 to −1.63. '
    'Planning simultaneous calls together explains this: batching alone gets −2.18. The coverage term\'s own effect is slightly less '
    'uncovered demand, with no significant change in late arrivals.</p>'
    f'<div class="src">Source: <a href="{REPO}/blob/main/reports/rolling_simulation/README.md" target="_blank">rolling-simulation report</a></div></div>'
    '<div class="q"><div class="big">19 <small>of 23</small></div>'
    '<p>Simulation-derived problems (4–12 qubits) where depth-3 QAOA put more probability on the optimum than random guessing among valid plans. '
    'On the real IBM chip ibm_fez (6 runs) a 4-qubit case hit the best plan 46–49% of the time against 20% for guessing; '
    'at 6 qubits the gain was marginal and unreliable. '
    'The exact solver is still faster at these sizes.</p>'
    f'<div class="src">Source: <a href="{REPO}/blob/main/reports/qaoa_benchmark/README.md" target="_blank">QAOA benchmark report</a></div></div>'
    '</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="honest"><b>Honest by design</b>'
    '<span>The city, calls and ambulances are synthetic test data. QAOA runs live on a noiseless simulator; three circuits also ran '
    'once on a real IBM quantum computer (see Classical vs Quantum). At these sizes an '
    'ordinary computer solves the problem instantly, so we claim no quantum advantage: we show where quantum fits, and what it would take.</span>'
    '</div>'
    f'<div class="foot"><span>PairCover-Q · coverage-aware ambulance dispatch</span>'
    f'<span><a href="{REPO}" target="_blank">Source code on GitHub</a></span></div>',
    unsafe_allow_html=True)
