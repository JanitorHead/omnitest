# Omnitest — Documento de traspaso (contexto para continuar el proyecto)

> **Versión actual: 1.0.0** — ver [CHANGELOG.md](CHANGELOG.md) para el detalle de cambios.
>
> Este documento pone en contexto a cualquier IA o desarrollador que continúe el
> proyecto. Resume la visión, el estado actual, las decisiones tomadas y los
> aprendizajes (sobre todo los dolorosos) para no repetir errores.

---

## 1. Qué es Omnitest (la visión)

**Omnitest** es una *navaja suiza / companion dashboard de estudio* para
estudiantes de carreras con mucho **examen tipo test** (Medicina y el MIR,
oposiciones, enfermería, derecho, etc.).

**Idea central:** coger preguntas tipo test estén **como estén** —enlaces de
Daypo, fotos de exámenes, PDFs escaneados, apuntes en Word, o texto pegado de
cualquier manera con artefactos— y convertirlas en **material de estudio limpio
y multiformato** con un clic.

Tagline: *"De cualquier fuente a tests para practicar."*
Icono/marca: 🎯 (la diana = acertar).

El proyecto **empezó** como "Daypo Extractor" (solo extraía un tipo de test de
una web) y ha **evolucionado** hacia esta visión de navaja suiza. El rebrand a
Omnitest refleja ese salto: ya no es sobre Daypo, es sobre *cualquier* fuente.

### Público y tono
- Hispanohablante (España sobre todo: MIR, oposiciones).
- UI en español. Mensajes claros, con emojis funcionales, sin jerga técnica
  innecesaria de cara al usuario.

---

## 2. Estado actual (qué hace HOY)

### Dos formas de ENTRADA de preguntas
1. **🔗 Daypo:** pegas enlaces (o texto que los contenga). Detecta los enlaces
   con regex, descarga el test vía el endpoint interno `/asps/load.php`,
   descifra la respuesta correcta (máscara numérica del XML) y baja las imágenes.
2. **🤖 IA (multi-API):** pegas texto desordenado **y/o** subes **fotos + PDFs +
   Word a la vez** (multi-fuente en una sola llamada). Proveedores: **Gemini**
   (multimodal), **Groq**, **Cerebras**, **Mistral**. Router automático + fallback
   si hay 429. La IA hace OCR, limpia artefactos y unifica todo. **Si la correcta
   no viene marcada, la deduce** con su conocimiento. Hay un **chat de correcciones**
   con fallback entre proveedores. Configuración en modal **⚙** con import/export JSON.

### Seis SALIDAS (todas desde un formato de datos común)
1. **📄 Word** (.docx) — con/sin respuestas, imágenes embebidas.
2. **🖨️ PDF** — con/sin respuestas.
3. **🧠 RemNote MCQ** — ZIP Markdown con sintaxis de tarjetas de opción múltiple.
4. **🃏 Anki** (.apkg) — nota interactiva: opciones barajadas cada repaso,
   feedback verde/rojo, modo claro/oscuro, el orden no cambia al girar la carta.
5. **🎯 Quiz interactivo** — mini-app HTML autocontenida y offline: selección de
   tests, navegación, **feedback inmediato** al responder, cuadrícula lateral de
   progreso (gris/verde/rojo), salto a preguntas, y pantalla final con %
   aciertos / fallos / sin responder. Persiste en localStorage.
6. **🖼️ Imágenes** — ZIP con todas las imágenes nombradas `{titulo}_{NNN}.jpg`.

Con varios tests: además ZIPs "por separado" (un .docx/.pdf por test) con
subcarpetas `Con_Respuesta/` y `Sin_Respuesta/`.

---

## 3. Arquitectura del código

Reestructurado de un único archivo de ~1600 líneas a un **paquete modular**:

