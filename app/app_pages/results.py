"""Every valid plan ranked, and every run compared."""

import streamlit as st

import app_shell as shell
import ui_components as ui

shell.page_header("Results & benchmarks", "Every valid plan for this scenario ranked by cost, where each method landed, "
                  "and the runs from this session side by side.", scenario_picker=True, eyebrow="Quantum")
scen = shell.current_scenario()
shell.set_active(scen)
ss = st.session_state
ui.render_results_and_benchmarks(results=ss["pq_results"], scenario=scen, failures=ss["pq_failures"])
