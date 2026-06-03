"""Estilos CSS — light/dark, contraste y dropzone coherente."""

OMNI_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0&display=swap');

:root {
    --font: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    --text-base: 15px;
    --text-sm: 14px;
    --text-xs: 13px;
    --text-lg: 16px;
    --ui-height: 42px;
    --ui-height-lg: 48px;
    --weight-normal: 400;
    --weight-medium: 500;
    --weight-semibold: 600;
    --weight-bold: 700;
    --tracking-tight: -0.03em;
    --tracking-ui: -0.018em;
    --tracking-body: -0.011em;
    --radius: 8px;
    --radius-lg: 12px;
    --ease: cubic-bezier(0.4, 0, 0.2, 1);
    --btn-font: var(--text-sm);
    --btn-weight: var(--weight-medium);
    --btn-radius: var(--radius);
    --btn-height: 40px;
    --btn-tracking: var(--tracking-ui);
    --btn-hover-glow: 0 0 0 1px var(--accent-glow-soft), 0 2px 12px var(--accent-glow-soft);
    --omni-panel-inset: none;
}

html {
    font-size: 16px;
}

body, .stApp {
    font-family: var(--font) !important;
    font-size: var(--text-base);
    letter-spacing: var(--tracking-body);
    color: var(--text);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

[class*="css"] {
    font-family: var(--font) !important;
    color: var(--text);
}

/* Hover: solo brillo, sin desplazamiento ni escala */
button:hover,
[data-baseweb="button"]:hover,
.export-card:hover,
.export-card:hover .export-icon,
div.stButton > button:hover,
div.stDownloadButton > button:hover {
    transform: none !important;
}

.stApp, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    background-image: var(--app-glow) !important;
    background-repeat: no-repeat !important;
}

#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; }
section[data-testid="stSidebar"] { display: none; }

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    padding-left: max(1rem, env(safe-area-inset-left, 0px)) !important;
    padding-right: max(1rem, env(safe-area-inset-right, 0px)) !important;
    max-width: 880px !important;
    box-sizing: border-box !important;
    overflow-x: hidden !important;
}

/* Scroll — toda la ventana (no solo la columna central) */
html, body {
    overflow-x: hidden !important;
    overflow-y: auto !important;
    max-width: 100% !important;
    width: 100% !important;
    height: auto !important;
    min-height: 100% !important;
}
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
section.main,
.main {
    overflow-x: hidden !important;
    overflow-y: visible !important;
    max-width: 100% !important;
    width: 100% !important;
    height: auto !important;
    min-height: 100vh !important;
}
[data-testid="stAppViewContainer"] > section,
[data-testid="stMainBlockContainer"] {
    overflow: visible !important;
    height: auto !important;
}
.block-container [data-testid="stHorizontalBlock"],
.block-container [data-testid="stVerticalBlock"],
.block-container [data-testid="stVerticalBlockBorderWrapper"],
.block-container [data-testid="stFileUploader"] {
    max-width: 100% !important;
    box-sizing: border-box !important;
}
.block-container [data-testid="stHorizontalBlock"] {
    margin-left: 0 !important;
    margin-right: 0 !important;
}
.block-container [data-testid="stElementContainer"] {
    max-width: 100% !important;
    min-width: 0 !important;
}

/* Wordmark + logo — icono ancho encima del texto */
.omni-wordmark {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.45rem;
    font-family: var(--font);
    line-height: 1;
    min-width: 0;
    max-width: 100%;
    overflow: visible;
}
.omni-wordmark-text {
    color: var(--text);
    font-size: 2.25rem;
    font-weight: var(--weight-bold);
    letter-spacing: var(--tracking-tight);
    margin-left: 0;
}
.omni-logo {
    width: 12rem;
    height: auto;
    max-width: min(100%, 12rem);
    min-width: 9rem;
    flex-shrink: 0;
    display: block;
    border-radius: 0;
}

/* Panel omnitest — misma estética que el dropzone de archivos */
.omni-panel,
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--omni-panel-bg) !important;
    border: var(--omni-panel-border) !important;
    border-radius: var(--radius-lg) !important;
    box-shadow: var(--omni-panel-inset) !important;
    transition: border-color 0.2s var(--ease), background 0.2s var(--ease),
                box-shadow 0.25s var(--ease) !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: var(--omni-panel-hover-border) !important;
    background: var(--omni-panel-bg) !important;
    box-shadow: var(--shadow-sm) !important;
}
[data-testid="stVerticalBlockBorderWrapper"] {
    padding: 0.65rem 1.35rem 1.35rem !important;
    margin: 0 !important;
}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stFileUploader"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    margin-top: 0 !important;
    padding-top: 1.25rem !important;
}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stFileUploader"]:hover {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
.dropzone-blocked {
    text-align: center;
    padding: 2rem 1rem 1.5rem;
    margin-top: 0.25rem;
}

/* Dropzone RemNote — Streamlit 1.58: la caja gris es stFileUploaderDropzone por dentro */
[data-testid="stFileUploader"] {
    background: var(--omni-panel-bg) !important;
    border: var(--omni-panel-border) !important;
    border-radius: var(--radius-lg) !important;
    box-shadow: var(--omni-panel-inset) !important;
    transition: border-color 0.2s var(--ease), background 0.2s var(--ease),
                box-shadow 0.25s var(--ease) !important;
    padding: 2rem 1.5rem 1.35rem !important;
    margin: 0.5rem 0 0 !important;
    min-height: 176px !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    align-items: center !important;
    text-align: center !important;
    gap: 0 !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--omni-panel-hover-border) !important;
    background: var(--highlight-soft) !important;
    box-shadow: var(--shadow-sm) !important;
}
[data-testid="stFileUploader"]::before {
    content: "";
    display: block;
    width: 132px;
    height: 40px;
    margin: 0 auto 1rem;
    background: center / contain no-repeat url("{{UPLOAD_ICONS}}");
}
[data-testid="stFileUploader"]::after {
    content: "PDF · JPG · PNG · WEBP · DOCX";
    display: block;
    margin-top: 0.85rem;
    font-size: var(--text-xs);
    color: var(--muted);
    letter-spacing: var(--tracking-body);
}
[data-testid="stFileUploader"] [data-testid="stWidgetLabel"],
[data-testid="stFileUploader"] > label {
    display: none !important;
}
[data-testid="stFileUploaderDropzone"] {
    width: 100% !important;
    min-height: 0 !important;
    height: auto !important;
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: wrap !important;
    justify-content: center !important;
    align-items: center !important;
    gap: 0.55rem !important;
    padding: 0 !important;
    margin: 0 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    cursor: pointer !important;
}
[data-testid="stFileUploaderDropzone"]::before {
    content: "Suelta tus archivos aquí o";
    font-family: var(--font);
    font-size: var(--text-base);
    font-weight: var(--weight-normal);
    color: var(--text);
    letter-spacing: var(--tracking-body);
    line-height: 1.35;
}
[data-testid="stFileUploaderDropzoneInstructions"],
[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] {
    display: none !important;
}
[data-testid="stFileUploaderDropzone"] > svg,
[data-testid="stFileUploaderDropzone"] [data-testid="stIconMaterial"],
[data-testid="stFileUploaderDropzone"] button svg {
    display: none !important;
}
[data-testid="stFileUploaderDropzone"] button *,
[data-testid="stFileUploaderDropzone"] [data-baseweb="button"] * {
    display: none !important;
}
[data-testid="stFileUploaderDropzone"] button,
[data-testid="stFileUploaderDropzone"] [data-baseweb="button"] {
    background: var(--accent) !important;
    color: transparent !important;
    border: none !important;
    border-radius: var(--btn-radius) !important;
    font-family: var(--font) !important;
    font-size: 0 !important;
    font-weight: var(--btn-weight) !important;
    min-height: var(--btn-height) !important;
    min-width: 9.5rem !important;
    padding: 0.5rem 1.15rem !important;
    margin: 0 !important;
    box-shadow: 0 2px 10px var(--accent-glow) !important;
    flex-shrink: 0 !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: background 0.2s var(--ease), box-shadow 0.25s var(--ease) !important;
}
[data-testid="stFileUploaderDropzone"] button:hover,
[data-testid="stFileUploaderDropzone"] [data-baseweb="button"]:hover {
    background: var(--accent-hover) !important;
    box-shadow: var(--btn-hover-glow) !important;
}
[data-testid="stFileUploaderDropzone"] button::after,
[data-testid="stFileUploaderDropzone"] [data-baseweb="button"]::after {
    content: "Seleccionar archivo";
    display: block;
    font-family: var(--font);
    font-size: var(--btn-font);
    font-weight: var(--btn-weight);
    color: #FFFFFF;
    letter-spacing: var(--btn-tracking);
    line-height: 1.35;
}
[data-testid="stFileUploader"] small {
    display: none !important;
}
[data-testid="stFileUploader"] [data-testid="stFileUploaderDeleteBtn"] {
    margin-top: 0.75rem !important;
}

.rn-or-divider {
    text-align: center;
    color: var(--muted);
    font-size: var(--text-sm);
    font-weight: var(--weight-normal);
    margin: 1.35rem 0 1rem;
    line-height: 1;
}

.rn-paste-hint-only {
    font-size: var(--text-sm);
    color: var(--muted);
    letter-spacing: var(--tracking-body);
    margin: 0 0 0.55rem;
    padding: 0 0.15rem;
}
.rn-paste-hint-only + div [data-testid="stTextArea"] textarea,
.rn-paste-hint-only + div [data-testid="stTextArea"] div[data-baseweb="textarea"],
[data-testid="stVerticalBlockBorderWrapper"] div:has(.rn-paste-hint-only) + div [data-testid="stTextArea"] textarea,
[data-testid="stVerticalBlockBorderWrapper"] div:has(.rn-paste-hint-only) + div [data-testid="stTextArea"] div[data-baseweb="textarea"] {
    border-radius: var(--radius-lg) !important;
    min-height: 52px !important;
    padding: 0.9rem 1.2rem !important;
    border: 1px solid var(--input-border) !important;
    box-shadow: var(--shadow-sm) !important;
}
.rn-paste-hint-only + div [data-testid="stTextArea"] textarea:focus,
.rn-paste-hint-only + div [data-testid="stTextArea"] div[data-baseweb="textarea"]:focus-within,
[data-testid="stVerticalBlockBorderWrapper"] div:has(.rn-paste-hint-only) + div [data-testid="stTextArea"] textarea:focus,
[data-testid="stVerticalBlockBorderWrapper"] div:has(.rn-paste-hint-only) + div [data-testid="stTextArea"] div[data-baseweb="textarea"]:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow-soft) !important;
}

[data-testid="stVerticalBlockBorderWrapper"]:hover,
[data-testid="stFileUploader"]:hover {
    border-color: var(--omni-panel-hover-border) !important;
    background: var(--highlight-soft) !important;
    box-shadow: var(--shadow-sm) !important;
}