```
app.py                 Punto de entrada Streamlit (single-page)
static/logo.svg        Logo
src/
  __init__.py          Metadatos (APP_NOMBRE, APP_VERSION, tagline)
  utils.py             nombre_archivo, generar_nombre_base, separar_opciones
  daypo.py             extraer_enlaces_daypo, obtener_imagen, extraer_test
  ai_import.py         Gemini REST: listar_modelos, _gemini_call, prompts
  ai_providers.py      Capa unificada Groq/Cerebras/Mistral/Gemini + fallback
  api_config.py        Config proveedores, import/export omnitest-config.json
  model_router.py      Router automático + plan de fallback
  exporters.py         Word/PDF/RemNote/Anki/imágenes + construir_resultado()
  quiz.py              generar_html_quiz (CSS+JS embebidos)
  ui/                  single_page, api_modal, styles, themes, faq, export_grid…
requirements.txt       streamlit, requests, python-docx, genanki, fpdf2
install.ps1 / .sh      Instaladores de un comando
CHANGELOG.md           Historial de versiones
README.md
HANDOFF.md             (este archivo)
```

### Formato de datos canónico (clave para entender todo)
Toda la app pasa "tests" en esta estructura. **Cualquier fuente nueva solo tiene
que producir esto, y automáticamente sirve para TODAS las salidas:**

```python
{
    "titulo": str,
    "preguntas": [
        {
            "enunciado": str,
            "opciones": [(texto: str, es_correcta: bool), ...],
            "img_bytes": bytes | None,
            "img_nombre": str | None,
        },
        ...
    ],
}
```

`construir_resultado(tests)` recibe una lista de estos dicts y genera **todos**
los formatos de golpe, devolviendo un dict que se guarda en
`st.session_state["resultado"]` y alimenta la pantalla de descargas.

### Flujo de la UI
- **Single-page** (`src/ui/single_page.py`): flujo `entrada → revision → export`.
- Modal **⚙** para APIs; FAQ al pie de entrada; tema claro/oscuro.
- `construir_resultado()` al pulsar Exportar; pantalla de descargas con grid de formatos.

---

## 4. Decisiones técnicas importantes (y por qué)

### Gemini: REST directo, SIN SDK de Google
**Aprendizaje doloroso:** los SDKs `google-generativeai` y `google-genai`
enrutan internamente a la API `v1beta`, que da **404** con muchos modelos
actuales. La solución que funciona es llamar directamente al **REST API**:
```
POST https://generativelanguage.googleapis.com/{v1|v1beta}/models/{modelo}:generateContent
Header: x-goog-api-key: <key>
Body:   {"contents":[{"parts":[{"text":...} | {"inlineData":{mimeType,data(base64)}}]}]}
```
- Solo usa `requests` (sin dependencias extra).
- Intenta `v1` y si 404 cae a `v1beta`.
- Imágenes/PDF van como `inlineData` base64. Word se convierte a texto antes.

### Modelos "thinking" (2.5, 3.x)
Devuelven varias `parts`: una con el razonamiento (`thought: true`) y otra con
la respuesta. **Hay que concatenar SOLO las parts que NO son thought**, o lees el
"pensamiento" vacío y crees que no hay preguntas. Maneja también `MAX_TOKENS`.

### Errores 429 (cuota) — MUY importante para el usuario
- El tier **gratuito / de créditos** de Gemini comparte cuota y a menudo da
  **`quotaValue: 0`** en ciertos modelos → 429 al primer intento aunque no hayas
  usado nada. **No es bug de la app.**
- Modelos `preview`/imagen/tts/pro suelen tener cuota 0 en gratuito. Los estables
  (`gemini-2.5-flash-lite`, `gemini-2.5-flash`, `gemini-flash-latest`) funcionan.
- Solución real: **añadir método de pago** en Google AI Studio (céntimos por
  examen). Tener créditos ≠ pago activo.
- La app incluye **🩺 Diagnóstico de modelos**: hace un ping mínimo a cada modelo
  y dice cuál funciona AHORA, autoseleccionando uno estable que vaya.
- Retry con backoff exponencial + jitter; distingue 429-CERO (cuota 0) vs
  429-DIARIO vs rate-limit por minuto, con mensajes específicos.
- La API REST de Gemini NO expone cuota restante; solo hay un contador local de
  peticiones de la sesión + enlace a ai.dev/rate-limit.

