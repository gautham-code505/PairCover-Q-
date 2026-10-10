# PairCover-Q — UI/UX Specification

Emergency-operations analytics console for coverage-aware ambulance assignment
(QUBO + QAOA). Implemented as reusable presentation components in
`app/ui_components.py`. The UI only **displays** backend results; it never
computes objectives, runs QUBO/QAOA, or invents metrics.

## 1. Principles

1. **Honest by default.** Every page shows a *SYNTHETIC DATA* banner. No claims of live GPS, live traffic, real deployment or quantum advantage. QAOA is labelled "simulator run".
2. **Missing ≠ zero.** Absent values render as `—` or an empty state, never `0`.
3. **Meaning never rests on colour alone.** Every status has an icon and a word (✔ Feasible, ✖ Infeasible, ⚠ unserved).
4. **Calm density.** Dark console, generous spacing, KPIs first, detail below.
5. **Derived numbers are labelled.** Best-of-N, per-method means and % difference vs a reference are display-time derivations and say "derived".

## 2. Visual system

| Token | Hex | Use | Contrast on `bg` |
|---|---|---|---|
| bg | `#0B1220` | app background | — |
| surface / surface_2 | `#121B2D` / `#182338` | cards / raised | — |
| border | `#566A91` | control/chart borders | 3.45:1 (≥3:1) |
| divider | `#2A3856` | decorative hairlines only | — |
| text | `#E6EDF7` | body | 15.9:1 |
| muted | `#9FB0C8` | captions, axes | 8.5:1 |
| **teal** | `#2DD4BF` | available resources, feasible, assigned | 10.1:1 |
| **amber** | `#F5A524` | coverage risk, unserved, synthetic label | 9.2:1 |
| **red** | `#FF6B6B` | critical, infeasible, errors | 6.7:1 |
| blue / violet | `#7AA2F7` / `#C4A7FF` | neutral series / quantum series | 7.4:1 / 9.2:1 |

Ratios computed (WCAG relative luminance) against `bg`. All text/background pairs meet WCAG AA (4.5:1); status colours meet it as text on `bg`. Method series use blue/violet/pink/cyan/grey so they never collide with the semantic teal/amber/red.

Typography: system sans; body ≥14 px, labels 12.5 px uppercase tracking; tabular numerals for metrics. Spacing on a 4/8 px rhythm; cards radius 12 px; max content width 1280 px. Focus rings (2 px blue) on all interactive elements; shimmer animation disabled under `prefers-reduced-motion`.

## 3. Views (navigation order = `ui.VIEWS`)

Each page: header (eyebrow, title, subtitle, `SYNTHETIC DATA` chip, scenario chip) → synthetic banner → content.

1. **Overview** — KPI strip (ambulances available in teal, calls, methods with results, failed runs in red), latest result per method with provenance badge, failure list, “scope” callout stating what is *not* claimed.
2. **Scenario Builder** — demand and travel-time tables (blank = ineligible), one atomic run form: backend-declared parameters, methods, optional availability/priorities (only when the backend honours them). Editing never triggers a run.
3. **Dispatch Simulator** — tabs: *Assignment* (KPIs, table, **schematic** ambulance→call diagram, never a map), *Method comparison* (grouped cost components, runtime, ★ lowest *feasible* raw objective with ties), *Objective definitions* (raw objective vs energies).
4. **Quantum Lab** — run selector; provenance + backend badges; optimizer-status callout (red if not converged); KPI strip with *expected energy* and *best feasible raw objective* shown separately; tabs *Energy & optimizer* (“which number is which” table, optimizer history or empty state, initial→final endpoints labelled not-a-trace), *Measured samples* (infeasible-share callout, outcome bar, statevector-vs-sampled-vs-baseline bars, top-k bitstring chart with decoded plans in hover and table), *Parameters*, *Raw payload*.
5. **Benchmark Analytics** — tabs *Summary* (per scenario×method; objective stats over feasible runs only; feasible rate as n/N; derived difference vs a chosen reference), *QAOA diagnostics* (backend values per run/seed), *Run history* (filter, drill-down, JSON export).

