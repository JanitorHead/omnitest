import streamlit as st
import requests
import re
import xml.etree.ElementTree as ET
import zipfile
from io import BytesIO
from docx import Document
from docx.shared import Inches, Pt, RGBColor

st.set_page_config(
    page_title="Daypo Extractor",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------

def limpiar_nombre_carpeta(texto: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", texto).strip()


def obtener_imagen(id_test: str, num_imagen: str, url_origen: str) -> bytes | None:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": url_origen,
        "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    }
    prefijo = id_test[:3]
    url_imagen = f"https://www.daypo.com/testimages/{prefijo}/{id_test}_{num_imagen}.jpg"
    try:
        respuesta = requests.get(url_imagen, headers=headers, timeout=8)
        if respuesta.status_code == 200:
            return respuesta.content
    except requests.RequestException:
        pass
    return None


def procesar_pregunta(doc: Document, num: int, enunciado: str,
                      img_bytes: bytes | None, opciones: list[tuple[str, bool]]) -> None:
    parrafo = doc.add_paragraph()
    run = parrafo.add_run(f"{num}. {enunciado}")
    run.bold = True
    run.font.size = Pt(11)

    if img_bytes:
        doc.add_picture(BytesIO(img_bytes), width=Inches(3.5))

    for texto_opcion, es_correcta in opciones:
        parrafo_op = doc.add_paragraph()
        if es_correcta:
            run_op = parrafo_op.add_run(f"   - {texto_opcion}  (correcta)")
            run_op.bold = True
            run_op.font.color.rgb = RGBColor(0x1A, 0x73, 0x28)
        else:
            parrafo_op.add_run(f"   - {texto_opcion}")

    doc.add_paragraph()


def extraer_datos_test(url: str, headers_web: dict) -> tuple[str, str, list] | None:
    try:
        res_html = requests.get(url, headers=headers_web, timeout=10)
        res_html.raise_for_status()
        match = re.search(r"ntest\s*=\s*(\d+)", res_html.text)
        if not match:
            return None
        id_test = match.group(1)
    except requests.RequestException:
        return None

    try:
        res_xml = requests.post(
            "https://www.daypo.com/asps/load.php",
            data={"tes": id_test},
            headers=headers_web,
            timeout=10,
        )
        res_xml.raise_for_status()
        raiz = ET.fromstring(res_xml.text)
    except (requests.RequestException, ET.ParseError):
        return None

    nodo_titulo = raiz.find(".//t")
    titulo = nodo_titulo.text.strip() if (nodo_titulo is not None and nodo_titulo.text) else f"Test {id_test}"

    contenedor = raiz.find("c")
    if contenedor is None:
        return None

    preguntas_raw = contenedor.findall("c")
    preguntas = []

    for q in preguntas_raw:
        nodo_p = q.find("p")
        enunciado = nodo_p.text.strip() if nodo_p is not None and nodo_p.text else "Sin enunciado"

        nodo_b = q.find("b")
        num_imagen = nodo_b.text.strip() if nodo_b is not None and nodo_b.text else None

        nodo_c = q.find("c")
        mascara = nodo_c.text if nodo_c is not None and nodo_c.text else ""
        indice_correcta = mascara.find("2")

        nodo_r = q.find("r")
        opciones = []
        if nodo_r is not None:
            for idx, nodo_o in enumerate(nodo_r.findall("o")):
                texto = nodo_o.text.strip() if nodo_o.text else ""
                opciones.append((texto, idx == indice_correcta))

        preguntas.append({
            "enunciado": enunciado,
            "num_imagen": num_imagen,
            "opciones": opciones,
        })

    return id_test, titulo, preguntas


def extraer_enlaces_daypo(texto: str) -> list[str]:
    """Extrae todos los enlaces de Daypo de cualquier bloque de texto."""
    patron = r'https?://(?:www\.)?daypo\.com/[^\s\n\r"\'<>()\[\]{}]+'
    candidatos = re.findall(patron, texto)
    # Eliminar puntuacion de cierre que no pertenece a la URL
    candidatos = [re.sub(r'[.,;:!?]+$', '', e) for e in candidatos]
    # Deduplicar manteniendo orden
    vistos: set[str] = set()
    resultado = []
    for e in candidatos:
        if e not in vistos:
            vistos.add(e)
            resultado.append(e)
    return resultado


def generar_texto_remnote(tests_datos: list[dict]) -> str:
    """
    Genera texto en formato RemNote MCQ listo para pegar en la app.

    Sintaxis: 'Pregunta>>A)' con las opciones indentadas con tabs.
    La opcion correcta va primera; RemNote baraja el orden al practicar.
    """
    lineas = []
    for test in tests_datos:
        lineas.append(test["titulo"])
        for pregunta in test["preguntas"]:
            correcta = None
            incorrectas = []
            for texto, es_correcta in pregunta["opciones"]:
                if not texto:
                    continue
                if es_correcta:
                    correcta = texto
                else:
                    incorrectas.append(texto)

            if correcta is None:
                continue

            lineas.append(f"\t{pregunta['enunciado']}>>A)")
            lineas.append(f"\t\t{correcta}")
            for inc in incorrectas:
                lineas.append(f"\t\t{inc}")
        lineas.append("")
    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# Interfaz de usuario (Streamlit)
# ---------------------------------------------------------------------------

st.title("📝 Daypo Extractor")
st.markdown(
    "Extrae preguntas, imagenes y respuestas correctas de cualquier test de "
    "[Daypo](https://www.daypo.com) y exportalos a documentos Word o en "
    "formato [RemNote](https://www.remnote.com) MCQ."
)

st.divider()

enlaces_texto = st.text_area(
    "Pega aqui tus enlaces de Daypo (o cualquier texto que los contenga):",
    height=220,
    placeholder=(
        "Puedes pegar los enlaces directamente, uno por linea, o cualquier texto "
        "que los contenga (correos, documentos, listas con texto extra...):\n\n"
        "https://www.daypo.com/tema-1-trauma.html\n"
        "https://www.daypo.com/tema-2-trauma.html"
    ),
)

# Previsualizar en tiempo real los enlaces detectados
if enlaces_texto.strip():
    enlaces_detectados = extraer_enlaces_daypo(enlaces_texto)
    if enlaces_detectados:
        with st.expander(f"🔍 {len(enlaces_detectados)} enlace(s) detectado(s) — haz clic para ver"):
            for e in enlaces_detectados:
                st.code(e)
    else:
        st.info("No se han detectado enlaces de Daypo en el texto introducido todavia.")

col1, col2 = st.columns([3, 1])
with col1:
    iniciar = st.button("Iniciar Extraccion", type="primary", use_container_width=True)
with col2:
    st.caption("Requiere conexion a internet")

if iniciar:
    enlaces = extraer_enlaces_daypo(enlaces_texto)

    if not enlaces:
        st.error("No se han detectado enlaces validos de Daypo en el texto introducido.")
        st.stop()

    es_multiple = len(enlaces) > 1
    headers_web = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    memoria_zip = BytesIO()
    todos_los_tests: list[dict] = []

    if es_multiple:
        doc_unificado = Document()
        doc_unificado.add_heading("Recopilacion completa de tests de Daypo", 0)

    barra = st.progress(0, text="Iniciando...")
    log = st.empty()
    errores = []

    with zipfile.ZipFile(memoria_zip, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for indice, url in enumerate(enlaces):
            nombre_corto = url.rstrip("/").split("/")[-1].replace(".html", "")
            barra.progress(
                int((indice / len(enlaces)) * 100),
                text=f"Procesando {indice + 1}/{len(enlaces)}: {nombre_corto}",
            )
            log.info(f"Procesando: {url}")

            resultado = extraer_datos_test(url, headers_web)
            if resultado is None:
                errores.append(url)
                st.warning(f"No se pudo procesar: {url}")
                continue

            id_test, titulo, preguntas = resultado
            titulo_carpeta = limpiar_nombre_carpeta(titulo)

            todos_los_tests.append({"titulo": titulo, "preguntas": preguntas})

            doc_indiv = Document()
            doc_indiv.add_heading(titulo, 1)

            if es_multiple:
                doc_unificado.add_heading(titulo, 1)

            for i, pregunta in enumerate(preguntas, start=1):
                img_bytes = None
                if pregunta["num_imagen"] is not None:
                    img_bytes = obtener_imagen(id_test, pregunta["num_imagen"], url)
                    if img_bytes:
                        zip_file.writestr(
                            f"{titulo_carpeta}/img_{id_test}_{pregunta['num_imagen']}.jpg",
                            img_bytes,
                        )

                procesar_pregunta(doc_indiv, i, pregunta["enunciado"], img_bytes, pregunta["opciones"])

                if es_multiple:
                    procesar_pregunta(doc_unificado, i, pregunta["enunciado"], img_bytes, pregunta["opciones"])

            buf_indiv = BytesIO()
            doc_indiv.save(buf_indiv)
            zip_file.writestr(f"{titulo_carpeta}/{titulo_carpeta}.docx", buf_indiv.getvalue())

            if es_multiple:
                doc_unificado.add_page_break()

        if es_multiple:
            buf_unif = BytesIO()
            doc_unificado.save(buf_unif)
            zip_file.writestr("TODOS_LOS_TESTS_UNIDOS.docx", buf_unif.getvalue())

    barra.progress(100, text="Extraccion completada.")
    log.empty()

    if errores:
        st.warning(f"No se pudieron procesar {len(errores)} enlace(s). Revisa tu conexion o que la URL sea correcta.")

    tests_ok = len(enlaces) - len(errores)
    memoria_zip.seek(0)
    st.success(f"Procesados {tests_ok} test(s) correctamente. Archivos listos para descargar.")

    col_word, col_remnote = st.columns(2)

    with col_word:
        st.download_button(
            label="⬇️ Descargar ZIP (Word)",
            data=memoria_zip.getvalue(),
            file_name="Banco_de_Preguntas_Daypo.zip",
            mime="application/zip",
            use_container_width=True,
        )

    with col_remnote:
        if todos_los_tests:
            texto_remnote = generar_texto_remnote(todos_los_tests)
            st.download_button(
                label="🧠 Descargar formato RemNote MCQ",
                data=texto_remnote.encode("utf-8"),
                file_name="Daypo_RemNote_MCQ.txt",
                mime="text/plain",
                use_container_width=True,
                help=(
                    "Abre RemNote, crea un documento nuevo y pega el contenido "
                    "del archivo. Las preguntas apareceran automaticamente como "
                    "tarjetas MCQ."
                ),
            )

    if todos_los_tests:
        with st.expander("ℹ️ Como usar el archivo RemNote MCQ"):
            st.markdown(
                """
1. Descarga el archivo **Daypo_RemNote_MCQ.txt**.
2. Abre RemNote y crea un documento nuevo (o abre uno existente).
3. Abre el archivo de texto, selecciona todo (`Ctrl+A`) y copialo.
4. Pega directamente en RemNote.
5. Las preguntas apareceran como tarjetas de opcion multiple (MCQ).
   RemNote baraja el orden de las opciones al practicar.
                """
            )
