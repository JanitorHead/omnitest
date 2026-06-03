"""Grid de exportación — estado final del flujo."""
import html as html_lib

import streamlit as st

from .export_icons import icono_export
from .state import ir_a_entrada


def _tarjeta_export(icon_id: str, nombre: str, desc: str) -> str:
    return (
        f'<div class="export-card">'
        f'<div class="export-card-header">{icono_export(icon_id)}'
        f'<h4>{html_lib.escape(nombre)}</h4></div>'
        f'<p>{html_lib.escape(desc)}</p></div>'
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

    modo = st.radio(
        "Formato Word/PDF",
        ["Todo junto", "Archivos separados (ZIP)"],
        horizontal=True,
    )
    version = st.radio(
        "Respuestas",
        ["Con respuestas", "Sin respuestas"],
        horizontal=True,
    )
    suf = "con" if version == "Con respuestas" else "sin"

    items = [
        ("html_quiz", "Quiz HTML", "Mini-app offline en cualquier navegador.", "quiz",
         "text/html", f"{nb}_Quiz.html"),
        ("apkg_anki", "Anki", "Mazo .apkg interactivo.", "anki",
         "application/octet-stream", f"{nb}_Anki.apkg"),
        ("zip_remnote", "RemNote", "ZIP Markdown MCQ.", "remnote",
         "application/zip", f"{nb}_RemNote.zip"),
    ]
    if modo == "Todo junto":
        items += [
            (f"word_combinado_{suf}", "Word", "Documento .docx.", "word",
             "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
             f"{nb}_Word_{suf}.docx"),
            (f"pdf_combinado_{suf}", "PDF", "PDF para imprimir.", "pdf",
             "application/pdf", f"{nb}_{suf}.pdf"),
        ]
    else:
        items += [
            ("zip_word_individuales", "Word (ZIP)", "Un .docx por test.", "word",
             "application/zip", f"{nb}_Word_individual.zip"),
            ("zip_pdf_individuales", "PDF (ZIP)", "Un .pdf por test.", "pdf",
             "application/zip", f"{nb}_PDF_individual.zip"),
        ]
    items.append(
        ("zip_imagenes", "Imágenes", "Todas las imágenes sueltas.", "images",
         "application/zip", f"{nb}_Imagenes.zip")
    )

    st.markdown('<div class="export-grid">', unsafe_allow_html=True)

    for i in range(0, len(items), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(items):
                break
            key, nombre, desc, icon_id, mime, fname = items[idx]
            with col:
                st.markdown(_tarjeta_export(icon_id, nombre, desc), unsafe_allow_html=True)
                st.download_button(
                    "Descargar",
                    data=res[key],
                    file_name=fname,
                    mime=mime,
                    use_container_width=True,
                    key=f"export_{key}_{suf}_{modo}",
                )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("← Convertir otro material", use_container_width=True):
        ir_a_entrada()
        st.rerun()
