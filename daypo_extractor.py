import streamlit as st
import requests
import re
import xml.etree.ElementTree as ET
import zipfile
from io import BytesIO
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# ---------------------------------------------------------------------------
# Configuracion de la pagina
# ---------------------------------------------------------------------------
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
    """Elimina caracteres no permitidos en nombres de archivos/carpetas."""
    return re.sub(r'[\\/*?:"<>|]', "", texto).strip()


def obtener_imagen(id_test: str, num_imagen: str, url_origen: str) -> bytes | None:
    """
    Descarga una imagen del servidor de Daypo.
    Usa la cabecera Referer para evitar bloqueos por hotlink.
    Patron de ruta: /testimages/{3 primeros digitos del ID}/{ID}_{num}.jpg
    """
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
    """Inserta una pregunta completa (enunciado + imagen + opciones) en el documento Word."""
    # Enunciado en negrita
    parrafo = doc.add_paragraph()
    run = parrafo.add_run(f"{num}. {enunciado}")
    run.bold = True
    run.font.size = Pt(11)

    # Imagen (si existe)
    if img_bytes:
        doc.add_picture(BytesIO(img_bytes), width=Inches(3.5))

    # Opciones de respuesta
    for texto_opcion, es_correcta in opciones:
        parrafo_op = doc.add_paragraph()
        if es_correcta:
            run_op = parrafo_op.add_run(f"   - {texto_opcion}  (correcta)")
            run_op.bold = True
            run_op.font.color.rgb = RGBColor(0x1A, 0x73, 0x28)  # verde oscuro
        else:
            parrafo_op.add_run(f"   - {texto_opcion}")

    doc.add_paragraph()  # Espacio entre preguntas


def extraer_datos_test(url: str, headers_web: dict) -> tuple[str, str, list] | None:
    """
    Obtiene el ID del test, el titulo y la lista de preguntas parseadas desde la API de Daypo.
    Devuelve (id_test, titulo, preguntas) o None si hay algun error.
    """
    # Paso 1: obtener el ID del test desde el HTML de la portada
    try:
        res_html = requests.get(url, headers=headers_web, timeout=10)
        res_html.raise_for_status()
        match = re.search(r"ntest\s*=\s*(\d+)", res_html.text)
        if not match:
            return None
        id_test = match.group(1)
    except requests.RequestException:
        return None

    # Paso 2: llamar a la API interna (POST a load.php con el ID del test)
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

    # Paso 3: extraer titulo y lista de preguntas del XML
    nodo_titulo = raiz.find(".//t")
    titulo = nodo_titulo.text.strip() if (nodo_titulo is not None and nodo_titulo.text) else f"Test {id_test}"

    contenedor = raiz.find("c")
    if contenedor is None:
        return None

    preguntas_raw = contenedor.findall("c")
    preguntas = []

    for q in preguntas_raw:
        # Enunciado
        nodo_p = q.find("p")
        enunciado = nodo_p.text.strip() if nodo_p is not None and nodo_p.text else "Sin enunciado"

        # Numero de imagen (si la hay)
        nodo_b = q.find("b")
        num_imagen = nodo_b.text.strip() if nodo_b is not None and nodo_b.text else None

        # Mascara de respuesta correcta: la posicion del '2' indica la opcion correcta
        nodo_c = q.find("c")
        mascara = nodo_c.text if nodo_c is not None and nodo_c.text else ""
        indice_correcta = mascara.find("2")

        # Opciones
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


# ---------------------------------------------------------------------------
# Interfaz de usuario (Streamlit)
# ---------------------------------------------------------------------------

st.title("📝 Daypo Extractor")
st.markdown(
    "Extrae preguntas, imagenes y respuestas correctas de cualquier test de "
    "[Daypo](https://www.daypo.com) y exportalos a documentos Word organizados."
)

st.divider()

enlaces_texto = st.text_area(
    "Pega aqui tus enlaces de Daypo (uno por linea):",
    height=220,
    placeholder=(
        "https://www.daypo.com/tema-1-trauma.html\n"
        "https://www.daypo.com/tema-2-trauma.html\n"
        "https://www.daypo.com/imagenes-trauma.html"
    ),
)

col1, col2 = st.columns([3, 1])
with col1:
    iniciar = st.button("Iniciar Extraccion", type="primary", use_container_width=True)
with col2:
    st.caption("Requiere conexion a internet")

if iniciar:
    enlaces = [l.strip() for l in enlaces_texto.splitlines() if l.strip().startswith("http")]

    if not enlaces:
        st.error("Introduce al menos un enlace valido de Daypo (debe comenzar por http).")
        st.stop()

    es_multiple = len(enlaces) > 1
    headers_web = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    memoria_zip = BytesIO()

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

            for i, pregunta in enumerate(preguntas, start=1):
                # Descargar imagen si la hay
                img_bytes = None
                if pregunta["num_imagen"] is not None:
                    img_bytes = obtener_imagen(id_test, pregunta["num_imagen"], url)
                    if img_bytes:
                        zip_file.writestr(
                            f"{titulo_carpeta}/img_{id_test}_{pregunta['num_imagen']}.jpg",
                            img_bytes,
                        )

                # Insertar pregunta en el documento individual
                procesar_pregunta(doc_indiv, i, pregunta["enunciado"], img_bytes, pregunta["opciones"])

                # Insertar pregunta en el documento unificado
                if es_multiple:
                    procesar_pregunta(doc_unificado, i, pregunta["enunciado"], img_bytes, pregunta["opciones"])

            # Guardar el Word individual dentro del ZIP
            buf_indiv = BytesIO()
            doc_indiv.save(buf_indiv)
            zip_file.writestr(f"{titulo_carpeta}/{titulo_carpeta}.docx", buf_indiv.getvalue())

            if es_multiple:
                doc_unificado.add_page_break()

        # Guardar el documento unificado en la raiz del ZIP (solo si hay varios tests)
        if es_multiple:
            buf_unif = BytesIO()
            doc_unificado.save(buf_unif)
            zip_file.writestr("TODOS_LOS_TESTS_UNIDOS.docx", buf_unif.getvalue())

    barra.progress(100, text="Extraccion completada.")
    log.empty()

    if errores:
        st.warning(f"No se pudieron procesar {len(errores)} enlace(s). Revisa tu conexion o que la URL sea correcta.")

    memoria_zip.seek(0)
    st.success(f"Procesados {len(enlaces) - len(errores)} tests correctamente. Archivo listo para descargar.")
    st.download_button(
        label="Descargar ZIP con todos los tests",
        data=memoria_zip.getvalue(),
        file_name="Banco_de_Preguntas_Daypo.zip",
        mime="application/zip",
        use_container_width=True,
    )
