"""Router automático de modelos — elige el más barato adecuado por trabajo."""
from __future__ import annotations

import json
from typing import Any

from . import ai_import
from .api_config import PROVEEDORES, proveedor_listo, proveedores_configurados
from .ai_providers import _openai_chat  # noqa: SLF001

# Modelos internos (nunca los elige el usuario)
MODELO_ROUTER: dict[str, str] = {
    "gemini": "gemini-2.5-flash-lite",
    "groq": "llama-3.1-8b-instant",
    "cerebras": "gpt-oss-120b",
    "mistral": "ministral-8b-latest",
}

_MAX_FALLBACK_POR_PROVEEDOR = 2
_ORDEN_TEXTO = ("groq", "cerebras", "mistral", "gemini")


def modelos_extraccion(config: dict, pid: str) -> list[str]:
    """Modelos descubiertos al probar/importar, o lista estática por defecto."""
    prov = config.get("providers", {}).get(pid, {})
    descubiertos = prov.get("modelos_disponibles") or []
    if descubiertos:
        return list(descubiertos)
    return list(MODELOS_EXTRACCION.get(pid, []))


def _modelos_plan_limitados(config: dict, pid: str) -> list[str]:
    """Como mucho N modelos por proveedor en el plan de fallback."""
    todos = modelos_extraccion(config, pid)
    ordenados = [m for m in MODELOS_EXTRACCION.get(pid, []) if m in todos]
    for m in todos:
        if m not in ordenados:
            ordenados.append(m)
    return ordenados[:_MAX_FALLBACK_POR_PROVEEDOR]


MODELOS_EXTRACCION: dict[str, list[str]] = {
    "gemini": [
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash-lite",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
    ],
    "groq": ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"],
    "cerebras": ["gpt-oss-120b", "llama-3.3-70b"],
    "mistral": ["ministral-8b-latest", "open-mistral-nemo", "mistral-small-latest"],
}

_PROMPT_ROUTER = """\
Eres el router de Omnitest. El usuario tiene preguntas tipo test YA EXISTENTES \
(desordenadas, OCR, PDF escaneado, etc.) y quiere extraerlas y limpiarlas. \
NO hay que inventar preguntas nuevas desde un temario.

Metadatos del trabajo:
{metadatos}

Modelos disponibles (solo puedes elegir de esta lista):
{disponibles}

Elige el modelo MAS LIGERO/BARATO que pueda hacer bien este trabajo. Prioriza ahorrar tokens.

Responde SOLO JSON valido:
{{"provider":"gemini|groq|cerebras|mistral","model":"nombre-exacto","reason":"una frase corta"}}

Reglas:
- PDF o imagenes -> obligatorio provider gemini; flash-lite si >5 archivos o >500KB total; flash si OCR muy sucio
- Solo texto corto (<4000 chars) y parece MCQ legible -> el modelo mas barato del provider adecuado (lite/8b)
- Texto largo o muy desordenado -> un escalon arriba (flash, no pro)
- Word/docx ya convertido a texto -> tratar como texto
- Si solo hay groq/cerebras/mistral y hay PDF/imagen -> devuelve el mejor texto posible pero indica en reason que hace falta gemini
"""


def analizar_metadatos_job(texto: str, archivos: list | None) -> dict[str, Any]:
    archivos = archivos or []
    tipos: list[dict[str, Any]] = []
    total_kb = 0
    tiene_pdf = tiene_img = tiene_docx = False

    for f in archivos:
        ext = f.name.rsplit(".", 1)[-1].lower()
        try:
            datos = f.read()
            if not isinstance(datos, (bytes, bytearray)):
                datos = b""
            kb = len(datos) // 1024
        except Exception:  # noqa: BLE001
            kb = 0
        tipos.append({"nombre": f.name, "ext": ext, "kb": kb})
        total_kb += kb
        tiene_pdf = tiene_pdf or ext == "pdf"
        tiene_img = tiene_img or ext in ("jpg", "jpeg", "png", "webp")
        tiene_docx = tiene_docx or ext in ("docx", "doc")

    texto = (texto or "").strip()
    preview = texto[:600].replace("\n", " ")
    parece_mcq = sum(1 for c in texto.lower() if c in "abcd") >= 3 or "?" in texto

    return {
        "texto_caracteres": len(texto),
        "texto_preview": preview,
        "parece_mcq": parece_mcq,
        "num_archivos": len(archivos),
        "archivos": tipos,
        "total_kb": total_kb,
        "tiene_pdf": tiene_pdf,
        "tiene_imagen": tiene_img,
        "tiene_docx": tiene_docx,
        "multimodal_necesario": tiene_pdf or tiene_img,
    }


