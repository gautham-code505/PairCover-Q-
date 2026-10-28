"""
PairCover-Q: coverage-aware ambulance dispatch with QUBO and QAOA (Q-Rescue).

Entry point. It sets up the page, theme and shared state, then hands over to the page the
user picked in the top navigation. Pages live in app/app_pages/; shared runners and the page
header live in app/app_shell.py.
"""

from __future__ import annotations

import os
import sys

# Project root and src/ on sys.path so both `app.` and `qrescue.` imports resolve.
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, ".."))
_SRC_DIR = os.path.join(_ROOT_DIR, "src")
for _p in (_ROOT_DIR, _SRC_DIR, _CURRENT_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st

st.set_page_config(
    page_title="PairCover-Q · coverage-aware dispatch",
    page_icon=os.path.join(_CURRENT_DIR, "assets", "logo_mark.svg"),
    layout="wide",
    initial_sidebar_state="collapsed",
)

import app_shell as shell  # noqa: E402
import ui_components as ui  # noqa: E402

ui.apply_theme()
shell.init_state()
st.logo(os.path.join(_CURRENT_DIR, "assets", "logo.svg"), size="large")

pages = {
    "": [
        st.Page(shell.PAGES["home"], title="Home", icon=":material/home:", default=True),
    ],
    "Try it": [
        st.Page(shell.PAGES["console"], title="Dispatch console", icon=":material/emergency:"),
        st.Page(shell.PAGES["custom"], title="Create your own emergency", icon=":material/add_location_alt:"),
    ],
    "Quantum": [
        st.Page(shell.PAGES["versus"], title="Classical vs Quantum", icon=":material/compare_arrows:"),
        st.Page(shell.PAGES["lab"], title="Quantum Lab", icon=":material/memory:"),
        st.Page(shell.PAGES["results"], title="Compare runs", icon=":material/leaderboard:"),
    ],
    "About": [
        st.Page(shell.PAGES["evidence"], title="Evidence", icon=":material/insights:"),
        st.Page(shell.PAGES["method"], title="Method & data", icon=":material/menu_book:"),
    ],
}

st.navigation(pages, position="top").run()
