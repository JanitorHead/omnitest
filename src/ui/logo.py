"""Logo Omnitest — icono app (static/icon.png, mismo estilo que og-image)."""
import base64
from functools import lru_cache
from pathlib import Path

_ICON_PATH = Path(__file__).resolve().parents[2] / "static" / "icon.png"


@lru_cache(maxsize=1)
def _icon_b64() -> str:
    return base64.b64encode(_ICON_PATH.read_bytes()).decode("ascii")


def _logo_img() -> str:
    return (
        f'<img class="omni-logo" src="data:image/png;base64,{_icon_b64()}" '
        'alt="" aria-hidden="true" decoding="async">'
    )


def wordmark_html() -> str:
    return (
        f'<div class="omni-wordmark">{_logo_img()}'
        '<span class="omni-wordmark-text">Omnitest</span></div>'
    )
