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
    candidatos = [re.sub(r'[.,;:!?]+$', '', e) for e in candidatos]
    vistos: set[str] = set()
    resultado = []
    for e in candidatos:
        if e not in vistos:
            vistos.add(e)
            resultado.append(e)
    return resultado


def generar_zip_remnote(tests_datos: list[dict]) -> bytes:
    """
    Genera un ZIP con un .md en sintaxis RemNote MCQ y una carpeta images/.

    Formato identico al que RemNote exporta internamente:
      - Pregunta >>A)        <- item de lista con el marcador MCQ
          - Opcion correcta  <- subitems con 4 espacios + guion
          - Opcion incorrecta
    Las imagenes se referencian por ruta relativa dentro del ZIP.
    Importar en RemNote: ajustes -> Importar -> Markdown -> subir el ZIP.
    """
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        lineas: list[str] = []

        for test in tests_datos:
            lineas.append(test["titulo"])
            lineas.append("")

            for pregunta in test["preguntas"]:
                correcta = None
                incorrectas: list[str] = []
                for texto, es_correcta in pregunta["opciones"]:
                    if not texto:
                        continue
                    if es_correcta:
                        correcta = texto
                    else:
                        incorrectas.append(texto)

                if correcta is None:
                    continue

                img_ref = ""
                if pregunta.get("img_bytes") and pregunta.get("img_nombre"):
                    nombre = pregunta["img_nombre"]
                    zf.writestr(f"images/{nombre}", pregunta["img_bytes"])
                    img_ref = f" ![](images/{nombre})"

                # Mismo formato que usa RemNote al exportar sus propias MCQ
                lineas.append(f"- {pregunta['enunciado']}{img_ref} >>A)")
                lineas.append(f"    - {correcta}")
                for inc in incorrectas:
                    lineas.append(f"    - {inc}")
                lineas.append("")

            lineas.append("")

        zf.writestr("Banco_de_Preguntas_MCQ.md", "\n".join(lineas).encode("utf-8"))

    buf.seek(0)
    return buf.getvalue()


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

# Resultados persistentes: sobreviven a la re-ejecucion que disparan los botones de descarga
if "resultado" not in st.session_state:
    st.session_state["resultado"] = None

# Pantalla de resultados: se muestra mientras haya datos en session_state
if st.session_state["resultado"] is not None:
    res = st.session_state["resultado"]

    if res["errores"]:
        st.warning(
            f"No se pudieron procesar {len(res['errores'])} enlace(s). "
            "Revisa tu conexion o que la URL sea correcta."
        )

    st.success(f"Procesados {res['tests_ok']} test(s) correctamente. Archivos listos para descargar.")

    col_word, col_remnote = st.columns(2)

    with col_word:
        st.download_button(
            label="⬇️ Descargar ZIP (Word)",
            data=res["zip_word"],
            file_name="Banco_de_Preguntas_Daypo.zip",
            mime="application/zip",
            use_container_width=True,
        )

    with col_remnote:
        st.download_button(
            label="🧠 Descargar ZIP RemNote MCQ",
            data=res["zip_remnote"],
            file_name="Daypo_RemNote_MCQ.zip",
            mime="application/zip",
            use_container_width=True,
            help="Importa este ZIP en RemNote: ajustes → Importar → Markdown.",
        )

    with st.expander("ℹ️ Como importar en RemNote"):
        st.markdown(
            """
1. Descarga el archivo **Daypo_RemNote_MCQ.zip**.
2. Abre RemNote → icono de ajustes → **Importar** → **Markdown**.
3. Sube el ZIP directamente (no hace falta descomprimirlo).
4. Los tests apareceran como documentos con tarjetas MCQ con sus imagenes.
5. RemNote baraja el orden de las opciones al practicar.
            """
        )

    st.divider()
    if st.button("🔄 Nueva extraccion", use_container_width=True):
        st.session_state["resultado"] = None
        st.rerun()

    st.stop()

# Pantalla de entrada: solo visible cuando no hay resultado activo
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

            doc_indiv = Document()
            doc_indiv.add_heading(titulo, 1)

            if es_multiple:
                doc_unificado.add_heading(titulo, 1)

            preguntas_con_img: list[dict] = []

            for i, pregunta in enumerate(preguntas, start=1):
                img_bytes = None
                img_nombre = None

                if pregunta["num_imagen"] is not None:
                    img_nombre = f"img_{id_test}_{pregunta['num_imagen']}.jpg"
                    img_bytes = obtener_imagen(id_test, pregunta["num_imagen"], url)
                    if img_bytes:
                        zip_file.writestr(
                            f"{titulo_carpeta}/{img_nombre}",
                            img_bytes,
                        )

                procesar_pregunta(doc_indiv, i, pregunta["enunciado"], img_bytes, pregunta["opciones"])

                if es_multiple:
                    procesar_pregunta(doc_unificado, i, pregunta["enunciado"], img_bytes, pregunta["opciones"])

                preguntas_con_img.append({
                    "enunciado": pregunta["enunciado"],
                    "opciones": pregunta["opciones"],
                    "img_bytes": img_bytes,
                    "img_nombre": img_nombre,
                })

            todos_los_tests.append({"titulo": titulo, "preguntas": preguntas_con_img})

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

    memoria_zip.seek(0)

    st.session_state["resultado"] = {
        "zip_word": memoria_zip.getvalue(),
        "zip_remnote": generar_zip_remnote(todos_los_tests),
        "tests_ok": len(enlaces) - len(errores),
        "errores": errores,
    }
    st.rerun()
