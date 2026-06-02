"""Componentes de interfaz (Streamlit): pantalla de resultados y pestañas."""
import json

import requests
import streamlit as st

from . import APP_ICONO, APP_NOMBRE
from .ai_import import (
    MODELO_POR_DEFECTO,
    MODELOS_GEMINI,
    aplicar_correccion_gemini,
    diagnosticar_modelo,
    es_preview,
    extraer_con_gemini_multi,
    listar_modelos_gemini,
)
from .daypo import extraer_enlaces_daypo, extraer_test
from .exporters import construir_resultado


# ---------------------------------------------------------------------------
# Estado de sesión
# ---------------------------------------------------------------------------

def init_estado() -> None:
    defaults = [
        ("resultado", None), ("ia_estado", None),
        ("ia_datos", None), ("ia_chat", []),
        ("ia_api_key", ""), ("ia_modelo", MODELO_POR_DEFECTO),
        ("ia_modelos_disponibles", None),
        ("ia_requests_sesion", 0), ("ia_diagnostico", None),
    ]
    for k, v in defaults:
        if k not in st.session_state:
            st.session_state[k] = v


# ---------------------------------------------------------------------------
# Pantalla de resultados (compartida)
# ---------------------------------------------------------------------------

def render_resultados() -> None:
    res = st.session_state["resultado"]

    if res["errores"]:
        st.warning(f"No se pudieron procesar {len(res['errores'])} fuente(s).")

    st.success(f"✅ {res['tests_ok']} test(s) listos. Elige tus formatos:")

    nb = res["nombre_base"]
    es_multi = res["es_multi"]

    version = st.radio("Versión de Word/PDF:", ["Con respuestas", "Sin respuestas"],
                       horizontal=True,
                       help="'Sin respuestas' es ideal para imprimir y responder a mano.")
    suf = "con" if version == "Con respuestas" else "sin"

    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button(
            "📄 Word" + (" (todos)" if es_multi else ""),
            data=res[f"word_combinado_{suf}"],
            file_name=f"{nb}_Word_{suf}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )
    with c2:
        st.download_button(
            "🧠 RemNote MCQ", data=res["zip_remnote"],
            file_name=f"{nb}_RemNote.zip", mime="application/zip",
            use_container_width=True,
            help="Importa el ZIP en RemNote: ajustes → Importar → Markdown.",
        )
    with c3:
        st.download_button(
            "🃏 Anki (.apkg)", data=res["apkg_anki"],
            file_name=f"{nb}_Anki.apkg", mime="application/octet-stream",
            use_container_width=True, help="Doble clic en el .apkg para importar.",
        )

    c4, c5, c6 = st.columns(3)
    with c4:
        st.download_button(
            "🖨️ PDF" + (" (todos)" if es_multi else ""),
            data=res[f"pdf_combinado_{suf}"],
            file_name=f"{nb}_{suf}.pdf", mime="application/pdf",
            use_container_width=True,
        )
    with c5:
        st.download_button(
            "🎯 Quiz interactivo", data=res["html_quiz"],
            file_name=f"{nb}_Quiz.html", mime="text/html",
            use_container_width=True,
            help="Abre en cualquier navegador. Funciona offline.",
        )
    with c6:
        st.download_button(
            "🖼️ Imágenes sueltas", data=res["zip_imagenes"],
            file_name=f"{nb}_Imagenes.zip", mime="application/zip",
            use_container_width=True,
        )

    if es_multi:
        st.markdown("---")
        ca, cb = st.columns(2)
        with ca:
            st.download_button(
                "📄 Word por separado (ZIP)", data=res["zip_word_individuales"],
                file_name=f"{nb}_Word_individual.zip", mime="application/zip",
                use_container_width=True,
                help="ZIP con Con_Respuesta/ y Sin_Respuesta/ — un .docx por test.",
            )
        with cb:
            st.download_button(
                "🖨️ PDF por separado (ZIP)", data=res["zip_pdf_individuales"],
                file_name=f"{nb}_PDF_individual.zip", mime="application/zip",
                use_container_width=True,
                help="ZIP con Con_Respuesta/ y Sin_Respuesta/ — un .pdf por test.",
            )

    with st.expander("ℹ️ Cómo importar en RemNote y Anki"):
        st.markdown("""
**RemNote:** descarga el ZIP → RemNote → ajustes → Importar → Markdown → sube el ZIP.

**Anki:** doble clic en el .apkg (o Archivo → Importar). Las opciones salen en orden
aleatorio en cada repaso; clic para seleccionar, Espacio para revelar, el orden no
cambia al girar la carta.
""")

    st.divider()
    if st.button("🔄 Empezar de nuevo", use_container_width=True):
        st.session_state["resultado"] = None
        st.rerun()


# ---------------------------------------------------------------------------
# Pestaña Daypo
# ---------------------------------------------------------------------------

def render_tab_daypo() -> None:
    st.markdown("Pega **enlaces de Daypo** (o cualquier texto que los contenga) y "
                "Omnitest extrae preguntas, opciones, respuestas correctas e imágenes.")

    enlaces_texto = st.text_area(
        "Enlaces de Daypo:", height=180,
        placeholder="Pega aquí tus enlaces de Daypo...",
    )

    if enlaces_texto.strip():
        detectados = extraer_enlaces_daypo(enlaces_texto)
        if detectados:
            st.success(f"🔍 {len(detectados)} enlace(s) detectado(s)")
            for e in detectados:
                st.caption(e)
        else:
            st.warning("No se han detectado enlaces de Daypo en el texto.")

    col1, col2 = st.columns([3, 1])
    with col1:
        iniciar = st.button("Extraer de Daypo", type="primary", use_container_width=True)
    with col2:
        st.caption("Requiere internet")

    if iniciar:
        enlaces = extraer_enlaces_daypo(enlaces_texto)
        if not enlaces:
            st.error("No se han detectado enlaces válidos de Daypo.")
            return

        tests: list[dict] = []
        errores: list[str] = []
        barra = st.progress(0, text="Iniciando...")
        log = st.empty()

        for indice, url in enumerate(enlaces):
            corto = url.rstrip("/").split("/")[-1].replace(".html", "")
            barra.progress(int((indice / len(enlaces)) * 100),
                           text=f"Procesando {indice + 1}/{len(enlaces)}: {corto}")
            log.info(f"Procesando: {url}")
            test = extraer_test(url)
            if test is None:
                errores.append(url)
                st.warning(f"No se pudo procesar: {url}")
                continue
            tests.append(test)

        barra.progress(100, text="Extracción completada.")
        log.empty()

        if not tests:
            st.error("No se pudo extraer ningún test.")
            return

        st.session_state["resultado"] = construir_resultado(tests, errores=errores)
        st.rerun()


# ---------------------------------------------------------------------------
# Pestaña IA
# ---------------------------------------------------------------------------

def _render_ia_preview() -> None:
    datos = st.session_state["ia_datos"]
    api_key = st.session_state["ia_api_key"]
    modelo = st.session_state["ia_modelo"]
    n_q = len(datos.get("preguntas", []))

    st.success(f"**{n_q} preguntas extraídas** — *{datos.get('titulo', '')}*")

    with st.expander("Ver preguntas extraídas", expanded=False):
        for i, p in enumerate(datos.get("preguntas", []), 1):
            st.markdown(f"**{i}. {p['enunciado']}**")
            for inc in p.get("incorrectas", []):
                st.caption(f"  × {inc}")
            st.caption(f"  ✓ **{p.get('correcta', '')}**")
            if i < n_q:
                st.divider()

    st.markdown("---")
    st.markdown("**Correcciones con IA** — describe cualquier ajuste y la IA actualiza las preguntas:")

    for msg in st.session_state["ia_chat"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    correccion = st.chat_input(
        "Ej: 'La correcta de la 3 es la B' · 'Elimina la 7' · 'Cambia el título a...'"
    )
    if correccion:
        st.session_state["ia_chat"].append({"role": "user", "content": correccion})
        respuesta = None
        with st.status("Aplicando corrección...", expanded=True) as estado:
            def _log_chat(msg: str):
                estado.write(msg)
            try:
                nuevos = aplicar_correccion_gemini(api_key, modelo, datos, correccion, log=_log_chat)
                st.session_state["ia_requests_sesion"] += 1
                st.session_state["ia_datos"] = nuevos
                n_nuevo = len(nuevos.get("preguntas", []))
                respuesta = f"Listo. Ahora hay **{n_nuevo} preguntas** en *{nuevos.get('titulo', '')}*."
                estado.update(label="Corrección aplicada", state="complete")
            except json.JSONDecodeError:
                respuesta = "No pude aplicar la corrección (JSON inválido). Inténtalo de otra forma."
                estado.update(label="JSON inválido", state="error")
            except requests.HTTPError as e:
                estado.update(label="Error de Gemini", state="error")
                respuesta = ("⏳ **Rate limit** — espera 1-2 minutos y reintenta."
                             if "429" in str(e) else f"Error de Gemini: {str(e)[:100]}")
            except Exception as e:  # noqa: BLE001
                respuesta = f"Error: {str(e)[:200]}"
                estado.update(label="Error", state="error")
        if respuesta:
            st.session_state["ia_chat"].append({"role": "assistant", "content": respuesta})
            st.rerun()

    st.markdown("---")
    col_gen, col_volver = st.columns(2)
    with col_gen:
        if st.button("✅ Generar todos los archivos", type="primary", use_container_width=True):
            from .ai_import import gemini_a_tests
            tests = gemini_a_tests(st.session_state["ia_datos"])
            st.session_state["resultado"] = construir_resultado(tests)
            st.session_state["ia_estado"] = None
            st.session_state["ia_chat"] = []
            st.rerun()
    with col_volver:
        if st.button("↩️ Empezar de nuevo", use_container_width=True):
            st.session_state["ia_estado"] = None
            st.session_state["ia_datos"] = None
            st.session_state["ia_chat"] = []
            st.rerun()


def _render_ia_formulario() -> None:
    st.markdown("Combina **texto pegado, fotos de exámenes, PDFs y Word** en una sola "
                "operación — la IA extrae y unifica todas las preguntas. Si no marcas la "
                "correcta, **la deduce** con su conocimiento.")

    api_key = st.text_input(
        "Clave API de Gemini:", type="password",
        value=st.session_state["ia_api_key"],
        help="Clave gratuita en [aistudio.google.com](https://aistudio.google.com)",
    )

    col_verif, col_diag = st.columns(2)
    with col_verif:
        verificar = st.button("🔍 Verificar key", use_container_width=True, disabled=not bool(api_key))
    with col_diag:
        diagnostico = st.button("🩺 Diagnóstico de modelos", use_container_width=True, disabled=not bool(api_key))

    if verificar:
        with st.spinner("Consultando modelos disponibles para tu API key..."):
            try:
                modelos = listar_modelos_gemini(api_key)
                if modelos:
                    st.session_state["ia_modelos_disponibles"] = modelos
                    st.session_state["ia_api_key"] = api_key
                    st.success(f"✅ API key válida. {len(modelos)} modelos disponibles.")
                else:
                    st.warning("La key es válida pero no devolvió modelos con generateContent.")
            except requests.HTTPError as e:
                code = getattr(e.response, "status_code", "?")
                st.error(f"❌ API key rechazada (HTTP {code}). Revisa que la copiaste completa.")
            except Exception as e:  # noqa: BLE001
                st.error(f"❌ No se pudo verificar la key: {str(e)[:200]}")

    if diagnostico:
        st.session_state["ia_api_key"] = api_key
        modelos_probar = st.session_state["ia_modelos_disponibles"] or MODELOS_GEMINI
        modelos_probar = sorted(modelos_probar, key=lambda m: (es_preview(m), m))
        resultados = []
        with st.status("Probando cada modelo con un ping mínimo...", expanded=True) as est:
            for m in modelos_probar:
                etq = f"`{m}`" + (" _(preview)_" if es_preview(m) else "")
                est.write(f"⏳ Probando {etq}...")
                estado_m, detalle_m = diagnosticar_modelo(api_key, m)
                if estado_m == "ok":
                    st.session_state["ia_requests_sesion"] += 1
                icono = {"ok": "✅", "cuota": "🚫", "no_existe": "❔", "error": "⚠️"}.get(estado_m, "•")
                est.write(f"{icono} {etq} — {detalle_m}")
                resultados.append((m, estado_m, detalle_m))
            est.update(label="Diagnóstico completado", state="complete")
        st.session_state["ia_diagnostico"] = resultados

    if st.session_state["ia_diagnostico"]:
        ok_models = [m for m, e, _ in st.session_state["ia_diagnostico"] if e == "ok"]
        if ok_models:
            st.success(f"✅ Modelos que funcionan AHORA: {', '.join(f'`{m}`' for m in ok_models)}")
            estables_ok = [m for m in ok_models if not es_preview(m)]
            if estables_ok and st.session_state["ia_modelo"] not in ok_models:
                st.session_state["ia_modelo"] = estables_ok[0]
        else:
            st.error(
                "🚫 **Ningún modelo respondió OK.** Casi siempre significa que tu cuenta está en "
                "**tier de créditos/gratuito**, que comparte cuota y a menudo da `quota 0`.\n\n"
                "**Solución real:** añade un **método de pago real** en tu proyecto de Google Cloud "
                "(céntimos por examen; tener créditos NO equivale a pago activo).\n\n"
                "- Activar pago: [aistudio.google.com](https://aistudio.google.com) → Get API key → Billing\n"
                "- Ver cuotas: "
                "[consola de cuotas](https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas) "
                "(filtra por *has limit*)"
            )

    opciones = st.session_state["ia_modelos_disponibles"] or MODELOS_GEMINI
    modelo_sel = st.selectbox(
        "Modelo:", options=opciones,
        index=(opciones.index(st.session_state["ia_modelo"])
               if st.session_state["ia_modelo"] in opciones else 0),
    )

    if st.session_state["ia_modelos_disponibles"] is None:
        st.caption("💡 Pulsa **Verificar key** para cargar tus modelos, o **Diagnóstico** "
                   "para ver cuáles funcionan ahora mismo.")
    else:
        st.caption(f"🔢 Peticiones de generación en esta sesión: "
                   f"**{st.session_state['ia_requests_sesion']}** · cuota en "
                   f"[ai.dev/rate-limit](https://ai.dev/rate-limit)")

    texto_input = st.text_area(
        "Texto (opcional) — pega preguntas (con o sin la respuesta marcada):",
        height=160,
        placeholder=("Pega preguntas tipo test. Si no marcas la correcta, la IA la deduce.\n\n"
                     "1. ¿Cuál es el tratamiento?\na) Opción A\nb) Opción B\nc) Opción C"),
    )

    archivos = st.file_uploader(
        "Archivos (opcional) — imágenes, PDFs o Word (varios a la vez):",
        type=["jpg", "jpeg", "png", "webp", "pdf", "docx"],
        accept_multiple_files=True,
    )

    hay_contenido = bool(texto_input.strip()) or bool(archivos)
    if hay_contenido:
        info = []
        if texto_input.strip():
            info.append(f"📝 Texto ({len(texto_input.strip())} caracteres)")
        for f in (archivos or []):
            ext = f.name.rsplit(".", 1)[-1].upper()
            icono = "🖼️" if ext in ("JPG", "JPEG", "PNG", "WEBP") else "📄"
            info.append(f"{icono} {f.name}")
        st.info("**Contenido a procesar:**\n" + "\n".join(f"- {p}" for p in info))

    procesar = st.button("Procesar con IA", type="primary", use_container_width=True,
                         disabled=not (bool(api_key) and hay_contenido))

    if procesar:
        with st.status("Procesando con Gemini...", expanded=True) as estado:
            def _log_ui(msg: str):
                estado.write(msg)
            try:
                datos = extraer_con_gemini_multi(api_key, modelo=modelo_sel,
                                                 texto=texto_input, archivos=archivos, log=_log_ui)
                st.session_state["ia_requests_sesion"] += 1
                if not datos.get("preguntas"):
                    estado.update(label="Sin preguntas encontradas", state="error")
                    st.error("La IA no encontró preguntas. Prueba con contenido más estructurado.")
                else:
                    n = len(datos["preguntas"])
                    _log_ui(f"✅ {n} preguntas extraídas.")
                    estado.update(label=f"{n} preguntas extraídas", state="complete")
                    st.session_state["ia_estado"] = "preview"
                    st.session_state["ia_datos"] = datos
                    st.session_state["ia_api_key"] = api_key
                    st.session_state["ia_modelo"] = modelo_sel
                    st.session_state["ia_chat"] = []
                    st.rerun()
            except json.JSONDecodeError:
                estado.update(label="JSON inválido", state="error")
                st.error("La IA no devolvió JSON válido. Prueba dividiendo el contenido.")
            except requests.HTTPError as e:
                estado.update(label="Error de Gemini", state="error")
                err = str(e)
                if "429-CERO" in err:
                    st.error("🚫 **Modelo con cuota CERO** en tu cuenta. Usa **🩺 Diagnóstico** "
                             "para ver cuáles funcionan, o activa facturación.\n\n" f"_{err[:250]}_")
                elif "429-DIARIO" in err:
                    st.error("🚫 **Cuota DIARIA agotada.** Cambia de modelo (usa Diagnóstico), "
                             "espera 24h, o activa facturación.\n\n" f"_{err.split('429-DIARIO — ')[-1][:300]}_")
                elif "429" in err:
                    st.warning(f"⏳ **Rate limit por minuto** — espera 1-2 min.\n\n_{err[:300]}_")
                elif "404" in err:
                    st.error("❌ El modelo no existe. Prueba con `gemini-2.5-flash`.")
                else:
                    st.error(f"Error en Gemini: {err[:400]}")
            except Exception as e:  # noqa: BLE001
                estado.update(label="Error", state="error")
                st.error(f"Error: {str(e)[:300]}")

    with st.expander("💡 Consejos y solución de problemas"):
        st.markdown("""
**Uso normal:**
- **Todo a la vez:** combina texto + fotos + PDF + Word en una sola operación.
- **PDFs escaneados:** se envían directamente a la IA para OCR.
- **Respuesta correcta:** si viene marcada la usa; **si no, la deduce** con su conocimiento.
- **Para casos clínicos o preguntas difíciles** usa un modelo potente (`gemini-2.5-flash`/`pro`).
  El `flash-lite` es más rápido pero acierta menos razonando.
- **Revisa siempre** las respuestas deducidas en el **chat de correcciones** antes de generar.

**Si recibes error de cuota (429):**
- Usa **🩺 Diagnóstico de modelos** para ver al instante cuáles funcionan.
- **Evita modelos `preview`**: suelen tener **cuota 0** en tier gratuito.
- Cada modelo tiene su propia cuota: cambia de modelo si uno se agota.
- El tier **gratuito/de créditos** tiene límites muy bajos (a veces 0) y da 429 al primer
  intento — **no es un fallo de la app**. Añadir un **método de pago real** sube la cuota
  enormemente (céntimos por examen).
""")


def render_tab_ia() -> None:
    if st.session_state["ia_estado"] == "preview":
        _render_ia_preview()
    else:
        _render_ia_formulario()
