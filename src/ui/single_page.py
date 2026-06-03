"""Single-page Omnitest — flujo iLovePDF en Streamlit."""
import base64
import html as html_lib
import time
from collections.abc import Callable

import requests
import streamlit as st

from ..daypo import completar_imagenes_tests, extraer_enlaces_daypo, extraer_test
from ..exporters import construir_resultado
from ..ai_providers import (
    aplicar_correccion_con_fallback,
    extraer_con_fallback,
    ia_a_tests,
)
from ..api_config import proveedores_configurados
from .api_modal import api_modal
from .logo import wordmark_html
from .export_grid import render_export
from .progress_ui import etiqueta_progreso
from .state import ir_a_editar_entrada, ir_a_entrada, ir_a_export, ir_a_revision
from .styles import inject_button_fixes, inject_styles
from .theme_toggle import render_theme_toggle
from .fuente_toggle import render_fuente_toggle
from .upload_zone import or_divider_html
from .faq import render_faq
from .work_log import work_log


def _render_header() -> None:
    c_brand, c_tools = st.columns([8, 1], gap="small")
    with c_brand:
        st.markdown(wordmark_html(), unsafe_allow_html=True)
    with c_tools:
        st.markdown('<div class="omni-header-tools-marker"></div>', unsafe_allow_html=True)
        c_theme, c_settings = st.columns(2, gap="small")
        with c_theme:
            render_theme_toggle()
        with c_settings:
            n = len(proveedores_configurados(st.session_state["api_config"]))
            tip = f"{n} API(s) activa(s)" if n else "Configurar APIs"
            if st.button("⚙️", key="btn_api_settings", help=tip, type="secondary"):
                api_modal()


def _render_hero() -> None:
    if st.session_state["flujo"] != "entrada":
        return
    if st.session_state.get("ia_datos") or st.session_state.get("daypo_tests"):
        return
    st.markdown(
        '<div class="omni-hero-gap" aria-hidden="true"></div>'
        '<h1 class="omni-h1">Convierte, ordena, limpia y estructura<br>'
        'tus <span class="omni-accent">preguntas tipo test</span></h1>'
        '<p class="omni-lead">Daypo, PDFs escaneados, fotos de exámenes, Word o texto mal pegado — '
        "Omnitest las unifica y te las devuelve en Word, PDF, Anki, RemNote, "
        "quiz offline e imágenes.</p>",
        unsafe_allow_html=True,
    )


