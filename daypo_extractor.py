import streamlit as st
import requests
import re
import xml.etree.ElementTree as ET
import zipfile
from io import BytesIO
from docx import Document
from docx.shared import Inches

st.set_page_config(page_title="Extractor Daypo Pro", page_icon="📝", layout="centered")

def limpiar_nombre(texto):
    return re.sub(r'[\/*?:"<>|]', "", texto).strip()

def obtener_imagen(id_test, num_imagen, url_origen):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': url_origen,
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8'
    }
    prefijo_3 = id_test[:3]
    ruta = f"https://www.daypo.com/testimages/{prefijo_3}/{id_test}_{num_imagen}.jpg"
    try:
        res_img = requests.get(ruta, headers=headers, timeout=5)
        if res_img.status_code == 200:
            return res_img.content
    except:
        pass
    return None

st.title("Extractor Automatico de Daypo")
st.markdown("Extrae preguntas, opciones, respuestas correctas e imagenes de tests de Daypo y los exporta a Word.")

enlaces_introducidos = st.text_area(
    "Pega aqui tus enlaces de Daypo (uno por linea):",
    height=250,
    placeholder="https://www.daypo.com/tu-test.html"
)

if st.button("Iniciar Extraccion", type="primary"):
    enlaces = [linea.strip() for linea in enlaces_introducidos.split("\n") if linea.strip()]
    if not enlaces:
        st.error("Por favor, introduce al menos un enlace valido.")
    else:
        es_multiple = len(enlaces) > 1
        memoria_zip = BytesIO()
        with zipfile.ZipFile(memoria_zip, 'w', zipfile.ZIP_DEFLATED) as archivo_zip:
            headers_xml = {'User-Agent': 'Mozilla/5.0'}
            if es_multiple:
                doc_merge = Document()
                doc_merge.add_heading('Recopilacion General de Tests Daypo', 0)
            barra_progreso = st.progress(0)
            estado_texto = st.empty()
            for indice, url in enumerate(enlaces):
                porcentaje = int((indice / len(enlaces)) * 100)
                barra_progreso.progress(porcentaje)
                nombre_corto = url.split('/')[-1].replace('.html', '')
                estado_texto.text(f"Procesando test {indice + 1} de {len(enlaces)}: {nombre_corto}...")
                try:
                    res_web = requests.get(url, headers=headers_xml, timeout=10)
                    match = re.search(r'ntest\s*=\s*(\d+)', res_web.text)
                    if not match:
                        st.warning(f"No se encontro el ID para: {url}")
                        continue
                    id_test = match.group(1)
                except Exception as e:
                    st.warning(f"Error de conexion: {url}")
                    continue
                try:
                    res_xml = requests.post("https://www.daypo.com/asps/load.php", data={'tes': id_test}, headers=headers_xml, timeout=10)
                    raiz = ET.fromstring(res_xml.text)
                except:
                    st.warning(f"Error descargando datos del test: {url}")
                    continue
                nodo_titulo = raiz.find('.//t')
                titulo_bruto = nodo_titulo.text if (nodo_titulo is not None and nodo_titulo.text) else f"Test_{id_test}"
                titulo_limpio = limpiar_nombre(titulo_bruto)
                doc_indiv = Document()
                doc_indiv.add_heading(titulo_bruto, level=1)
                if es_multiple:
                    doc_merge.add_heading(titulo_bruto, level=1)
                contenedor = raiz.find('c')
                if contenedor is None:
                    continue
                preguntas = contenedor.findall('c')
                for i, q in enumerate(preguntas):
                    nodo_p = q.find('p')
                    enunciado = nodo_p.text if nodo_p is not None else "Pregunta sin texto"
                    texto_enunciado = f"{i+1}. {enunciado}"
                    doc_indiv.add_paragraph().add_run(texto_enunciado).bold = True
                    if es_multiple:
                        doc_merge.add_paragraph().add_run(texto_enunciado).bold = True
                    nodo_b = q.find('b')
                    if nodo_b is not None and nodo_b.text:
                        num_imagen = nodo_b.text.strip()
                        img_bytes = obtener_imagen(id_test, num_imagen, url_origen=url)
                        if img_bytes:
                            nombre_img = f"img_{id_test}_{num_imagen}.jpg"
                            archivo_zip.writestr(f"{titulo_limpio}/{nombre_img}", img_bytes)
                            doc_indiv.add_picture(BytesIO(img_bytes), width=Inches(3.0))
                            if es_multiple:
                                doc_merge.add_picture(BytesIO(img_bytes), width=Inches(3.0))
                    nodo_c = q.find('c')
                    mascara = nodo_c.text if nodo_c is not None else ""
                    indice_correcta = mascara.find('2')
                    nodo_r = q.find('r')
                    if nodo_r is not None:
                        opciones = nodo_r.findall('o')
                        for o_idx, nodo_o in enumerate(opciones):
                            texto_opcion = nodo_o.text if nodo_o.text else ""
                            texto_final = f"  - {texto_opcion}"
                            if o_idx == indice_correcta:
                                texto_final += " (correcta)"
                            doc_indiv.add_paragraph(texto_final)
                            if es_multiple:
                                doc_merge.add_paragraph(texto_final)
                memoria_doc_indiv = BytesIO()
                doc_indiv.save(memoria_doc_indiv)
                archivo_zip.writestr(f"{titulo_limpio}/{titulo_limpio}.docx", memoria_doc_indiv.getvalue())
                if es_multiple:
                    doc_merge.add_page_break()
            if es_multiple:
                memoria_doc_merge = BytesIO()
                doc_merge.save(memoria_doc_merge)
                archivo_zip.writestr("DOCUMENTO_TODOS_LOS_TEMAS_UNIDOS.docx", memoria_doc_merge.getvalue())
        barra_progreso.progress(100)
        estado_texto.text("Extraccion completada con exito!")
        memoria_zip.seek(0)
        st.success("Tu archivo esta listo para descargar!")
        st.download_button(
            label="Descargar todos los Tests (ZIP)",
            data=memoria_zip.getvalue(),
            file_name="Banco_de_Preguntas_Daypo.zip",
            mime="application/zip",
            use_container_width=True
        )
