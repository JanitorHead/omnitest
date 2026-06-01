# Daypo Extractor

**Herramienta web local** para extraer preguntas, opciones, respuestas correctas e imágenes de cualquier test público de [Daypo](https://www.daypo.com) y exportarlos automáticamente a documentos Word (.docx) organizados por carpetas.

> Desarrollada con Python y Streamlit. Se ejecuta 100% en tu ordenador — tus datos no salen a ningún servidor externo.

---

## ¿Qué hace?

Dado uno o varios enlaces de Daypo, la herramienta:

1. Se conecta a la API interna de Daypo para descargar los datos del test (sin necesidad de navegar manualmente por la web).
2. Descifra automáticamente cuál es la respuesta correcta de cada pregunta.
3. Descarga las imágenes asociadas a cada pregunta desde los servidores de Daypo.
4. Genera un documento Word por cada test, con el enunciado en negrita, la imagen incrustada y la opción correcta marcada con **(correcta)**.
5. Si se introducen varios enlaces, genera además un **documento Word unificado** con todos los tests seguidos.
6. Empaqueta todo en un archivo ZIP listo para descargar con un solo clic.

---

## Requisito único: Python

Necesitas tener **Python 3.8 o superior** instalado en tu ordenador.  
Las dependencias del proyecto (Streamlit, Requests, python-docx) se instalan automáticamente al usar los scripts de lanzamiento.

- Descarga Python: [https://www.python.org/downloads/](https://www.python.org/downloads/)
- **Windows**: durante la instalación, marca la casilla **"Add Python to PATH"**.

---

## Instalación y uso

### Paso 1 — Descarga el proyecto

Clona el repositorio o descárgalo como ZIP desde el botón verde **Code → Download ZIP**.

```bash
git clone https://github.com/JanitorHead/extractor-daypo.git
cd extractor-daypo
```

### Paso 2 — Arranca la aplicación

Elige el script correspondiente a tu sistema operativo y ejecútalo. **Instala las dependencias automáticamente y abre la app en el navegador.**

#### Windows
Haz **doble clic** en `windows_launcher.bat`

O desde PowerShell / CMD:
```bat
windows_launcher.bat
```

#### macOS
La primera vez necesitas dar permiso de ejecución al script. Abre una terminal en la carpeta del proyecto y ejecuta:
```bash
chmod +x macos_launcher.command
```
Después, **doble clic** en `macos_launcher.command` (o ejecútalo desde la terminal).

Si macOS bloquea el archivo, ve a **Preferencias del Sistema → Privacidad y Seguridad → Permitir de todas formas**.

#### Linux
```bash
chmod +x linux_launcher.sh
./linux_launcher.sh
```

---

### Paso 3 — Usa la interfaz web

1. Se abrirá automáticamente una pestaña en tu navegador en `http://localhost:8501`.
2. Pega tus enlaces de Daypo en el cuadro de texto (uno por línea).
3. Haz clic en **Iniciar Extracción**.
4. Cuando termine, pulsa **Descargar todos los Tests (ZIP)**.

> **Importante:** no cierres la ventana de terminal mientras usas la app. Es el servidor local que la mantiene activa.

---

## Estructura del ZIP resultante

```
Banco_de_Preguntas_Daypo.zip
│
├── DOCUMENTO_TODOS_LOS_TEMAS_UNIDOS.docx   ← Solo aparece si introduces varios enlaces
│
├── Tema 1 Trauma/
│   ├── Tema 1 Trauma.docx
│   ├── img_1073001_0.jpg
│   └── img_1073001_1.jpg
│
├── Tema 2 Trauma/
│   ├── Tema 2 Trauma.docx
│   └── img_1073002_0.jpg
│
└── ...
```

---

## Ejemplo de enlaces (Traumatología 2025)

Puedes pegar este bloque directamente en la aplicación:

```
https://www.daypo.com/tema-1-trauma.html
https://www.daypo.com/tema-2-trauma.html
https://www.daypo.com/tema-3-trauma.html
https://www.daypo.com/tema-4-trauma.html
https://www.daypo.com/tema-5-trauma.html
https://www.daypo.com/tema-7-truma-tumores.html
https://www.daypo.com/tema-10-trauma.html
https://www.daypo.com/tema-13-trauma.html
https://www.daypo.com/tema-14-trauma.html
https://www.daypo.com/tema-15-trauma.html
https://www.daypo.com/tema-19-trauma.html
https://www.daypo.com/tema-22-trauma.html
https://www.daypo.com/tema-23-trauma.html
https://www.daypo.com/tema-25-trauma.html
https://www.daypo.com/tema-26-trauma.html
https://www.daypo.com/tema-27-trauma.html
https://www.daypo.com/tema-28-trauma.html
https://www.daypo.com/tema-29-trauma.html
https://www.daypo.com/tema-32-trauma.html
https://www.daypo.com/tema-33-trauma.html
https://www.daypo.com/tema-34-35-trauma.html
https://www.daypo.com/imagenes-trauma.html
```

---

## Archivos del proyecto

| Archivo | Descripción |
|---|---|
| `daypo_extractor.py` | Aplicación principal (Streamlit) |
| `windows_launcher.bat` | Script de arranque para Windows |
| `macos_launcher.command` | Script de arranque para macOS |
| `linux_launcher.sh` | Script de arranque para Linux |

---

## Notas técnicas

- La herramienta accede al endpoint `/asps/load.php` de Daypo, que es el mismo que usa el navegador internamente al cargar un test. No se realiza ningún tipo de bypass ni automatización del navegador.
- Las imágenes se descargan desde `https://www.daypo.com/testimages/{prefijo}/{id}_{num}.jpg`.
- La respuesta correcta está codificada en el XML del test mediante una máscara numérica (ej: `2111` indica que la primera opción es la correcta).
- Uso responsable: esta herramienta es para uso personal y educativo. Respeta los Términos de Uso de Daypo y los derechos de autor de los creadores de los tests.
