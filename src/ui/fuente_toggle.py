"""Selector Fuente — toggle pill; ambos botones secondary (evita negro de Streamlit)."""
import streamlit as st


def render_fuente_toggle(opciones: dict[str, str]) -> str:
    if "fuente" not in st.session_state:
        st.session_state["fuente"] = "ia"

    actual = st.session_state["fuente"]
    labels = list(opciones.keys())

    st.markdown(
        f'<div class="fuente-picker-marker fuente-active-{actual}"></div>',
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2, gap="small")
    for col, label in zip((col1, col2), labels, strict=True):
        slug = opciones[label]
        with col:
            if st.button(
                label,
                key=f"fuente_{slug}",
                use_container_width=True,
                type="secondary",
            ):
                if slug != actual:
                    st.session_state["fuente"] = slug
                    st.rerun()

    return st.session_state["fuente"]