def _catalogo_usuario(config: dict) -> list[dict[str, Any]]:
    out = []
    for pid in proveedores_configurados(config):
        out.append({
            "provider": pid,
            "nombre": PROVEEDORES[pid]["nombre"],
            "multimodal": PROVEEDORES[pid]["multimodal"],
            "modelos": modelos_extraccion(config, pid),
        })
    return out


def _proveedor_router_barato(config: dict) -> tuple[str, str] | None:
    orden = ["groq", "gemini", "cerebras", "mistral"]
    for pid in orden:
        if proveedor_listo(config, pid):
            return pid, MODELO_ROUTER[pid]
    return None


def _llamada_router(config: dict, metadatos: dict, log=None) -> dict | None:
    par = _proveedor_router_barato(config)
    if not par:
        return None
    pid, modelo = par
    catalogo = _catalogo_usuario(config)
    prov = config["providers"][pid]
    api_key = prov["api_key"].strip()

    prompt = _PROMPT_ROUTER.format(
        metadatos=json.dumps(metadatos, ensure_ascii=False),
        disponibles=json.dumps(catalogo, ensure_ascii=False),
    )
    if log:
        log("Analizando qué modelo conviene…")

    try:
        if pid == "gemini":
            raw = ai_import._gemini_call(api_key, modelo, [prompt], log=log)  # noqa: SLF001
        else:
            raw = _openai_chat(pid, api_key, modelo, prompt, log=log, max_tokens=200)
        return ai_import._extraer_json(raw)  # noqa: SLF001
    except Exception:  # noqa: BLE001
        return None


def _validar_eleccion(config: dict, pid: str, modelo: str) -> bool:
    if not proveedor_listo(config, pid):
        return False
    modelos = modelos_extraccion(config, pid)
    return modelo in modelos


def _heuristica(config: dict, meta: dict) -> tuple[str, str, str]:
    """Fallback sin LLM."""
    listos = proveedores_configurados(config)
    if meta["multimodal_necesario"]:
        if "gemini" in listos:
            m = "gemini-2.5-flash-lite"
            if meta["total_kb"] > 500 or meta["num_archivos"] > 3:
                m = "gemini-2.5-flash-lite"
            return "gemini", m, "Multimodal — Gemini flash-lite"
        pid = listos[0]
        mods = modelos_extraccion(config, pid)
        return pid, mods[0], "Sin Gemini para PDF/imagen — mejor esfuerzo texto"

    for pid in _ORDEN_TEXTO:
        if pid not in listos:
            continue
        mods = modelos_extraccion(config, pid)
        if meta["texto_caracteres"] > 12000 and len(mods) > 1:
            return pid, mods[-1], "Texto largo — modelo medio"
        return pid, mods[0], "Solo texto — proveedor ligero"

    pid = listos[0]
    mods = modelos_extraccion(config, pid)
    return pid, mods[0], "Por defecto — modelo ligero"


def elegir_modelo(
    config: dict,
    metadatos: dict,
    log=None,
) -> tuple[str, str, str]:
    """Devuelve (provider_id, model, reason)."""
    eleccion = _llamada_router(config, metadatos, log=log)
    if eleccion:
        pid = eleccion.get("provider", "")
        modelo = eleccion.get("model", "")
        reason = eleccion.get("reason", "Router IA")
        if _validar_eleccion(config, pid, modelo):
            if metadatos["multimodal_necesario"] and pid != "gemini":
                pass  # cae a heurística
            elif (
                not metadatos["multimodal_necesario"]
                and pid == "gemini"
                and any(proveedor_listo(config, p) for p in _ORDEN_TEXTO if p != "gemini")
            ):
                pass  # texto solo: preferir groq/cerebras/mistral
            else:
                return pid, modelo, reason

    return _heuristica(config, metadatos)


def plan_fallback(config: dict, meta: dict, pid_primero: str, modelo_primero: str) -> list[tuple[str, str]]:
    """Orden de intentos tras el primero."""
    vistos = {(pid_primero, modelo_primero)}
    plan: list[tuple[str, str]] = [(pid_primero, modelo_primero)]

    if meta["multimodal_necesario"]:
        pids = []
        if proveedor_listo(config, "gemini"):
            pids.append("gemini")
        pids.extend(p for p in proveedores_configurados(config) if p != "gemini")
    else:
        pids = [p for p in _ORDEN_TEXTO if proveedor_listo(config, p)]

    for pid in pids:
        for m in _modelos_plan_limitados(config, pid):
            if (pid, m) in vistos:
                continue
            if meta["multimodal_necesario"] and pid != "gemini":
                continue
            plan.append((pid, m))
            vistos.add((pid, m))
    return plan
