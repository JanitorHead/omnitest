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


def generar_nombre_base(tests_datos: list[dict]) -> str:
    """
    Nombre de archivo representativo para la extraccion.
    - 1 test  → titulo del test (espacios → guiones bajos)
    - N tests → palabra mas frecuente en los titulos + '_N_tests';
                si no hay palabra comun, primer titulo truncado + '_y_N_mas'
    """
    if not tests_datos:
        return "Daypo"

    def normalizar(t: str) -> str:
        return re.sub(r'\s+', '_', limpiar_nombre_carpeta(t)).strip('_')

    if len(tests_datos) == 1:
        return normalizar(tests_datos[0]["titulo"])

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

    primer = normalizar(titulos[0])[:25].rstrip('_')
    return f"{primer}_y_{len(titulos) - 1}_mas"


def extraer_enlaces_daypo(texto: str) -> list[str]:
    """Extrae todos los enlaces de Daypo de cualquier bloque de texto."""
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


def generar_zip_remnote(tests_datos: list[dict]) -> bytes:
    """
    Genera un ZIP con un .md en sintaxis RemNote MCQ y una carpeta images/.

    Formato identico al que RemNote exporta internamente:
      - **Pregunta en negrita     <- abre negrita, sin cerrar
      **![](images/img.jpg) >>A)  <- cierra negrita, imagen, marcador MCQ
          - Opcion correcta       <- subitems con 4 espacios + guion
          - Opcion incorrecta
    Las imagenes se referencian por ruta relativa dentro del ZIP.
    """
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
                    # Enunciado en negrita en linea 1, imagen en linea 2 + marcador MCQ
                    # Replica exacta del formato que RemNote usa al exportar sus MCQ
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


