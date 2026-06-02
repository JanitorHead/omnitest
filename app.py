"""Omnitest — punto de entrada de la app Streamlit.

De cualquier fuente (Daypo, fotos, PDFs, Word, texto o IA) a material de
estudio tipo test: Word, PDF, RemNote, Anki y un quiz interactivo offline.

Ejecutar con:  streamlit run app.py
"""
import streamlit as st

from src import APP_ICONO, APP_NOMBRE, APP_TAGLINE
from src.ui import init_estado, render_resultados, render_tab_daypo, render_tab_ia

st.set_page_config(
    page_title=APP_NOMBRE,
    page_icon=APP_ICONO,
    layout="centered",
    initial_sidebar_state="collapsed",
)

init_estado()

st.title(f"{APP_ICONO} {APP_NOMBRE}")
st.caption(APP_TAGLINE)
st.divider()

# Si ya hay resultados, mostramos la pantalla de descargas y paramos aquí.
if st.session_state["resultado"] is not None:
    render_resultados()
    st.stop()

tab_daypo, tab_ia = st.tabs(["🔗 Extraer de Daypo", "🤖 Importar con IA"])

with tab_daypo:
    render_tab_daypo()

with tab_ia:
    render_tab_ia()