def _procesar_daypo(texto: str, progress, status) -> bool:
    enlaces = extraer_enlaces_daypo(texto)
    if not enlaces:
        st.session_state["error_inline"] = "No se detectaron enlaces válidos de Daypo."
        return False

    n_enlaces = len(enlaces)
    inicio = time.monotonic()
    log_incidencias: list[str] = []

    def _log(msg: str) -> None:
        log_incidencias.append(msg)
        status.write(msg)

    progress.progress(0.05, text=etiqueta_progreso("Preparando extracción…", 0.05, inicio))
    status.caption("Registro de incidencias (solo avisos y errores).")

    tests: list[dict] = []
    errores: list[str] = []

    def _actualizar(actual: int, total: int, msg: str, indice_enlace: int) -> None:
        if n_enlaces > 1:
            msg = f"Test {indice_enlace + 1}/{n_enlaces} · {msg}"

        if total > 0:
            fraccion_enlace = actual / total
        elif actual == 0:
            fraccion_enlace = 0.05
        else:
            fraccion_enlace = 1.0

        base = 0.08 + (indice_enlace / n_enlaces) * 0.82
        span = 0.82 / n_enlaces
        fraccion = min(base + fraccion_enlace * span, 0.90)
        progress.progress(fraccion, text=etiqueta_progreso(msg, fraccion, inicio))

    for i, url in enumerate(enlaces):
        corto = url.rstrip("/").split("/")[-1][:40]

        def _cb(actual: int, total: int, msg: str, idx: int = i) -> None:
            _actualizar(actual, total, msg, idx)

        test = extraer_test(url, progreso=_cb)
        if test is None:
            errores.append(url)
            _log(f"❌ No se pudo extraer: {corto}")
        else:
            tests.append(test)

    progress.progress(0.92, text=etiqueta_progreso("Validando estructura…", 0.92, inicio))

    img_esperadas = sum(t.get("imagenes_esperadas", 0) for t in tests)
    img_ok = sum(t.get("imagenes_ok", 0) for t in tests)
    if img_esperadas and img_ok < img_esperadas:
        _log(f"⚠️ Reintentando imágenes ({img_ok}/{img_esperadas})…")

        def _cb_img(actual: int, total: int, msg: str) -> None:
            fraccion = 0.92 + (actual / max(total, 1)) * 0.06
            progress.progress(
                min(fraccion, 0.98),
                text=etiqueta_progreso(msg, fraccion, inicio),
            )

        img_ok, img_esperadas = completar_imagenes_tests(tests, progreso=_cb_img)
    if img_esperadas and img_ok < img_esperadas:
        _log(f"⚠️ Imágenes: {img_ok}/{img_esperadas} descargadas")
        st.session_state["daypo_aviso_imagenes"] = (
            f"Solo se pudieron descargar {img_ok} de {img_esperadas} imágenes. "
            "El test puede usar imágenes protegidas o enlaces de otro dominio Daypo."
        )
    elif img_esperadas:
        st.session_state.pop("daypo_aviso_imagenes", None)
    else:
        st.session_state.pop("daypo_aviso_imagenes", None)

    if not tests:
        st.session_state["error_inline"] = "No se pudo extraer ningún test de esos enlaces."
        return False

    st.session_state["daypo_tests"] = tests
    st.session_state["daypo_errores"] = errores
    st.session_state["ia_procesado_con"] = ""
    total_preg = sum(len(t.get("preguntas", [])) for t in tests)
    progress.progress(
        1.0,
        text=etiqueta_progreso(f"Listo — {total_preg} preguntas", 1.0, inicio),
    )
    if not log_incidencias:
        status.caption("Extracción completada sin incidencias.")
    return True


def _procesar_ia(texto: str, archivos, progress, status) -> bool:
    config = st.session_state["api_config"]

    def _log(msg: str):
        status.write(msg)

    def _progress(p: int):
        progress.progress(min(p, 99) / 100.0)

    status.markdown("**Iniciando…**")
    _progress(5)

    try:
        datos, etiqueta, _fb, pid, modelo = extraer_con_fallback(
            config,
            texto=texto,
            archivos=archivos,
            log=_log,
            progress=_progress,
        )
        st.session_state["ia_requests_sesion"] += 1
    except requests.HTTPError as e:
        if "429" in str(e):
            st.session_state["banner_429"] = True
        st.session_state["error_inline"] = str(e)[:300]
        return False
    except Exception as e:  # noqa: BLE001
        err = str(e)
        if "429" in err:
            st.session_state["banner_429"] = True
        st.session_state["error_inline"] = err[:300]
        return False

    if not datos.get("preguntas"):
        st.session_state["error_inline"] = "No se encontraron preguntas en el material."
        return False

    n = len(datos["preguntas"])
    status.write(f"✅ {n} preguntas encontradas")
    status.markdown("**Validando estructura…**")
    _progress(95)
    st.session_state["ia_datos"] = datos
    st.session_state["ia_procesado_con"] = etiqueta
    st.session_state["ia_pid_usado"] = pid
    st.session_state["ia_modelo_usado"] = modelo
    st.session_state["ia_chat"] = []
    _progress(100)
    return True


def _conteo_preview() -> int:
    if st.session_state.get("fuente") == "ia":
        return len((st.session_state.get("ia_datos") or {}).get("preguntas", []))
    total = 0
    for test in st.session_state.get("daypo_tests") or []:
        total += len(test.get("preguntas", []))
    return total


