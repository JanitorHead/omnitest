"""Toggle tema claro / oscuro — default oscuro."""
import streamlit as st


def render_theme_toggle() -> None:
    tema = st.session_state.get("tema", "dark")
    icon = "☀" if tema == "dark" else "☽"
    if st.button(icon, key="btn_theme_toggle", help=_tooltip(tema), type="secondary"):
        st.session_state["tema"] = "light" if tema == "dark" else "dark"
        st.rerun()


def _tooltip(tema: str) -> str:
    return "Cambiar a modo claro" if tema == "dark" else "Cambiar a modo oscuro"
