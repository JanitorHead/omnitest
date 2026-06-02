"""Generador del quiz interactivo HTML autocontenido (offline)."""
import base64
import json

from .utils import separar_opciones

_QUIZ_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;background:#0f172a;color:#e2e8f0;min-height:100vh;padding:16px 12px}
#app{max-width:1100px;margin:0 auto}
.hdr{display:flex;justify-content:space-between;align-items:center;background:#1e293b;border-radius:12px;padding:12px 16px;margin-bottom:12px}
.hdr-title{font-size:13px;color:#94a3b8;font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:60%}
.hdr-score{font-size:13px;color:#60a5fa;font-weight:700;white-space:nowrap}
.pbar{width:100%;height:5px;background:#1e293b;border-radius:99px;margin-bottom:16px;overflow:hidden}
.pfill{height:100%;background:linear-gradient(90deg,#3b82f6,#8b5cf6);border-radius:99px;transition:width .3s ease}
.main{display:flex;gap:16px;align-items:flex-start}
.quiz-area{flex:1;min-width:0}
.card{background:#1e293b;border-radius:14px;padding:24px;box-shadow:0 4px 20px rgba(0,0,0,.3)}
.qnum{font-size:11px;color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:.06em;margin-bottom:10px}
.qtext{font-size:17px;font-weight:600;line-height:1.55;color:#f1f5f9;margin-bottom:16px}
.qimg{width:100%;max-height:260px;object-fit:contain;border-radius:8px;margin-bottom:16px;border:1px solid #334155}
.opts{display:flex;flex-direction:column;gap:8px;margin-bottom:16px}
.opt{padding:12px 15px;background:#0f172a;border:2px solid #334155;border-radius:9px;color:#cbd5e1;font-size:14px;text-align:left;cursor:pointer;transition:all .14s ease;width:100%}
.opt:hover:not(:disabled){border-color:#60a5fa;background:#1e3a5f;color:#e2e8f0}
.opt.sel{border-color:#3b82f6;background:#1d4ed8;color:#fff}
.opt.ok{border-color:#22c55e!important;background:#14532d!important;color:#bbf7d0!important}
.opt.bad{border-color:#ef4444!important;background:#7f1d1d!important;color:#fecaca!important}
.opt:disabled{cursor:default}
.navbar{display:flex;gap:8px;flex-wrap:wrap}
.btn{padding:10px 14px;border:none;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;transition:all .14s ease}
.btn:disabled{opacity:.4;cursor:default}
.btn-prev{background:#334155;color:#94a3b8;flex-shrink:0}.btn-prev:hover:not(:disabled){background:#475569;color:#e2e8f0}
.btn-skip{background:#334155;color:#94a3b8}.btn-skip:hover:not(:disabled){background:#475569;color:#e2e8f0}
.btn-next{background:#3b82f6;color:#fff;flex-shrink:0}.btn-next:hover:not(:disabled){background:#2563eb}
.grid-panel{width:180px;flex-shrink:0;background:#1e293b;border-radius:14px;padding:14px;position:sticky;top:16px}
.gp-title{font-size:11px;color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:.06em;margin-bottom:10px}
.grid{display:grid;grid-template-columns:repeat(5,1fr);gap:5px}
.gq{aspect-ratio:1;border:none;border-radius:5px;font-size:11px;font-weight:700;cursor:pointer;transition:all .12s;color:#94a3b8;background:#0f172a;display:flex;align-items:center;justify-content:center}
.gq:hover{filter:brightness(1.3)}.gq.cur{outline:2px solid #60a5fa;outline-offset:1px;color:#e2e8f0}
.gq.ok{background:#15803d;color:#bbf7d0}.gq.bad{background:#b91c1c;color:#fecaca}
.legend{margin-top:10px;display:flex;flex-direction:column;gap:5px}
.li{display:flex;align-items:center;gap:6px;font-size:11px;color:#64748b}
.ld{width:9px;height:9px;border-radius:2px;flex-shrink:0}
.btn-change{width:100%;margin-top:12px;padding:8px;background:#0f172a;border:none;border-radius:7px;color:#64748b;font-size:11px;font-weight:600;cursor:pointer;transition:all .14s}
.btn-change:hover{background:#334155;color:#94a3b8}
.sel-screen{text-align:center;padding:32px 16px}
.sel-title{font-size:22px;font-weight:700;color:#f1f5f9;margin-bottom:6px}
.sel-sub{font-size:14px;color:#64748b;margin-bottom:24px}
.test-list{display:flex;flex-direction:column;gap:10px;margin-bottom:28px;text-align:left}
.test-item{display:flex;align-items:center;gap:12px;padding:14px 16px;background:#0f172a;border:2px solid #334155;border-radius:10px;cursor:pointer;transition:border-color .15s}
.test-item:hover{border-color:#475569}.test-item.on{border-color:#3b82f6}
.test-item input[type=checkbox]{width:17px;height:17px;cursor:pointer;accent-color:#3b82f6;flex-shrink:0}
.t-name{font-size:14px;font-weight:600;color:#e2e8f0}.t-count{font-size:12px;color:#64748b;margin-top:2px}
.btn-start{background:#3b82f6;color:#fff;border:none;padding:14px 36px;border-radius:10px;font-size:15px;font-weight:700;cursor:pointer}.btn-start:hover{background:#2563eb}
.end{text-align:center;padding:36px 16px}
.end-pct{font-size:68px;font-weight:800;background:linear-gradient(135deg,#3b82f6,#8b5cf6);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.end-sub{font-size:18px;color:#94a3b8;margin:8px 0 28px}
.end-btns{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
.btn-restart{background:#3b82f6;color:#fff;padding:12px 26px;border-radius:9px;font-size:14px;font-weight:700;cursor:pointer;border:none}.btn-restart:hover{background:#2563eb}
@media(max-width:640px){.main{flex-direction:column-reverse}.grid-panel{width:100%;position:static}.grid{grid-template-columns:repeat(8,1fr)}}
"""

_QUIZ_JS = r"""
const TESTS=QUIZ_TESTS_DATA;const TITULO="QUIZ_TITLE";const MULTI=TESTS.length>1;
let selIdx=TESTS.map((_,i)=>i),qs=[],ans=[],rev=[],cho=[],cur=0;
const app=document.getElementById('app');
function shuf(a){const b=[...a];for(let i=b.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[b[i],b[j]]=[b[j],b[i]];}return b;}
const KEY='dq_'+TESTS.reduce((s,t)=>s+t.nombre.slice(0,3),'')+TESTS.reduce((s,t)=>s+t.preguntas.length,0);
function save(){try{localStorage.setItem(KEY,JSON.stringify({qs,ans,rev,cho,cur,selIdx}));}catch(e){}}
function loadSaved(){try{const sv=JSON.parse(localStorage.getItem(KEY)||'null');if(sv&&sv.qs&&sv.qs.length>0){qs=sv.qs;ans=sv.ans;rev=sv.rev;cho=sv.cho;cur=sv.cur||0;selIdx=sv.selIdx||selIdx;return true;}}catch(e){}return false;}
function buildQuestions(idx){qs=[];idx.forEach(i=>shuf(TESTS[i].preguntas).forEach(q=>qs.push({...q})));qs=shuf(qs);qs.forEach(q=>{if(!q._opts)q._opts=shuf([q.correct,...q.wrong]);});ans=qs.map(()=>null);rev=qs.map(()=>false);cho=qs.map(()=>null);cur=0;}
function score(){return ans.filter(a=>a==='correct').length;}
function done(){return rev.filter(Boolean).length;}
function renderSelect(){
  app.innerHTML=`<div class="card sel-screen"><div class="sel-title">${TITULO}</div><div class="sel-sub">Elige los tests que quieres practicar</div><div class="test-list">${TESTS.map((t,i)=>`<label class="test-item on" id="lbl${i}"><input type="checkbox" id="chk${i}" checked onchange="toggleItem(${i})"><div><div class="t-name">${t.nombre}</div><div class="t-count">${t.preguntas.length} preguntas</div></div></label>`).join('')}</div><button class="btn-start" onclick="startSel()">Empezar &rarr;</button></div>`;
}
function toggleItem(i){document.getElementById('lbl'+i).classList.toggle('on',document.getElementById('chk'+i).checked);}
function startSel(){selIdx=TESTS.map((_,i)=>document.getElementById('chk'+i).checked?i:-1).filter(i=>i>=0);if(!selIdx.length){alert('Selecciona al menos un test.');return;}buildQuestions(selIdx);save();renderQuiz();}
function renderQuiz(){
  const q=qs[cur],opts=q._opts,ci=opts.indexOf(q.correct),isRev=rev[cur];
  const imgHtml=q.img?`<img class="qimg" src="data:image/jpeg;base64,${q.img}" alt="">`:'';
  const optsHtml=opts.map((o,i)=>{let c='opt';if(isRev){if(i===ci)c+=' ok';else if(i===cho[cur])c+=' bad';}else if(i===cho[cur])c+=' sel';return`<button class="${c}"${isRev?' disabled':''} onclick="pick(${i})">${o}</button>`;}).join('');
  const navHtml=isRev
    ?`<button class="btn btn-prev" onclick="prev()"${cur===0?' disabled':''}>&larr;</button><span style="flex:1"></span><button class="btn btn-next" onclick="next()">${cur<qs.length-1?'Siguiente &rarr;':'Ver resultado &rarr;'}</button>`
    :`<button class="btn btn-prev" onclick="prev()"${cur===0?' disabled':''}>&larr;</button><span style="flex:1"></span><button class="btn btn-skip" onclick="skipQ()">Saltar sin responder &rarr;</button>`;
  const gridHtml=qs.map((_,i)=>{let c='gq';if(ans[i]==='correct')c+=' ok';else if(ans[i]==='wrong')c+=' bad';if(i===cur)c+=' cur';return`<button class="${c}" onclick="goTo(${i})">${i+1}</button>`;}).join('');
  const pct=qs.length?Math.round(cur/qs.length*100):0;
  app.innerHTML=`<div class="hdr"><span class="hdr-title">${TITULO}</span><span class="hdr-score">${score()}/${done()}</span></div><div class="pbar"><div class="pfill" style="width:${pct}%"></div></div><div class="main"><div class="quiz-area"><div class="card"><div class="qnum">Pregunta ${cur+1} / ${qs.length}</div><div class="qtext">${q.q}</div>${imgHtml}<div class="opts">${optsHtml}</div><div class="navbar">${navHtml}</div></div></div><div class="grid-panel"><div class="gp-title">Preguntas</div><div class="grid">${gridHtml}</div><div class="legend"><div class="li"><div class="ld" style="background:#0f172a;outline:1px solid #334155"></div>Sin responder</div><div class="li"><div class="ld" style="background:#15803d"></div>Correcta</div><div class="li"><div class="ld" style="background:#b91c1c"></div>Incorrecta</div></div>${MULTI?`<button class="btn-change" onclick="renderSelect()">Cambiar tests</button>`:''}</div></div>`;
}
function pick(i){if(rev[cur])return;cho[cur]=i;rev[cur]=true;const ci=qs[cur]._opts.indexOf(qs[cur].correct);ans[cur]=(i===ci)?'correct':'wrong';save();renderQuiz();}
function prev(){if(cur>0){cur--;renderQuiz();}}
function next(){if(cur<qs.length-1){cur++;renderQuiz();}else{renderEnd();}}
function goTo(i){cur=i;renderQuiz();}
function skipQ(){for(let i=cur+1;i<qs.length;i++){if(!rev[i]){cur=i;renderQuiz();return;}}for(let i=0;i<cur;i++){if(!rev[i]){cur=i;renderQuiz();return;}}renderEnd();}
function renderEnd(){
  const tot=qs.length,sc=score(),resp=done(),fallos=resp-sc,sinResp=tot-resp;
  const p=tot?Math.round(sc/tot*100):0;
  const chip=(bg,col,txt)=>`<div style="background:${bg};color:${col};padding:10px 18px;border-radius:10px;font-weight:700;font-size:14px">${txt}</div>`;
  app.innerHTML=`<div class="card end">
    <div class="end-pct">${p}%</div>
    <div class="end-sub">${sc} de ${tot} preguntas acertadas</div>
    <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-bottom:28px">
      ${chip('#14532d','#bbf7d0','✓ '+sc+' aciertos')}
      ${chip('#7f1d1d','#fecaca','✗ '+fallos+' fallos')}
      ${sinResp>0?chip('#334155','#cbd5e1','— '+sinResp+' sin responder'):''}
    </div>
    <div class="end-btns">
      <button class="btn-restart" onclick="restart()">&#x1F504; Repetir quiz</button>
      ${sinResp>0?`<button class="btn-restart" style="background:#475569" onclick="goPending()">Ir a sin responder</button>`:''}
      ${MULTI?`<button class="btn-restart" style="background:#334155" onclick="renderSelect()">Cambiar tests</button>`:''}
    </div>
  </div>`;
}
function goPending(){for(let i=0;i<qs.length;i++){if(!rev[i]){cur=i;renderQuiz();return;}}}
function restart(){buildQuestions(selIdx);save();renderQuiz();}
document.addEventListener('keydown',e=>{
  if(['INPUT','TEXTAREA'].includes(document.activeElement.tagName))return;
  if(e.code==='ArrowLeft'){e.preventDefault();prev();}
  if(e.code==='ArrowRight'||e.code==='Space'){e.preventDefault();if(rev[cur])next();else skipQ();}
  const n=parseInt(e.key);if(!isNaN(n)&&n>=1&&n<=9&&!rev[cur])pick(n-1);
});
(function(){if(MULTI&&!loadSaved()){renderSelect();}else{if(!loadSaved())buildQuestions(selIdx);renderQuiz();}})();
"""

_QUIZ_HTML = (
    "<!DOCTYPE html><html lang='es'><head>"
    "<meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<title>QUIZ_TITLE</title><style>" + _QUIZ_CSS + "</style></head>"
    "<body><div id='app'></div><script>" + _QUIZ_JS + "</script></body></html>"
)


def generar_html_quiz(tests_datos: list[dict], nombre: str) -> bytes:
    tests_js = []
    for test in tests_datos:
        preguntas = []
        for p in test["preguntas"]:
            correcta, incorrectas = separar_opciones(p["opciones"])
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
    nombre_safe = nombre.replace('"', "").replace("'", "")
    html = _QUIZ_HTML.replace("QUIZ_TESTS_DATA", data_json).replace("QUIZ_TITLE", nombre_safe)
    return html.encode("utf-8")
