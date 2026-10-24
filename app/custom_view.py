"""
"Create your own emergency" screen.

The user builds a situation on the synthetic city (click the map or use the form), and the
standard dispatch console below solves it. The engine lives in app/custom_emergency.py.
"""

from __future__ import annotations

from typing import Any, Callable, MutableMapping

import numpy as np
import plotly.graph_objects as go
import streamlit as st

import custom_emergency as ce
import ui_components as ui
from qrescue.simulation.region import default_region

PRIORITY_LABELS = {1: "P1 · life-threatening", 2: "P2 · urgent", 3: "P3 · routine"}


def _city_figure(calls: list[tuple[int, int]], busy: list[str]) -> go.Figure:
    """Synthetic city: zones (shaded by expected demand), stations, hospitals and the user's calls."""
    region = default_region()
    c = ui.COLORS
    z = region.zones
    share = region.demand_share
    fig = go.Figure()
    # Zones: the clickable layer. Larger, darker squares = more calls expected.
    fig.add_trace(go.Scatter(
        x=z[:, 0], y=z[:, 1], mode="markers+text",
        marker=dict(symbol="square", size=40, color=share, colorscale=[[0, c["surface_2"]], [1, c["amber"]]],
                    opacity=0.55, line=dict(width=1, color=c["border"])),
        text=[ce.zone_label(i) for i in range(len(z))], textfont=dict(size=10, color=c["muted"]),
        customdata=np.arange(len(z)),
        hovertemplate="Zone %{text}<br>%{customdata} · click to add a call here<extra></extra>",
        name="zones", showlegend=False,
        selected=dict(marker=dict(opacity=0.85)), unselected=dict(marker=dict(opacity=0.55)),
    ))
    names = ce.ambulance_names()
    for s_idx, (x, y) in enumerate(region.stations):
        units = [n for n, h in zip(names, region.home_station) if h == s_idx]
        free = [u for u in units if u not in busy]
        fig.add_trace(go.Scatter(
            x=[x], y=[y], mode="markers+text", text=[" ".join(units)], textposition="bottom center",
            textfont=dict(size=12, color=c["text"]),
            marker=dict(symbol="square", size=16, color=c["blue"] if free else c["muted"], line=dict(width=1.5, color=c["surface"])),
            hovertemplate=f"Station: {', '.join(units)}<br>{'available: ' + ', '.join(free) if free else 'all busy'}<extra></extra>",
            showlegend=False))
    fig.add_trace(go.Scatter(
        x=region.hospitals[:, 0], y=region.hospitals[:, 1], mode="markers+text", text=["H", "H"],
        textposition="middle center", textfont=dict(size=11, color=c["surface"]),
        marker=dict(symbol="circle", size=18, color=c["teal"]), hovertemplate="Hospital<extra></extra>", showlegend=False))
    if calls:
        pts = np.array([region.zones[zz] for zz, _ in calls])
        fig.add_trace(go.Scatter(
            x=pts[:, 0] + 0.9, y=pts[:, 1] + 0.9, mode="markers+text",
            text=[f"C{k + 1}" for k in range(len(calls))], textposition="top center",
            textfont=dict(size=13, color=c["red"]),
            marker=dict(symbol="circle", size=[22 - 3 * (p - 1) for _, p in calls], color=c["red"],
                        line=dict(width=2, color=c["surface"])),
            hovertemplate=[f"C{k + 1}: zone {ce.zone_label(zz)}, {PRIORITY_LABELS[p]}<extra></extra>" for k, (zz, p) in enumerate(calls)],
            showlegend=False))
    # A click selects a zone; keep every other marker at full strength instead of Plotly's faded look.
    for tr in fig.data[1:]:
        tr.update(unselected=dict(marker=dict(opacity=1)))
    fig.update_layout(
        height=430, margin=dict(l=8, r=8, t=8, b=8), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        clickmode="event+select", dragmode=False, hoverlabel=dict(bgcolor=c["surface"], font=dict(color=c["text"])),
        xaxis=dict(range=[-0.5, 24.5], visible=False, fixedrange=True),
        yaxis=dict(range=[-0.5, 24.5], visible=False, fixedrange=True, scaleanchor="x"),
    )
    return fig


def _clicked_zone(event: Any) -> int | None:
    """Zone index from a Plotly selection event, or None."""
    try:
        for pt in event.selection.points:
            if pt.get("curve_number") == 0:
                return int(pt["customdata"] if not isinstance(pt["customdata"], list) else pt["customdata"][0])
    except (AttributeError, KeyError, TypeError, ValueError):
        return None
    return None


