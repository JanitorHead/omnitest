# Changelog

Todos los cambios relevantes de Omnitest se documentan aquí.
El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el proyecto usa [Versionado Semántico](https://semver.org/lang/es/).

---

## [1.0.2] — 2026-06-02

Iteración de pulido UI tras **1.0.1**: progreso legible, exportación Word/PDF coherente en claro/oscuro, modal de APIs alineado con Streamlit 1.58 y FAQ sin artefactos en las esquinas.

### Añadido

- Leyenda bajo la rejilla de exportación explicando **Unificados**, **Separados** (un ZIP con un documento por test) y **con/sin respuestas**.
- Etiquetas de progreso con **mensaje + % + ETA** en extracción IA y en barras de preview/export.
- Desarrollo local: Streamlit en `localhost` con tema oscuro por defecto en `config.toml`.

### Cambiado

- **Word/PDF**: popover + botón partido sustituido por **selectbox + Descargar** secundario (más claro y estable).
- Etiquetas de export: «Todo junto» / «Un archivo por test» → **Unificados** / **Separados**.
- Header con **contenedor horizontal flex** (logo · espaciador · tema · APIs), responsive en móvil y desktop.
- CSS de progreso apuntando a `[data-testid="stProgressBarTrack"]` (Streamlit 1.58), sin recortar el texto del label.

### Corregido

- Texto **ilegible encima de la barra de progreso** (solo se veían los pies de las letras) en conversión, preview y export.
- **Selectbox Word/PDF** en modo oscuro: fondo blanco y menú desalineado (selectores globales; `.export-grid` no envuelve widgets en el DOM de Streamlit).
- **Campos API key** en el modal ⚙: inputs oscuros en dark mode (`stTextInputRootElement`, Streamlit 1.58).
- **Icono ojo** del password: alineado a la **derecha** dentro del cuadro, sin tapar el texto (estructura `base-input` interna).
- **FAQ expanders**: bordes duplicados y «mordisco» en esquinas; ahora un solo borde como el resto de paneles.
- Preview/revisión: resumen de preguntas legible tras corregir estilos de progreso compartidos.

### Notas

- El toggle claro/oscuro de la app sigue mandando sobre los colores finos vía CSS inyectado; el tema nativo de Streamlit en `config.toml` evita widgets blancos por defecto en dark.
- Para probar en local: `streamlit run app.py` (abre navegador en localhost).

---

## [1.0.1] — 2026-06-02

Mejoras de interfaz móvil y desktop tras el lanzamiento inicial.

### Cambiado

- Header con **3 columnas planas** (wordmark · tema · APIs) y grid `1fr auto auto` en **todos los anchos** — los botones ☀️ y ⚙️ quedan juntos también en desktop.
- **Emojis unificados** en la toolbar: ☀️ / 🌙 (tema) y ⚙️ (APIs), mismo estilo en móvil y desktop.
- Logo y título **más grandes en móvil** (8.75rem / 2.125rem).

### Corregido

- Botones de tema y configuración **apilados o separados** en pantallas estrechas o anchas.
- **Scroll horizontal fantasma** en smartphone (overflow de márgenes negativos de Streamlit).
- Toolbar alineada **dentro del margen del contenido**, no pegada al borde de la pantalla.

### Notas

- Si **omnitest.streamlit.app** sigue mostrando la UI antigua, Streamlit Cloud puede tardar unos minutos en redeployar tras el push; prueba recarga forzada (Ctrl+Shift+R).
- El preview de WhatsApp/Telegram usa `og:description` generado por **Streamlit Cloud desde el README** (sin markdown en negrita en frases clave, o el texto se rompe).

---

## [1.0.0] — 2026-06-02

Primera versión pública con flujo single-page, multi-API y exportación completa.

### Añadido

- **Flujo single-page** estilo iLovePDF: entrada → revisión → exportación, sin pestañas.
- **Multi-API de IA**: Google Gemini, Groq, Cerebras y Mistral con router automático que elige el modelo más adecuado por trabajo.
- **Fallback inteligente** entre proveedores y modelos si hay error 429, cuota diaria agotada o fallo de red.
- **Modal de configuración ⚙** con prueba de claves, toggles por proveedor y recopilación real de modelos vía API.
- **Import/export JSON** (`omnitest-config.json`) para restaurar claves en segundos; validación automática al importar.
- **Modo Daypo** sin IA: extracción directa de enlaces con imágenes y respuesta correcta descifrada.
- **Modo IA multimodal**: texto, Word, PDF e imágenes en una sola conversión (PDF/imagen requiere Gemini).
- **Chat de correcciones** en la revisión con fallback entre proveedores configurados.
- **Seis salidas**: Word, PDF, RemNote MCQ, Anki (.apkg), quiz HTML offline e imágenes ZIP.
- Opciones de exportación: todo junto o ZIP por test; con o sin respuestas marcadas.
- **Tema claro / oscuro** con estética RemNote (lavanda, Inter, bordes finos).
- **FAQ** desplegable al pie de la pantalla de entrada.
- **Wordmark** con logo SVG y hero con slogan de producto.
- Scripts de instalación en un comando (`install.ps1`, `install.sh`) y lanzadores por SO.

### Cambiado

- Reorganización modular del código: `src/ui/`, `api_config.py`, `ai_providers.py`, `model_router.py`.
- La IA ya no depende solo de Gemini: Groq/Cerebras/Mistral para texto; Gemini reservado a multimodal.
- Mensajes de progreso en tiempo real durante extracción (`st.status` con log detallado).
- Tras importar JSON, la página principal se actualiza al instante (sin pulsar «Listo»).

### Corregido

- Fallback ya no prueba decenas de modelos Gemini con cuota agotada (máx. 2 modelos/proveedor; salto de proveedor en 429).
- Router de texto solo prefiere proveedores ligeros (Groq → Cerebras → Mistral) antes que Gemini.
- Etiquetas de radio invisibles en modo claro en la pantalla de exportación.
- Modal JSON: la config importada ya no se pierde ni se reabre sola; toggles sincronizados en verde.
- Correcciones IA con fallback si el proveedor principal falla (p. ej. 401 Mistral).
- Botón «Editar» ya no borra el preview ni resetea el flujo.
- Cerebras: extracción usa `reasoning` cuando falta `content` en la respuesta.

---

## [0.2.0] — 2025 (rebrand Omnitest)

### Añadido

- Rebrand de «Daypo Extractor» a **Omnitest**.
- Quiz HTML con feedback inmediato, cuadrícula de progreso y pantalla de resultados.
- Paquete modular (`src/daypo.py`, `ai_import.py`, `exporters.py`, `quiz.py`).

### Corregido

- La IA deduce la respuesta correcta cuando no viene marcada (antes omitía todas las preguntas).
- Modelos *thinking* de Gemini: concatenación correcta de parts sin incluir el razonamiento vacío.
- Migración a REST API directa de Gemini (sin SDK `google-generativeai` / `google-genai`).

---

## [0.1.0] — 2025 (orígenes)

### Añadido

- Extracción de tests desde Daypo (`/asps/load.php`).
- Exportación Word, PDF, RemNote, Anki e imágenes.
- Importación IA con Gemini (texto + imágenes + PDF + Word).
- Chat de correcciones, diagnóstico de modelos y manejo de errores 429.
- Despliegue en Streamlit Community Cloud.

---

[1.0.2]: https://github.com/JanitorHead/omnitest/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/JanitorHead/omnitest/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/JanitorHead/omnitest/compare/v0.2.0...v1.0.0
[0.2.0]: https://github.com/JanitorHead/omnitest/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/JanitorHead/omnitest/releases/tag/v0.1.0
