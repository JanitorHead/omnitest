"""Preguntas frecuentes e instrucciones — pie de la pantalla de entrada."""
import streamlit as st


def render_faq() -> None:
    with st.container(border=False):
        st.markdown(
            '<div class="omni-faq-marker"></div>'
            '<div class="omni-faq-spacer" aria-hidden="true"></div>'
            '<p class="omni-faq-title">Preguntas frecuentes</p>',
            unsafe_allow_html=True,
        )

        with st.expander("¿Qué hace Omnitest?", expanded=False):
            st.markdown(
                "Omnitest convierte preguntas tipo test **desordenadas o mal formateadas** "
                "en material limpio listo para estudiar. Acepta enlaces de Daypo, PDFs escaneados, "
                "fotos de exámenes, Word o texto pegado a medias.\n\n"
                "El flujo es simple: **elige fuente → convierte → revisa → exporta**. "
                "Puedes descargar Word, PDF, Anki, RemNote, un quiz HTML offline o un ZIP de imágenes."
            )

        with st.expander("Modo Daypo — enlaces directos", expanded=False):
            st.markdown(
                "1. En **Fuente**, deja seleccionado **Daypo**.\n"
                "2. Pega uno o varios enlaces a tests de daypo.com (también vale un texto que los contenga).\n"
                "3. Pulsa **Convertir**. Omnitest descarga las preguntas, descifra la respuesta correcta "
                "y baja las imágenes.\n"
                "4. Revisa el resultado y pulsa **Exportar →** para elegir formato.\n\n"
                "No necesitas configurar APIs: la extracción es directa desde Daypo."
            )

        with st.expander("Modo IA — PDF, fotos, Word y texto", expanded=False):
            st.markdown(
                "1. Configura al menos una API en **⚙** (Google Gemini, Groq, Cerebras o Mistral). "
                "Todas tienen plan gratuito.\n"
                "2. En **Fuente**, elige **IA: PDF · foto · texto**.\n"
                "3. Sube archivos (PDF, JPG, PNG, Word…) y/o pega texto desordenado.\n"
                "4. Pulsa **Convertir**. La IA extrae preguntas, limpia OCR y puede deducir la correcta "
                "si no viene marcada.\n"
                "5. En la revisión puedes usar **Ajustar con IA** para pedir cambios concretos "
                "(«la 3 es la B», «quita duplicados»…).\n\n"
                "**PDF e imágenes** requieren **Google Gemini** (multimodal). Con Groq, Cerebras o Mistral "
                "puedes usar texto y Word."
            )

        with st.expander("¿Qué formatos puedo exportar?", expanded=False):
            st.markdown(
                "| Formato | Para qué |\n"
                "|---|---|\n"
                "| **Word / PDF** | Documento imprimible, con o sin respuestas marcadas |\n"
                "| **RemNote MCQ** | ZIP en Markdown para importar tarjetas de opción múltiple |\n"
                "| **Anki (.apkg)** | Mazo con opciones barajadas y feedback al responder |\n"
                "| **Quiz HTML** | Mini-app offline en el navegador, sin instalar nada |\n"
                "| **Imágenes (ZIP)** | Todas las imágenes de los tests, nombradas por pregunta |\n\n"
                "Si tienes varios tests, también puedes bajar un ZIP con un archivo por test."
            )

        with st.expander("¿Cómo configuro las APIs de IA?", expanded=False):
            st.markdown(
                "1. Pulsa **⚙** arriba a la derecha.\n"
                "2. Pega la clave de cada proveedor que quieras usar (hay enlace «¿Dónde consigo la key?»).\n"
                "3. Pulsa **Probar** — se verifica la conexión y se recopilan los modelos disponibles.\n"
                "4. Activa **Usar esta API** en las que quieras tener disponibles.\n"
                "5. Omnitest elige automáticamente el modelo más eficiente en cada conversión.\n\n"
                "Las claves **solo viven en tu sesión** del navegador; Omnitest no las guarda en servidor. "
                "Para no pegarlas cada vez, usa el archivo JSON del modal (ver explicación en ⚙)."
            )

        with st.expander("¿Qué pasa si la IA da error o se queda sin cuota?", expanded=False):
            st.markdown(
                "Si una API alcanza el límite gratuito (error 429), verás un aviso en pantalla. "
                "Espera unos minutos o añade otra clave en **⚙**.\n\n"
                "Omnitest prueba otros proveedores y modelos automáticamente si el primero falla. "
                "Tener **varias APIs activas** mejora la fiabilidad."
            )
