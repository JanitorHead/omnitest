"""Decoración HTML — zona de subida estilo RemNote."""

UPLOAD_ICONS_SVG = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 132 40'%3E"
    "%3Crect x='2' y='4' width='28' height='32' rx='6' fill='%23FEE2E2'/%3E"
    "%3Ctext x='16' y='25' text-anchor='middle' font-size='9' font-weight='700' fill='%23DC2626'%3EPDF%3C/text%3E"
    "%3Crect x='52' y='4' width='28' height='32' rx='6' fill='%23DBEAFE'/%3E"
    "%3Ctext x='66' y='25' text-anchor='middle' font-size='8' font-weight='700' fill='%232563EB'%3EDOC%3C/text%3E"
    "%3Crect x='102' y='4' width='28' height='32' rx='6' fill='%23EDE9FE'/%3E"
    "%3Ctext x='116' y='25' text-anchor='middle' font-size='8' font-weight='700' fill='%237C3AED'%3EIMG%3C/text%3E"
    "%3C/svg%3E"
)


UPLOAD_ICON_GHOST_SVG = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' "
    "fill='none' stroke='%23111827' stroke-width='1.5' stroke-linecap='round' "
    "stroke-linejoin='round'%3E%3Cpath d='M8 2.5v7M8 2.5L5.5 5M8 2.5l2.5 2.5'/%3E"
    "%3Cpath d='M3 11.5h10'/%3E%3Cpath d='M4.5 13.5h7'/%3E%3C/svg%3E"
)

UPLOAD_ICON_GHOST_SVG_DARK = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' "
    "fill='none' stroke='%23E2E8F0' stroke-width='1.5' stroke-linecap='round' "
    "stroke-linejoin='round'%3E%3Cpath d='M8 2.5v7M8 2.5L5.5 5M8 2.5l2.5 2.5'/%3E"
    "%3Cpath d='M3 11.5h10'/%3E%3Cpath d='M4.5 13.5h7'/%3E%3C/svg%3E"
)


def or_divider_html() -> str:
    return '<p class="rn-or-divider">o</p>'