### Prompt de extracción
La regla clave: si la correcta está marcada (*, círculo, (C), "respuesta: X"…)
úsala; **si no, dedúcela** con conocimiento experto (siempre elige una). Nunca
descartar preguntas por no estar marcadas. (Un bug pasado descartaba TODAS las
preguntas de examen porque no traían marca.)

### RemNote
Formato exacto que funciona (tras varias iteraciones):
```
- **Enunciado
**![](images/img.jpg) >>A)
    - Opción correcta (va primera)
    - Opción incorrecta
```
Las opciones son items de lista indentados, NO tabs. La imagen va pegada al
enunciado en negrita.

### Anki
Note type custom `genanki.Model` con HTML/CSS/JS: Fisher-Yates shuffle guardado
en `sessionStorage` para que NO se re-baraje al girar la carta. Si cambias la
plantilla, **sube el model id** para forzar reimport (va por 1607392324).

### PDF (fpdf2)
Márgenes A4 explícitos (20mm), `set_x()` antes de cada `multi_cell`, y try/except
en cada celda para evitar el error "Not enough horizontal space".

### Privacidad
El usuario no quiere que aparezca ningún correo suyo en commits. Usar el email
noreply de GitHub. (Hubo que reescribir historial una vez por un gmail expuesto.)

---

## 5. Despliegue

- **Streamlit Community Cloud**, main file = `app.py`.
- Repo: **github.com/JanitorHead/omnitest** (renombrado desde `extractor-daypo`).
- **Aprendizaje:** al renombrar el repo o borrar+recrear la app, el subdominio
  borrado queda reservado un rato → da "You do not have access / does not exist".
  Solución: usar un subdominio nuevo o esperar. El primer build tarda 2-5 min;
  no abrir la URL antes de que termine.
- Alternativas si Streamlit da guerra: Hugging Face Spaces, o local con los
  instaladores de un clic.

---

## 6. Ideas / posibles próximos pasos (no implementado)

Ideas alineadas con la visión de "companion dashboard de estudio". Para validar
con el usuario antes de construir:

- **Persistencia / biblioteca de tests:** guardar tests generados (cuenta de
  usuario, o export/import de un "paquete Omnitest") en vez de regenerar siempre.
- **Estadísticas de estudio:** que el quiz registre histórico de aciertos por
  tema/pregunta a lo largo del tiempo (no solo la sesión).
- **Repetición espaciada nativa** en el quiz (estilo Anki) sin salir de Omnitest.
- **Modo "examen"** cronometrado con nota final tipo MIR (penalización por fallo).
- **Detección de duplicados / fusión** de preguntas al combinar muchas fuentes.
- **Más fuentes de entrada:** otras webs de tests, Quizlet, CSV/Excel, etc.
- **Edición manual** de preguntas en la propia UI (no solo vía chat de IA).
- **Internacionalización** (i18n) si se quiere abrir a inglés.
- **Tests por categorías/asignaturas** y filtrado en el quiz.

---

## 7. Cómo arrancar en local (para la IA/dev que continúe)

```bash
git clone https://github.com/JanitorHead/omnitest.git
cd omnitest
pip install -r requirements.txt
streamlit run app.py
```

Para probar el pipeline de exportación sin UI:
```python
from src.exporters import construir_resultado
test = {"titulo": "Demo", "preguntas": [
    {"enunciado": "¿2+2?", "opciones": [("4", True), ("5", False)],
     "img_bytes": None, "img_nombre": None}
]}
res = construir_resultado([test])   # genera word/pdf/anki/remnote/quiz/imágenes
```

La IA debe producir el formato canónico (sección 3) desde cualquier fuente nueva
y el resto sale gratis.

---

## 8. Estilo de trabajo que esperaba el usuario

- Cambios coherentes y commiteados con mensajes descriptivos (co-author Claude).
- Commitear/pushear cuando se completa algo; rama main del repo.
- Explicaciones claras en español, sin marear; ir al grano con la causa real de
  los problemas (el usuario valora entender el "por qué", p. ej. el lío del 429).
- No exponer datos personales en el repo.
