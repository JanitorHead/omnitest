"""Omnitest — punto de entrada Streamlit (single-page)."""
import streamlit as st

from src import APP_NOMBRE
from src.ui import init_estado, render_app
from src.ui.styles import inject_styles

st.set_page_config(
    page_title=APP_NOMBRE,
    page_icon="static/logo.svg",
    layout="centered",
    initial_sidebar_state="collapsed",
)

init_estado()
inject_styles()
render_app()
