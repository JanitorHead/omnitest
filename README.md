# 🎯 Omnitest

**De cualquier fuente a tests para practicar.**

Omnitest es la navaja suiza de estudio para carreras con mucho examen tipo test
(Medicina, MIR, oposiciones, enfermería, derecho…). Coge tus preguntas estén
**como estén** —enlaces de Daypo, fotos de exámenes, PDFs escaneados, apuntes en
Word o texto pegado de cualquier manera— y las convierte en material limpio y
listo para estudiar en **5 formatos distintos**, incluido un **quiz interactivo**.

---

## Usar online (sin instalar nada)

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://omnitest.streamlit.app)

**https://omnitest.streamlit.app**

> La app corre en la nube. Tus datos no se almacenan; los archivos se generan al
> vuelo y se descargan a tu equipo.

---

## ¿Qué hace?

### Dos formas de meter preguntas

| Fuente | Cómo |
|---|---|
| 🔗 **Daypo** | Pega uno o varios enlaces (o cualquier texto que los contenga). Omnitest detecta los enlaces, descarga las preguntas, descifra la respuesta correcta y baja las imágenes. |
| 🤖 **IA (Gemini)** | Pega texto desordenado **y/o** sube **fotos, PDFs y Word** a la vez. La IA hace OCR, limpia artefactos y unifica todo. Si la respuesta correcta no viene marcada, **la deduce** con su conocimiento. Incluye un **chat de correcciones** para afinar el resultado antes de exportar. |

### Cinco formatos de salida (+ imágenes)

| Formato | Para qué |
|---|---|
| 📄 **Word** | Documento con preguntas, imágenes y la correcta marcada. Versión **con** o **sin** respuestas (para imprimir y responder a mano). |
| 🖨️ **PDF** | Igual que Word, en PDF. Con o sin respuestas. |
| 🧠 **RemNote MCQ** | ZIP en Markdown listo para importar como tarjetas de opción múltiple. |
| 🃏 **Anki (.apkg)** | Mazo con nota interactiva: opciones barajadas cada repaso, feedback verde/rojo, modo claro y oscuro. |
| 🎯 **Quiz interactivo** | Mini-app HTML autocontenida: elige tests, navega, feedback inmediato, cuadrícula de progreso y resultado final con porcentaje. **Funciona offline en cualquier navegador.** |
| 🖼️ **Imágenes** | ZIP con todas las imágenes nombradas por test. |

Con varios tests puedes descargar además un **ZIP con un archivo por test**
(carpetas `Con_Respuesta/` y `Sin_Respuesta/`).

---

## Instalar en local (opcional)

### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/JanitorHead/omnitest/main/install.ps1 | iex
```

> Si PowerShell se queja de la política de ejecución, ejecuta primero:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

### macOS / Linux (Terminal)

```bash
curl -fsSL https://raw.githubusercontent.com/JanitorHead/omnitest/main/install.sh | bash
```

El instalador descarga el proyecto, instala Python (si falta) y las dependencias,
y abre Omnitest en tu navegador.

### Manual

```bash
git clone https://github.com/JanitorHead/omnitest.git
cd omnitest
pip install -r requirements.txt
streamlit run app.py
```

---

## La IA y los errores de cuota (429)

La importación con IA usa la **API de Gemini** con tu propia clave (gratuita en
[aistudio.google.com](https://aistudio.google.com)). El tier gratuito tiene
límites por modelo que **a veces son 0** según tu cuenta o región.

Si ves un error **429**:

1. Pulsa **🩺 Diagnóstico de modelos** — prueba cada modelo y te dice cuál
   funciona ahora mismo en tu cuenta.
2. **Cambia de modelo:** cada uno tiene cuota independiente. Evita los `preview`.
3. Si ninguno funciona, **activa facturación** en Google AI Studio: es pago por
   uso (céntimos por examen) y los límites suben enormemente. *Tener créditos no
   equivale a tener pago activo.*

---

## Cómo importar los formatos

**RemNote:** descarga el ZIP → ajustes → Importar → Markdown → sube el ZIP.

**Anki:** doble clic en el `.apkg`. Las opciones salen barajadas en cada repaso;
clic para elegir, Espacio para revelar; el orden no cambia al girar la carta.

**Quiz:** abre el `.html` en cualquier navegador. Elige tests, responde (feedback
inmediato), navega con la cuadrícula y mira tu porcentaje al final. Guarda el
progreso en el navegador.

---

## Estructura del proyecto

```
app.py                 Punto de entrada (Streamlit)
src/
  __init__.py          Metadatos de la app
  utils.py             Nombres de archivo y utilidades comunes
  daypo.py             Extracción de tests de Daypo
  ai_import.py         Importación con IA (Gemini, REST)
  exporters.py         Word, PDF, RemNote, Anki, imágenes + orquestación
  quiz.py              Generador del quiz interactivo HTML
  ui.py                Componentes de interfaz (Streamlit)
requirements.txt       Dependencias
install.ps1 / .sh      Instaladores de un comando
*_launcher.*           Lanzadores locales (Windows / macOS / Linux)
```

---

## Notas técnicas

- **Daypo:** se usa el endpoint `/asps/load.php` (el mismo que el navegador). La
  respuesta correcta va codificada en una máscara numérica del XML.
- **IA:** llamada directa al REST API de Gemini (`v1`/`v1beta`), sin SDK de Google.
  Reintentos con backoff + jitter ante 429 y manejo de modelos *thinking*.
- **Uso responsable:** herramienta para uso personal y educativo. Respeta los
  términos de Daypo y los derechos de autor de los creadores de los tests.
