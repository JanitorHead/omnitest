"""Extracción de tests públicos de Daypo.

Accede al endpoint interno /asps/load.php (el mismo que usa el navegador) y
descifra la respuesta correcta a partir de la máscara numérica del XML.
Las imágenes siguen la ruta que usa test7.js:
  testimages/{floor(id_test/10000)}/{id_test}_{n}.jpg
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

import requests

_HEADERS_WEB = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}

_DAYPO_HOSTS = ("daypo.com", "daypo.net")
_EXT_IMAGEN = ("jpg", "jpeg", "png", "webp", "gif")


def extraer_enlaces_daypo(texto: str) -> list[str]:
    """Detecta y deduplica enlaces de Daypo dentro de cualquier texto."""
    patron = (
        r"https?://(?:[a-z0-9-]+\.)*daypo\.(?:com|net)"
        r"/[^\s\n\r\"'<>()\[\]{}]+"
    )
    candidatos = [re.sub(r"[.,;:!?]+$", "", e) for e in re.findall(patron, texto, re.I)]
    vistos: set[str] = set()
    resultado: list[str] = []
    for enlace in candidatos:
        normalizado = _normalizar_url(enlace)
        if normalizado not in vistos:
            vistos.add(normalizado)
            resultado.append(normalizado)
    return resultado


def _normalizar_url(url: str) -> str:
    """Canonicaliza a www.daypo.com (donde responden load.php y testimages)."""
    parsed = urlparse(url.strip())
    host = (parsed.netloc or "").lower()
    if not any(host.endswith(h) for h in _DAYPO_HOSTS):
        return url.strip()
    path = parsed.path or "/"
    if not path.startswith("/"):
        path = "/" + path
    return f"https://www.daypo.com{path}"


def _prefijo_imagen(id_test: str) -> str:
    return str(int(id_test) // 10_000)


def _numero_imagen(nodo_b: ET.Element) -> str | None:
    """Índice de imagen en el XML (<b>0</b>); ignora vídeos de YouTube."""
    if nodo_b.get("y"):
        return None
    texto = (nodo_b.text or "").strip()
    if texto != "":
        return texto
    # Respaldo por si Daypo deja el índice solo en atributos.
    for attr in ("i", "n"):
        valor = (nodo_b.get(attr) or "").strip()
        if valor.isdigit():
            return valor
    return None


def obtener_imagen(
    id_test: str,
    num_imagen: str,
    url_origen: str,
    *,
    intentos: int = 3,
) -> bytes | None:
    headers = {
        **_HEADERS_WEB,
        "Referer": _normalizar_url(url_origen),
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    }
    prefijo = _prefijo_imagen(id_test)
    base = f"https://www.daypo.com/testimages/{prefijo}/{id_test}_{num_imagen}"
    for ext in _EXT_IMAGEN:
        url = f"{base}.{ext}"
        for _ in range(intentos):
            try:
                r = requests.get(url, headers=headers, timeout=20)
                if r.status_code == 200 and r.content:
                    ctype = (r.headers.get("Content-Type") or "").lower()
                    if "image" in ctype or ext in ("jpg", "jpeg", "png", "gif", "webp"):
                        return r.content
                if r.status_code in (403, 404, 410):
                    break
            except requests.RequestException:
                continue
    return None


def _parsear_test(url: str) -> tuple[str, str, list] | None:
    """Devuelve (id_test, titulo, preguntas_crudas) o None si falla."""
    url = _normalizar_url(url)
    try:
        res_html = requests.get(url, headers=_HEADERS_WEB, timeout=20)
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
            timeout=20,
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
        enunciado = (
            nodo_p.text.strip()
            if nodo_p is not None and nodo_p.text
            else "Sin enunciado"
        )
        nodo_b = q.find("b")
        num_imagen = _numero_imagen(nodo_b) if nodo_b is not None else None
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


def completar_imagenes_test(test: dict) -> int:
    """Reintenta descargas fallidas. Devuelve cuántas imágenes quedaron listas."""
    id_test = test.get("id_test")
    url = test.get("url_origen")
    if not id_test or not url:
        return sum(1 for p in test.get("preguntas", []) if p.get("img_bytes"))

    listas = 0
    for pregunta in test.get("preguntas", []):
        num = pregunta.get("img_num") or pregunta.get("num_imagen")
        if not num:
            continue
        if pregunta.get("img_bytes"):
            listas += 1
            continue
        img_bytes = obtener_imagen(id_test, num, url)
        if img_bytes:
            pregunta["img_bytes"] = img_bytes
            pregunta.setdefault(
                "img_nombre",
                f"img_{id_test}_{num}.jpg",
            )
            listas += 1
    return listas


def completar_imagenes_tests(tests: list[dict]) -> tuple[int, int]:
    """Devuelve (imágenes_listas, imágenes_esperadas)."""
    esperadas = 0
    listas = 0
    for test in tests:
        for pregunta in test.get("preguntas", []):
            if pregunta.get("img_num") or pregunta.get("num_imagen"):
                esperadas += 1
        listas += completar_imagenes_test(test)
    return listas, esperadas


def extraer_test(url: str, descargar_imagenes: bool = True) -> dict | None:
    """
    Extrae un test de Daypo al formato canónico de la app (ver utils).
    Descarga las imágenes de cada pregunta. Devuelve None si no se pudo.
    """
    url = _normalizar_url(url)
    parsed = _parsear_test(url)
    if parsed is None:
        return None
    id_test, titulo, preguntas = parsed

    preguntas_final: list[dict] = []
    imagenes_esperadas = 0
    imagenes_ok = 0
    for pregunta in preguntas:
        img_bytes = None
        img_nombre = None
        img_num = pregunta.get("num_imagen")
        if img_num is not None:
            imagenes_esperadas += 1
            img_nombre = f"img_{id_test}_{img_num}.jpg"
            if descargar_imagenes:
                img_bytes = obtener_imagen(id_test, img_num, url)
                if img_bytes:
                    imagenes_ok += 1
        preguntas_final.append({
            "enunciado": pregunta["enunciado"],
            "opciones": pregunta["opciones"],
            "img_num": img_num,
            "img_bytes": img_bytes,
            "img_nombre": img_nombre,
        })

    return {
        "titulo": titulo,
        "id_test": id_test,
        "url_origen": url,
        "preguntas": preguntas_final,
        "imagenes_esperadas": imagenes_esperadas,
        "imagenes_ok": imagenes_ok,
    }
