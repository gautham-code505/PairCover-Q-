"""Dispatch console: the fixed scenarios, solved by the method the user picks."""

import streamlit as st

import app_shell as shell
import ui_components as ui

shell.page_header("Dispatch console", "Calls on the left, the response zone in the middle, the decision on the right. "
                  "Run two methods and the console explains what changed.", scenario_picker=True, eyebrow="Try it")
scen = shell.current_scenario()
shell.set_active(scen)
ss = st.session_state
ui.render_dispatch_console(scenario=scen, results=ss["pq_results"], current_key=ss.get("current_run_key"),
                           on_run=shell.on_run, failures=ss["pq_failures"], on_compare=shell.on_compare)
