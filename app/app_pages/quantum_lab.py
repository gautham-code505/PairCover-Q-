"""Quantum Lab: what QAOA actually did on the selected scenario."""

import streamlit as st

import app_shell as shell
import ui_components as ui

shell.page_header("Quantum Lab", "Configure and run QAOA, then inspect the optimiser, the measured samples and how "
                  "often it found the true optimum compared with random guessing.", scenario_picker=True, eyebrow="Quantum")
scen = shell.current_scenario()
shell.set_active(scen)
ss = st.session_state
ui.render_quantum_lab(results=ss["pq_results"], scenario=scen, current_key=ss.get("current_run_key"),
                      on_run=shell.on_run, failures=ss["pq_failures"])
