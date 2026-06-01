# Daypo Extractor

**Herramienta web local** para extraer preguntas, opciones, respuestas correctas e imágenes de cualquier test público de [Daypo](https://www.daypo.com) y exportarlos automáticamente a documentos Word (.docx) organizados por carpetas.

---

## ¿Qué hace?

Dado uno o varios enlaces de Daypo, la herramienta:

1. Se conecta directamente a la API interna de Daypo para descargar los datos del test (sin necesidad de navegar manualmente por la web).
2. Descifra automáticamente cuál es la respuesta correcta de cada pregunta.
3. Descarga las imágenes asociadas a cada pregunta desde los servidores de Daypo.
4. Genera un documento Word por cada test, con el enunciado en negrita, las imágenes incrustadas y la opción correcta marcada con **(correcta)**.
5. Si se introducen varios enlaces, genera además un **documento Word unificado** con todos los tests seguidos.
6. Empaqueta todo en un archivo ZIP listo para descargar.

### Estructura del ZIP resultante

```
Banco_de_Preguntas_Daypo.zip
│
├── DOCUMENTO_TODOS_LOS_TEMAS_UNIDOS.docx   ← Todos los tests en un solo Word (solo si hay varios enlaces)
│
├── Tema 1 Trauma/
│   ├── Tema 1 Trauma.docx
│   ├── img_123456_0.jpg
│   └── img_123456_1.jpg
│
├── Tema 2 Trauma/
│   ├── Tema 2 Trauma.docx
│   └── img_789012_0.jpg
│
└── ...
```

---

## Requisitos

- **Python 3.8 o superior** instalado en el sistema ([descargar aquí](https://www.python.org/downloads/))
- Conexión a internet

> Las dependencias de Python (Streamlit, Requests, python-docx) se instalan automáticamente al ejecutar el script de arranque correspondiente a tu sistema operativo.

---

## Instalación y arranque

Elige el método según tu sistema operativo. **Solo tienes que hacer doble clic** en el script correspondiente la primera vez; él se encarga de instalar todo lo necesario y abrir la aplicación en tu navegador.

### Windows

Haz doble clic en el archivo:

```
windows_launcher.bat
```

O ejecuta este one-liner desde PowerShell o CMD (en la carpeta del proyecto):

```powershell
pip install streamlit requests python-docx -q && streamlit run daypo_extractor.py
```

### macOS

La primera vez, abre Terminal, navega a la carpeta del proyecto y ejecuta:

```bash
chmod +x macos_launcher.command && open macos_launcher.command
```

A partir de ahí, puedes hacer **doble clic** en `macos_launcher.command` directamente.

O ejecuta este one-liner desde Terminal:

```bash
pip3 install streamlit requests python-docx -q && python3 -m streamlit run daypo_extractor.py
```

### Linux

Dale permisos de ejecución y ejecútalo:

```bash
chmod +x linux_launcher.sh && ./linux_launcher.sh
```

O ejecuta el one-liner directamente:

```bash
pip3 install streamlit requests python-docx -q && python3 -m streamlit run daypo_extractor.py
```

---

## Uso de la aplicación

1. Ejecuta el lanzador de tu sistema operativo. Se abrirá automáticamente una pestaña en tu navegador (normalmente en `http://localhost:8501`).
2. Pega en el cuadro de texto uno o varios enlaces de Daypo, **uno por línea**:
   ```
   https://www.daypo.com/tema-1-trauma.html
   https://www.daypo.com/tema-2-trauma.html
   https://www.daypo.com/imagenes-trauma.html
   ```
3. Haz clic en **"Iniciar Extracción"**.
4. Espera a que la barra de progreso complete el proceso.
5. Descarga el archivo ZIP con el botón que aparecerá al finalizar.
6. Descomprime el ZIP y tendrás todos los documentos y carpetas listos.

---

## Archivos del proyecto

| Archivo | Descripción |
|---|---|
| `daypo_extractor.py` | Aplicación principal (interfaz web Streamlit + lógica de extracción) |
| `windows_launcher.bat` | Script de arranque para Windows |
| `macos_launcher.command` | Script de arranque para macOS |
| `linux_launcher.sh` | Script de arranque para Linux |
| `README.md` | Este manual |

---

## Notas técnicas

- La herramienta utiliza la API interna `load.php` de Daypo para obtener los datos del test en formato XML, evitando así el scraping de la interfaz gráfica.
- La respuesta correcta se determina a partir de la máscara de respuesta del XML (etiqueta `<c>`): la posición del dígito `2` indica la opción correcta.
- Las imágenes se descargan desde `https://www.daypo.com/testimages/{prefijo_3_digitos}/{id_test}_{num_imagen}.jpg`.
- Toda la ejecución es **100% local**: ningún dato sale de tu ordenador salvo las peticiones a Daypo para descargar el contenido del test.

---

## Aviso legal

Esta herramienta está diseñada para uso personal y educativo. Respeta los [Términos de Uso de Daypo](https://www.daypo.com/condiciones.html) y los derechos de autor de los creadores de los tests. No utilices esta herramienta para distribuir o comercializar el contenido extraído.
