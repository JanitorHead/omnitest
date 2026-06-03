"""Toggle tema claro / oscuro — default oscuro."""
import streamlit as st

# Emojis con presentación color (mismo estilo en móvil y desktop)
_ICON_LIGHT = "☀️"   # modo oscuro activo → pulsar para claro
_ICON_DARK = "🌙"    # modo claro activo → pulsar para oscuro


def render_theme_toggle() -> None:
    tema = st.session_state.get("tema", "dark")
    icon = _ICON_LIGHT if tema == "dark" else _ICON_DARK
    if st.button(icon, key="btn_theme_toggle", help=_tooltip(tema), type="secondary"):
        st.session_state["tema"] = "light" if tema == "dark" else "dark"
        st.rerun()


def _tooltip(tema: str) -> str:
    return "Cambiar a modo claro" if tema == "dark" else "Cambiar a modo oscuro"
