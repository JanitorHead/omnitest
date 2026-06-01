import streamlit as st
import requests
import re
import xml.etree.ElementTree as ET
import zipfile
import tempfile
import os
import base64
import json
from io import BytesIO
from docx import Document
from docx.shared import Inches, Pt, RGBColor
import genanki
from fpdf import FPDF

st.set_page_config(
    page_title="Daypo Extractor",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------

def limpiar_nombre_carpeta(texto: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", texto).strip()


def nombre_archivo(texto: str) -> str:
    return re.sub(r'\s+', '_', limpiar_nombre_carpeta(texto)).strip('_')


def obtener_imagen(id_test: str, num_imagen: str, url_origen: str) -> bytes | None:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": url_origen,
        "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    }
    prefijo = id_test[:3]
    url_imagen = f"https://www.daypo.com/testimages/{prefijo}/{id_test}_{num_imagen}.jpg"
    try:
        respuesta = requests.get(url_imagen, headers=headers, timeout=8)
        if respuesta.status_code == 200:
            return respuesta.content
    except requests.RequestException:
        pass
    return None


def procesar_pregunta(doc: Document, num: int, enunciado: str,
                      img_bytes: bytes | None, opciones: list[tuple[str, bool]]) -> None:
    parrafo = doc.add_paragraph()
    run = parrafo.add_run(f"{num}. {enunciado}")
    run.bold = True
    run.font.size = Pt(11)

    if img_bytes:
        doc.add_picture(BytesIO(img_bytes), width=Inches(3.5))

    for texto_opcion, es_correcta in opciones:
        parrafo_op = doc.add_paragraph()
        if es_correcta:
            run_op = parrafo_op.add_run(f"   - {texto_opcion}  (correcta)")
            run_op.bold = True
            run_op.font.color.rgb = RGBColor(0x1A, 0x73, 0x28)
        else:
            parrafo_op.add_run(f"   - {texto_opcion}")

    doc.add_paragraph()


def extraer_datos_test(url: str, headers_web: dict) -> tuple[str, str, list] | None:
    try:
        res_html = requests.get(url, headers=headers_web, timeout=10)
        res_html.raise_for_status()
        match = re.search(r"ntest\s*=\s*(\d+)", res_html.text)
        if not match:
            return None
        id_test = match.group(1)
    except requests.RequestException:
        return None

    try:
        res_xml = requests.post(
            "https://www.daypo.com/asps/load.php",
            data={"tes": id_test},
            headers=headers_web,
            timeout=10,
        )
        res_xml.raise_for_status()
        raiz = ET.fromstring(res_xml.text)
    except (requests.RequestException, ET.ParseError):
        return None

    nodo_titulo = raiz.find(".//t")
    titulo = nodo_titulo.text.strip() if (nodo_titulo is not None and nodo_titulo.text) else f"Test {id_test}"

    contenedor = raiz.find("c")
    if contenedor is None:
        return None

    preguntas_raw = contenedor.findall("c")
    preguntas = []

    for q in preguntas_raw:
        nodo_p = q.find("p")
        enunciado = nodo_p.text.strip() if nodo_p is not None and nodo_p.text else "Sin enunciado"

        nodo_b = q.find("b")
        num_imagen = nodo_b.text.strip() if nodo_b is not None and nodo_b.text else None

        nodo_c = q.find("c")
        mascara = nodo_c.text if nodo_c is not None and nodo_c.text else ""
        indice_correcta = mascara.find("2")

        nodo_r = q.find("r")
        opciones = []
        if nodo_r is not None:
            for idx, nodo_o in enumerate(nodo_r.findall("o")):
                texto = nodo_o.text.strip() if nodo_o.text else ""
                opciones.append((texto, idx == indice_correcta))

        preguntas.append({
            "enunciado": enunciado,
            "num_imagen": num_imagen,
            "opciones": opciones,
        })

    return id_test, titulo, preguntas


def extraer_enlaces_daypo(texto: str) -> list[str]:
    patron = r'https?://(?:www\.)?daypo\.com/[^\s\n\r"\'<>()\[\]{}]+'
    candidatos = re.findall(patron, texto)
    candidatos = [re.sub(r'[.,;:!?]+$', '', e) for e in candidatos]
    vistos: set[str] = set()
    resultado = []
    for e in candidatos:
        if e not in vistos:
            vistos.add(e)
            resultado.append(e)
    return resultado


def generar_nombre_base(tests_datos: list[dict]) -> str:
    if not tests_datos:
        return "Daypo"
    if len(tests_datos) == 1:
        return nombre_archivo(tests_datos[0]["titulo"])
    titulos = [t["titulo"] for t in tests_datos]
    conteo: dict[str, int] = {}
    for titulo in titulos:
        for palabra in set(re.findall(r'[a-zA-ZÀ-ɏ]{4,}', titulo.lower())):
            conteo[palabra] = conteo.get(palabra, 0) + 1
    umbral = max(2, len(titulos) // 2)
    candidatos = [(p, c) for p, c in conteo.items() if c >= umbral]
    if candidatos:
        palabra = max(candidatos, key=lambda x: x[1])[0]
        return f"{palabra.capitalize()}_{len(titulos)}_tests"
    primer = nombre_archivo(titulos[0])[:25].rstrip('_')
    return f"{primer}_y_{len(titulos) - 1}_mas"


# ---------------------------------------------------------------------------
# Exportadores
# ---------------------------------------------------------------------------

def generar_zip_remnote(tests_datos: list[dict]) -> bytes:
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        lineas: list[str] = []
        for test in tests_datos:
            lineas.append(test["titulo"])
            lineas.append("")
            for pregunta in test["preguntas"]:
                correcta = None
                incorrectas: list[str] = []
                for texto, es_correcta in pregunta["opciones"]:
                    if not texto:
                        continue
                    if es_correcta:
                        correcta = texto
                    else:
                        incorrectas.append(texto)
                if correcta is None:
                    continue
                if pregunta.get("img_bytes") and pregunta.get("img_nombre"):
                    nombre = pregunta["img_nombre"]
                    zf.writestr(f"images/{nombre}", pregunta["img_bytes"])
                    lineas.append(f"- **{pregunta['enunciado']}")
                    lineas.append(f"**![](images/{nombre}) >>A)")
                else:
                    lineas.append(f"- **{pregunta['enunciado']}** >>A)")
                lineas.append(f"    - {correcta}")
                for inc in incorrectas:
                    lineas.append(f"    - {inc}")
                lineas.append("")
            lineas.append("")
        zf.writestr("Banco_de_Preguntas_MCQ.md", "\n".join(lineas).encode("utf-8"))
    buf.seek(0)
    return buf.getvalue()


def generar_zip_imagenes(tests_datos: list[dict]) -> bytes:
    """ZIP con todas las imagenes nombradas {titulo}_{N:03d}.jpg."""
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for test in tests_datos:
            carpeta = nombre_archivo(test["titulo"])
            n = 1
            for p in test["preguntas"]:
                if p.get("img_bytes"):
                    zf.writestr(f"{carpeta}/{carpeta}_{n:03d}.jpg", p["img_bytes"])
                    n += 1
    buf.seek(0)
    return buf.getvalue()


def generar_zip_word_individuales(todos_los_tests: list[dict]) -> bytes:
    """ZIP con un .docx por test (con imagenes embebidas)."""
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for t in todos_los_tests:
            nb = nombre_archivo(t["titulo"])
            zf.writestr(f"{nb}.docx", t["_word_bytes"])
    buf.seek(0)
    return buf.getvalue()


def generar_zip_pdf_individuales(todos_los_tests: list[dict]) -> bytes:
    """ZIP con un .pdf por test."""
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for t in todos_los_tests:
            nb = nombre_archivo(t["titulo"])
            zf.writestr(f"{nb}.pdf", generar_pdf([t]))
    buf.seek(0)
    return buf.getvalue()


def generar_pdf(tests_datos: list[dict]) -> bytes:
    """PDF con preguntas, imagenes y opcion correcta marcada con >>."""
    def safe(t: str) -> str:
        return t.encode("latin-1", errors="replace").decode("latin-1")

    MARGEN = 20
    W = 170

    pdf = FPDF(format="A4")
    pdf.set_margins(MARGEN, MARGEN, MARGEN)
    pdf.set_auto_page_break(auto=True, margin=MARGEN)

    for test in tests_datos:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_x(MARGEN)
        try:
            pdf.multi_cell(W, 10, safe(test["titulo"]), align="L")
        except Exception:
            pass
        pdf.ln(4)

        for i, p in enumerate(test["preguntas"], 1):
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_x(MARGEN)
            try:
                pdf.multi_cell(W, 8, safe(f"{i}. {p['enunciado']}"), align="L")
            except Exception:
                pass

            if p.get("img_bytes"):
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
                    f.write(p["img_bytes"])
                    tmp = f.name
                try:
                    pdf.image(tmp, x=MARGEN, w=100)
                    pdf.ln(2)
                except Exception:
                    pass
                finally:
                    os.unlink(tmp)

            for texto, es_correcta in p["opciones"]:
                if not texto:
                    continue
                pdf.set_x(MARGEN + 4)
                if es_correcta:
                    pdf.set_font("Helvetica", "B", 11)
                    try:
                        pdf.multi_cell(W - 4, 7, safe(f">> {texto}"), align="L")
                    except Exception:
                        pass
                else:
                    pdf.set_font("Helvetica", "", 11)
                    try:
                        pdf.multi_cell(W - 4, 7, safe(texto), align="L")
                    except Exception:
                        pass
            pdf.ln(4)

    return bytes(pdf.output())


# ---------------------------------------------------------------------------
# Anki
# ---------------------------------------------------------------------------

_ANKI_MODEL = genanki.Model(
    1607392323,
    "Daypo MCQ Interactive",
    fields=[
        {"name": "Question"},
        {"name": "Image"},
        {"name": "Option A"},
        {"name": "Option B"},
        {"name": "Option C"},
        {"name": "Option D"},
        {"name": "Option E"},
        {"name": "Correct Answer"},
    ],
    templates=[
        {
            "name": "MCQ Card",
            "qfmt": """\
<div class="card-container">
  <div class="question">{{Question}}</div>
  {{#Image}}<div class="image">{{Image}}</div>{{/Image}}
  <hr>
  <div class="options-container" id="options-box">
    {{#Option A}}<button class="option-btn" id="btn-A" onclick="selectOption('A')">{{Option A}}</button>{{/Option A}}
    {{#Option B}}<button class="option-btn" id="btn-B" onclick="selectOption('B')">{{Option B}}</button>{{/Option B}}
    {{#Option C}}<button class="option-btn" id="btn-C" onclick="selectOption('C')">{{Option C}}</button>{{/Option C}}
    {{#Option D}}<button class="option-btn" id="btn-D" onclick="selectOption('D')">{{Option D}}</button>{{/Option D}}
    {{#Option E}}<button class="option-btn" id="btn-E" onclick="selectOption('E')">{{Option E}}</button>{{/Option E}}
  </div>
</div>
<script>
function selectOption(letter) {
  var btns = document.getElementsByClassName("option-btn");
  for (var i = 0; i < btns.length; i++) btns[i].classList.remove("selected");
  document.getElementById("btn-" + letter).classList.add("selected");
  sessionStorage.setItem("ankiUserChoice", letter);
}
(function initOptions() {
  var box  = document.getElementById("options-box");
  var btns = Array.from(box.children);
  var saved = sessionStorage.getItem("ankiOrder");
  if (saved) {
    saved.split(",").forEach(function(id) {
      var el = document.getElementById(id);
      if (el) box.appendChild(el);
    });
  } else {
    sessionStorage.removeItem("ankiUserChoice");
    for (var i = btns.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var tmp = btns[i]; btns[i] = btns[j]; btns[j] = tmp;
    }
    sessionStorage.setItem("ankiOrder", btns.map(function(b) { return b.id; }).join(","));
    btns.forEach(function(b) { box.appendChild(b); });
  }
})();
</script>""",
            "afmt": """\
{{FrontSide}}
<div id="correct-key" style="display:none;">{{Correct Answer}}</div>
<script>
var correct = document.getElementById("correct-key").innerText.trim().toUpperCase();
var chosen  = sessionStorage.getItem("ankiUserChoice") || "";
var cBtn = document.getElementById("btn-" + correct);
if (cBtn) cBtn.classList.add("correct");
if (chosen && chosen !== correct) {
  var wBtn = document.getElementById("btn-" + chosen);
  if (wBtn) wBtn.classList.add("incorrect");
}
sessionStorage.removeItem("ankiOrder");
</script>""",
        }
    ],
    css="""\
.card { font-family: Arial, Helvetica, sans-serif; font-size: 16px; text-align: left; color: #1a1a1a; background-color: #f0f0f0; }
.card-container { max-width: 620px; margin: 20px auto; padding: 20px; background: #ffffff; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,.12); }
.question { font-size: 1.2em; font-weight: bold; margin-bottom: 14px; color: #1a1a1a; }
.image { margin: 12px 0; }
.image img { max-width: 100%; max-height: 280px; border-radius: 6px; }
.options-container { display: flex; flex-direction: column; gap: 10px; }
.option-btn { text-align: left; padding: 13px 16px; border: 2px solid #d0d0d0; border-radius: 8px; background: #fafafa; color: #1a1a1a; cursor: pointer; font-size: 1em; transition: all .18s ease; }
.option-btn:hover  { background: #efefef; border-color: #aaa; }
.option-btn.selected { border-color: #0056b3; background: #dceeff; color: #003a80; }
.option-btn.correct   { border-color: #28a745 !important; background: #d4edda !important; color: #155724 !important; }
.option-btn.incorrect { border-color: #dc3545 !important; background: #f8d7da !important; color: #721c24 !important; }
.card.nightMode { color: #e8e8e8; background-color: #1e1e1e; }
.card.nightMode .card-container { background: #2a2a2a; box-shadow: 0 4px 10px rgba(0,0,0,.5); }
.card.nightMode .question { color: #e8e8e8; }
.card.nightMode .option-btn { background: #333; border-color: #555; color: #e8e8e8; }
.card.nightMode .option-btn:hover { background: #3d3d3d; border-color: #777; }
.card.nightMode .option-btn.selected { border-color: #5aabff; background: #1a3a5c; color: #a8d4ff; }
.card.nightMode .option-btn.correct   { border-color: #2ecc71 !important; background: #1a3d2b !important; color: #7fdca0 !important; }
.card.nightMode .option-btn.incorrect { border-color: #e74c3c !important; background: #3d1a1a !important; color: #f5a0a0 !important; }
""",
)


def generar_apkg_anki(tests_datos: list[dict]) -> bytes:
    deck = genanki.Deck(2059400110, "Daypo Extractor")
    with tempfile.TemporaryDirectory() as tmpdir:
        media_files: list[str] = []
        for test in tests_datos:
            for pregunta in test["preguntas"]:
                correcta = None
                incorrectas: list[str] = []
                for texto, es_correcta in pregunta["opciones"]:
                    if not texto:
                        continue
                    if es_correcta:
                        correcta = texto
                    else:
                        incorrectas.append(texto)
                if correcta is None:
                    continue
                opciones_campos = [correcta] + incorrectas
                fields_opciones = [opciones_campos[i] if i < len(opciones_campos) else "" for i in range(5)]
                image_html = ""
                if pregunta.get("img_bytes") and pregunta.get("img_nombre"):
                    nombre = pregunta["img_nombre"]
                    img_path = os.path.join(tmpdir, nombre)
                    with open(img_path, "wb") as f:
                        f.write(pregunta["img_bytes"])
                    media_files.append(img_path)
                    image_html = f'<img src="{nombre}">'
                note = genanki.Note(
                    model=_ANKI_MODEL,
                    fields=[pregunta["enunciado"], image_html, *fields_opciones, "A"],
                    guid=genanki.guid_for(test["titulo"], pregunta["enunciado"]),
                )
                deck.add_note(note)
        package = genanki.Package(deck)
        package.media_files = media_files
        apkg_path = os.path.join(tmpdir, "daypo.apkg")
        package.write_to_file(apkg_path)
        with open(apkg_path, "rb") as f:
            return f.read()


# ---------------------------------------------------------------------------
# HTML Quiz mini-app
# ---------------------------------------------------------------------------

_QUIZ_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;
  background:#0f172a;color:#e2e8f0;min-height:100vh;padding:16px 12px}
#app{max-width:1100px;margin:0 auto}
.hdr{display:flex;justify-content:space-between;align-items:center;
  background:#1e293b;border-radius:12px;padding:12px 16px;margin-bottom:12px}
.hdr-title{font-size:13px;color:#94a3b8;font-weight:500;overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap;max-width:60%}
.hdr-score{font-size:13px;color:#60a5fa;font-weight:700;white-space:nowrap}
.pbar{width:100%;height:5px;background:#1e293b;border-radius:99px;
  margin-bottom:16px;overflow:hidden}
.pfill{height:100%;background:linear-gradient(90deg,#3b82f6,#8b5cf6);
  border-radius:99px;transition:width .3s ease}
.main{display:flex;gap:16px;align-items:flex-start}
.quiz-area{flex:1;min-width:0}
.card{background:#1e293b;border-radius:14px;padding:24px;
  box-shadow:0 4px 20px rgba(0,0,0,.3)}
.qnum{font-size:11px;color:#64748b;font-weight:600;text-transform:uppercase;
  letter-spacing:.06em;margin-bottom:10px}
.qtext{font-size:17px;font-weight:600;line-height:1.55;color:#f1f5f9;margin-bottom:16px}
.qimg{width:100%;max-height:260px;object-fit:contain;border-radius:8px;
  margin-bottom:16px;border:1px solid #334155}
.opts{display:flex;flex-direction:column;gap:8px;margin-bottom:16px}
.opt{padding:12px 15px;background:#0f172a;border:2px solid #334155;
  border-radius:9px;color:#cbd5e1;font-size:14px;text-align:left;
  cursor:pointer;transition:all .14s ease;width:100%}
.opt:hover:not(:disabled){border-color:#60a5fa;background:#1e3a5f;color:#e2e8f0}
.opt.sel{border-color:#3b82f6;background:#1d4ed8;color:#fff}
.opt.ok{border-color:#22c55e!important;background:#14532d!important;color:#bbf7d0!important}
.opt.bad{border-color:#ef4444!important;background:#7f1d1d!important;color:#fecaca!important}
.opt:disabled{cursor:default}
.navbar{display:flex;gap:8px;flex-wrap:wrap}
.btn{padding:10px 14px;border:none;border-radius:8px;font-size:13px;
  font-weight:600;cursor:pointer;transition:all .14s ease}
.btn:disabled{opacity:.4;cursor:default}
.btn-prev{background:#334155;color:#94a3b8;flex-shrink:0}
.btn-prev:hover:not(:disabled){background:#475569;color:#e2e8f0}
.btn-skip{background:#334155;color:#94a3b8}
.btn-skip:hover:not(:disabled){background:#475569;color:#e2e8f0}
.btn-show{background:#475569;color:#e2e8f0;flex:1}
.btn-show:hover:not(:disabled){background:#64748b}
.btn-next{background:#3b82f6;color:#fff;flex-shrink:0}
.btn-next:hover:not(:disabled){background:#2563eb}
.kbd{display:inline-block;background:#0f172a;color:#64748b;font-size:10px;
  padding:1px 4px;border-radius:3px;font-family:monospace;margin-left:3px}
.grid-panel{width:180px;flex-shrink:0;background:#1e293b;border-radius:14px;
  padding:14px;position:sticky;top:16px}
.gp-title{font-size:11px;color:#64748b;font-weight:600;text-transform:uppercase;
  letter-spacing:.06em;margin-bottom:10px}
.grid{display:grid;grid-template-columns:repeat(5,1fr);gap:5px}
.gq{aspect-ratio:1;border:none;border-radius:5px;font-size:11px;font-weight:700;
  cursor:pointer;transition:all .12s;color:#94a3b8;background:#0f172a;
  display:flex;align-items:center;justify-content:center}
.gq:hover{filter:brightness(1.3)}
.gq.cur{outline:2px solid #60a5fa;outline-offset:1px;color:#e2e8f0}
.gq.ok{background:#15803d;color:#bbf7d0}
.gq.bad{background:#b91c1c;color:#fecaca}
.legend{margin-top:10px;display:flex;flex-direction:column;gap:5px}
.li{display:flex;align-items:center;gap:6px;font-size:11px;color:#64748b}
.ld{width:9px;height:9px;border-radius:2px;flex-shrink:0}
.btn-change{width:100%;margin-top:12px;padding:8px;background:#0f172a;
  border:none;border-radius:7px;color:#64748b;font-size:11px;font-weight:600;
  cursor:pointer;transition:all .14s}
.btn-change:hover{background:#334155;color:#94a3b8}
.sel-screen{text-align:center;padding:32px 16px}
.sel-title{font-size:22px;font-weight:700;color:#f1f5f9;margin-bottom:6px}
.sel-sub{font-size:14px;color:#64748b;margin-bottom:24px}
.test-list{display:flex;flex-direction:column;gap:10px;margin-bottom:28px;text-align:left}
.test-item{display:flex;align-items:center;gap:12px;padding:14px 16px;
  background:#0f172a;border:2px solid #334155;border-radius:10px;cursor:pointer;
  transition:border-color .15s}
.test-item:hover{border-color:#475569}
.test-item.on{border-color:#3b82f6}
.test-item input[type=checkbox]{width:17px;height:17px;cursor:pointer;accent-color:#3b82f6;flex-shrink:0}
.t-name{font-size:14px;font-weight:600;color:#e2e8f0}
.t-count{font-size:12px;color:#64748b;margin-top:2px}
.btn-start{background:#3b82f6;color:#fff;border:none;padding:14px 36px;
  border-radius:10px;font-size:15px;font-weight:700;cursor:pointer}
.btn-start:hover{background:#2563eb}
.end{text-align:center;padding:36px 16px}
.end-pct{font-size:68px;font-weight:800;
  background:linear-gradient(135deg,#3b82f6,#8b5cf6);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent}
.end-sub{font-size:18px;color:#94a3b8;margin:8px 0 28px}
.end-btns{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
.btn-restart{background:#3b82f6;color:#fff;padding:12px 26px;border-radius:9px;
  font-size:14px;font-weight:700;cursor:pointer;border:none}
.btn-restart:hover{background:#2563eb}
@media(max-width:640px){
  .main{flex-direction:column-reverse}
  .grid-panel{width:100%;position:static}
  .grid{grid-template-columns:repeat(8,1fr)}
}
"""

_QUIZ_JS = r"""
const TESTS = QUIZ_TESTS_DATA;
const TITULO = "QUIZ_TITLE";
const MULTI = TESTS.length > 1;
let selIdx = TESTS.map((_,i)=>i);
let qs=[],ans=[],rev=[],cho=[],cur=0;
const app=document.getElementById('app');

function shuf(a){const b=[...a];for(let i=b.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[b[i],b[j]]=[b[j],b[i]];}return b;}

const KEY='dq_'+TESTS.reduce((s,t)=>s+t.nombre.slice(0,3),'')+'_'+TESTS.reduce((s,t)=>s+t.preguntas.length,0);

function save(){try{localStorage.setItem(KEY,JSON.stringify({qs,ans,rev,cho,cur,selIdx}));}catch(e){}}

function loadSaved(){
  try{
    const sv=JSON.parse(localStorage.getItem(KEY)||'null');
    if(sv&&sv.qs&&sv.qs.length>0){qs=sv.qs;ans=sv.ans;rev=sv.rev;cho=sv.cho;cur=sv.cur||0;selIdx=sv.selIdx||selIdx;return true;}
  }catch(e){}
  return false;
}

function buildQuestions(idx){
  qs=[];
  idx.forEach(i=>shuf(TESTS[i].preguntas).forEach(q=>qs.push({...q})));
  qs=shuf(qs);
  qs.forEach(q=>{if(!q._opts)q._opts=shuf([q.correct,...q.wrong]);});
  ans=qs.map(()=>null);rev=qs.map(()=>false);cho=qs.map(()=>null);cur=0;
}

function score(){return ans.filter(a=>a==='correct').length;}
function done(){return rev.filter(Boolean).length;}

function renderSelect(){
  app.innerHTML=`
    <div class="card sel-screen">
      <div class="sel-title">${TITULO}</div>
      <div class="sel-sub">Elige los tests que quieres practicar</div>
      <div class="test-list">
        ${TESTS.map((t,i)=>`
          <label class="test-item on" id="lbl${i}">
            <input type="checkbox" id="chk${i}" checked onchange="toggleItem(${i})">
            <div><div class="t-name">${t.nombre}</div><div class="t-count">${t.preguntas.length} preguntas</div></div>
          </label>`).join('')}
      </div>
      <button class="btn-start" onclick="startSel()">Empezar &rarr;</button>
    </div>`;
}

function toggleItem(i){
  document.getElementById('lbl'+i).classList.toggle('on',document.getElementById('chk'+i).checked);
}

function startSel(){
  selIdx=TESTS.map((_,i)=>document.getElementById('chk'+i).checked?i:-1).filter(i=>i>=0);
  if(!selIdx.length){alert('Selecciona al menos un test.');return;}
  buildQuestions(selIdx);save();renderQuiz();
}

function renderQuiz(){
  const q=qs[cur];const opts=q._opts;const ci=opts.indexOf(q.correct);const isRev=rev[cur];
  const imgHtml=q.img?`<img class="qimg" src="data:image/jpeg;base64,${q.img}" alt="">`:'';
  const optsHtml=opts.map((o,i)=>{
    let c='opt';
    if(isRev){if(i===ci)c+=' ok';else if(i===cho[cur])c+=' bad';}else if(i===cho[cur])c+=' sel';
    return `<button class="${c}"${isRev?' disabled':''} onclick="pick(${i})">${o}</button>`;
  }).join('');
  const navHtml=isRev
    ?`<button class="btn btn-prev" onclick="prev()"${cur===0?' disabled':''}>&larr;</button>
      <span style="flex:1"></span>
      <button class="btn btn-next" onclick="next()">${cur<qs.length-1?'Siguiente &rarr;':'Ver resultado &rarr;'}</button>`
    :`<button class="btn btn-prev" onclick="prev()"${cur===0?' disabled':''}>&larr;</button>
      <button class="btn btn-skip" onclick="skipQ()">Saltar</button>
      <button class="btn btn-show" onclick="reveal()">Mostrar<span class="kbd">Esp</span></button>
      <button class="btn btn-next" onclick="next()"${cur>=qs.length-1?' disabled':''}>&rarr;</button>`;
  const gridHtml=qs.map((_,i)=>{
    let c='gq';if(ans[i]==='correct')c+=' ok';else if(ans[i]==='wrong')c+=' bad';if(i===cur)c+=' cur';
    return `<button class="${c}" onclick="goTo(${i})">${i+1}</button>`;
  }).join('');
  const pct=qs.length?Math.round(cur/qs.length*100):0;
  app.innerHTML=`
    <div class="hdr">
      <span class="hdr-title">${TITULO}</span>
      <span class="hdr-score">${score()}/${done()}</span>
    </div>
    <div class="pbar"><div class="pfill" style="width:${pct}%"></div></div>
    <div class="main">
      <div class="quiz-area">
        <div class="card">
          <div class="qnum">Pregunta ${cur+1} / ${qs.length}</div>
          <div class="qtext">${q.q}</div>
          ${imgHtml}
          <div class="opts">${optsHtml}</div>
          <div class="navbar">${navHtml}</div>
        </div>
      </div>
      <div class="grid-panel">
        <div class="gp-title">Preguntas</div>
        <div class="grid">${gridHtml}</div>
        <div class="legend">
          <div class="li"><div class="ld" style="background:#0f172a;outline:1px solid #334155"></div>Sin responder</div>
          <div class="li"><div class="ld" style="background:#15803d"></div>Correcta</div>
          <div class="li"><div class="ld" style="background:#b91c1c"></div>Incorrecta</div>
        </div>
        ${MULTI?`<button class="btn-change" onclick="renderSelect()">Cambiar tests</button>`:''}
      </div>
    </div>`;
}

function pick(i){if(rev[cur])return;cho[cur]=i;renderQuiz();}

function reveal(){
  if(rev[cur])return;rev[cur]=true;
  const ci=qs[cur]._opts.indexOf(qs[cur].correct);
  ans[cur]=(cho[cur]===ci)?'correct':'wrong';
  save();renderQuiz();
}

function prev(){if(cur>0){cur--;renderQuiz();}}

function next(){
  if(cur<qs.length-1){cur++;renderQuiz();}
  else if(done()===qs.length)renderEnd();
}

function goTo(i){cur=i;renderQuiz();}

function skipQ(){
  for(let i=cur+1;i<qs.length;i++){if(!rev[i]){cur=i;renderQuiz();return;}}
  for(let i=0;i<cur;i++){if(!rev[i]){cur=i;renderQuiz();return;}}
  renderEnd();
}

function renderEnd(){
  const tot=done(),sc=score(),p=tot?Math.round(sc/tot*100):0;
  app.innerHTML=`
    <div class="card end">
      <div class="end-pct">${p}%</div>
      <div class="end-sub">${sc} de ${tot} respondidas correctamente</div>
      <div class="end-btns">
        <button class="btn-restart" onclick="restart()">&#x1F504; De nuevo</button>
        ${MULTI?`<button class="btn-restart" style="background:#334155" onclick="renderSelect()">Cambiar tests</button>`:''}
      </div>
    </div>`;
}

function restart(){buildQuestions(selIdx);save();renderQuiz();}

document.addEventListener('keydown',e=>{
  if(['INPUT','TEXTAREA'].includes(document.activeElement.tagName))return;
  if(e.code==='Space'){e.preventDefault();if(!rev[cur])reveal();}
  if(e.code==='ArrowLeft')prev();
  if(e.code==='ArrowRight'){if(rev[cur])next();}
  if(e.key==='s'||e.key==='S')skipQ();
  const n=parseInt(e.key);
  if(!isNaN(n)&&n>=1&&n<=9&&!rev[cur])pick(n-1);
});

(function(){
  if(MULTI&&!loadSaved()){renderSelect();}
  else{if(!loadSaved())buildQuestions(selIdx);renderQuiz();}
})();
"""

_QUIZ_HTML = (
    "<!DOCTYPE html><html lang='es'><head>"
    "<meta charset='UTF-8'>"
    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<title>QUIZ_TITLE</title>"
    "<style>" + _QUIZ_CSS + "</style></head>"
    "<body><div id='app'></div>"
    "<script>" + _QUIZ_JS + "</script>"
    "</body></html>"
)


def generar_html_quiz(tests_datos: list[dict], nombre: str) -> bytes:
    """HTML autocontenido con quiz interactivo, grid de navegacion y seleccion de tests."""
    tests_js = []
    for test in tests_datos:
        preguntas = []
        for p in test["preguntas"]:
            correcta = None
            incorrectas: list[str] = []
            for texto, es_correcta in p["opciones"]:
                if not texto:
                    continue
                if es_correcta:
                    correcta = texto
                else:
                    incorrectas.append(texto)
            if correcta is None:
                continue
            img_b64 = ""
            if p.get("img_bytes"):
                img_b64 = base64.b64encode(p["img_bytes"]).decode()
            preguntas.append({"q": p["enunciado"], "img": img_b64,
                               "correct": correcta, "wrong": incorrectas})
        if preguntas:
            tests_js.append({"nombre": test["titulo"], "preguntas": preguntas})

    data_json = json.dumps(tests_js, ensure_ascii=False).replace("</script>", "<\\/script>")
    nombre_safe = nombre.replace('"', '').replace("'", "")
    html = _QUIZ_HTML.replace("QUIZ_TESTS_DATA", data_json).replace("QUIZ_TITLE", nombre_safe)
    return html.encode("utf-8")


# ---------------------------------------------------------------------------
# Interfaz de usuario (Streamlit)
# ---------------------------------------------------------------------------

st.title("📝 Daypo Extractor")
st.markdown(
    "Extrae preguntas, imagenes y respuestas correctas de cualquier test de "
    "[Daypo](https://www.daypo.com) y exportalos a Word, PDF, "
    "[RemNote](https://www.remnote.com) MCQ, [Anki](https://apps.ankiweb.net) "
    "o como mini-app quiz offline."
)

st.divider()

if "resultado" not in st.session_state:
    st.session_state["resultado"] = None

# ── Pantalla de resultados ────────────────────────────────────────────────
if st.session_state["resultado"] is not None:
    res = st.session_state["resultado"]

    if res["errores"]:
        st.warning(f"No se pudieron procesar {len(res['errores'])} enlace(s).")

    st.success(f"Procesados {res['tests_ok']} test(s). Archivos listos para descargar.")

    nb = res["nombre_base"]
    es_multi = res["es_multi"]

    # Fila 1
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button(
            label="📄 Word" + (" (todos)" if es_multi else ""),
            data=res["word_combinado"],
            file_name=f"{nb}_Word.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            help="Documento Word con preguntas e imagenes embebidas.",
        )
    with c2:
        st.download_button(
            label="🧠 RemNote MCQ",
            data=res["zip_remnote"],
            file_name=f"{nb}_RemNote.zip",
            mime="application/zip",
            use_container_width=True,
            help="Importa el ZIP en RemNote: ajustes → Importar → Markdown.",
        )
    with c3:
        st.download_button(
            label="🃏 Anki (.apkg)",
            data=res["apkg_anki"],
            file_name=f"{nb}_Anki.apkg",
            mime="application/octet-stream",
            use_container_width=True,
            help="Doble clic en el .apkg para importar en Anki.",
        )

    # Fila 2
    c4, c5, c6 = st.columns(3)
    with c4:
        st.download_button(
            label="🖨️ PDF" + (" (todos)" if es_multi else ""),
            data=res["pdf_combinado"],
            file_name=f"{nb}.pdf",
            mime="application/pdf",
            use_container_width=True,
            help="PDF con preguntas, imagenes y respuesta correcta marcada.",
        )
    with c5:
        st.download_button(
            label="🌐 Mini-App Quiz",
            data=res["html_quiz"],
            file_name=f"{nb}_Quiz.html",
            mime="text/html",
            use_container_width=True,
            help="Abre en cualquier navegador. Funciona offline. Sin instalar nada.",
        )
    with c6:
        st.download_button(
            label="🖼️ Imagenes sueltas",
            data=res["zip_imagenes"],
            file_name=f"{nb}_Imagenes.zip",
            mime="application/zip",
            use_container_width=True,
            help="ZIP con todas las imagenes nombradas por test y numero correlativo.",
        )

    # Botones "por separado" (solo si hay varios tests)
    if es_multi:
        st.markdown("---")
        ca, cb = st.columns(2)
        with ca:
            st.download_button(
                label="📄 Word por separado (ZIP)",
                data=res["zip_word_individuales"],
                file_name=f"{nb}_Word_individual.zip",
                mime="application/zip",
                use_container_width=True,
                help="ZIP con un .docx por cada test.",
            )
        with cb:
            st.download_button(
                label="🖨️ PDF por separado (ZIP)",
                data=res["zip_pdf_individuales"],
                file_name=f"{nb}_PDF_individual.zip",
                mime="application/zip",
                use_container_width=True,
                help="ZIP con un .pdf por cada test.",
            )

    with st.expander("ℹ️ Como importar en RemNote"):
        st.markdown("""
1. Descarga **{nb}_RemNote.zip**.
2. RemNote → icono de ajustes → **Importar** → **Markdown** → sube el ZIP.
3. Las preguntas apareceran con imagen y como tarjetas MCQ.
4. RemNote baraja las opciones al practicar.
""")

    with st.expander("ℹ️ Como importar en Anki"):
        st.markdown("""
1. Descarga el **.apkg** y haz **doble clic** (o Archivo → Importar en Anki).
2. Se crea el mazo **Daypo Extractor** con el tipo de nota **Daypo MCQ Interactive**.

**Funcionamiento:**
- Las opciones aparecen en **orden aleatorio** diferente en cada repaso.
- Haz **clic** en la opcion que creas correcta antes de girar la carta.
- Pulsa **Espacio** para revelar la respuesta.
- Correcto → verde · Incorrecto → rojo. El orden NO cambia al girar.
""")

    st.divider()
    if st.button("🔄 Nueva extraccion", use_container_width=True):
        st.session_state["resultado"] = None
        st.rerun()

    st.stop()

# ── Pantalla de entrada ───────────────────────────────────────────────────
enlaces_texto = st.text_area(
    "Pega aqui tus enlaces de Daypo (o cualquier texto que los contenga):",
    height=220,
    placeholder="Pega aqui tus enlaces de Daypo...",
)

if enlaces_texto.strip():
    enlaces_detectados = extraer_enlaces_daypo(enlaces_texto)
    if enlaces_detectados:
        st.success(f"🔍 {len(enlaces_detectados)} enlace(s) detectado(s)")
        for e in enlaces_detectados:
            st.caption(e)
    else:
        st.warning("No se han detectado enlaces de Daypo en el texto introducido.")

col1, col2 = st.columns([3, 1])
with col1:
    iniciar = st.button("Iniciar Extraccion", type="primary", use_container_width=True)
with col2:
    st.caption("Requiere conexion a internet")

if iniciar:
    enlaces = extraer_enlaces_daypo(enlaces_texto)

    if not enlaces:
        st.error("No se han detectado enlaces validos de Daypo.")
        st.stop()

    es_multiple = len(enlaces) > 1
    headers_web = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    todos_los_tests: list[dict] = []
    doc_unificado: Document | None = None
    if es_multiple:
        doc_unificado = Document()
        doc_unificado.add_heading("Recopilacion completa de tests de Daypo", 0)

    barra = st.progress(0, text="Iniciando...")
    log = st.empty()
    errores = []

    for indice, url in enumerate(enlaces):
        nombre_corto = url.rstrip("/").split("/")[-1].replace(".html", "")
        barra.progress(
            int((indice / len(enlaces)) * 100),
            text=f"Procesando {indice + 1}/{len(enlaces)}: {nombre_corto}",
        )
        log.info(f"Procesando: {url}")

        resultado = extraer_datos_test(url, headers_web)
        if resultado is None:
            errores.append(url)
            st.warning(f"No se pudo procesar: {url}")
            continue

        id_test, titulo, preguntas = resultado

        doc_indiv = Document()
        doc_indiv.add_heading(titulo, 1)
        if doc_unificado:
            doc_unificado.add_heading(titulo, 1)

        preguntas_con_img: list[dict] = []

        for i, pregunta in enumerate(preguntas, start=1):
            img_bytes = None
            img_nombre = None

            if pregunta["num_imagen"] is not None:
                img_nombre = f"img_{id_test}_{pregunta['num_imagen']}.jpg"
                img_bytes = obtener_imagen(id_test, pregunta["num_imagen"], url)

            # Word CON imagenes embebidas (sin archivos .jpg sueltos en el ZIP)
            procesar_pregunta(doc_indiv, i, pregunta["enunciado"], img_bytes, pregunta["opciones"])
            if doc_unificado:
                procesar_pregunta(doc_unificado, i, pregunta["enunciado"], img_bytes, pregunta["opciones"])

            preguntas_con_img.append({
                "enunciado": pregunta["enunciado"],
                "opciones": pregunta["opciones"],
                "img_bytes": img_bytes,
                "img_nombre": img_nombre,
            })

        buf_indiv = BytesIO()
        doc_indiv.save(buf_indiv)

        todos_los_tests.append({
            "titulo": titulo,
            "preguntas": preguntas_con_img,
            "_word_bytes": buf_indiv.getvalue(),
        })

        if doc_unificado:
            doc_unificado.add_page_break()

    barra.progress(100, text="Extraccion completada.")
    log.empty()

    # Word combinado
    if es_multiple and doc_unificado:
        buf_unif = BytesIO()
        doc_unificado.save(buf_unif)
        word_combinado = buf_unif.getvalue()
    else:
        word_combinado = todos_los_tests[0]["_word_bytes"] if todos_los_tests else b""

    nombre_base = generar_nombre_base(todos_los_tests)

    st.session_state["resultado"] = {
        "nombre_base": nombre_base,
        "es_multi": es_multiple,
        "word_combinado": word_combinado,
        "zip_word_individuales": generar_zip_word_individuales(todos_los_tests) if es_multiple else b"",
        "zip_pdf_individuales": generar_zip_pdf_individuales(todos_los_tests) if es_multiple else b"",
        "zip_imagenes": generar_zip_imagenes(todos_los_tests),
        "zip_remnote": generar_zip_remnote(todos_los_tests),
        "apkg_anki": generar_apkg_anki(todos_los_tests),
        "pdf_combinado": generar_pdf(todos_los_tests),
        "html_quiz": generar_html_quiz(todos_los_tests, nombre_base),
        "tests_ok": len(enlaces) - len(errores),
        "errores": errores,
    }
    st.rerun()
