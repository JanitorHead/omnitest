"""Configuración de proveedores de IA: metadatos, carga/guardado de claves API.

Las claves viven solo en la sesión de Streamlit (o en un archivo JSON que el
usuario descarga y vuelve a subir). Omnitest no persiste keys en servidor.
"""
from __future__ import annotations

import json
from copy import deepcopy
from typing import Any

CONFIG_VERSION = 1
CONFIG_FILENAME = "omnitest-config.json"

PROVEEDORES: dict[str, dict[str, Any]] = {
    "gemini": {
        "nombre": "Google AI Studio",
        "icono": "🔷",
        "descripcion": "Gemini — la mejor opción multimodal (texto, fotos, PDF).",
        "registro_url": "https://aistudio.google.com/apikey",
        "multimodal": True,
        "modelo_defecto": "gemini-2.5-flash-lite",
        "modelos_sugeridos": [
            "gemini-2.5-flash-lite",
            "gemini-2.5-flash",
            "gemini-flash-latest",
            "gemini-2.0-flash",
        ],
    },
    "groq": {
        "nombre": "Groq Cloud",
        "icono": "⚡",
        "descripcion": "Llama y Mixtral ultrarrápidos. Ideal para texto y Word.",
        "registro_url": "https://console.groq.com/keys",
        "multimodal": False,
        "modelo_defecto": "llama-3.3-70b-versatile",
        "modelos_sugeridos": [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
        ],
    },
    "cerebras": {
        "nombre": "Cerebras Cloud",
        "icono": "🚀",
        "descripcion": "Llama optimizado — millones de tokens gratis al día.",
        "registro_url": "https://cloud.cerebras.ai/",
        "multimodal": False,
        "modelo_defecto": "gpt-oss-120b",
        "modelos_sugeridos": [
            "gpt-oss-120b",
            "llama-3.3-70b",
        ],
    },
    "mistral": {
        "nombre": "Mistral AI",
        "icono": "🇫🇷",
        "descripcion": "Modelos europeos; muy buenos en español y redacción.",
        "registro_url": "https://console.mistral.ai/api-keys/",
        "multimodal": False,
        "modelo_defecto": "mistral-small-latest",
        "modelos_sugeridos": [
            "mistral-small-latest",
            "open-mistral-nemo",
            "ministral-8b-latest",
        ],
    },
}


def config_vacia() -> dict[str, Any]:
    """Estado inicial de configuración API en sesión."""
    providers = {}
    for pid, meta in PROVEEDORES.items():
        providers[pid] = {
            "api_key": "",
            "modelo": meta["modelo_defecto"],
            "habilitado": False,
            "modelos_disponibles": [],
        }
    return {
        "version": CONFIG_VERSION,
        "proveedor_activo": "gemini",
        "providers": providers,
    }


def serializar_config(config: dict[str, Any]) -> str:
    """Exporta solo proveedores con clave (para descarga)."""
    export = {
        "version": CONFIG_VERSION,
        "proveedor_activo": config.get("proveedor_activo", "gemini"),
        "providers": {},
    }
    for pid, datos in config.get("providers", {}).items():
        key = (datos.get("api_key") or "").strip()
        if not key:
            continue
        export["providers"][pid] = {"api_key": key}
    return json.dumps(export, ensure_ascii=False, indent=2)


def cargar_config_desde_json(raw: str) -> tuple[dict[str, Any], list[str]]:
    """Fusiona un JSON subido con la plantilla vacía. Devuelve (config, avisos)."""
    avisos: list[str] = []
    base = config_vacia()
    try:
        datos = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON inválido: {e}") from e

    if datos.get("version", 1) != CONFIG_VERSION:
        avisos.append(
            f"Versión de archivo {datos.get('version')!r} — se importará lo posible."
        )

    activo = datos.get("proveedor_activo", "gemini")
    if activo in PROVEEDORES:
        base["proveedor_activo"] = activo

    for pid, prov in datos.get("providers", {}).items():
        if pid not in PROVEEDORES:
            avisos.append(f"Proveedor desconocido omitido: {pid}")
            continue
        key = (prov.get("api_key") or "").strip()
        if not key:
            continue
        base["providers"][pid]["api_key"] = key
        base["providers"][pid]["habilitado"] = True
        if prov.get("modelos_disponibles"):
            base["providers"][pid]["modelos_disponibles"] = list(prov["modelos_disponibles"])

    return base, avisos


def proveedor_activo(config: dict[str, Any]) -> str:
    return config.get("proveedor_activo", "gemini")


def datos_proveedor(config: dict[str, Any], pid: str | None = None) -> dict[str, Any]:
    pid = pid or proveedor_activo(config)
    return config.get("providers", {}).get(pid, {})


def proveedor_listo(config: dict[str, Any], pid: str | None = None) -> bool:
    d = datos_proveedor(config, pid)
    key = (d.get("api_key") or "").strip()
    if not key:
        return False
    return d.get("habilitado", True)


def proveedores_configurados(config: dict[str, Any]) -> list[str]:
    return [pid for pid in PROVEEDORES if proveedor_listo(config, pid)]


def resumen_estado(config: dict[str, Any]) -> str:
    """Texto corto para el dashboard."""
    listos = proveedores_configurados(config)
    if not listos:
        return "Sin claves API — configura al menos un proveedor"
    activo = proveedor_activo(config)
    meta = PROVEEDORES.get(activo, {})
    nombre = meta.get("nombre", activo)
    if proveedor_listo(config, activo):
        return f"Activo: {meta.get('icono', '')} {nombre} · {len(listos)} proveedor(es) listo(s)"
    return f"{len(listos)} proveedor(es) listo(s) — el activo ({nombre}) no tiene clave"


def merge_config(destino: dict[str, Any], origen: dict[str, Any]) -> dict[str, Any]:
    """Copia profunda de origen sobre destino (p. ej. tras importar JSON)."""
    out = deepcopy(origen)
    return out


def sincronizar_widgets_modal(config: dict[str, Any], forzar: bool = False) -> None:
    """Alinea widgets Streamlit del modal con api_config (evita pisar keys importadas)."""
    import streamlit as st

    for pid, prov in config.get("providers", {}).items():
        key = (prov.get("api_key") or "").strip()
        wkey = f"modal_key_{pid}"
        won = f"modal_on_{pid}"
        if forzar:
            st.session_state[wkey] = key
            st.session_state[won] = bool(key and prov.get("habilitado", True))
            continue
        if wkey not in st.session_state:
            st.session_state[wkey] = key
        elif key and not str(st.session_state.get(wkey, "")).strip():
            st.session_state[wkey] = key
        habilitado = bool(key and prov.get("habilitado", True))
        if won not in st.session_state:
            st.session_state[won] = habilitado
        elif habilitado and not st.session_state.get(won, False):
            st.session_state[won] = True
