# Daypo Extractor

Extrae preguntas, opciones, respuestas correctas e imagenes de cualquier test publico de [Daypo](https://www.daypo.com) y exportalos a **Word**, **RemNote MCQ** o **Anki** con un solo clic.

---

## Usar online (sin instalar nada)

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://extractor-daypo.streamlit.app)

La aplicacion esta desplegada gratuitamente en Streamlit Community Cloud. Abrela directamente en el navegador, sin instalar Python ni ninguna dependencia:

**https://extractor-daypo.streamlit.app**

> La app se ejecuta en la nube. Tu navegador envia los enlaces a Daypo y recibe los archivos; ningun dato tuyo se almacena.

---

## Instalar en local (opcional)

Si prefieres ejecutarla en tu propio ordenador, usa el instalador de un solo comando para tu sistema.

### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/JanitorHead/extractor-daypo/main/install.ps1 | iex
```

> Si PowerShell muestra un error de politica de ejecucion, ejecuta primero:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

### macOS / Linux (Terminal)

```bash
curl -fsSL https://raw.githubusercontent.com/JanitorHead/extractor-daypo/main/install.sh | bash
```

> El script detecta automaticamente tu distribucion (Debian/Ubuntu, Fedora/RHEL, Arch) e instala Python con el gestor de paquetes correspondiente.

---

## Que hace?

Dado uno o varios enlaces de Daypo (o cualquier texto que los contenga), la herramienta:

1. Detecta automaticamente los enlaces de Daypo en el texto pegado.
2. Se conecta a la API interna de Daypo y descifra cual es la respuesta correcta de cada pregunta.
3. Descarga las imagenes asociadas a cada pregunta.
4. Genera tres tipos de exportacion con un solo clic:

| Exportacion | Descripcion |
|---|---|
| **ZIP Word** | Un `.docx` por test con enunciados en negrita, imagenes incrustadas y la opcion correcta marcada en verde. Incluye un documento unificado si hay varios tests. |
| **ZIP RemNote MCQ** | Markdown con sintaxis `>>A)` listo para importar en RemNote (Import → Markdown). Preguntas en negrita, imagenes en linea. |
| **Anki (.apkg)** | Mazo con tipo de nota MCQ interactivo: botones clicables, orden aleatorio en cada repaso, feedback verde/rojo al girar. Compatible con modo claro y oscuro. |

---

## Uso

1. Pega tus enlaces de Daypo en el cuadro de texto. Puedes pegar los enlaces directamente, uno por linea, o cualquier texto que los contenga (correos, documentos, listas...).
2. La app muestra en tiempo real cuantos enlaces ha detectado.
3. Pulsa **Iniciar Extraccion**.
4. Cuando termine, descarga el formato que necesites.

---

## Como importar en RemNote

1. Descarga **Daypo_RemNote_MCQ.zip**.
2. RemNote → icono de ajustes → **Importar** → **Markdown** → sube el ZIP.
3. Los tests apareceran como documentos con tarjetas MCQ e imagenes incrustadas.
4. RemNote baraja el orden de las opciones al practicar.

## Como importar en Anki

1. Descarga **Daypo_Anki.apkg**.
2. Abre Anki → **Archivo** → **Importar** → selecciona el archivo.
3. Se crea el mazo **Daypo Extractor** con el tipo de nota **Daypo MCQ Interactive**.
4. Anverso: enunciado + imagen + opciones en orden aleatorio. Reverso: respuesta correcta en verde, eleccion incorrecta en rojo.

---

## Ejemplo de enlaces

Puedes pegar este bloque directamente en la aplicacion:

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

| Archivo | Descripcion |
|---|---|
| `daypo_extractor.py` | Aplicacion principal (Streamlit) |
| `requirements.txt` | Dependencias para Streamlit Cloud y entornos virtuales |
| `install.ps1` | Instalador one-liner para Windows (PowerShell) |
| `install.sh` | Instalador one-liner para macOS y Linux (bash) |
| `windows_launcher.bat` | Lanzador alternativo para Windows (requiere Python instalado) |
| `macos_launcher.command` | Lanzador alternativo para macOS (requiere Python instalado) |
| `linux_launcher.sh` | Lanzador alternativo para Linux (requiere Python instalado) |

---

## Notas tecnicas

- La herramienta accede al endpoint `/asps/load.php` de Daypo, el mismo que usa el navegador al cargar un test.
- Las imagenes se descargan desde `https://www.daypo.com/testimages/{prefijo}/{id}_{num}.jpg`.
- La respuesta correcta esta codificada en el XML mediante una mascara numerica (ej: `2111` indica que la primera opcion es la correcta).
- Uso responsable: esta herramienta es para uso personal y educativo. Respeta los Terminos de Uso de Daypo y los derechos de autor de los creadores de los tests.