## 4. Quantity vocabulary (never mixed)
Raw objective (dispatch cost) · QUBO energy · Expected energy ⟨H⟩ · Sampled mean energy · Penalised surrogate. Definitions live in `ui_helpers.QUANTITIES` and are shown in Dispatch Simulator and Quantum Lab. Classical vs sampled QAOA is shown by a provenance badge on every result; inferred provenance says “(inferred)”.

## 5. States
| State | Treatment |
|---|---|
| Loading | `loading_state` / `run_with_loading` status box with steps; `skeleton()` placeholders |
| Empty | dashed card: icon, title, reason, next step (`empty_state`) — per panel, so one missing input never blanks a page |
| Error | red `role="alert"` card + technical details; failure recorded, excluded from analytics |
| Optimizer not converged | red callout, run kept and visible |
| Infeasible result / samples | red badge + alert (result); share-of-shots callout, red + hatched “x” bars (samples) |
| Schema drift | collapsed warning; renderable results still shown |
| Large tables | height-capped scrolling tables, row cap with “first N of M” note |

## 6. Result and experiment schema
See `docs/ui_integration_note.md` §2 (single source of truth).

## 7. Accessibility
- Contrast: text ≥ AA, control borders ≥ 3:1. Status never colour-only: icon + word, and chart series also differ by pattern (feasible solid, infeasible “x” hatch, unclassified dots) or marker shape.
- Every chart has a “Data for …” expander or an adjacent table with the same numbers. Hover adds detail but is never the only source of a status.
- `role="alert"` for errors/infeasibility, `role="note"/"status"` otherwise; decorative glyphs `aria-hidden` (Streamlit’s sanitiser may strip some attributes — verify).
- Focus ring on interactive elements; shimmer disabled under `prefers-reduced-motion`; text ≥ 12.5 px (labels) / 14 px (body); long values wrap (`overflow-wrap:anywhere`).
- Narrow screens: columns stack (Streamlit), KPI font shrinks below 640 px, charts use horizontal legends below the plot.
- Plotly figures have no alt text; the data expanders are the text alternative.

## 8. UI validation checklist (manual, in a browser)
- [ ] Every page shows the `SYNTHETIC DATA` chip and banner; schematic caption says “not a geographic map”.
- [ ] Empty session: every view shows an empty state, none crashes.
- [ ] Run a feasible classical method: ★ appears only on a feasible result; infeasible results are faded and never starred.
- [ ] QAOA with `success=False`: red optimizer callout; run still in history.
- [ ] QAOA without `history`: empty state + endpoints chart captioned “not a convergence curve”.
- [ ] QAOA with infeasible shots: callout shows the share; samples marked feasible/infeasible/unclassified with legend and pattern.
- [ ] Keys decode as documented (`000001` → first variable); axis says Qiskit order.
- [ ] Expected energy, raw objective and surrogate appear as separate labelled rows; no sum or difference is shown between them.
- [ ] Force a backend exception: red panel, failure listed on Overview/Benchmarks, no chart gets a point for it.
- [ ] 375 px width: no horizontal page scroll, KPI text wraps, tables scroll inside their frame.
- [ ] Keyboard: tab order reaches tabs, selects and the run button with a visible focus ring.
- [ ] 200+ rows of history: table scrolls, row-cap note shown.
- [ ] Light-theme browser: dark console still readable (config.toml applied).

## 9. Testing status
Pure helpers: `tests/test_ui_helpers.py` (executed, passing). Component smoke tests via Streamlit `AppTest`: `tests/test_ui_components_smoke.py` (executed with Streamlit 1.65.0 / Plotly 7.1.0, passing; checks no exceptions, not appearance). Fixtures are synthetic and are not QAOA output.
