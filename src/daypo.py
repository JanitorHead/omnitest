"""Extracción de tests públicos de Daypo.

Accede al endpoint interno /asps/load.php (el mismo que usa el navegador) y
descifra la respuesta correcta a partir de la máscara numérica del XML.
"""
import re
import xml.etree.ElementTree as ET

import requests

_HEADERS_WEB = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def extraer_enlaces_daypo(texto: str) -> list[str]:
    """Detecta y deduplica enlaces de Daypo dentro de cualquier texto."""
    patron = r'https?://(?:www\.)?daypo\.com/[^\s\n\r"\'<>()\[\]{}]+'
    candidatos = [re.sub(r"[.,;:!?]+$", "", e) for e in re.findall(patron, texto)]
    vistos: set[str] = set()
    resultado = []
    for e in candidatos:
        if e not in vistos:
            vistos.add(e)
            resultado.append(e)
    return resultado


def obtener_imagen(id_test: str, num_imagen: str, url_origen: str) -> bytes | None:
    headers = {
        **_HEADERS_WEB,
        "Referer": url_origen,
        "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    }
    prefijo = id_test[:3]
    url = f"https://www.daypo.com/testimages/{prefijo}/{id_test}_{num_imagen}.jpg"
    try:
        r = requests.get(url, headers=headers, timeout=8)
        if r.status_code == 200:
            return r.content
    except requests.RequestException:
        pass
    return None


def _parsear_test(url: str) -> tuple[str, str, list] | None:
    """Devuelve (id_test, titulo, preguntas_crudas) o None si falla."""
    try:
        res_html = requests.get(url, headers=_HEADERS_WEB, timeout=10)
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
            headers=_HEADERS_WEB,
            timeout=10,
        )
        res_xml.raise_for_status()
        raiz = ET.fromstring(res_xml.text)
    except (requests.RequestException, ET.ParseError):
        return None

    nodo_titulo = raiz.find(".//t")
    titulo = (
        nodo_titulo.text.strip()
        if (nodo_titulo is not None and nodo_titulo.text)
        else f"Test {id_test}"
    )

    contenedor = raiz.find("c")
    if contenedor is None:
        return None

    preguntas = []
    for q in contenedor.findall("c"):
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
        preguntas.append({"enunciado": enunciado, "num_imagen": num_imagen, "opciones": opciones})

    return id_test, titulo, preguntas


def extraer_test(url: str, descargar_imagenes: bool = True) -> dict | None:
    """
    Extrae un test de Daypo al formato canónico de la app (ver utils).
    Descarga las imágenes de cada pregunta. Devuelve None si no se pudo.
    """
    parsed = _parsear_test(url)
    if parsed is None:
        return None
    id_test, titulo, preguntas = parsed

    preguntas_final: list[dict] = []
    for pregunta in preguntas:
        img_bytes = None
        img_nombre = None
        if descargar_imagenes and pregunta["num_imagen"] is not None:
            img_nombre = f"img_{id_test}_{pregunta['num_imagen']}.jpg"
            img_bytes = obtener_imagen(id_test, pregunta["num_imagen"], url)
        preguntas_final.append({
            "enunciado": pregunta["enunciado"],
            "opciones": pregunta["opciones"],
            "img_bytes": img_bytes,
            "img_nombre": img_nombre,
        })

    return {"titulo": titulo, "preguntas": preguntas_final}
