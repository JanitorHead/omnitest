"""Logo SVG Omnitest — icono oficial desde static/logo.svg."""
from pathlib import Path

_LOGO_PATH = Path(__file__).resolve().parents[2] / "static" / "logo.svg"


def _logo_svg() -> str:
    raw = _LOGO_PATH.read_text(encoding="utf-8").strip()
    if 'class="omni-logo"' in raw:
        return raw
    return raw.replace("<svg", '<svg class="omni-logo" aria-hidden="true"', 1)


def wordmark_html() -> str:
    return (
        f'<div class="omni-wordmark">{_logo_svg()}'
        '<span class="omni-wordmark-text">Omnitest</span></div>'
    )
