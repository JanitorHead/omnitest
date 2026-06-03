"""Omnitest — punto de entrada Streamlit (single-page)."""
import streamlit as st

from src import APP_NOMBRE, APP_VERSION
from src.ui import init_estado, render_app
from src.ui.styles import inject_styles

st.set_page_config(
    page_title=APP_NOMBRE,
    page_icon="static/logo.svg",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Versión desplegada (visible en metadatos; ayuda a confirmar redeploy en Streamlit Cloud)
st.session_state.setdefault("_omni_version", APP_VERSION)

init_estado()
inject_styles()
render_app()