def _render_entrada() -> None:
    config = st.session_state["api_config"]
    listos_ia = proveedores_configurados(config)
    n_preview = _conteo_preview()

    if n_preview:
        c_prev, c_nuevo = st.columns([2, 1])
        with c_prev:
            if st.button(
                f"← Volver al preview ({n_preview} preguntas)",
                use_container_width=True,
                key="btn_volver_preview",
            ):
                ir_a_revision()
                st.rerun()
        with c_nuevo:
            if st.button("Empezar de cero", use_container_width=True, key="btn_empezar_cero"):
                ir_a_entrada()
                st.rerun()
        st.caption(
            "Puedes cambiar el material abajo y pulsar Convertir de nuevo, "
            "o volver al preview sin perder el resultado actual."
        )
        st.markdown('<div class="omni-separator omni-separator--light"></div>', unsafe_allow_html=True)

    if st.session_state.get("banner_429"):
        st.markdown(
            '<div class="banner-amber">Tus APIs han alcanzado el límite. '
            "Espera unos minutos o añade otra clave en ⚙.</div>",
            unsafe_allow_html=True,
        )
        if st.button("Entendido", key="dismiss_429"):
            st.session_state["banner_429"] = False
            st.rerun()

    st.markdown('<div class="omni-separator"></div>', unsafe_allow_html=True)
    st.markdown('<p class="source-label">Fuente</p>', unsafe_allow_html=True)

    opciones = {"Daypo": "daypo", "IA: PDF · foto · texto": "ia"}
    fuente = render_fuente_toggle(opciones)

    st.markdown('<div class="omni-separator omni-separator--light"></div>', unsafe_allow_html=True)

    texto_daypo = ""
    texto_ia = ""
    archivos = None
    hay_contenido = False
    puede = False

    if fuente == "daypo":
        with st.container(border=True):
            st.markdown('<p class="dropzone-label">Enlaces de Daypo</p>', unsafe_allow_html=True)
            st.caption("Pega uno o varios enlaces a tests de daypo.com — sin IA, extracción directa.")
            texto_daypo = st.text_area(
                "daypo",
                height=160,
                placeholder="https://www.daypo.com/…\nhttps://www.daypo.com/…",
                label_visibility="collapsed",
                key="input_daypo",
            )
            hay_contenido = bool(texto_daypo.strip())
            puede = hay_contenido
    else:
        with st.container(border=False):
            bloqueado = not listos_ia
            if bloqueado:
                st.markdown(
                    '<div class="dropzone-blocked">'
                    "<p><strong>Modo IA</strong></p>"
                    "<p>Configura al menos una API para limpiar preguntas con IA.</p>"
                    "</div>",
                    unsafe_allow_html=True,
                )
                if st.button("Configurar APIs", type="primary", key="blocked_api", use_container_width=True):
                    api_modal()
                return

            archivos = st.file_uploader(
                "Suelta tus archivos aquí o",
                type=["jpg", "jpeg", "png", "webp", "pdf", "docx"],
                accept_multiple_files=True,
                label_visibility="collapsed",
                key="input_ia_archivos",
            )
            st.markdown(or_divider_html(), unsafe_allow_html=True)
            st.markdown(
                '<p class="rn-paste-hint-only">Pega texto si no subes archivos</p>',
                unsafe_allow_html=True,
            )
            texto_ia = st.text_area(
                "ia",
                height=120,
                placeholder="Pega aquí preguntas mal formateadas, con OCR raro, sin marcar la correcta…",
                label_visibility="collapsed",
                key="input_ia_texto",
            )
            hay_contenido = bool(texto_ia.strip()) or bool(archivos)
            puede = hay_contenido and listos_ia

    if st.session_state.get("error_inline"):
        st.markdown(
            f'<p class="inline-error">{html_lib.escape(st.session_state["error_inline"])}</p>',
            unsafe_allow_html=True,
        )

    if st.button(
        "Convertir",
        type="primary",
        use_container_width=True,
        disabled=not puede,
        key="btn_convertir",
    ):
        st.session_state["error_inline"] = ""
        progress = st.progress(0, text="Procesando…")
        with work_log("Trabajando…") as status_box:
            ok = False
            if fuente == "daypo":
                ok = _procesar_daypo(texto_daypo, progress, status_box)
            else:
                ok = _procesar_ia(texto_ia, archivos, progress, status_box)

            if ok:
                status_box.update(label="Listo", state="complete")
            else:
                status_box.update(label="Error", state="error")

        if ok:
            ir_a_revision()
            st.rerun()


