"""Estado de sesión — máquina de flujo single-page."""
import streamlit as st

from ..api_config import config_vacia


def init_estado() -> None:
    defaults = [
        ("flujo", "entrada"),           # entrada | revision | export
        ("fuente", "ia"),               # daypo | ia
        ("resultado", None),
        ("ia_datos", None),
        ("ia_chat", []),
        ("ia_requests_sesion", 0),
        ("ia_procesado_con", ""),
        ("ia_pid_usado", ""),
        ("ia_modelo_usado", ""),
        ("ia_pid_usado", ""),
        ("daypo_tests", None),
        ("daypo_errores", []),
        ("error_inline", ""),
        ("banner_429", False),
        ("tema", "dark"),               # dark | light
        ("api_config", None),
        ("export_modo", "Todo junto"),
        ("modal_upload_id", 0),
        ("api_modal_reopen", False),
        ("api_import_msg", ""),
    ]
    for k, v in defaults:
        if k not in st.session_state:
            st.session_state[k] = v
    if st.session_state["api_config"] is None:
        st.session_state["api_config"] = config_vacia()


def ir_a_entrada() -> None:
    """Reinicia por completo (nuevo material)."""
    st.session_state["flujo"] = "entrada"
    st.session_state["resultado"] = None
    st.session_state["ia_datos"] = None
    st.session_state["ia_chat"] = []
    st.session_state["daypo_tests"] = None
    st.session_state["daypo_errores"] = []
    st.session_state["error_inline"] = ""
    st.session_state["banner_429"] = False
    st.session_state["ia_procesado_con"] = ""
    st.session_state["ia_pid_usado"] = ""
    st.session_state["ia_modelo_usado"] = ""


def ir_a_editar_entrada() -> None:
    """Vuelve al formulario para cambiar el material sin borrar el preview."""
    st.session_state["flujo"] = "entrada"
    st.session_state["error_inline"] = ""


def ir_a_revision() -> None:
    st.session_state["flujo"] = "revision"


def ir_a_export() -> None:
    st.session_state["flujo"] = "export"
