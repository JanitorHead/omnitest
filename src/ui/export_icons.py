"""Iconos SVG para tarjetas de exportación (estilo app, tipo RemNote)."""

_ICONS: dict[str, str] = {
    "quiz": (
        '<div class="export-icon export-icon--quiz">'
        '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="3" y="4" width="18" height="14" rx="2"/>'
        '<path d="M8 20h8"/><path d="M12 18v2"/>'
        '<path d="m9 9 2 2 4-4"/>'
        "</svg></div>"
    ),
    "anki": (
        '<div class="export-icon export-icon--anki">'
        '<svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">'
        '<path d="M12 2l2.4 4.9 5.4.8-3.9 3.8.9 5.3L12 14.8 7.2 17l.9-5.3L4.2 7.7l5.4-.8L12 2z"/>'
        "</svg></div>"
    ),
    "remnote": (
        '<div class="export-icon export-icon--remnote">'
        '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>'
        '<path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>'
        '<line x1="9" y1="7" x2="15" y2="7"/><line x1="9" y1="11" x2="13" y2="11"/>'
        "</svg></div>"
    ),
    "word": (
        '<div class="export-icon export-icon--word">'
        '<svg width="22" height="22" viewBox="0 0 24 24" fill="none">'
        '<rect x="4" y="2" width="16" height="20" rx="2" fill="currentColor" opacity="0.15"/>'
        '<rect x="4" y="2" width="16" height="20" rx="2" stroke="currentColor" stroke-width="1.75"/>'
        '<text x="12" y="15" text-anchor="middle" fill="currentColor" '
        'font-size="9" font-weight="700" font-family="Inter,system-ui,sans-serif">W</text>'
        "</svg></div>"
    ),
    "pdf": (
        '<div class="export-icon export-icon--pdf">'
        '<svg width="22" height="22" viewBox="0 0 24 24" fill="none">'
        '<rect x="4" y="2" width="16" height="20" rx="2" fill="currentColor" opacity="0.12"/>'
        '<rect x="4" y="2" width="16" height="20" rx="2" stroke="currentColor" stroke-width="1.75"/>'
        '<text x="12" y="14.5" text-anchor="middle" fill="currentColor" '
        'font-size="6.5" font-weight="700" font-family="Inter,system-ui,sans-serif">PDF</text>'
        "</svg></div>"
    ),
    "images": (
        '<div class="export-icon export-icon--images">'
        '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="3" y="5" width="18" height="14" rx="2"/>'
        '<circle cx="8.5" cy="10" r="1.5" fill="currentColor" stroke="none"/>'
        '<path d="m21 17-5.5-5.5a1.5 1.5 0 0 0-2.1 0L8 17"/>'
        "</svg></div>"
    ),
}


def icono_export(icon_id: str) -> str:
    return _ICONS.get(icon_id, _ICONS["quiz"])