def render_custom_emergency(
    ss: MutableMapping,
    results: list,
    failures: list,
    on_run: Callable[[str, dict[str, Any]], None],
    on_compare: Callable[[list[str]], None],
    set_active: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any] | None:
    """Builder panel plus the dispatch console for the user's situation. Returns the scenario or None."""
    ss.setdefault("ce_calls", [tuple(x) for x in ce.PRESETS["Town keeps its only ambulance"]["calls"]])
    ss.setdefault("ce_busy", [])
    ss.setdefault("ce_lambda", ce.DEFAULT_LAMBDA)

    st.markdown(
        '<div class="status-line idle"><span class="k">Create your own emergency.</span> '
        'Click a zone on the city map to add a call there, or start from a ready-made situation. '
        'Then run the methods below and compare them. The city, its stations and its demand are synthetic.</div>',
        unsafe_allow_html=True)

    preset_cols = st.columns(len(ce.PRESETS))
    for col, (name, pre) in zip(preset_cols, ce.PRESETS.items()):
        if col.button(name, key=f"ce_preset_{name}", use_container_width=True):
            ss["ce_calls"] = [tuple(x) for x in pre["calls"]]
            ss["ce_busy"] = list(pre["busy"])
            ss["ce_busy_pick"] = list(pre["busy"])
            st.rerun()

    left, right = st.columns([1.35, 1])
    with left:
        st.markdown('<div class="pc-eyebrow">Synthetic city · 24 × 24 km · click a zone to add a call</div>', unsafe_allow_html=True)
        event = st.plotly_chart(_city_figure(ss["ce_calls"], ss["ce_busy"]), key="ce_city_map", on_select="rerun",
                                selection_mode="points", config={"displayModeBar": False}, use_container_width=True)
        zone = _clicked_zone(event)
        if zone is not None and ss.get("_ce_last_click") != zone:
            ss["_ce_last_click"] = zone
            if len(ss["ce_calls"]) < ce.MAX_CALLS:
                ss["ce_calls"] = ss["ce_calls"] + [(zone, int(ss.get("ce_new_priority", 2)))]
                st.rerun()
            else:
                st.warning(f"At most {ce.MAX_CALLS} calls at once. Remove one first.")
        elif zone is None:
            ss["_ce_last_click"] = None
        st.caption("Darker zones expect more calls. Blue squares are stations (grey when every unit there is busy); "
                   "green circles are hospitals. Travel time = straight-line distance × 1.3 at 50 km/h.")

    with right:
        st.markdown('<div class="pc-eyebrow">Your calls</div>', unsafe_allow_html=True)
        st.radio("Priority for the next call", [1, 2, 3], index=1, horizontal=True, key="ce_new_priority",
                 format_func=lambda p: PRIORITY_LABELS[p].split(" · ")[0],
                 help="P1 counts three times as much as P3 when adding up response time.")
        if not ss["ce_calls"]:
            st.markdown('<div class="empty">No calls yet. Click a zone on the map or use the form below.</div>', unsafe_allow_html=True)
        for k, (zz, p) in enumerate(ss["ce_calls"]):
            c1, c2 = st.columns([5, 1], vertical_alignment="center")
            c1.markdown(f'<div class="call"><div class="top"><span class="id">C{k + 1} · zone {ce.zone_label(zz)}</span>'
                        f'<span class="pr{" hi" if p == 1 else ""}">{PRIORITY_LABELS[p]}</span></div>'
                        f'<div class="sub">{ce.zone_area(zz)}</div></div>', unsafe_allow_html=True)
            if c2.button("✕", key=f"ce_rm_{k}", help=f"Remove C{k + 1}"):
                ss["ce_calls"] = [x for i, x in enumerate(ss["ce_calls"]) if i != k]
                st.rerun()
        with st.form("ce_add_form", border=False):
            f1, f2 = st.columns([3, 2], vertical_alignment="bottom")
            add_zone = f1.selectbox("Or pick a zone", range(36), format_func=lambda z: f"{ce.zone_label(z)} · {ce.zone_area(z)}",
                                    index=14, key="ce_add_zone")
            if f2.form_submit_button("Add call", use_container_width=True, disabled=len(ss["ce_calls"]) >= ce.MAX_CALLS):
                ss["ce_calls"] = ss["ce_calls"] + [(int(add_zone), int(ss.get("ce_new_priority", 2)))]
                st.rerun()
        busy = st.multiselect("Ambulances already busy", ce.ambulance_names(),
                              default=None if "ce_busy_pick" in ss else ss["ce_busy"], key="ce_busy_pick",
                              help="Busy ambulances cannot be sent and do not count as backup.")
        if busy != ss["ce_busy"]:
            ss["ce_busy"] = busy
            st.rerun()
        lam = st.slider("How much to protect backup coverage (λ)", 0.0, 40.0, float(ss["ce_lambda"]), 1.0, key="ce_lambda_pick",
                        help="0 ignores coverage. 5 is what the 7-day simulation found never made arrivals later. "
                             "Higher values keep more areas covered at the cost of slower responses.")
        if lam != ss["ce_lambda"]:
            ss["ce_lambda"] = lam
            st.rerun()

    try:
        scen = ce.build_scenario(ss["ce_calls"], ss["ce_busy"], ss["ce_lambda"])
    except ValueError as exc:
        st.info(str(exc))
        return None
    if set_active:
        set_active(scen)   # runs started from the console below must solve this situation
    ok, why = ce.qaoa_available(scen)
    st.caption(f"This situation has {len(scen['landscape']['feasible'])} valid plans. "
               + (f"QAOA will use {why}." if ok else f"QAOA is not available here: {why}"))
    st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
    ui.render_dispatch_console(scenario=scen, results=results, current_key=ss.get("current_run_key"),
                               on_run=on_run, failures=failures, key_prefix="ce", on_compare=on_compare)
    return scen