def _preguntas_preview_ia() -> list[dict]:
    return st.session_state["ia_datos"].get("preguntas", [])


def _preguntas_preview_daypo(
    on_progress: Callable[[int, int], None] | None = None,
) -> list[dict]:
    out = []
    tests = st.session_state.get("daypo_tests") or []
    total = sum(len(t.get("preguntas", [])) for t in tests)
    n = 0
    for test in tests:
        for p in test.get("preguntas", []):
            n += 1
            correcta = next((o[0] for o in p["opciones"] if o[1]), "")
            incorrectas = [o[0] for o in p["opciones"] if not o[1]]
            item = {
                "enunciado": p["enunciado"],
                "correcta": correcta,
                "incorrectas": incorrectas,
            }
            if p.get("img_bytes"):
                item["img_b64"] = base64.b64encode(p["img_bytes"]).decode("ascii")
            out.append(item)
            if on_progress and (n == total or n % 8 == 0):
                on_progress(n, total)
    return out


def _build_preview_html(
    preguntas: list[dict],
    on_chunk: Callable[[int, int], None] | None = None,
) -> str:
    html_parts = ['<div class="preview-scroll">']
    total = len(preguntas)
    for i, p in enumerate(preguntas, 1):
        if on_chunk:
            on_chunk(i, total)
        enc = html_lib.escape(p["enunciado"])
        html_parts.append(f'<div class="preview-q"><strong>{i}. {enc}</strong>')
        if p.get("img_b64"):
            html_parts.append(
                f'<br><img class="preview-img" '
                f'src="data:image/jpeg;base64,{p["img_b64"]}" alt="">'
            )
        for inc in p.get("incorrectas", []):
            html_parts.append(
                f'<br><span class="preview-wrong">× {html_lib.escape(str(inc))}</span>'
            )
        corr = p.get("correcta", "")
        if corr:
            html_parts.append(
                f'<br><span class="preview-ok">✓ {html_lib.escape(str(corr))}</span>'
            )
        html_parts.append("</div>")
    html_parts.append("</div>")
    return "".join(html_parts)