.omni-hero-gap {
    display: block;
    height: 6rem;
    width: 100%;
    margin: 0;
    padding: 0;
    flex-shrink: 0;
}
.omni-h1 {
    font-family: var(--font);
    font-size: 1.875rem;
    font-weight: var(--weight-bold);
    letter-spacing: var(--tracking-tight);
    color: var(--text);
    margin: 0 0 0.75rem 0 !important;
    line-height: 1.25;
}
.omni-accent {
    background: linear-gradient(135deg, var(--highlight) 0%, var(--accent) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.omni-lead {
    font-family: var(--font);
    color: var(--muted);
    font-size: var(--text-base);
    font-weight: var(--weight-normal);
    letter-spacing: var(--tracking-body);
    line-height: 1.65;
    margin-bottom: 0;
    max-width: 640px;
}

/* Separadores y selector de fuente */
.omni-separator {
    height: 0;
    margin: 2.25rem 0 1.5rem;
}
.omni-separator--light {
    height: 0;
    margin: 1.25rem 0 1.15rem;
}

.omni-faq-marker { display: none; }
.omni-faq-spacer {
    display: block;
    height: 0;
    margin: 5rem 0 0;
    border: none;
    border-top: 1px solid var(--border);
    opacity: 0.35;
}
.omni-faq-title {
    text-align: center;
    font-size: 0.9375rem;
    font-weight: var(--weight-semibold);
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--muted);
    margin: 2.25rem 0 1.5rem;
    opacity: 0.72;
}
.block-container:has(.omni-faq-marker) {
    max-width: 680px;
    margin-left: auto !important;
    margin-right: auto !important;
    padding-bottom: 3.5rem;
}
.block-container:has(.omni-faq-marker) [data-testid="stExpander"] {
    border: 1px solid var(--border-strong) !important;
    border-radius: var(--radius) !important;
    background: var(--surface) !important;
    box-shadow: none !important;
    outline: none !important;
    margin-bottom: 0.75rem !important;
    overflow: hidden !important;
    transition: border-color 0.2s var(--ease) !important;
}
.block-container:has(.omni-faq-marker) [data-testid="stExpander"]:hover {
    border-color: var(--omni-panel-hover-border) !important;
    box-shadow: none !important;
}
.block-container:has(.omni-faq-marker) [data-testid="stExpander"] > div,
.block-container:has(.omni-faq-marker) [data-testid="stExpander"] > div > div,
.block-container:has(.omni-faq-marker) [data-testid="stExpanderDetails"] {
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
    background: transparent !important;
}
.block-container:has(.omni-faq-marker) [data-testid="stExpander"] > div > div:first-child {
    display: flex !important;
    align-items: center !important;
    gap: 0.55rem !important;
    padding: 1rem 1.15rem !important;
    min-height: 3.25rem;
    opacity: 1;
    background: transparent !important;
    border-bottom: none !important;
}
.block-container:has(.omni-faq-marker) [data-testid="stExpander"] > div > div:first-child [data-testid="stMarkdownContainer"],
.block-container:has(.omni-faq-marker) [data-testid="stExpander"] > div > div:first-child [data-testid="stMarkdownContainer"] p,
.block-container:has(.omni-faq-marker) [data-testid="stExpander"] > div > div:first-child [data-testid="stMarkdownContainer"] span,
.block-container:has(.omni-faq-marker) [data-testid="stExpander"] > div > div:first-child p,
.block-container:has(.omni-faq-marker) [data-testid="stExpander"] > div > div:first-child span {
    font-family: var(--font) !important;
    font-weight: var(--weight-semibold) !important;
    font-size: var(--text-sm) !important;
    letter-spacing: var(--tracking-ui) !important;
    color: var(--text) !important;
    -webkit-text-fill-color: var(--text) !important;
    flex: 1 1 auto !important;
    min-width: 0 !important;
}
.block-container:has(.omni-faq-marker) [data-testid="stExpander"] > div > div:first-child svg,
.block-container:has(.omni-faq-marker) [data-testid="stExpander"] > div > div:first-child [data-testid="stIconMaterial"] {
    font-family: "Material Symbols Rounded", "Material Icons" !important;
    flex-shrink: 0 !important;
    width: 1rem !important;
    height: 1rem !important;
    font-size: 1.125rem !important;
    line-height: 1 !important;
    opacity: 0.45 !important;
    color: var(--muted) !important;
    -webkit-text-fill-color: var(--muted) !important;
}
.block-container:has(.omni-faq-marker) [data-testid="stExpanderDetails"] {
    padding: 0 1.4rem 1.4rem !important;
    background: transparent !important;
}
.block-container:has(.omni-faq-marker) [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p,
.block-container:has(.omni-faq-marker) [data-testid="stExpander"] [data-testid="stMarkdownContainer"] li,
.block-container:has(.omni-faq-marker) [data-testid="stExpander"] [data-testid="stMarkdownContainer"] td {
    color: var(--muted) !important;
    font-size: 0.875rem !important;
    line-height: 1.65 !important;
}
.block-container:has(.omni-faq-marker) [data-testid="stExpander"] [data-testid="stMarkdownContainer"] strong {
    color: var(--text) !important;
    font-weight: 600 !important;
}

.source-label {
    font-size: var(--text-sm);
    font-weight: var(--weight-semibold);
    letter-spacing: var(--tracking-ui);
    color: var(--text);
    margin: 0 0 0.65rem;
}

/* Panel de entrada — títulos internos */
.dropzone-label {
    font-size: var(--text-sm);
    font-weight: var(--weight-semibold);
    letter-spacing: var(--tracking-ui);
    color: var(--text);
    margin: 0.75rem 0 0.35rem;
}

.dropzone-blocked p { color: var(--muted); margin: 0.5rem 0 1rem; }
.dropzone-blocked p strong { color: var(--text); }

/* Selector Fuente — ver inject_button_fixes() al final del render */

/* Inputs — textareas en toda la app (Daypo, IA, etc.) */
.block-container [data-testid="stTextArea"] textarea,
.block-container [data-testid="stTextArea"] div[data-baseweb="textarea"],
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stTextArea"] textarea,
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stTextArea"] div[data-baseweb="textarea"] {
    background-color: var(--input-bg) !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
    font-size: var(--text-base) !important;
    letter-spacing: var(--tracking-body) !important;
    line-height: 1.5 !important;
    border: 1px solid var(--input-border) !important;
    border-radius: var(--radius) !important;
    transition: border-color 0.2s var(--ease), box-shadow 0.2s var(--ease) !important;
}
.block-container [data-testid="stTextArea"] textarea:focus,
.block-container [data-testid="stTextArea"] div[data-baseweb="textarea"]:focus-within,
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stTextArea"] textarea:focus,
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stTextArea"] div[data-baseweb="textarea"]:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow-soft) !important;
}

/* Botones primarios — Convertir, Configurar APIs */
.block-container div.stButton > button[kind="primary"],
.block-container div.stButton > button[data-testid="stBaseButton-primary"],
[data-testid="stVerticalBlockBorderWrapper"] div.stButton > button[kind="primary"],
[data-testid="stVerticalBlockBorderWrapper"] div.stButton > button[data-testid="stBaseButton-primary"] {
    font-family: var(--font) !important;
    font-size: var(--btn-font) !important;
    font-weight: var(--btn-weight) !important;
    letter-spacing: var(--btn-tracking) !important;
    line-height: 1.35 !important;
    min-height: var(--btn-height) !important;
    border-radius: var(--btn-radius) !important;
    background: var(--accent) !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 2px 12px var(--accent-glow) !important;
    transition: background 0.2s var(--ease), box-shadow 0.25s var(--ease) !important;
}
.block-container div.stButton > button[kind="primary"]:hover:not(:disabled),
.block-container div.stButton > button[data-testid="stBaseButton-primary"]:hover:not(:disabled),
[data-testid="stVerticalBlockBorderWrapper"] div.stButton > button[kind="primary"]:hover:not(:disabled),
[data-testid="stVerticalBlockBorderWrapper"] div.stButton > button[data-testid="stBaseButton-primary"]:hover:not(:disabled) {
    background: var(--accent-hover) !important;
    box-shadow: var(--btn-hover-glow) !important;
}
.block-container div.stButton > button[kind="primary"]:disabled {
    opacity: 0.45 !important;
    box-shadow: none !important;
}
.block-container div.stButton > button[kind="primary"] *,
.block-container div.stButton > button[data-testid="stBaseButton-primary"] *,
[data-testid="stVerticalBlockBorderWrapper"] div.stButton > button[kind="primary"] *,
[data-testid="stVerticalBlockBorderWrapper"] div.stButton > button[data-testid="stBaseButton-primary"] * {
    font-family: inherit !important;
    font-size: inherit !important;
    font-weight: inherit !important;
    letter-spacing: inherit !important;
    color: #FFFFFF !important;
}

/* Botones genéricos */
div.stButton > button,
div.stDownloadButton > button,
div.stButton [data-baseweb="button"],
div.stDownloadButton [data-baseweb="button"] {
    font-family: var(--font) !important;
    font-size: var(--btn-font) !important;
    font-weight: var(--btn-weight) !important;
    letter-spacing: var(--btn-tracking) !important;
    line-height: 1.35 !important;
    min-height: var(--btn-height) !important;
    padding: 0.6rem 1.15rem !important;
    border-radius: var(--btn-radius) !important;
    transition: background 0.2s var(--ease), border-color 0.2s var(--ease),
                box-shadow 0.25s var(--ease) !important;
}
div.stButton [data-baseweb="button"] > div,
div.stButton [data-baseweb="button"] span,
div.stButton [data-baseweb="button"] p,
div.stDownloadButton [data-baseweb="button"] > div,
div.stDownloadButton [data-baseweb="button"] span,
div.stDownloadButton [data-baseweb="button"] p {
    font-family: inherit !important;
    font-size: inherit !important;
    font-weight: inherit !important;
    letter-spacing: inherit !important;
}

div.stButton > button[kind="primary"],
div.stButton > button[data-testid="stBaseButton-primary"],
div.stButton:has(> button[kind="primary"]) [data-baseweb="button"],
div.stButton:has(> button[data-testid="stBaseButton-primary"]) [data-baseweb="button"] {
    font-size: var(--btn-font) !important;
    min-height: var(--btn-height) !important;
    padding: 0.6rem 1.15rem !important;
}

div.stButton > button[kind="primary"],
div.stButton > button[data-testid="stBaseButton-primary"] {
    background: var(--accent) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: var(--btn-radius) !important;
    font-weight: var(--btn-weight) !important;
    box-shadow: 0 2px 12px var(--accent-glow) !important;
}
div.stButton > button[kind="primary"]:hover,
div.stButton > button[data-testid="stBaseButton-primary"]:hover,
div.stDownloadButton > button:hover,
div.stDownloadButton [data-baseweb="button"]:hover {
    box-shadow: var(--btn-hover-glow) !important;
}
div.stButton > button[kind="primary"]:hover,
div.stButton > button[data-testid="stBaseButton-primary"]:hover {
    background: var(--accent-hover) !important;
}
div.stButton > button[kind="secondary"]:hover,
div.stDownloadButton > button:hover {
    border-color: var(--accent) !important;
}

