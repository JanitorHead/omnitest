# Daypo Extractor

**Herramienta web local** para extraer preguntas, opciones, respuestas correctas e imagenes de cualquier test publico de [Daypo](https://www.daypo.com) y exportarlos automaticamente a documentos Word (.docx) organizados por carpetas.

> Desarrollada con Python y Streamlit. Se ejecuta 100% en tu ordenador - tus datos no salen a ningun servidor externo.

---

## Instalacion con un solo comando

Abre la terminal de tu sistema, pega el comando correspondiente y pulsa Enter. El script instalara Python si no lo tienes, descargara la aplicacion y la abrira automaticamente en el navegador.

### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/JanitorHead/extractor-daypo/main/install.ps1 | iex
```

> Si PowerShell muestra un error de politica de ejecucion, ejecuta primero:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

### macOS (Terminal)

```bash
curl -fsSL https://raw.githubusercontent.com/JanitorHead/extractor-daypo/main/install.sh | bash
```

### Linux (terminal)

```bash
curl -fsSL https://raw.githubusercontent.com/JanitorHead/extractor-daypo/main/install.sh | bash
```

> El script detecta automaticamente tu distribucion (Debian/Ubuntu, Fedora/RHEL, Arch) e instala Python con el gestor de paquetes correspondiente.

---

## Que hace?

Dado uno o varios enlaces de Daypo, la herramienta:

1. Se conecta a la API interna de Daypo para descargar los datos del test (sin necesidad de navegar manualmente por la web).
2. Descifra automaticamente cual es la respuesta correcta de cada pregunta.
3. Descarga las imagenes asociadas a cada pregunta desde los servidores de Daypo.
4. Genera un documento Word por cada test, con el enunciado en negrita, la imagen incrustada y la opcion correcta marcada con **(correcta)**.
5. Si se introducen varios enlaces, genera ademas un **documento Word unificado** con todos los tests seguidos.
6. Empaqueta todo en un archivo ZIP listo para descargar con un solo clic.

---

## Requisito unico: Python

Los scripts de instalacion se encargan de todo automaticamente. Si prefieres instalar Python manualmente:

- Descarga Python: [https://www.python.org/downloads/](https://www.python.org/downloads/)
- **Windows**: durante la instalacion, marca la casilla **"Add Python to PATH"**.

---

## Uso de la aplicacion

Tras ejecutar el comando de instalacion, se abrira automaticamente una pestana en tu navegador en `http://localhost:8501`.

1. Pega tus enlaces de Daypo en el cuadro de texto (uno por linea).
2. Haz clic en **Iniciar Extraccion**.
3. Cuando termine, pulsa **Descargar ZIP con todos los tests**.

> **Importante:** no cierres la ventana de terminal mientras usas la app. Es el servidor local que la mantiene activa.

---

## Estructura del ZIP resultante

```
Banco_de_Preguntas_Daypo.zip
|
+-- TODOS_LOS_TESTS_UNIDOS.docx        Solo aparece si introduces varios enlaces
|
+-- Tema 1 Trauma/
|   +-- Tema 1 Trauma.docx
|   +-- img_1073001_0.jpg
|   +-- img_1073001_1.jpg
|
+-- Tema 2 Trauma/
|   +-- Tema 2 Trauma.docx
|   +-- img_1073002_0.jpg
|
+-- ...
```

---

## Ejemplo de enlaces (Traumatologia 2025)

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
| `install.ps1` | Instalador one-liner para Windows (PowerShell) |
| `install.sh` | Instalador one-liner para macOS y Linux (bash) |
| `windows_launcher.bat` | Lanzador alternativo para Windows (requiere Python instalado) |
| `macos_launcher.command` | Lanzador alternativo para macOS (requiere Python instalado) |
| `linux_launcher.sh` | Lanzador alternativo para Linux (requiere Python instalado) |

---

## Notas tecnicas

- La herramienta accede al endpoint `/asps/load.php` de Daypo, que es el mismo que usa el navegador internamente al cargar un test.
- Las imagenes se descargan desde `https://www.daypo.com/testimages/{prefijo}/{id}_{num}.jpg`.
- La respuesta correcta esta codificada en el XML del test mediante una mascara numerica (ej: `2111` indica que la primera opcion es la correcta).
- Uso responsable: esta herramienta es para uso personal y educativo. Respeta los Terminos de Uso de Daypo y los derechos de autor de los creadores de los tests.