def _render_revision() -> None:
    fuente = st.session_state["fuente"]
    prep_bar = None
    total_prev = 0

    if fuente == "ia":
        preguntas = _preguntas_preview_ia()
        titulo = st.session_state["ia_datos"].get("titulo", "Test")
        total_prev = len(preguntas)
    else:
        tests = st.session_state.get("daypo_tests") or []
        titulo = tests[0]["titulo"] if len(tests) == 1 else f"{len(tests)} tests Daypo"
        total_prev = sum(len(t.get("preguntas", [])) for t in tests)
        if total_prev > 40:
            prep_bar = st.progress(0, text="Preparando preview…")
            inicio_prep = time.monotonic()

            def _prep_chunk(actual: int, total: int) -> None:
                fr = actual / total
                prep_bar.progress(
                    fr * 0.45,
                    text=etiqueta_progreso(
                        f"Preparando {actual}/{total}", fr * 0.45, inicio_prep,
                    ),
                )

            preguntas = _preguntas_preview_daypo(on_progress=_prep_chunk)
        else:
            preguntas = _preguntas_preview_daypo()

    n = len(preguntas)
    st.markdown(f'<p class="review-summary">{n} preguntas listas</p>', unsafe_allow_html=True)
    st.caption(titulo)
    if fuente == "daypo" and st.session_state.get("daypo_aviso_imagenes"):
        st.warning(st.session_state["daypo_aviso_imagenes"])
    if st.session_state.get("ia_procesado_con"):
        st.markdown(
            f'<span class="model-badge">Procesado con {html_lib.escape(st.session_state["ia_procesado_con"])}</span>',
            unsafe_allow_html=True,
        )

    if n > 40:
        base_fr = 0.45 if prep_bar is not None else 0.0
        preview_bar = st.progress(base_fr, text="Montando preview…")
        inicio_preview = time.monotonic()

        def _preview_chunk(actual: int, total: int) -> None:
            fr = base_fr + (actual / total) * (1.0 - base_fr)
            preview_bar.progress(
                fr,
                text=etiqueta_progreso(f"Pregunta {actual}/{total}", fr, inicio_preview),
            )

        preview_html = _build_preview_html(preguntas, on_chunk=_preview_chunk)
        preview_bar.empty()
        if prep_bar is not None:
            prep_bar.empty()
    else:
        preview_html = _build_preview_html(preguntas)

    st.markdown(preview_html, unsafe_allow_html=True)

    if fuente == "ia":
        with st.expander("Ajustar con IA (opcional)", expanded=False):
            for msg in st.session_state["ia_chat"]:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

            correccion = st.chat_input("Ej: «La correcta de la 3 es la B» · «Quita duplicados»")
            if correccion:
                st.session_state["ia_chat"].append({"role": "user", "content": correccion})
                config = st.session_state["api_config"]
                try:
                    nuevos, pid_corr, modelo_corr = aplicar_correccion_con_fallback(
                        config,
                        st.session_state["ia_datos"],
                        correccion,
                        pid=st.session_state.get("ia_pid_usado") or None,
                        modelo=st.session_state.get("ia_modelo_usado") or None,
                    )
                    st.session_state["ia_datos"] = nuevos
                    st.session_state["ia_pid_usado"] = pid_corr
                    st.session_state["ia_modelo_usado"] = modelo_corr
                    st.session_state["ia_requests_sesion"] += 1
                    st.session_state["ia_chat"].append({
                        "role": "assistant",
                        "content": f"Listo — {len(nuevos.get('preguntas', []))} preguntas.",
                    })
                    st.rerun()
                except Exception as e:  # noqa: BLE001
                    st.session_state["ia_chat"].append({
                        "role": "assistant",
                        "content": f"Error: {str(e)[:150]}",
                    })
                    st.rerun()

    c1, c2 = st.columns([2, 1])
    with c1:
        if st.button("Exportar →", type="primary", use_container_width=True):
            inicio_export = time.monotonic()
            export_bar = st.progress(0, text="Generando exportables…")

            def _export_progress(actual: int, total: int, msg: str) -> None:
                fr = actual / max(total, 1)
                export_bar.progress(
                    fr,
                    text=etiqueta_progreso(msg, fr, inicio_export),
                )

            if fuente == "ia":
                tests = ia_a_tests(st.session_state["ia_datos"])
                st.session_state["resultado"] = construir_resultado(
                    tests,
                    progreso=_export_progress,
                )
            else:
                st.session_state["resultado"] = construir_resultado(
                    st.session_state["daypo_tests"],
                    errores=st.session_state.get("daypo_errores") or [],
                    progreso=_export_progress,
                )
            export_bar.progress(1.0, text="Listo · 100%")
            ir_a_export()
            st.rerun()
    with c2:
        if st.button("← Cambiar material", use_container_width=True):
            ir_a_editar_entrada()
            st.rerun()


def render_app() -> None:
    inject_styles()
    inject_button_fixes()
    _render_header()
    if st.session_state.pop("api_modal_reopen", False):
        api_modal()
    _render_hero()

    flujo = st.session_state["flujo"]
    if flujo == "entrada":
        _render_entrada()
        if not (st.session_state.get("ia_datos") or st.session_state.get("daypo_tests")):
            render_faq()
    elif flujo == "revision":
        _render_revision()
    elif flujo == "export":
        render_export()