/* Solo la pista de la barra — el label también es div > div y no debe medir 4px */
.stProgress > div:first-child > div,
.stProgress > div:first-child [data-testid="stMarkdownContainer"],
.stProgress > div:first-child [data-testid="stMarkdownContainer"] > div {
    height: auto !important;
    max-height: none !important;
    overflow: visible !important;
    background: transparent !important;
}
.stProgress > div:last-child {
    height: auto !important;
    overflow: visible !important;
    background: transparent !important;
}
.stProgress [data-testid="stProgressBarTrack"] {
    background: var(--surface-2) !important;
    border: none !important;
    border-radius: 999px !important;
    overflow: hidden !important;
    height: 4px !important;
}
.stProgress [data-testid="stProgressBarTrack"] > div {
    background: var(--accent) !important;
    height: 100% !important;
    border-radius: 999px !important;
}
.stProgress {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0.75rem 0 0.35rem !important;
    overflow: visible !important;
    position: relative !important;
    z-index: 5 !important;
}
.stProgress > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    overflow: visible !important;
}
.stProgress > div:first-child {
    position: relative !important;
    z-index: 6 !important;
    overflow: visible !important;
    min-height: 1.3rem !important;
    margin-bottom: 0.35rem !important;
    padding-bottom: 0.15rem !important;
    background: var(--bg) !important;
}
.stProgress label[data-testid="stProgressLabel"],
.stProgress [data-testid="stProgressLabel"],
.stProgress [data-testid="stProgressLabel"] > div,
.stProgress [data-testid="stProgressLabel"] p,
.stProgress > div:first-child,
.stProgress > div:first-child [data-testid="stMarkdownContainer"],
.stProgress > div:first-child [data-testid="stMarkdownContainer"] p,
.stProgress > div:first-child [data-testid="stMarkdownContainer"] span,
.stProgress > div:first-child p,
.stProgress > div:first-child span,
.stProgress [data-testid="stMarkdownContainer"] p,
.stProgress p {
    font-family: var(--font) !important;
    font-size: var(--text-sm) !important;
    font-weight: var(--weight-medium) !important;
    letter-spacing: var(--tracking-ui) !important;
    color: var(--text) !important;
    -webkit-text-fill-color: var(--text) !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 0 0.4rem 0 !important;
    margin: 0 !important;
    opacity: 1 !important;
    visibility: visible !important;
    line-height: 1.45 !important;
    min-height: auto !important;
}
[data-testid="stElementContainer"]:has(.stProgress),
[data-testid="stElementContainer"]:has([data-testid="stProgress"]) {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0.85rem 0 0.15rem !important;
    margin-top: 0.35rem !important;
    overflow: visible !important;
    position: relative !important;
    z-index: 5 !important;
}
.block-container .st-key-btn_convertir {
    margin-bottom: 0.15rem !important;
}

/* st.status / st.expander — ver inject_button_fixes() (Streamlit 1.58 → stExpander) */

/* Panel de trabajo — HTML propio (sin st.container / st.status) */
.omni-worklog-panel {
    margin-top: 0.65rem;
    padding: 0.85rem 1.15rem 1rem;
    background-color: var(--surface) !important;
    background-image: none !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    box-shadow: var(--shadow-sm) !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
}
.omni-worklog-header {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    margin: 0 0 0.35rem;
    padding: 0.1rem 0;
    background: transparent !important;
    color: var(--text) !important;
}
.omni-worklog-title {
    font-family: var(--font) !important;
    font-size: var(--text-sm);
    font-weight: var(--weight-semibold);
    color: var(--text) !important;
    -webkit-text-fill-color: var(--text) !important;
    letter-spacing: var(--tracking-ui);
}
.omni-worklog-body {
    margin: 0.25rem 0 0.35rem;
}
.omni-worklog-line {
    margin: 0.2rem 0;
    font-family: var(--font) !important;
    font-size: var(--text-sm);
    font-weight: var(--weight-normal);
    letter-spacing: var(--tracking-body);
    color: var(--text) !important;
    line-height: 1.45;
}
.omni-worklog-foot {
    margin: 0.35rem 0 0;
    font-family: var(--font) !important;
    font-size: var(--text-xs);
    font-weight: var(--weight-normal);
    letter-spacing: var(--tracking-body);
    color: var(--muted) !important;
    line-height: 1.45;
}
.omni-worklog-spinner {
    display: inline-block;
    width: 1rem;
    height: 1rem;
    flex-shrink: 0;
    border: 2px solid var(--border-strong);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: omni-worklog-spin 0.75s linear infinite;
}
@keyframes omni-worklog-spin {
    to { transform: rotate(360deg); }
}
.omni-worklog-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 1rem;
    height: 1rem;
    flex-shrink: 0;
    font-size: 0.75rem;
    font-weight: 700;
    border-radius: 999px;
}
.omni-worklog-icon--ok {
    color: #16A34A;
    background: rgba(34, 197, 94, 0.15);
}
.omni-worklog-icon--err {
    color: var(--error);
    background: rgba(220, 38, 38, 0.12);
}

.model-badge {
    font-size: 0.75rem;
    color: var(--muted);
}

.preview-scroll {
    max-height: 440px;
    overflow-y: auto;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem;
    background: var(--surface-2);
    transition: border-color 0.2s var(--ease), box-shadow 0.2s var(--ease);
}
.preview-scroll:hover {
    border-color: var(--border-strong);
    box-shadow: var(--shadow-sm);
}
.preview-q {
    margin-bottom: 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border);
    color: var(--text);
}
.preview-q:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
.preview-wrong { color: var(--muted); font-size: 0.8125rem; }
.preview-ok { color: var(--accent); font-size: 0.8125rem; }
.preview-img {
    display: block;
    max-width: min(100%, 320px);
    max-height: 200px;
    margin-top: 0.45rem;
    border-radius: 6px;
}

