"""Create your own emergency on the synthetic city."""

import streamlit as st

import app_shell as shell
from custom_view import render_custom_emergency

shell.page_header("Create your own emergency", "Click the city to place calls, set how urgent they are, mark ambulances busy, "
                  "then see which plan each method chooses.", eyebrow="Try it")
ss = st.session_state
render_custom_emergency(ss, ss["pq_results"], ss["pq_failures"], on_run=shell.on_run,
                        on_compare=shell.on_compare, set_active=shell.set_active)