# Modelo Anki con botones interactivos, shuffle en JS y feedback verde/rojo.
# La correcta va SIEMPRE en Option A; el template la baraja visualmente cada vez.
# ID fijo para que Anki reconozca el tipo de nota entre importaciones.
_ANKI_MODEL = genanki.Model(
    1607392323,
    "Daypo MCQ Interactive",
    fields=[
        {"name": "Question"},
        {"name": "Image"},
        {"name": "Option A"},   # siempre la respuesta correcta
        {"name": "Option B"},
        {"name": "Option C"},
        {"name": "Option D"},
        {"name": "Option E"},
        {"name": "Correct Answer"},  # siempre "A"
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
    // Reverso (FrontSide re-ejecuta este script): restaurar orden, no barajar
    saved.split(",").forEach(function(id) {
      var el = document.getElementById(id);
      if (el) box.appendChild(el);
    });
  } else {
    // Nueva carta (anverso): barajar con Fisher-Yates y guardar orden
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
// Limpiar orden para que la siguiente carta baraje de nuevo
sessionStorage.removeItem("ankiOrder");
</script>""",
        }
    ],
    css="""\
/* ── Light mode ─────────────────────────────────────────── */
.card {
  font-family: Arial, Helvetica, sans-serif;
  font-size: 16px;
  text-align: left;
  color: #1a1a1a;
  background-color: #f0f0f0;
}
.card-container {
  max-width: 620px;
  margin: 20px auto;
  padding: 20px;
  background: #ffffff;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0,0,0,.12);
}
.question { font-size: 1.2em; font-weight: bold; margin-bottom: 14px; color: #1a1a1a; }
.image { margin: 12px 0; }
.image img { max-width: 100%; max-height: 280px; border-radius: 6px; }
.options-container { display: flex; flex-direction: column; gap: 10px; }
.option-btn {
  text-align: left; padding: 13px 16px;
  border: 2px solid #d0d0d0; border-radius: 8px;
  background: #fafafa; color: #1a1a1a;
  cursor: pointer; font-size: 1em; transition: all .18s ease;
}
.option-btn:hover  { background: #efefef; border-color: #aaa; }
.option-btn.selected { border-color: #0056b3; background: #dceeff; color: #003a80; }
.option-btn.correct   { border-color: #28a745 !important; background: #d4edda !important; color: #155724 !important; }
.option-btn.incorrect { border-color: #dc3545 !important; background: #f8d7da !important; color: #721c24 !important; }

/* ── Dark mode (.nightMode añadido por Anki) ─────────────── */
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
    """
    Genera un .apkg de Anki con nota MCQ interactiva.

    La correcta va en Option A; el template JS la baraja visualmente en cada repaso.
    Al girar la tarjeta: la correcta se pinta verde, la elegida incorrecta en rojo.
    """
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

                # Correcta en Option A; incorrectas en B-E; Correct Answer siempre "A"
                opciones_campos = [correcta] + incorrectas
                fields_opciones = [opciones_campos[i] if i < len(opciones_campos) else ""
                                   for i in range(5)]

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
                    fields=[
                        pregunta["enunciado"],
                        image_html,
                        *fields_opciones,  # Option A..E
                        "A",               # Correct Answer
                    ],
                    guid=genanki.guid_for(test["titulo"], pregunta["enunciado"]),
                )
                deck.add_note(note)

        package = genanki.Package(deck)
        package.media_files = media_files

        apkg_path = os.path.join(tmpdir, "daypo.apkg")
        package.write_to_file(apkg_path)

        with open(apkg_path, "rb") as f:
            return f.read()


def generar_zip_imagenes(tests_datos: list[dict]) -> bytes:
    """ZIP con solo las imagenes, organizadas por test."""
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for test in tests_datos:
            carpeta = limpiar_nombre_carpeta(test["titulo"])
            for p in test["preguntas"]:
                if p.get("img_bytes") and p.get("img_nombre"):
                    zf.writestr(f"{carpeta}/{p['img_nombre']}", p["img_bytes"])
    buf.seek(0)
    return buf.getvalue()


def generar_pdf(tests_datos: list[dict]) -> bytes:
    """PDF con preguntas, imagenes incrustadas y opcion correcta marcada con >>."""
    def safe(t: str) -> str:
        return t.encode("latin-1", errors="replace").decode("latin-1")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(15, 15, 15)

    for test in tests_datos:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.multi_cell(0, 10, safe(test["titulo"]))
        pdf.ln(5)

        for i, p in enumerate(test["preguntas"], 1):
            pdf.set_font("Helvetica", "B", 12)
            pdf.multi_cell(0, 8, safe(f"{i}. {p['enunciado']}"))

            if p.get("img_bytes"):
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
                    f.write(p["img_bytes"])
                    tmp = f.name
                try:
                    pdf.image(tmp, w=110)
                    pdf.ln(2)
                except Exception:
                    pass
                finally:
                    os.unlink(tmp)

            for texto, es_correcta in p["opciones"]:
                if not texto:
                    continue
                if es_correcta:
                    pdf.set_font("Helvetica", "B", 11)
                    pdf.multi_cell(0, 7, safe(f"  >> {texto}"))
                else:
                    pdf.set_font("Helvetica", "", 11)
                    pdf.multi_cell(0, 7, safe(f"     {texto}"))
            pdf.ln(4)

    return bytes(pdf.output())


# ---------------------------------------------------------------------------
# HTML quiz autocontenida
# ---------------------------------------------------------------------------

_QUIZ_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;
  background:#0f172a;color:#e2e8f0;min-height:100vh;display:flex;
  flex-direction:column;align-items:center;padding:16px 12px}
#app{width:100%;max-width:680px}
.hdr{display:flex;justify-content:space-between;align-items:center;
  background:#1e293b;border-radius:12px;padding:12px 16px;margin-bottom:14px}
.hdr-title{font-size:13px;color:#94a3b8;font-weight:500;white-space:nowrap;
  overflow:hidden;text-overflow:ellipsis;max-width:60%}
.hdr-score{font-size:13px;color:#60a5fa;font-weight:700;white-space:nowrap}
.pbar{width:100%;height:6px;background:#1e293b;border-radius:99px;
  margin-bottom:18px;overflow:hidden}
.pfill{height:100%;background:linear-gradient(90deg,#3b82f6,#8b5cf6);
  border-radius:99px;transition:width .35s ease}
.card{background:#1e293b;border-radius:16px;padding:26px;
  box-shadow:0 4px 24px rgba(0,0,0,.35)}
.qnum{font-size:11px;color:#64748b;font-weight:600;text-transform:uppercase;
  letter-spacing:.06em;margin-bottom:10px}
.qtext{font-size:18px;font-weight:600;line-height:1.55;color:#f1f5f9;
  margin-bottom:18px}
.qimg{width:100%;max-height:270px;object-fit:contain;border-radius:10px;
  margin-bottom:18px;border:1px solid #334155}
.opts{display:flex;flex-direction:column;gap:9px;margin-bottom:18px}
.opt{padding:13px 16px;background:#0f172a;border:2px solid #334155;
  border-radius:10px;color:#cbd5e1;font-size:15px;text-align:left;
  cursor:pointer;transition:all .15s ease;width:100%}
.opt:hover:not(:disabled){border-color:#60a5fa;background:#1e3a5f;color:#e2e8f0}
.opt.sel{border-color:#3b82f6;background:#1d4ed8;color:#fff}
.opt.ok{border-color:#22c55e!important;background:#14532d!important;color:#bbf7d0!important}
.opt.bad{border-color:#ef4444!important;background:#7f1d1d!important;color:#fecaca!important}
.opt:disabled{cursor:default}
.acts{display:flex;gap:10px}
.btn{flex:1;padding:13px;border:none;border-radius:10px;font-size:15px;
  font-weight:600;cursor:pointer;transition:all .15s ease}
.btn-show{background:#334155;color:#94a3b8}
.btn-show:hover{background:#475569;color:#e2e8f0}
.btn-next{background:#3b82f6;color:#fff}
.btn-next:hover{background:#2563eb}
.end{text-align:center;padding:36px 16px}
.end-pct{font-size:72px;font-weight:800;
  background:linear-gradient(135deg,#3b82f6,#8b5cf6);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent}
.end-sub{font-size:19px;color:#94a3b8;margin:8px 0 32px}
.end-btns{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
.btn-restart{background:#3b82f6;color:#fff;padding:13px 26px;border-radius:10px;
  font-size:15px;font-weight:600;cursor:pointer;border:none}
.btn-restart:hover{background:#2563eb}
.kbd{display:inline-block;background:#334155;color:#94a3b8;font-size:11px;
  padding:1px 5px;border-radius:4px;font-family:monospace;margin-left:4px}
"""

_QUIZ_JS = r"""
const PREGUNTAS = QUIZ_DATA;
const TITULO = "QUIZ_TITLE";

function shuf(a){
  const b=[...a];
  for(let i=b.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[b[i],b[j]]=[b[j],b[i]];}
  return b;
}

const KEY = 'dq_' + PREGUNTAS.length + '_' + (PREGUNTAS[0]||{q:''}).q.slice(0,8);
let qs = shuf(PREGUNTAS);
let cur = 0, score = 0, rev = false, sel = null;

try {
  const sv = JSON.parse(localStorage.getItem(KEY)||'null');
  if(sv && sv.qs && sv.qs.length===qs.length){qs=sv.qs;cur=sv.cur||0;score=sv.sc||0;}
} catch(e){}

function save(){try{localStorage.setItem(KEY,JSON.stringify({qs,cur,sc:score}));}catch(e){}}
const app = document.getElementById('app');
const pct = ()=> qs.length ? Math.round(cur/qs.length*100) : 0;

function render(){
  if(cur>=qs.length){renderEnd();return;}
  const q=qs[cur];
  if(!q._opts) q._opts=shuf([q.correct,...q.wrong]);
  rev=false; sel=null;
  const img=q.img?`<img class="qimg" src="data:image/jpeg;base64,${q.img}" alt="">`:'' ;
  const opts=q._opts.map((o,i)=>`<button class="opt" id="o${i}" onclick="pick(${i})">${o}</button>`).join('');
  app.innerHTML=`
    <div class="hdr">
      <span class="hdr-title">${TITULO}</span>
      <span class="hdr-score">${score}/${cur} correctas</span>
    </div>
    <div class="pbar"><div class="pfill" style="width:${pct()}%"></div></div>
    <div class="card">
      <div class="qnum">Pregunta ${cur+1} / ${qs.length}</div>
      <div class="qtext">${q.q}</div>
      ${img}
      <div class="opts">${opts}</div>
      <div class="acts">
        <button class="btn btn-show" onclick="reveal()">
          Mostrar respuesta <span class="kbd">Espacio</span>
        </button>
      </div>
    </div>`;
}

function pick(i){
  if(rev)return;
  sel=i;
  document.querySelectorAll('.opt').forEach((b,j)=>b.classList.toggle('sel',j===i));
}

function reveal(){
  if(rev)return; rev=true;
  const q=qs[cur];
  const ci=q._opts.indexOf(q.correct);
  document.querySelectorAll('.opt').forEach((b,i)=>{
    b.disabled=true;
    if(i===ci)b.classList.add('ok');
    else if(i===sel)b.classList.add('bad');
  });
  if(sel!==null && q._opts[sel]===q.correct) score++;
  save();
  document.querySelector('.acts').innerHTML=`
    <button class="btn btn-next" onclick="next()">
      ${cur+1<qs.length?'Siguiente &rarr;':'Ver resultado &rarr;'} <span class="kbd">&rarr;</span>
    </button>`;
}

function next(){cur++;save();render();}

function renderEnd(){
  const p=qs.length?Math.round(score/qs.length*100):0;
  app.innerHTML=`
    <div class="card end">
      <div class="end-pct">${p}%</div>
      <div class="end-sub">${score} de ${qs.length} correctas</div>
      <div class="end-btns">
        <button class="btn-restart" onclick="restart()">&#x1F504; Empezar de nuevo</button>
      </div>
    </div>`;
}

function restart(){
  qs=shuf(PREGUNTAS); qs.forEach(q=>delete q._opts);
  cur=0; score=0; save(); render();
}

document.addEventListener('keydown',e=>{
  if(e.code==='Space'&&!rev){e.preventDefault();reveal();}
  if((e.code==='ArrowRight'||e.code==='Enter')&&rev) next();
  const n=parseInt(e.key);
  if(!rev&&n>=1&&n<=9){const b=document.getElementById('o'+(n-1));if(b)b.click();}
});
render();
"""

_QUIZ_HTML = (
    "<!DOCTYPE html>\n<html lang='es'>\n<head>\n"
    "<meta charset='UTF-8'>\n"
    "<meta name='viewport' content='width=device-width, initial-scale=1.0'>\n"
    "<title>QUIZ_TITLE</title>\n"
    "<style>" + _QUIZ_CSS + "</style>\n"
    "</head>\n<body>\n<div id='app'></div>\n"
    "<script>" + _QUIZ_JS + "</script>\n"
    "</body>\n</html>"
)


def generar_html_quiz(tests_datos: list[dict], nombre: str) -> bytes:
    """HTML autocontenido con quiz interactivo (shuffle, feedback, progreso)."""
    preguntas = []
    for test in tests_datos:
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
            preguntas.append({
                "q": p["enunciado"],
                "img": img_b64,
                "correct": correcta,
                "wrong": incorrectas,
            })

    data_json = json.dumps(preguntas, ensure_ascii=False)
    # Escape </script> inside JSON data to avoid breaking the script tag
    data_json = data_json.replace("</script>", "<\\/script>")
    nombre_safe = nombre.replace('"', '').replace("'", "")

    html = _QUIZ_HTML.replace("QUIZ_DATA", data_json).replace("QUIZ_TITLE", nombre_safe)
    return html.encode("utf-8")


# ---------------------------------------------------------------------------
# Interfaz de usuario (Streamlit)
# ---------------------------------------------------------------------------

st.title("📝 Daypo Extractor")
st.markdown(
    "Extrae preguntas, imagenes y respuestas correctas de cualquier test de "
    "[Daypo](https://www.daypo.com) y exportalos a Word, "
    "[RemNote](https://www.remnote.com) MCQ o [Anki](https://apps.ankiweb.net)."
)

st.divider()

if "resultado" not in st.session_state:
    st.session_state["resultado"] = None

# Pantalla de resultados
if st.session_state["resultado"] is not None:
    res = st.session_state["resultado"]

    if res["errores"]:
        st.warning(
            f"No se pudieron procesar {len(res['errores'])} enlace(s). "
            "Revisa tu conexion o que la URL sea correcta."
        )

    st.success(f"Procesados {res['tests_ok']} test(s) correctamente. Archivos listos para descargar.")

    nb = res["nombre_base"]

    # Fila 1: formatos de estudio
    col_word, col_remnote, col_anki = st.columns(3)
    with col_word:
        st.download_button(
            label="📄 Word (con imágenes)",
            data=res["zip_word"],
            file_name=f"{nb}_Word.zip",
            mime="application/zip",
            use_container_width=True,
            help="ZIP con un .docx por test. Las imagenes van incrustadas dentro del Word.",
        )
    with col_remnote:
        st.download_button(
            label="🧠 RemNote MCQ",
            data=res["zip_remnote"],
            file_name=f"{nb}_RemNote.zip",
            mime="application/zip",
            use_container_width=True,
            help="Importa el ZIP en RemNote: ajustes → Importar → Markdown.",
        )
    with col_anki:
        st.download_button(
            label="🃏 Anki (.apkg)",
            data=res["apkg_anki"],
            file_name=f"{nb}_Anki.apkg",
            mime="application/octet-stream",
            use_container_width=True,
            help="Doble clic en el .apkg para importar directamente en Anki.",
        )

    # Fila 2: formatos extra
    col_pdf, col_html, col_imgs = st.columns(3)
    with col_pdf:
        st.download_button(
            label="🖨️ PDF",
            data=res["pdf"],
            file_name=f"{nb}.pdf",
            mime="application/pdf",
            use_container_width=True,
            help="PDF con preguntas, imagenes y respuesta correcta marcada.",
        )
    with col_html:
        st.download_button(
            label="🌐 Mini-App Quiz (.html)",
            data=res["html_quiz"],
            file_name=f"{nb}_Quiz.html",
            mime="text/html",
            use_container_width=True,
            help="Abre el archivo en cualquier navegador. Sin instalar nada. Funciona offline.",
        )
    with col_imgs:
        st.download_button(
            label="🖼️ Imágenes sueltas",
            data=res["zip_imagenes"],
            file_name=f"{nb}_Imagenes.zip",
            mime="application/zip",
            use_container_width=True,
            help="ZIP solo con las imagenes de las preguntas, organizadas por test.",
        )

    with st.expander("ℹ️ Como importar en RemNote"):
        st.markdown(
            """
1. Descarga **Daypo_RemNote_MCQ.zip**.
2. RemNote → icono de ajustes → **Importar** → **Markdown** → sube el ZIP.
3. Las preguntas apareceran con imagen (si la tienen) y como tarjetas MCQ.
4. RemNote baraja el orden de las opciones al practicar.
            """
        )

    with st.expander("ℹ️ Como importar en Anki"):
        st.markdown(
            """
1. Descarga el archivo **.apkg** y haz **doble clic** sobre el para importarlo directamente
   (o desde Anki: **Archivo → Importar**).
2. Se crea el mazo **Daypo Extractor** con el tipo de nota **Daypo MCQ Interactive**.

**Funcionamiento de las flashcards:**
- Las opciones aparecen en **orden aleatorio diferente** en cada repaso.
- Haz **clic** en la opcion que creas correcta antes de girar la carta.
- Pulsa **Espacio** (o el boton de mostrar) para revelar el reverso.
- La opcion correcta se ilumina en **verde**; si fallaste, tu eleccion en **rojo**.
- El orden no cambia al girar — las opciones permanecen donde las viste.
            """
        )

    st.divider()
    if st.button("🔄 Nueva extraccion", use_container_width=True):
        st.session_state["resultado"] = None
        st.rerun()

    st.stop()

# Pantalla de entrada
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
        st.warning("No se han detectado enlaces de Daypo en el texto introducido todavia.")

col1, col2 = st.columns([3, 1])
with col1:
    iniciar = st.button("Iniciar Extraccion", type="primary", use_container_width=True)
with col2:
    st.caption("Requiere conexion a internet")

if iniciar:
    enlaces = extraer_enlaces_daypo(enlaces_texto)

    if not enlaces:
        st.error("No se han detectado enlaces validos de Daypo en el texto introducido.")
        st.stop()

    es_multiple = len(enlaces) > 1
    headers_web = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    memoria_zip = BytesIO()
    todos_los_tests: list[dict] = []

    if es_multiple:
        doc_unificado = Document()
        doc_unificado.add_heading("Recopilacion completa de tests de Daypo", 0)

    barra = st.progress(0, text="Iniciando...")
    log = st.empty()
    errores = []

    with zipfile.ZipFile(memoria_zip, "w", zipfile.ZIP_DEFLATED) as zip_file:
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
            titulo_carpeta = limpiar_nombre_carpeta(titulo)

            doc_indiv = Document()
            doc_indiv.add_heading(titulo, 1)

            if es_multiple:
                doc_unificado.add_heading(titulo, 1)

            preguntas_con_img: list[dict] = []

            for i, pregunta in enumerate(preguntas, start=1):
                img_bytes = None
                img_nombre = None

                if pregunta["num_imagen"] is not None:
                    img_nombre = f"img_{id_test}_{pregunta['num_imagen']}.jpg"
                    img_bytes = obtener_imagen(id_test, pregunta["num_imagen"], url)
                    if img_bytes:
                        zip_file.writestr(
                            f"{titulo_carpeta}/{img_nombre}",
                            img_bytes,
                        )

                procesar_pregunta(doc_indiv, i, pregunta["enunciado"], img_bytes, pregunta["opciones"])

                if es_multiple:
                    procesar_pregunta(doc_unificado, i, pregunta["enunciado"], img_bytes, pregunta["opciones"])

                preguntas_con_img.append({
                    "enunciado": pregunta["enunciado"],
                    "opciones": pregunta["opciones"],
                    "img_bytes": img_bytes,
                    "img_nombre": img_nombre,
                })

            todos_los_tests.append({"titulo": titulo, "preguntas": preguntas_con_img})

            buf_indiv = BytesIO()
            doc_indiv.save(buf_indiv)
            zip_file.writestr(f"{titulo_carpeta}/{titulo_carpeta}.docx", buf_indiv.getvalue())

            if es_multiple:
                doc_unificado.add_page_break()

        if es_multiple:
            buf_unif = BytesIO()
            doc_unificado.save(buf_unif)
            zip_file.writestr("TODOS_LOS_TESTS_UNIDOS.docx", buf_unif.getvalue())

    barra.progress(100, text="Extraccion completada.")
    log.empty()

    memoria_zip.seek(0)

    nombre_base = generar_nombre_base(todos_los_tests)
    st.session_state["resultado"] = {
        "nombre_base": nombre_base,
        "zip_word": memoria_zip.getvalue(),
        "zip_imagenes": generar_zip_imagenes(todos_los_tests),
        "zip_remnote": generar_zip_remnote(todos_los_tests),
        "apkg_anki": generar_apkg_anki(todos_los_tests),
        "pdf": generar_pdf(todos_los_tests),
        "html_quiz": generar_html_quiz(todos_los_tests, nombre_base),
        "tests_ok": len(enlaces) - len(errores),
        "errores": errores,
    }
    st.rerun()