.export-grid {
    margin-top: 0.5rem;
}
.export-grid [data-testid="column"] {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}
.export-card {
    border: 1px solid var(--border);
    border-radius: var(--btn-radius);
    padding: 0.875rem 1rem;
    background: var(--surface);
    flex: 1;
    box-shadow: var(--shadow-sm);
    transition: border-color 0.2s var(--ease), box-shadow 0.25s var(--ease) !important;
}
.export-card:hover {
    border-color: rgba(88, 101, 242, 0.35);
    box-shadow: var(--btn-hover-glow) !important;
}
.export-card-header {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    margin-bottom: 0.35rem;
}
.export-icon {
    width: 40px;
    height: 40px;
    border-radius: 9px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: box-shadow 0.25s var(--ease) !important;
}
.export-card:hover .export-icon {
    box-shadow: 0 0 16px var(--accent-glow-soft);
}
.export-icon--quiz   { background: #EEF2FF; color: #4F46E5; }
.export-icon--anki   { background: #DBEAFE; color: #2563EB; }
.export-icon--remnote { background: #E0E7FF; color: #4338CA; }
.export-icon--word   { background: #DBEAFE; color: #1D4ED8; }
.export-icon--pdf    { background: #FEE2E2; color: #DC2626; }
.export-icon--images { background: #D1FAE5; color: #059669; }
.export-card h4 {
    margin: 0;
    font-size: 0.9375rem;
    font-weight: 600;
    color: var(--text);
    line-height: 1.25;
}
.export-card p {
    margin: 0;
    font-size: 0.8125rem;
    color: var(--muted);
    line-height: 1.45;
    min-height: 2.35rem;
}
.export-grid [data-testid="column"] .stDownloadButton button,
.export-grid [data-testid="column"] button[kind="secondary"] {
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: var(--btn-radius) !important;
    font-family: var(--font) !important;
    font-weight: var(--btn-weight) !important;
    font-size: var(--btn-font) !important;
    letter-spacing: var(--btn-tracking) !important;
    min-height: var(--btn-height) !important;
    box-shadow: none !important;
}
.export-grid [data-testid="column"] .stDownloadButton button:hover,
.export-grid [data-testid="column"] button[kind="secondary"]:hover {
    background: var(--surface-2) !important;
    border-color: var(--accent) !important;
    color: var(--text) !important;
    box-shadow: var(--btn-hover-glow) !important;
}
[data-testid="stSelectbox"] {
    margin: 0.15rem 0 0.35rem !important;
}
[data-testid="stSelectbox"] label {
    display: none !important;
}
[data-testid="stSelectbox"] div[data-baseweb="select"],
[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
[data-testid="stSelectbox"] div[data-baseweb="select"] div[role="combobox"],
[data-testid="stSelectbox"] div[data-baseweb="select"] > div > div,
[data-testid="stSelectbox"] div[data-baseweb="select"] [data-baseweb="input"],
[data-testid="stSelectbox"] [data-testid="stSelectboxVirtualDropdown"] {
    background: var(--surface) !important;
    background-color: var(--surface) !important;
    background-image: none !important;
    border-color: var(--border-strong) !important;
    color: var(--text) !important;
}
[data-testid="stSelectbox"] div[data-baseweb="select"] span,
[data-testid="stSelectbox"] div[data-baseweb="select"] p,
[data-testid="stSelectbox"] div[data-baseweb="select"] input {
    color: var(--text) !important;
    -webkit-text-fill-color: var(--text) !important;
}
[data-testid="stSelectbox"] div[data-baseweb="select"] div[role="combobox"] > div {
    background: transparent !important;
    background-color: transparent !important;
    color: var(--text) !important;
    -webkit-text-fill-color: var(--text) !important;
}
[data-testid="stSelectbox"] div[data-baseweb="select"] div[role="combobox"] {
    border: 1px solid var(--border-strong) !important;
    border-radius: var(--btn-radius) !important;
    min-height: 2.35rem !important;
    font-family: var(--font) !important;
    font-size: 0.8125rem !important;
}
[data-testid="stSelectbox"] div[data-baseweb="select"] div[role="combobox"]:focus-within,
[data-testid="stSelectbox"] div[data-baseweb="select"] div[role="combobox"][aria-expanded="true"] {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 1px var(--accent-soft) !important;
    background-color: var(--surface) !important;
}
[data-testid="stSelectbox"] svg {
    color: var(--muted) !important;
    fill: var(--muted) !important;
}

.export-format-legend {
    margin: 1.35rem 0 0.5rem;
    padding: 0.85rem 1rem;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background: var(--surface);
    font-size: 0.8125rem;
    color: var(--muted);
    line-height: 1.55;
}
.export-format-legend p {
    margin: 0 0 0.45rem;
    color: var(--text);
    font-weight: var(--weight-semibold);
    font-size: 0.8125rem;
}
.export-format-legend ul {
    margin: 0;
    padding-left: 1.15rem;
}
.export-format-legend li {
    margin: 0.2rem 0;
}
.export-format-legend strong {
    color: var(--text);
    font-weight: var(--weight-semibold);
}

.banner-amber {
    background: rgba(217, 119, 6, 0.12);
    border: 1px solid rgba(217, 119, 6, 0.35);
    border-radius: var(--radius);
    padding: 0.75rem 1rem;
    color: var(--muted);
    font-size: 0.875rem;
    margin-bottom: 1rem;
}

.inline-error { color: var(--error); font-size: 0.8125rem; margin-top: 0.5rem; }

.review-summary {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 0.25rem;
    line-height: 1.35;
    height: auto !important;
    overflow: visible !important;
}
.block-container [data-testid="stMarkdownContainer"] .review-summary,
.block-container p.review-summary {
    height: auto !important;
    max-height: none !important;
    overflow: visible !important;
}

/* Toolbar — ver inject_button_fixes() al final del render */

/* Radios y expanders — etiquetas legibles (Streamlit a veces fuerza blanco) */
[data-testid="stRadio"] [data-testid="stWidgetLabel"] p,
[data-testid="stRadio"] > label > [data-testid="stMarkdownContainer"] p,
[data-testid="stRadio"] label[data-baseweb="radio"] p,
[data-testid="stRadio"] label[data-baseweb="radio"] span,
[data-testid="stRadio"] label[data-baseweb="radio"] [data-testid="stMarkdownContainer"] p,
[data-testid="stRadio"] div[role="radiogroup"] label p,
[data-testid="stRadio"] div[role="radiogroup"] label span {
    color: var(--text) !important;
    -webkit-text-fill-color: var(--text) !important;
}
[data-testid="stRadio"] > label > [data-testid="stMarkdownContainer"] p,
[data-testid="stRadio"] [data-testid="stWidgetLabel"] p {
    color: var(--muted) !important;
    -webkit-text-fill-color: var(--muted) !important;
    font-size: var(--text-sm) !important;
    font-weight: var(--weight-medium) !important;
}
div[data-testid="stRadio"] label {
    transition: color 0.15s var(--ease) !important;
}

.stCaption,
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p {
    color: var(--muted) !important;
    font-family: var(--font) !important;
    font-size: var(--text-sm) !important;
    letter-spacing: var(--tracking-body) !important;
    line-height: 1.45 !important;
}

/* Modal APIs — shell + estética RemNote */
[data-testid="stDialog"],
[data-testid="stDialog"] > div,
[data-testid="stDialog"] section,
div[data-testid="stModal"] > div,
[data-testid="stDialog"] [data-baseweb="modal"],
[data-testid="stDialog"] [data-baseweb="modal"] > div,
[data-testid="stDialog"] [role="dialog"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
[data-testid="stDialog"] [data-testid="stMarkdownContainer"] p,
[data-testid="stDialog"] [data-testid="stMarkdownContainer"] span,
[data-testid="stDialog"] label,
[data-testid="stDialog"] h1,
[data-testid="stDialog"] h2,
[data-testid="stDialog"] h3 {
    color: var(--text) !important;
}
[data-testid="stDialog"] [data-testid="stCaptionContainer"],
[data-testid="stDialog"] [data-testid="stCaptionContainer"] p,
[data-testid="stDialog"] .stCaption {
    color: var(--muted) !important;
}
[data-testid="stDialog"] [data-testid="stAlert"],
[data-testid="stDialog"] [data-baseweb="notification"] {
    background: var(--surface-2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border-strong) !important;
}
[data-testid="stDialog"] div.stLinkButton > a,
[data-testid="stDialog"] a[data-testid="stBaseLinkButton-secondary"] {
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: var(--btn-radius) !important;
}
[data-testid="stDialog"] [data-testid="stToggle"] label span,
[data-testid="stDialog"] [data-testid="stCheckbox"] [data-testid="stWidgetLabel"] p,
[data-testid="stDialog"] [data-testid="stCheckbox"] label [data-testid="stMarkdownContainer"] p {
    color: var(--text) !important;
}

/* Modal — toggles (st.toggle → data-testid stCheckbox) */
[data-testid="stDialog"] [data-testid="stCheckbox"] label[data-baseweb="checkbox"]:not(:has(input:checked)) > :first-child:not(input):not([data-testid="stWidgetLabel"]) {
    background-color: var(--toggle-track-border) !important;
    border: 1px solid var(--border-strong) !important;
    box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.04) !important;
}
[data-testid="stDialog"] [data-testid="stCheckbox"] label[data-baseweb="checkbox"] > :first-child:not(input):not([data-testid="stWidgetLabel"]) > div {
    background-color: var(--surface) !important;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.12) !important;
}
[data-testid="stDialog"] [data-testid="stCheckbox"] label[data-baseweb="checkbox"]:has(input:checked) > :first-child:not(input):not([data-testid="stWidgetLabel"]) {
    background: var(--switch-on) !important;
    background-color: var(--switch-on) !important;
    border-color: var(--switch-on-border) !important;
}
[data-testid="stDialog"] [data-testid="stCheckbox"] label[data-baseweb="checkbox"]:has(input:checked) > :first-child:not(input):not([data-testid="stWidgetLabel"]) > div {
    background-color: #FFFFFF !important;
}
[data-testid="stDialog"] [data-testid="stCheckbox"] label[data-baseweb="checkbox"] > [data-testid="stWidgetLabel"],
[data-testid="stDialog"] [data-testid="stCheckbox"] label[data-baseweb="checkbox"] > :not(:first-child):not(input) {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
[data-testid="stDialog"] [data-testid="stTextInput"] [data-testid="stTextInputRootElement"] {
    display: flex !important;
    align-items: stretch !important;
    background: var(--input-bg) !important;
    background-color: var(--input-bg) !important;
    background-image: none !important;
    border: 1px solid var(--input-border) !important;
    border-radius: var(--radius) !important;
    box-shadow: none !important;
    overflow: hidden !important;
    padding: 0 !important;
}
[data-testid="stDialog"] [data-testid="stTextInput"] [data-testid="stTextInputRootElement"] > div[data-baseweb="base-input"],
[data-testid="stDialog"] [data-testid="stTextInput"] [data-testid="stTextInputRootElement"] > div {
    display: flex !important;
    flex: 1 1 auto !important;
    flex-direction: row !important;
    align-items: center !important;
    width: 100% !important;
    min-width: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
}
[data-testid="stDialog"] [data-testid="stTextInput"] [data-testid="stTextInputRootElement"] input {
    flex: 1 1 auto !important;
    min-width: 0 !important;
    width: 100% !important;
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    font-family: var(--font) !important;
    font-size: var(--text-sm) !important;
    color: var(--text) !important;
    -webkit-text-fill-color: var(--text) !important;
    min-height: 2.625rem !important;
    height: auto !important;
    box-shadow: none !important;
    padding-left: 0.85rem !important;
    padding-right: 0.35rem !important;
}
[data-testid="stDialog"] [data-testid="stTextInput"] [data-testid="stTextInputRootElement"] button[type="button"] {
    flex: 0 0 2.75rem !important;
    width: 2.75rem !important;
    min-width: 2.75rem !important;
    height: auto !important;
    align-self: stretch !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin: 0 !important;
    padding: 0 !important;
    background: transparent !important;
    border: none !important;
    border-left: 1px solid var(--input-border) !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    cursor: pointer !important;
    color: var(--muted) !important;
    order: 99 !important;
}
[data-testid="stDialog"] [data-testid="stTextInput"] [data-testid="stTextInputRootElement"] button[type="button"] svg {
    width: 1.125rem !important;
    height: 1.125rem !important;
    flex-shrink: 0 !important;
    display: block !important;
}
[data-testid="stDialog"] [data-testid="stTextInput"] [data-testid="stIconMaterial"],
[data-testid="stDialog"] [data-testid="stTextInput"] button [data-testid="stIconMaterial"],
[data-testid="stDialog"] [data-testid="stTextInput"] button span {
    font-family: "Material Symbols Rounded", "Material Icons" !important;
    color: var(--muted) !important;
    -webkit-text-fill-color: var(--muted) !important;
}
[data-testid="stDialog"] [data-testid="stTextInput"] [data-testid="stTextInputRootElement"]:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow-soft) !important;
}

/* Importar JSON — botón ghost compacto (distinto del dropzone IA) */
[data-testid="stDialog"] [data-testid="stFileUploader"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    min-height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
}
[data-testid="stDialog"] [data-testid="stFileUploader"]:hover {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
[data-testid="stDialog"] [data-testid="stFileUploader"]::before,
[data-testid="stDialog"] [data-testid="stFileUploader"]::after {
    display: none !important;
}
[data-testid="stDialog"] [data-testid="stFileUploaderDropzone"] {
    flex-direction: row !important;
    justify-content: stretch !important;
    padding: 0 !important;
    min-height: 0 !important;
    width: 100% !important;
    background: transparent !important;
    border: none !important;
    cursor: pointer !important;
}
[data-testid="stDialog"] [data-testid="stFileUploaderDropzone"]::before,
[data-testid="stDialog"] [data-testid="stFileUploaderDropzoneInstructions"] {
    display: none !important;
}
[data-testid="stDialog"] [data-testid="stFileUploaderDropzone"] > svg,
[data-testid="stDialog"] [data-testid="stFileUploaderDropzone"] button svg {
    display: none !important;
}
[data-testid="stDialog"] [data-testid="stFileUploaderDropzone"] button *,
[data-testid="stDialog"] [data-testid="stFileUploaderDropzone"] [data-baseweb="button"] * {
    display: none !important;
}
[data-testid="stDialog"] [data-testid="stFileUploaderDropzone"] button,
[data-testid="stDialog"] [data-testid="stFileUploaderDropzone"] [data-baseweb="button"] {
    background: var(--surface) !important;
    color: transparent !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: var(--radius) !important;
    font-size: 0 !important;
    min-height: var(--btn-height) !important;
    width: 100% !important;
    padding: 0.5rem 1rem !important;
    margin: 0 !important;
    box-shadow: none !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 0.5rem !important;
    transition: background 0.2s var(--ease), border-color 0.2s var(--ease) !important;
}
[data-testid="stDialog"] [data-testid="stFileUploaderDropzone"] button:hover,
[data-testid="stDialog"] [data-testid="stFileUploaderDropzone"] [data-baseweb="button"]:hover {
    background: var(--highlight-soft) !important;
    border-color: var(--accent) !important;
    box-shadow: none !important;
}
[data-testid="stDialog"] [data-testid="stFileUploaderDropzone"] button::before,
[data-testid="stDialog"] [data-testid="stFileUploaderDropzone"] [data-baseweb="button"]::before {
    content: "";
    display: inline-block;
    width: 16px;
    height: 16px;
    flex-shrink: 0;
    background: center / contain no-repeat url("{{UPLOAD_GHOST_ICON}}");
}
[data-testid="stDialog"] [data-testid="stFileUploaderDropzone"] button::after,
[data-testid="stDialog"] [data-testid="stFileUploaderDropzone"] [data-baseweb="button"]::after {
    content: "Importar JSON";
    display: inline;
    font-family: var(--font);
    font-size: var(--btn-font);
    font-weight: var(--btn-weight);
    color: var(--text);
    letter-spacing: var(--btn-tracking);
    line-height: 1.35;
}
[data-testid="stDialog"] [data-testid="stFileUploader"] small {
    display: none !important;
}

[data-testid="stDialog"] div.stDownloadButton > button,
[data-testid="stDialog"] div.stButton > button[kind="secondary"],
[data-testid="stDialog"] div.stButton > button[data-testid="stBaseButton-secondary"] {
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border-strong) !important;
    font-weight: var(--btn-weight) !important;
    box-shadow: none !important;
}
[data-testid="stDialog"] div.stDownloadButton > button:hover,
[data-testid="stDialog"] div.stButton > button[kind="secondary"]:hover,
[data-testid="stDialog"] div.stButton > button[data-testid="stBaseButton-secondary"]:hover {
    background: var(--highlight-soft) !important;
    border-color: var(--accent) !important;
    box-shadow: none !important;
}
[data-testid="stDialog"] div.stButton > button[kind="primary"],
[data-testid="stDialog"] div.stButton > button[data-testid="stBaseButton-primary"] {
    background: var(--accent) !important;
    color: #FFFFFF !important;
    border: none !important;
    font-weight: var(--btn-weight) !important;
    box-shadow: 0 2px 8px var(--accent-glow-soft) !important;
}
[data-testid="stDialog"] div.stButton > button[kind="primary"]:hover,
[data-testid="stDialog"] div.stButton > button[data-testid="stBaseButton-primary"]:hover {
    background: var(--accent-hover) !important;
    box-shadow: var(--btn-hover-glow) !important;
}
[data-testid="stDialog"] div.stButton > button[kind="primary"] *,
[data-testid="stDialog"] div.stButton > button[data-testid="stBaseButton-primary"] * {
    color: #FFFFFF !important;
}
[data-testid="stDialog"] hr,
[data-testid="stDialog"] [data-testid="stDivider"] {
    border-color: var(--border) !important;
}

/* Modal — panel JSON / instrucciones */
[data-testid="stDialog"] .modal-intro {
    color: var(--muted);
    font-size: 0.9375rem;
    line-height: 1.55;
    margin: 0 0 1.25rem;
}
[data-testid="stDialog"] .modal-json-panel {
    background: var(--surface);
    border: 1px solid var(--border-strong);
    border-radius: 12px;
    padding: 1.35rem 1.4rem 1.5rem;
    margin-bottom: 1.75rem;
    box-shadow: var(--shadow-sm);
}
[data-testid="stDialog"] .modal-json-eyebrow {
    font-size: 0.6875rem;
    font-weight: var(--weight-semibold);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--accent);
    margin: 0 0 0.35rem;
    opacity: 0.9;
}
[data-testid="stDialog"] .modal-json-title {
    font-size: 1.0625rem;
    font-weight: 600;
    color: var(--text);
    margin: 0 0 0.75rem;
    line-height: 1.3;
}
[data-testid="stDialog"] .modal-json-lead {
    color: var(--muted);
    font-size: 0.875rem;
    line-height: 1.6;
    margin: 0 0 1.25rem;
    padding-bottom: 1.15rem;
    border-bottom: 1px solid var(--border);
}
[data-testid="stDialog"] .modal-json-lead code {
    font-size: 0.8125rem;
    padding: 0.1rem 0.35rem;
    border-radius: 4px;
    background: var(--surface-2);
    border: 1px solid var(--border);
    color: var(--text);
}
[data-testid="stDialog"] .modal-json-steps {
    display: flex;
    flex-direction: column;
    gap: 0.85rem;
}
[data-testid="stDialog"] .modal-json-step {
    display: flex;
    gap: 0.85rem;
    align-items: flex-start;
}
[data-testid="stDialog"] .modal-json-step-num {
    flex-shrink: 0;
    width: 1.65rem;
    height: 1.65rem;
    border-radius: 999px;
    background: var(--accent-soft);
    color: var(--accent);
    font-size: 0.8125rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 0.1rem;
}
[data-testid="stDialog"] .modal-json-step-title {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--text);
    margin: 0 0 0.25rem;
}
[data-testid="stDialog"] .modal-json-step-text {
    font-size: 0.8125rem;
    line-height: 1.55;
    color: var(--muted);
    margin: 0;
}
[data-testid="stDialog"] .modal-json-step-text strong {
    color: var(--text);
    font-weight: 600;
}
[data-testid="stDialog"] .modal-json-actions-label {
    font-size: 0.6875rem;
    font-weight: var(--weight-semibold);
    letter-spacing: 0.07em;
    text-transform: uppercase;
    color: var(--muted);
    margin: 0 0 0.65rem;
    opacity: 0.85;
}
[data-testid="stDialog"] .modal-json-actions-label + div[data-testid="stHorizontalBlock"] {
    margin-bottom: 0.5rem;
}
[data-testid="stDialog"] .modal-json-actions-label ~ div [data-testid="stCaptionContainer"] {
    margin-bottom: 0.45rem !important;
}

/* Cerrar modal — icono visible en light y dark */
[data-testid="stDialog"] button[aria-label="Close"],
[data-testid="stModal"] button[aria-label="Close"] {
    background-color: var(--surface) !important;
    background-image: none !important;
    color: var(--text) !important;
    border: 1px solid var(--border-strong) !important;
    box-shadow: none !important;
    opacity: 1 !important;
}
[data-testid="stDialog"] button[aria-label="Close"]:hover,
[data-testid="stModal"] button[aria-label="Close"]:hover {
    background-color: var(--highlight-soft) !important;
    border-color: var(--accent) !important;
}
[data-testid="stDialog"] button[aria-label="Close"] svg,
[data-testid="stDialog"] button[aria-label="Close"] path,
[data-testid="stModal"] button[aria-label="Close"] svg,
[data-testid="stModal"] button[aria-label="Close"] path {
    fill: var(--text) !important;
    stroke: var(--text) !important;
    color: var(--text) !important;
}

/* Tipografía unificada — todos los botones e hijos Streamlit */
button,
[data-baseweb="button"],
div.stButton > button,
div.stDownloadButton > button,
div.stLinkButton > a,
[data-testid="stFileUploaderDropzone"] button::after,
[data-testid="stFileUploaderDropzone"] [data-baseweb="button"]::after,
[data-testid="stDialog"] [data-testid="stFileUploaderDropzone"] button::after,
[data-testid="stDialog"] [data-testid="stFileUploaderDropzone"] [data-baseweb="button"]::after {
    font-family: var(--font) !important;
    font-size: var(--btn-font) !important;
    font-weight: var(--btn-weight) !important;
    letter-spacing: var(--btn-tracking) !important;
    -webkit-font-smoothing: antialiased !important;
}
button *,
[data-baseweb="button"] *,
div.stButton > button *,
div.stDownloadButton > button *,
div.stLinkButton > a *,
div.stButton [data-baseweb="button"] > div,
div.stButton [data-baseweb="button"] span,
div.stButton [data-baseweb="button"] p,
div.stDownloadButton [data-baseweb="button"] > div,
div.stDownloadButton [data-baseweb="button"] span,
div.stDownloadButton [data-baseweb="button"] p,
div.stLinkButton [data-baseweb="button"] > div,
div.stLinkButton [data-baseweb="button"] span,
div.stLinkButton [data-baseweb="button"] p {
    font-family: inherit !important;
    font-size: inherit !important;
    font-weight: inherit !important;
    letter-spacing: inherit !important;
}

</style>
"""


def inject_styles() -> None:
    import streamlit as st

    from .themes import DARK_EXTRA_CSS, DARK_THEME_CSS, LIGHT_EXTRA_CSS, LIGHT_THEME_CSS
    from .upload_zone import UPLOAD_ICON_GHOST_SVG, UPLOAD_ICON_GHOST_SVG_DARK, UPLOAD_ICONS_SVG

    tema = st.session_state.get("tema", "dark")
    theme_css = DARK_THEME_CSS if tema == "dark" else LIGHT_THEME_CSS
    extra_css = DARK_EXTRA_CSS if tema == "dark" else LIGHT_EXTRA_CSS
    ghost_icon = UPLOAD_ICON_GHOST_SVG_DARK if tema == "dark" else UPLOAD_ICON_GHOST_SVG

    css = (
        OMNI_CSS.replace("{{UPLOAD_ICONS}}", UPLOAD_ICONS_SVG)
        .replace("{{UPLOAD_GHOST_ICON}}", ghost_icon)
        .replace("</style>", f"{theme_css}{extra_css}</style>")
    )
    st.markdown(css, unsafe_allow_html=True)


BUTTON_FIXES_CSS = """
<style>
/* Header — logo + botones en una fila (flex container, sin columnas) */
.omni-header-marker { display: none; }
.omni-header-spacer {
    flex: 1 1 auto !important;
    min-width: 0 !important;
    width: auto !important;
    height: 1px !important;
    margin: 0 !important;
    padding: 0 !important;
    visibility: hidden !important;
}
.omni-header-brand {
    flex: 0 1 auto !important;
    min-width: 0 !important;
    max-width: calc(100% - 6rem) !important;
}
[data-testid="stElementContainer"]:has(.omni-header-marker)
    + [data-testid="stElementContainer"] [data-testid="stHorizontalBlock"],
div[data-testid="stHorizontalBlock"]:has(.omni-header-brand) {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: flex-start !important;
    justify-content: flex-start !important;
    gap: 0.35rem !important;
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    box-sizing: border-box !important;
}
[data-testid="stElementContainer"]:has(.omni-header-marker)
    + [data-testid="stElementContainer"] [data-testid="stHorizontalBlock"] > div,
div[data-testid="stHorizontalBlock"]:has(.omni-header-brand) > div,
div[data-testid="stHorizontalBlock"]:has(.omni-header-brand) > [data-testid="column"] {
    flex: 0 0 auto !important;
    width: auto !important;
    min-width: 0 !important;
    max-width: none !important;
    padding: 0 !important;
    margin: 0 !important;
}
[data-testid="stElementContainer"]:has(.omni-header-marker)
    + [data-testid="stElementContainer"] [data-testid="stHorizontalBlock"] > div:has(.omni-header-brand),
div[data-testid="stHorizontalBlock"]:has(.omni-header-brand) > div:has(.omni-header-brand),
div[data-testid="stHorizontalBlock"]:has(.omni-header-brand) > [data-testid="column"]:has(.omni-header-brand) {
    flex: 0 1 auto !important;
    min-width: 0 !important;
    max-width: calc(100% - 6rem) !important;
}
[data-testid="stElementContainer"]:has(.omni-header-marker)
    + [data-testid="stElementContainer"] [data-testid="stHorizontalBlock"] > div:has(.omni-header-spacer),
div[data-testid="stHorizontalBlock"]:has(.omni-header-brand) > div:has(.omni-header-spacer) {
    flex: 1 1 auto !important;
    min-width: 0 !important;
}

@media (max-width: 640px) {
    .block-container {
        padding-left: max(1.15rem, env(safe-area-inset-left, 0px)) !important;
        padding-right: max(1.15rem, env(safe-area-inset-right, 0px)) !important;
    }
    [data-testid="stElementContainer"]:has(.omni-header-marker)
        + [data-testid="stElementContainer"] [data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
    }
    .omni-header-brand {
        max-width: calc(100% - 6.25rem) !important;
    }
    .omni-wordmark {
        gap: 0.35rem !important;
        max-width: 100% !important;
    }
    .omni-wordmark-text {
        font-size: 2.125rem !important;
        margin-left: 0 !important;
    }
    .omni-logo {
        width: 10.5rem !important;
        min-width: 8.5rem !important;
        height: auto !important;
        max-width: 100% !important;
        display: block !important;
    }
    .omni-hero-gap {
        height: 4.25rem !important;
    }
    .st-key-btn_theme_toggle button,
    .st-key-btn_api_settings button,
    .st-key-btn_theme_toggle [data-testid="stBaseButton-secondary"],
    .st-key-btn_api_settings [data-testid="stBaseButton-secondary"] {
        width: 44px !important;
        min-width: 44px !important;
        max-width: 44px !important;
        min-height: 44px !important;
        font-size: 1.25rem !important;
    }
}
.st-key-btn_theme_toggle,
.st-key-btn_api_settings {
    margin: 0 !important;
    padding: 0 !important;
}
.st-key-btn_theme_toggle button,
.st-key-btn_api_settings button,
.st-key-btn_theme_toggle button[class*="st-emotion-cache"],
.st-key-btn_api_settings button[class*="st-emotion-cache"],
.st-key-btn_theme_toggle [data-testid="stBaseButton-secondary"],
.st-key-btn_api_settings [data-testid="stBaseButton-secondary"] {
    background-color: {{BTN_SURFACE}} !important;
    background-image: none !important;
    color: {{BTN_TEXT}} !important;
    -webkit-text-fill-color: {{BTN_TEXT}} !important;
    border: 1px solid {{BTN_BORDER}} !important;
    box-shadow: none !important;
    width: 40px !important;
    min-width: 40px !important;
    max-width: 40px !important;
    min-height: 40px !important;
    padding: 0.35rem 0 !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 1.2rem !important;
    line-height: 1 !important;
}
/* Toolbar header — emojis ☀️ / ⚙️ a color (mismo estilo móvil y desktop) */
.st-key-btn_theme_toggle button,
.st-key-btn_api_settings button,
.st-key-btn_theme_toggle button *,
.st-key-btn_api_settings button * {
    color: unset !important;
    -webkit-text-fill-color: unset !important;
    font-family: "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji",
        "Twemoji Mozilla", sans-serif !important;
}
.st-key-btn_theme_toggle button:hover,
.st-key-btn_api_settings button:hover {
    background-color: var(--highlight-soft) !important;
    border-color: var(--accent) !important;
}

/* Panel Daypo — borde explícito (modo IA sin recuadro externo) */
[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid {{PANEL_BORDER}} !important;
    box-shadow: 0 0 0 1px {{PANEL_BORDER_SOFT}} !important;
}

/* Dropzone IA — botón Seleccionar archivo (solo página principal, no modal) */
.block-container [data-testid="stFileUploaderDropzone"] button,
.block-container [data-testid="stFileUploaderDropzone"] [data-baseweb="button"] {
    background: var(--accent) !important;
    background-color: var(--accent) !important;
    background-image: none !important;
    color: transparent !important;
    border: none !important;
    box-shadow: 0 2px 10px var(--accent-glow) !important;
}
.block-container [data-testid="stFileUploaderDropzone"] button::after,
.block-container [data-testid="stFileUploaderDropzone"] [data-baseweb="button"]::after {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}
.block-container [data-testid="stFileUploaderDropzone"] button:hover,
.block-container [data-testid="stFileUploaderDropzone"] [data-baseweb="button"]:hover {
    background: var(--accent-hover) !important;
    background-color: var(--accent-hover) !important;
}

/* Modal — Importar JSON (override final) */
[data-testid="stDialog"] [data-testid="stFileUploaderDropzone"] button,
[data-testid="stDialog"] [data-testid="stFileUploaderDropzone"] [data-baseweb="button"] {
    background: {{BTN_SURFACE}} !important;
    background-color: {{BTN_SURFACE}} !important;
    background-image: none !important;
    color: transparent !important;
    border: 1px solid {{BTN_BORDER}} !important;
    box-shadow: none !important;
}
[data-testid="stDialog"] [data-testid="stFileUploaderDropzone"] button::after,
[data-testid="stDialog"] [data-testid="stFileUploaderDropzone"] [data-baseweb="button"]::after {
    color: {{BTN_TEXT}} !important;
    -webkit-text-fill-color: {{BTN_TEXT}} !important;
}
[data-testid="stDialog"] [data-testid="stFileUploaderDropzone"] button::before,
[data-testid="stDialog"] [data-testid="stFileUploaderDropzone"] [data-baseweb="button"]::before {
    filter: none !important;
    opacity: 1 !important;
    background-image: url("{{GHOST_ICON}}") !important;
}
[data-testid="stDialog"] [data-testid="stFileUploaderDropzone"] button:hover,
[data-testid="stDialog"] [data-testid="stFileUploaderDropzone"] [data-baseweb="button"]:hover {
    background: var(--highlight-soft) !important;
    background-color: var(--highlight-soft) !important;
    border-color: var(--accent) !important;
}

/* Modal — toggles visibles en light/dark */
[data-testid="stDialog"] [data-testid="stCheckbox"] label[data-baseweb="checkbox"]:not(:has(input:checked)) > :first-child:not(input):not([data-testid="stWidgetLabel"]) {
    background-color: {{BTN_BORDER}} !important;
    border: 1px solid {{BTN_BORDER}} !important;
}
[data-testid="stDialog"] [data-testid="stCheckbox"] label[data-baseweb="checkbox"] > :first-child:not(input):not([data-testid="stWidgetLabel"]) > div {
    background-color: {{BTN_SURFACE}} !important;
}
[data-testid="stDialog"] [data-testid="stCheckbox"] label[data-baseweb="checkbox"]:has(input:checked) > :first-child:not(input):not([data-testid="stWidgetLabel"]) {
    background: {{SWITCH_ON}} !important;
    background-color: {{SWITCH_ON}} !important;
    background-image: none !important;
    border-color: {{SWITCH_ON_BORDER}} !important;
}
[data-testid="stDialog"] [data-testid="stCheckbox"] label[data-baseweb="checkbox"]:has(input:checked) > :first-child:not(input):not([data-testid="stWidgetLabel"]) > div {
    background-color: #FFFFFF !important;
}
[data-testid="stDialog"] [data-testid="stCheckbox"] label[data-baseweb="checkbox"] > [data-testid="stWidgetLabel"],
[data-testid="stDialog"] [data-testid="stCheckbox"] label[data-baseweb="checkbox"] > :not(:first-child):not(input) {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* Cerrar modal — override final en light */
button[aria-label="Close"] {
    background-color: {{BTN_SURFACE}} !important;
    color: {{BTN_TEXT}} !important;
    border: 1px solid {{BTN_BORDER}} !important;
}
button[aria-label="Close"] svg,
button[aria-label="Close"] path {
    fill: {{BTN_TEXT}} !important;
    stroke: {{BTN_TEXT}} !important;
}

/* Textareas — fondo claro en light (Streamlit emotion-cache) */
[data-testid="stTextArea"] > div,
[data-testid="stTextArea"] [data-baseweb="base-input"],
[data-testid="stTextArea"] textarea,
[data-testid="stTextArea"] [data-baseweb="textarea"],
[data-testid="stTextArea"] div[data-baseweb="textarea"] {
    background-color: {{INPUT_BG}} !important;
    color: {{BTN_TEXT}} !important;
    -webkit-text-fill-color: {{BTN_TEXT}} !important;
    caret-color: {{BTN_TEXT}} !important;
    border-color: {{BTN_BORDER}} !important;
}
[data-testid="stTextArea"] textarea {
    background-color: {{INPUT_BG}} !important;
}
[data-testid="stTextArea"] textarea::placeholder {
    color: var(--muted) !important;
    -webkit-text-fill-color: var(--muted) !important;
    opacity: 1 !important;
}

/* Secundarios globales */
button[data-testid="stBaseButton-secondary"],
button[kind="secondary"] {
    background-color: {{BTN_SURFACE}} !important;
    background-image: none !important;
    color: {{BTN_TEXT}} !important;
    border: 1px solid {{BTN_BORDER}} !important;
    box-shadow: none !important;
    font-weight: var(--btn-weight) !important;
}
button[data-testid="stBaseButton-secondary"] p,
button[data-testid="stBaseButton-secondary"] span,
button[kind="secondary"] p,
button[kind="secondary"] span {
    color: {{BTN_TEXT}} !important;
    font-weight: inherit !important;
}
button[data-testid="stBaseButton-primary"],
button[kind="primary"] {
    font-weight: var(--btn-weight) !important;
}
button[data-testid="stBaseButton-primary"] p,
button[data-testid="stBaseButton-primary"] span {
    color: #FFFFFF !important;
    font-weight: inherit !important;
}

/* Fuente — track pill (contenedor gris de ambos botones) */
.block-container:has(.fuente-picker-marker)
    [data-testid="stHorizontalBlock"]:has(.st-key-fuente_daypo):has(.st-key-fuente_ia) {
    background: {{TRACK_BG}} !important;
    border: 1px solid {{TRACK_BORDER}} !important;
    border-radius: var(--radius) !important;
    padding: 0.25rem !important;
    gap: 0.25rem !important;
    margin-bottom: 0 !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
    max-width: 100% !important;
    width: 100% !important;
    box-sizing: border-box !important;
}
.block-container:has(.fuente-picker-marker)
    [data-testid="stHorizontalBlock"]:has(.st-key-fuente_daypo):has(.st-key-fuente_ia) .stButton {
    margin: 0 !important;
}
.block-container:has(.fuente-picker-marker) .st-key-fuente_daypo button,
.block-container:has(.fuente-picker-marker) .st-key-fuente_ia button,
.block-container:has(.fuente-picker-marker) .st-key-fuente_daypo [data-testid="stBaseButton-secondary"],
.block-container:has(.fuente-picker-marker) .st-key-fuente_ia [data-testid="stBaseButton-secondary"] {
    width: 100% !important;
    min-height: 36px !important;
    border-radius: 6px !important;
    background-color: transparent !important;
    background-image: none !important;
    color: var(--muted) !important;
    border: 1px solid transparent !important;
    box-shadow: none !important;
    font-weight: var(--weight-medium) !important;
}
.block-container:has(.fuente-picker-marker) .st-key-fuente_daypo button *,
.block-container:has(.fuente-picker-marker) .st-key-fuente_ia button * {
    color: var(--muted) !important;
}
/* Fuente — inactivo explícito (dentro del pill gris) */
.block-container:has(.fuente-active-daypo) .st-key-fuente_ia button,
.block-container:has(.fuente-active-daypo) .st-key-fuente_ia [data-testid="stBaseButton-secondary"],
.block-container:has(.fuente-active-ia) .st-key-fuente_daypo button,
.block-container:has(.fuente-active-ia) .st-key-fuente_daypo [data-testid="stBaseButton-secondary"] {
    background-color: transparent !important;
    border: 1px solid transparent !important;
    box-shadow: none !important;
    color: var(--muted) !important;
    font-weight: var(--weight-medium) !important;
}
.block-container:has(.fuente-active-daypo) .st-key-fuente_ia button *,
.block-container:has(.fuente-active-ia) .st-key-fuente_daypo button * {
    color: var(--muted) !important;
    font-weight: inherit !important;
}
.block-container:has(.fuente-active-daypo) .st-key-fuente_daypo button,
.block-container:has(.fuente-active-daypo) .st-key-fuente_daypo [data-testid="stBaseButton-secondary"] {
    background-color: {{BTN_SURFACE}} !important;
    color: {{BTN_TEXT}} !important;
    border: 1px solid var(--accent) !important;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08), 0 0 0 1px var(--accent-soft) !important;
    font-weight: var(--btn-weight) !important;
}
.block-container:has(.fuente-active-daypo) .st-key-fuente_daypo button * {
    color: {{BTN_TEXT}} !important;
    font-weight: inherit !important;
}
.block-container:has(.fuente-active-ia) .st-key-fuente_ia button,
.block-container:has(.fuente-active-ia) .st-key-fuente_ia [data-testid="stBaseButton-secondary"] {
    background-color: {{BTN_SURFACE}} !important;
    color: {{BTN_TEXT}} !important;
    border: 1px solid var(--accent) !important;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08), 0 0 0 1px var(--accent-soft) !important;
    font-weight: var(--btn-weight) !important;
}
.block-container:has(.fuente-active-ia) .st-key-fuente_ia button * {
    color: {{BTN_TEXT}} !important;
    font-weight: inherit !important;
}
div[data-testid="stElementContainer"]:has(.fuente-picker-marker)
    + div[data-testid="stElementContainer"] [data-testid="stHorizontalBlock"] .stButton > button:hover,
.block-container:has(.fuente-picker-marker)
    [data-testid="stHorizontalBlock"]:has(.st-key-fuente_daypo):has(.st-key-fuente_ia) .stButton > button:hover {
    background-color: var(--highlight-soft) !important;
    color: var(--text) !important;
}

/* Panel Daypo — textarea con borde visible (light/dark) */
.block-container [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stTextArea"] > div,
.block-container [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stTextArea"] [data-baseweb="base-input"],
.block-container [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stTextArea"] textarea,
.block-container [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stTextArea"] div[data-baseweb="textarea"] {
    background-color: {{INPUT_BG}} !important;
    color: {{BTN_TEXT}} !important;
    border: 1px solid {{PANEL_BORDER}} !important;
    box-shadow: var(--shadow-sm) !important;
}

/* Panel Trabajando / log — borde fino como el resto de paneles */
.block-container .omni-worklog-panel {
    background-color: {{BTN_SURFACE}} !important;
    border: 1px solid {{BTN_BORDER}} !important;
    box-shadow: var(--shadow-sm) !important;
    color: {{BTN_TEXT}} !important;
    font-family: var(--font) !important;
}
.block-container .omni-worklog-title {
    font-family: var(--font) !important;
    font-weight: var(--weight-semibold) !important;
    font-size: var(--text-sm) !important;
    letter-spacing: var(--tracking-ui) !important;
    color: {{BTN_TEXT}} !important;
    -webkit-text-fill-color: {{BTN_TEXT}} !important;
}
.block-container .omni-worklog-line {
    font-family: var(--font) !important;
    font-weight: var(--weight-normal) !important;
    font-size: var(--text-sm) !important;
    letter-spacing: var(--tracking-body) !important;
    color: {{BTN_TEXT}} !important;
    -webkit-text-fill-color: {{BTN_TEXT}} !important;
}
.block-container .omni-worklog-foot {
    font-family: var(--font) !important;
    font-weight: var(--weight-normal) !important;
    font-size: var(--text-xs) !important;
    letter-spacing: var(--tracking-body) !important;
    color: var(--muted) !important;
    -webkit-text-fill-color: var(--muted) !important;
}
.block-container [data-testid="stElementContainer"]:has(.omni-worklog-panel),
.block-container [data-testid="stElementContainer"]:has(.omni-worklog-panel) > div,
.block-container [data-testid="stElementContainer"]:has(.omni-worklog-panel) [data-testid="stMarkdownContainer"],
.block-container [data-testid="stElementContainer"]:has(.omni-worklog-panel) [class*="st-emotion-cache"] {
    background: transparent !important;
    background-color: transparent !important;
    background-image: none !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}

/* FAQ expanders — misma estética que paneles Daypo/export */
.block-container:has(.omni-faq-marker) [data-testid="stExpander"],
.block-container:has(.omni-faq-marker) .stExpander {
    background-color: {{BTN_SURFACE}} !important;
    background-image: none !important;
    border: 1px solid {{BTN_BORDER}} !important;
    border-radius: var(--radius) !important;
    box-shadow: none !important;
    outline: none !important;
    overflow: hidden !important;
}
.block-container:has(.omni-faq-marker) [data-testid="stExpander"]:hover {
    border-color: var(--omni-panel-hover-border) !important;
    box-shadow: none !important;
}
.block-container:has(.omni-faq-marker) [data-testid="stExpander"] > div,
.block-container:has(.omni-faq-marker) [data-testid="stExpander"] > div > div,
.block-container:has(.omni-faq-marker) [data-testid="stExpanderDetails"] {
    background-color: transparent !important;
    background-image: none !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
}
.block-container:has(.omni-faq-marker) [data-testid="stExpander"] > div > div:first-child,
.block-container:has(.omni-faq-marker) [data-testid="stExpander"] > div > div:first-child [class*="st-emotion-cache"] {
    background-color: transparent !important;
    background-image: none !important;
    color: {{BTN_TEXT}} !important;
    border: none !important;
    border-bottom: none !important;
    display: flex !important;
    align-items: center !important;
    gap: 0.55rem !important;
}
.block-container:has(.omni-faq-marker) [data-testid="stExpander"] > div > div:first-child [data-testid="stMarkdownContainer"],
.block-container:has(.omni-faq-marker) [data-testid="stExpander"] > div > div:first-child [data-testid="stMarkdownContainer"] p,
.block-container:has(.omni-faq-marker) [data-testid="stExpander"] > div > div:first-child [data-testid="stMarkdownContainer"] span,
.block-container:has(.omni-faq-marker) [data-testid="stExpander"] > div > div:first-child p,
.block-container:has(.omni-faq-marker) [data-testid="stExpander"] > div > div:first-child span {
    font-family: var(--font) !important;
    font-weight: var(--weight-semibold) !important;
    font-size: var(--text-sm) !important;
    letter-spacing: var(--tracking-ui) !important;
    color: {{BTN_TEXT}} !important;
    -webkit-text-fill-color: {{BTN_TEXT}} !important;
    flex: 1 1 auto !important;
    min-width: 0 !important;
}
.block-container:has(.omni-faq-marker) [data-testid="stExpander"] > div > div:first-child svg,
.block-container:has(.omni-faq-marker) [data-testid="stExpander"] > div > div:first-child [data-testid="stIconMaterial"] {
    font-family: "Material Symbols Rounded", "Material Icons" !important;
    flex-shrink: 0 !important;
    font-size: 1.125rem !important;
    line-height: 1 !important;
    opacity: 0.45 !important;
    color: var(--muted) !important;
    -webkit-text-fill-color: var(--muted) !important;
}
.block-container:has(.omni-faq-marker) [data-testid="stExpanderDetails"],
.block-container:has(.omni-faq-marker) [data-testid="stExpanderDetails"] [class*="st-emotion-cache"] {
    background-color: transparent !important;
    background-image: none !important;
    border: none !important;
}
.block-container:has(.omni-faq-marker) [data-testid="stExpanderDetails"] p,
.block-container:has(.omni-faq-marker) [data-testid="stExpanderDetails"] span,
.block-container:has(.omni-faq-marker) [data-testid="stExpanderDetails"] [data-testid="stMarkdownContainer"] p,
.block-container:has(.omni-faq-marker) [data-testid="stExpanderDetails"] code {
    color: {{BTN_TEXT}} !important;
    -webkit-text-fill-color: {{BTN_TEXT}} !important;
}
.block-container:has(.omni-faq-marker) [data-testid="stExpander"] [data-testid="stCaptionContainer"] p,
.block-container:has(.omni-faq-marker) [data-testid="stExpanderDetails"] [data-testid="stCaptionContainer"] p {
    color: var(--muted) !important;
    -webkit-text-fill-color: var(--muted) !important;
}

/* Progreso — solo texto + barra, sin caja */
.stProgress,
.stProgress > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    overflow: visible !important;
    position: relative !important;
    z-index: 5 !important;
}
.stProgress {
    margin-top: 0.75rem !important;
}
.stProgress > div:first-child {
    position: relative !important;
    z-index: 6 !important;
    overflow: visible !important;
    min-height: 1.3rem !important;
    margin-bottom: 0.35rem !important;
    padding-bottom: 0.15rem !important;
    background: var(--bg) !important;
}
.stProgress label,
.stProgress [data-testid="stProgressLabel"],
.stProgress [data-testid="stProgressLabel"] > div,
.stProgress [data-testid="stProgressLabel"] p,
.stProgress > div:first-child,
.stProgress > div:first-child [data-testid="stMarkdownContainer"],
.stProgress > div:first-child [data-testid="stMarkdownContainer"] p,
.stProgress > div:first-child [data-testid="stMarkdownContainer"] span,
.stProgress > div:first-child p,
.stProgress > div:first-child span,
.stProgress [data-testid="stMarkdownContainer"] p {
    font-family: var(--font) !important;
    font-size: var(--text-sm) !important;
    font-weight: var(--weight-medium) !important;
    letter-spacing: var(--tracking-ui) !important;
    color: {{BTN_TEXT}} !important;
    -webkit-text-fill-color: {{BTN_TEXT}} !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 0 0.4rem 0 !important;
    opacity: 1 !important;
    visibility: visible !important;
    line-height: 1.45 !important;
}
.stProgress > div:first-child > div,
.stProgress > div:first-child [data-testid="stMarkdownContainer"],
.stProgress > div:first-child [data-testid="stMarkdownContainer"] > div {
    height: auto !important;
    max-height: none !important;
    overflow: visible !important;
    background: transparent !important;
}
.stProgress > div:last-child {
    height: auto !important;
    overflow: visible !important;
    background: transparent !important;
}
.stProgress [data-testid="stProgressBarTrack"] {
    background: var(--surface-2) !important;
    border: none !important;
    border-radius: 999px !important;
    overflow: hidden !important;
    height: 4px !important;
}
.stProgress [data-testid="stProgressBarTrack"] > div {
    background: var(--accent) !important;
    height: 100% !important;
    border-radius: 999px !important;
}
[data-testid="stElementContainer"]:has(.stProgress),
[data-testid="stElementContainer"]:has([data-testid="stProgress"]) {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0.85rem 0 0.15rem !important;
    margin-top: 0.35rem !important;
    overflow: visible !important;
    position: relative !important;
    z-index: 5 !important;
}
.block-container .st-key-btn_convertir {
    margin-bottom: 0.15rem !important;
}

/* Export grid — Word/PDF: mismo botón secundario que el resto de tarjetas */
.export-grid [data-testid="column"] .stDownloadButton button,
.export-grid [data-testid="column"] .stDownloadButton [data-baseweb="button"],
.export-grid [data-testid="column"] .stDownloadButton button[data-testid="stBaseButton-primary"],
.export-grid [data-testid="column"] .stDownloadButton button[kind="primary"] {
    background-color: {{BTN_SURFACE}} !important;
    background-image: none !important;
    color: {{BTN_TEXT}} !important;
    -webkit-text-fill-color: {{BTN_TEXT}} !important;
    border: 1px solid {{BTN_BORDER}} !important;
    box-shadow: none !important;
}
.export-grid [data-testid="column"] .stDownloadButton button:hover,
.export-grid [data-testid="column"] .stDownloadButton [data-baseweb="button"]:hover {
    background-color: var(--surface-2) !important;
    border-color: var(--accent) !important;
    box-shadow: var(--btn-hover-glow) !important;
}
/* Selectbox — global (export-grid no envuelve widgets en el DOM de Streamlit) */
[data-testid="stSelectbox"] div[data-baseweb="select"],
[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
[data-testid="stSelectbox"] div[data-baseweb="select"] div[role="combobox"],
[data-testid="stSelectbox"] div[data-baseweb="select"] > div > div,
[data-testid="stSelectbox"] div[data-baseweb="select"] [data-baseweb="input"],
[data-testid="stSelectbox"] [class*="st-emotion-cache"] {
    background-color: {{BTN_SURFACE}} !important;
    background-image: none !important;
    border-color: {{BTN_BORDER}} !important;
    color: {{BTN_TEXT}} !important;
}
[data-testid="stSelectbox"] div[data-baseweb="select"] span,
[data-testid="stSelectbox"] div[data-baseweb="select"] p,
[data-testid="stSelectbox"] div[data-baseweb="select"] input,
[data-testid="stSelectbox"] div[data-baseweb="select"] div[role="combobox"] > div {
    color: {{BTN_TEXT}} !important;
    -webkit-text-fill-color: {{BTN_TEXT}} !important;
    background: transparent !important;
    background-color: transparent !important;
}
[data-testid="stSelectbox"] div[data-baseweb="select"] div[role="combobox"] {
    border: 1px solid {{BTN_BORDER}} !important;
    border-radius: var(--btn-radius) !important;
    min-height: 2.35rem !important;
    background-color: {{BTN_SURFACE}} !important;
}
[data-testid="stSelectbox"] div[data-baseweb="select"] div[role="combobox"]:focus-within,
[data-testid="stSelectbox"] div[data-baseweb="select"] div[role="combobox"][aria-expanded="true"] {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 1px var(--accent-soft) !important;
    background-color: {{BTN_SURFACE}} !important;
}

/* Selectbox — menú desplegable (portal en body, light/dark) */
div[data-baseweb="popover"] > div,
[data-baseweb="popover"] > div {
    background-color: transparent !important;
    background-image: none !important;
    border: none !important;
    box-shadow: none !important;
}
div[data-baseweb="popover"],
[data-baseweb="popover"] {
    background-color: {{BTN_SURFACE}} !important;
    background-image: none !important;
}
[data-baseweb="popover"] [data-baseweb="menu"],
[data-baseweb="popover"] ul[role="listbox"],
div[data-baseweb="popover"] [role="listbox"],
[data-baseweb="popover"] [data-testid="stSelectboxVirtualDropdown"],
[data-baseweb="popover"] [data-baseweb="popover"] {
    background-color: {{BTN_SURFACE}} !important;
    background-image: none !important;
    border: 1px solid {{BTN_BORDER}} !important;
    box-shadow: var(--shadow-md) !important;
}
[data-baseweb="popover"] li,
[data-baseweb="popover"] [role="option"],
[data-baseweb="popover"] ul li {
    background-color: {{BTN_SURFACE}} !important;
    background-image: none !important;
    color: {{BTN_TEXT}} !important;
    -webkit-text-fill-color: {{BTN_TEXT}} !important;
    font-family: var(--font) !important;
    font-size: 0.8125rem !important;
}
[data-baseweb="popover"] li:hover,
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="popover"] [aria-selected="true"],
[data-baseweb="popover"] li[aria-selected="true"],
[data-baseweb="popover"] [data-highlighted="true"],
[data-baseweb="popover"] li[data-highlighted="true"] {
    background-color: var(--highlight-soft) !important;
    color: {{BTN_TEXT}} !important;
    -webkit-text-fill-color: {{BTN_TEXT}} !important;
}
[data-baseweb="popover"] li *,
[data-baseweb="popover"] [role="option"] * {
    color: inherit !important;
    -webkit-text-fill-color: inherit !important;
    background: transparent !important;
}

.block-container .export-format-legend {
    background-color: {{BTN_SURFACE}} !important;
    border: 1px solid var(--border) !important;
    color: var(--muted) !important;
}
.block-container .export-format-legend p,
.block-container .export-format-legend strong {
    color: {{BTN_TEXT}} !important;
    -webkit-text-fill-color: {{BTN_TEXT}} !important;
}
.block-container .review-summary,
.block-container [data-testid="stMarkdownContainer"] .review-summary,
.block-container p.review-summary {
    color: {{BTN_TEXT}} !important;
    -webkit-text-fill-color: {{BTN_TEXT}} !important;
    height: auto !important;
    max-height: none !important;
    overflow: visible !important;
    line-height: 1.35 !important;
}

/* Modal API — input password (Streamlit 1.58: ojo dentro de base-input, a la derecha) */
[data-testid="stDialog"] [data-testid="stTextInput"] [data-testid="stTextInputRootElement"] {
    display: flex !important;
    align-items: stretch !important;
    background-color: {{INPUT_BG}} !important;
    background-image: none !important;
    border: 1px solid {{BTN_BORDER}} !important;
    border-radius: var(--radius) !important;
    box-shadow: none !important;
    overflow: hidden !important;
    padding: 0 !important;
}
[data-testid="stDialog"] [data-testid="stTextInput"] [data-testid="stTextInputRootElement"] > div[data-baseweb="base-input"],
[data-testid="stDialog"] [data-testid="stTextInput"] [data-testid="stTextInputRootElement"] > div {
    display: flex !important;
    flex: 1 1 auto !important;
    flex-direction: row !important;
    align-items: center !important;
    width: 100% !important;
    min-width: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    border: none !important;
    background: transparent !important;
    background-color: transparent !important;
    box-shadow: none !important;
}
[data-testid="stDialog"] [data-testid="stTextInput"] [data-testid="stTextInputRootElement"] input {
    flex: 1 1 auto !important;
    min-width: 0 !important;
    width: 100% !important;
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    color: {{BTN_TEXT}} !important;
    -webkit-text-fill-color: {{BTN_TEXT}} !important;
    min-height: 2.625rem !important;
    height: auto !important;
    padding-left: 0.85rem !important;
    padding-right: 0.35rem !important;
}
[data-testid="stDialog"] [data-testid="stTextInput"] input::placeholder {
    color: var(--muted) !important;
    -webkit-text-fill-color: var(--muted) !important;
    opacity: 1 !important;
}
[data-testid="stDialog"] [data-testid="stTextInput"] [data-testid="stTextInputRootElement"] button[type="button"] {
    flex: 0 0 2.75rem !important;
    width: 2.75rem !important;
    min-width: 2.75rem !important;
    height: auto !important;
    align-self: stretch !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin: 0 !important;
    padding: 0 !important;
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    border-left: 1px solid {{BTN_BORDER}} !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    cursor: pointer !important;
    order: 99 !important;
}
[data-testid="stDialog"] [data-testid="stTextInput"] [data-testid="stTextInputRootElement"] button[type="button"] svg {
    width: 1.125rem !important;
    height: 1.125rem !important;
    flex-shrink: 0 !important;
    display: block !important;
}
[data-testid="stDialog"] [data-testid="stTextInput"] [data-testid="stIconMaterial"],
[data-testid="stDialog"] [data-testid="stTextInput"] button [data-testid="stIconMaterial"] {
    font-family: "Material Symbols Rounded", "Material Icons" !important;
    color: var(--muted) !important;
    -webkit-text-fill-color: var(--muted) !important;
}
[data-testid="stDialog"] [data-testid="stTextInput"] [data-testid="stTextInputRootElement"]:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow-soft) !important;
}

/* Scroll — rueda del ratón en toda la ventana */
html, body {
    overflow-y: auto !important;
    height: auto !important;
}
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
section.main,
.main {
    overflow-y: visible !important;
    height: auto !important;
    min-height: 100vh !important;
}
[data-testid="stAppViewContainer"] > section {
    overflow: visible !important;
}

/* Radios — override final (pantalla exportar, etc.) */
[data-testid="stRadio"] [data-testid="stWidgetLabel"] p,
[data-testid="stRadio"] label[data-baseweb="radio"] p,
[data-testid="stRadio"] label[data-baseweb="radio"] span,
[data-testid="stRadio"] label[data-baseweb="radio"] [data-testid="stMarkdownContainer"] p,
[data-testid="stRadio"] div[role="radiogroup"] label p,
[data-testid="stRadio"] div[role="radiogroup"] label span {
    color: var(--text) !important;
    -webkit-text-fill-color: var(--text) !important;
}
[data-testid="stRadio"] > label > [data-testid="stMarkdownContainer"] p {
    color: var(--muted) !important;
    -webkit-text-fill-color: var(--muted) !important;
}
</style>
"""


def inject_button_fixes() -> None:
    import streamlit as st

    from .upload_zone import UPLOAD_ICON_GHOST_SVG, UPLOAD_ICON_GHOST_SVG_DARK

    tema = st.session_state.get("tema", "dark")
    if tema == "light":
        btn_surface = "#FFFFFF"
        btn_text = "#111827"
        btn_border = "#CBD5E1"
        input_bg = "#FFFFFF"
        panel_border = "#94A3B8"
        panel_border_soft = "rgba(124, 105, 239, 0.25)"
        ghost_icon = UPLOAD_ICON_GHOST_SVG
        track_bg = "#F3F4F6"
        track_border = "#CBD5E1"
    else:
        btn_surface = "#16181F"
        btn_text = "#F1F5F9"
        btn_border = "#2D3340"
        input_bg = "#1E2129"
        panel_border = "#3D4451"
        panel_border_soft = "rgba(155, 138, 251, 0.2)"
        ghost_icon = UPLOAD_ICON_GHOST_SVG_DARK
        track_bg = "#1E2129"
        track_border = "#2D3340"

    switch_on = "#22C55E"
    switch_on_border = "#16A34A"

    css = (
        BUTTON_FIXES_CSS.replace("{{BTN_SURFACE}}", btn_surface)
        .replace("{{BTN_TEXT}}", btn_text)
        .replace("{{BTN_BORDER}}", btn_border)
        .replace("{{INPUT_BG}}", input_bg)
        .replace("{{PANEL_BORDER}}", panel_border)
        .replace("{{PANEL_BORDER_SOFT}}", panel_border_soft)
        .replace("{{GHOST_ICON}}", ghost_icon)
        .replace("{{SWITCH_ON}}", switch_on)
        .replace("{{SWITCH_ON_BORDER}}", switch_on_border)
        .replace("{{TRACK_BG}}", track_bg)
        .replace("{{TRACK_BORDER}}", track_border)
    )
    st.markdown(css, unsafe_allow_html=True)
