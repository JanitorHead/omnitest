"""Utilidades compartidas: nombres de archivo y manejo de opciones.

El formato canónico de un "test" en toda la app es:

    {
        "titulo": str,
        "preguntas": [
            {
                "enunciado": str,
                "opciones": [(texto: str, es_correcta: bool), ...],
                "img_bytes": bytes | None,
                "img_nombre": str | None,
            },
            ...
        ],
    }
"""
import re


def limpiar_nombre_carpeta(texto: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", texto).strip()


def nombre_archivo(texto: str) -> str:
    return re.sub(r"\s+", "_", limpiar_nombre_carpeta(texto)).strip("_")


def generar_nombre_base(tests_datos: list[dict]) -> str:
    """Nombre de archivo representativo del conjunto de tests."""
    if not tests_datos:
        return "Omnitest"
    if len(tests_datos) == 1:
        return nombre_archivo(tests_datos[0]["titulo"])
    titulos = [t["titulo"] for t in tests_datos]
    conteo: dict[str, int] = {}
    for titulo in titulos:
        for palabra in set(re.findall(r"[a-zA-ZÀ-ɏ]{4,}", titulo.lower())):
            conteo[palabra] = conteo.get(palabra, 0) + 1
    umbral = max(2, len(titulos) // 2)
    candidatos = [(p, c) for p, c in conteo.items() if c >= umbral]
    if candidatos:
        palabra = max(candidatos, key=lambda x: x[1])[0]
        return f"{palabra.capitalize()}_{len(titulos)}_tests"
    return f"{nombre_archivo(titulos[0])[:25].rstrip('_')}_y_{len(titulos) - 1}_mas"


def separar_opciones(opciones: list[tuple[str, bool]]) -> tuple[str | None, list[str]]:
    """Devuelve (texto_correcta, [incorrectas]) ignorando opciones vacías."""
    correcta = None
    incorrectas: list[str] = []
    for texto, es_correcta in opciones:
        if not texto:
            continue
        if es_correcta:
            correcta = texto
        else:
            incorrectas.append(texto)
    return correcta, incorrectas
