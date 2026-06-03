"""Etiquetas de progreso con % y ETA."""
import time


def fmt_eta(seconds: float) -> str:
    s = max(0, int(seconds))
    if s < 60:
        return f"{s}s"
    m, s = divmod(s, 60)
    if m < 60:
        return f"{m}:{s:02d} min"
    h, m = divmod(m, 60)
    return f"{h}:{m:02d} h"


def etiqueta_progreso(msg: str, fraccion: float, inicio: float) -> str:
    pct = int(min(max(fraccion, 0.0), 1.0) * 100)
    partes = [msg, f"{pct}%"]
    if fraccion >= 0.03:
        transcurrido = time.monotonic() - inicio
        restante = transcurrido / fraccion * (1.0 - fraccion)
        if restante >= 2:
            partes.append(f"~{fmt_eta(restante)} restante")
    return " · ".join(partes)
