"""Variables CSS por tema — inyectadas en :root según session_state."""

LIGHT_THEME_CSS = """
:root {
    --accent: #7C69EF;
    --accent-hover: #6B58E8;
    --accent-soft: rgba(124, 105, 239, 0.18);
    --accent-glow: rgba(124, 105, 239, 0.28);
    --accent-glow-soft: rgba(124, 105, 239, 0.14);
    --highlight: #8B5CF6;
    --highlight-soft: rgba(139, 92, 246, 0.16);
    --surface: #FFFFFF;
    --surface-2: #F3F4F6;
    --bg: #FFFFFF;
    --border: rgba(0, 0, 0, 0.10);
    --border-strong: #CBD5E1;
    --text: #111827;
    --muted: #475569;
    --error: #DC2626;
    --input-bg: #FFFFFF;
    --input-border: #CBD5E1;
    --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.04);
    --shadow-md: 0 4px 24px rgba(15, 23, 42, 0.06), 0 1px 3px rgba(15, 23, 42, 0.04);
    --omni-panel-bg: var(--surface);
    --omni-panel-border: 1px solid #CBD5E1;
    --omni-panel-hover-border: rgba(124, 105, 239, 0.55);
    --toggle-active-bg: #FFFFFF;
    --toggle-active-text: #111827;
    --toggle-track-bg: #F3F4F6;
    --toggle-track-border: #CBD5E1;
    --switch-on: #22C55E;
    --switch-on-border: #16A34A;
    --btn-weight: var(--weight-semibold);
}
"""

LIGHT_EXTRA_CSS = """
.stApp, [data-testid="stAppViewContainer"] {
    background-image:
        radial-gradient(ellipse 95% 60% at 12% -8%, rgba(139, 92, 246, 0.24), transparent 58%),
        radial-gradient(ellipse 75% 50% at 92% 2%, rgba(124, 105, 239, 0.20), transparent 55%),
        radial-gradient(ellipse 65% 45% at 50% 108%, rgba(167, 139, 250, 0.16), transparent 58%) !important;
}
[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid #94A3B8 !important;
    box-shadow: 0 0 0 1px rgba(124, 105, 239, 0.22) !important;
}
"""

DARK_THEME_CSS = """
:root {
    --accent: #9B8AFB;
    --accent-hover: #B4A6FC;
    --accent-soft: rgba(155, 138, 251, 0.14);
    --accent-glow: rgba(155, 138, 251, 0.32);
    --accent-glow-soft: rgba(155, 138, 251, 0.18);
    --highlight: #A78BFA;
    --highlight-soft: rgba(167, 139, 250, 0.10);
    --surface: #16181F;
    --surface-2: #1E2129;
    --bg: #0D0F14;
    --border: rgba(255, 255, 255, 0.08);
    --border-strong: #2D3340;
    --text: #F1F5F9;
    --muted: #94A3B8;
    --error: #F87171;
    --input-bg: #1E2129;
    --input-border: #2D3340;
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.25);
    --shadow-md: 0 4px 28px rgba(0,0,0,0.35), 0 1px 2px rgba(0,0,0,0.2);
    --omni-panel-bg: var(--surface);
    --omni-panel-border: 1px solid var(--border-strong);
    --omni-panel-hover-border: rgba(155, 138, 251, 0.45);
    --toggle-active-bg: #262730;
    --toggle-active-text: #F1F5F9;
    --toggle-track-bg: #1E2129;
    --toggle-track-border: #2D3340;
    --switch-on: #22C55E;
    --switch-on-border: #16A34A;
}
"""

DARK_EXTRA_CSS = """
[data-testid="stVerticalBlockBorderWrapper"]:hover,
[data-testid="stFileUploader"]:hover {
    background: rgba(139, 92, 246, 0.18) !important;
}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stFileUploader"]:hover {
    background: transparent !important;
}
.export-icon--quiz    { background: rgba(79,70,229,0.22); color: #A5B4FC; }
.export-icon--anki    { background: rgba(37,99,235,0.22); color: #93C5FD; }
.export-icon--remnote { background: rgba(67,56,202,0.22); color: #A5B4FC; }
.export-icon--word    { background: rgba(29,78,216,0.22); color: #93C5FD; }
.export-icon--pdf     { background: rgba(220,38,38,0.2); color: #FCA5A5; }
.export-icon--images  { background: rgba(5,150,105,0.2); color: #6EE7B7; }
"""
