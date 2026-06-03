"""Grid de exportación — estado final del flujo."""
import html as html_lib
from typing import Any

import streamlit as st

from .export_icons import icono_export
from .state import ir_a_entrada

MIME_WORD = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
MIME_PDF = "application/pdf"
MIME_ZIP = "application/zip"


def _tarjeta_export(icon_id: str, nombre: str, desc: str) -> str:
    return (
        f'<div class="export-card">'
        f'<div class="export-card-header">{icono_export(icon_id)}'
        f'<h4>{html_lib.escape(nombre)}</h4></div>'
        f'<p>{html_lib.escape(desc)}</p></div>'
    )


def _variantes_word_pdf(
    res: dict,
    nb: str,
    es_multi: bool,
    *,
    combinado_con: str,
    combinado_sin: str,
    zip_con: str,
    zip_sin: str,
    fname_con: str,
    fname_sin: str,
    fname_zip_con: str,
    fname_zip_sin: str,
    mime: str,
) -> list[dict[str, Any]]:
    variantes = [
        {
            "label": "Unificados · con respuestas",
            "key": combinado_con,
            "fname": fname_con,
            "mime": mime,
        },
        {
            "label": "Unificados · sin respuestas",
            "key": combinado_sin,
            "fname": fname_sin,
            "mime": mime,
        },
    ]
    if es_multi:
        variantes.extend([
            {
                "label": "Separados · con respuestas",
                "key": zip_con,
                "fname": fname_zip_con,
                "mime": MIME_ZIP,
            },
            {
                "label": "Separados · sin respuestas",
                "key": zip_sin,
                "fname": fname_zip_sin,
                "mime": MIME_ZIP,
            },
        ])
    return [v for v in variantes if res.get(v["key"])]


def _render_split_download(
    card_id: str,
    icon_id: str,
    nombre: str,
    desc: str,
    variantes: list[dict[str, Any]],
    res: dict,
) -> None:
    if not variantes:
        st.markdown(_tarjeta_export(icon_id, nombre, desc), unsafe_allow_html=True)
        st.caption("No disponible para este conjunto de tests.")
        return

    labels = [v["label"] for v in variantes]

    st.markdown(_tarjeta_export(icon_id, nombre, desc), unsafe_allow_html=True)
    selected = st.selectbox(
        "Opciones de descarga",
        options=labels,
        key=f"export_sel_{card_id}",
        label_visibility="collapsed",
    )
    idx = labels.index(selected)
    actual = variantes[idx]
    data = res.get(actual["key"]) or b""

    st.download_button(
        "Descargar",
        data=data,
        file_name=actual["fname"],
        mime=actual["mime"],
        use_container_width=True,
        key=f"dl_{card_id}",
    )


def _render_simple_download(
    key: str,
    nombre: str,
    desc: str,
    icon_id: str,
    mime: str,
    fname: str,
    res: dict,
) -> None:
    st.markdown(_tarjeta_export(icon_id, nombre, desc), unsafe_allow_html=True)
    st.download_button(
        "Descargar",
        data=res[key],
        file_name=fname,
        mime=mime,
        use_container_width=True,
        key=f"export_{key}",
    )


def render_export() -> None:
    res = st.session_state.get("resultado")
    if not res:
        st.warning("No hay resultados. Vuelve atrás y extrae preguntas primero.")
        if st.button("← Volver"):
            ir_a_entrada()
            st.rerun()
        return

    st.markdown(
        f'<p class="review-summary">{res["tests_ok"]} test(s) · listos para descargar</p>',
        unsafe_allow_html=True,
    )
    if st.session_state.get("ia_procesado_con"):
        st.markdown(
            f'<span class="model-badge">Procesado con {html_lib.escape(st.session_state["ia_procesado_con"])}</span>',
            unsafe_allow_html=True,
        )

    nb = res["nombre_base"]
    es_multi = res.get("es_multi", False)

    word_vars = _variantes_word_pdf(
        res,
        nb,
        es_multi,
        combinado_con="word_combinado_con",
        combinado_sin="word_combinado_sin",
        zip_con="zip_word_individuales_con",
        zip_sin="zip_word_individuales_sin",
        fname_con=f"{nb}_Word_con.docx",
        fname_sin=f"{nb}_Word_sin.docx",
        fname_zip_con=f"{nb}_Word_por_test_con.zip",
        fname_zip_sin=f"{nb}_Word_por_test_sin.zip",
        mime=MIME_WORD,
    )
    pdf_vars = _variantes_word_pdf(
        res,
        nb,
        es_multi,
        combinado_con="pdf_combinado_con",
        combinado_sin="pdf_combinado_sin",
        zip_con="zip_pdf_individuales_con",
        zip_sin="zip_pdf_individuales_sin",
        fname_con=f"{nb}_con.pdf",
        fname_sin=f"{nb}_sin.pdf",
        fname_zip_con=f"{nb}_PDF_por_test_con.zip",
        fname_zip_sin=f"{nb}_PDF_por_test_sin.zip",
        mime=MIME_PDF,
    )

    st.markdown('<div class="export-grid">', unsafe_allow_html=True)

    row1 = st.columns(3)
    with row1[0]:
        _render_simple_download(
            "html_quiz", "Quiz HTML", "Mini-app offline en cualquier navegador.",
            "quiz", "text/html", f"{nb}_Quiz.html", res,
        )
    with row1[1]:
        _render_simple_download(
            "apkg_anki", "Anki", "Mazo .apkg interactivo.",
            "anki", "application/octet-stream", f"{nb}_Anki.apkg", res,
        )
    with row1[2]:
        _render_simple_download(
            "zip_remnote", "RemNote", "ZIP Markdown MCQ.",
            "remnote", MIME_ZIP, f"{nb}_RemNote.zip", res,
        )

    row2 = st.columns(3)
    with row2[0]:
        _render_split_download("word", "word", "Word", "Documento .docx.", word_vars, res)
    with row2[1]:
        _render_split_download("pdf", "pdf", "PDF", "PDF para imprimir.", pdf_vars, res)
    with row2[2]:
        _render_simple_download(
            "zip_imagenes", "Imágenes", "Todas las imágenes sueltas.",
            "images", MIME_ZIP, f"{nb}_Imagenes.zip", res,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    if word_vars or pdf_vars:
        por_test = (
            '<li><strong>Separados</strong>: un ZIP con un documento distinto por cada test.</li>'
            if es_multi
            else ""
        )
        st.markdown(
            '<div class="export-format-legend">'
            "<p>Word y PDF — opciones del desplegable</p>"
            "<ul>"
            "<li><strong>Unificados</strong>: un solo archivo con todos los tests juntos.</li>"
            f"{por_test}"
            "<li><strong>Con / sin respuestas</strong>: incluye o no la opción correcta marcada.</li>"
            "</ul></div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    if st.button("← Convertir otro material", use_container_width=True):
        ir_a_entrada()
        st.rerun()
