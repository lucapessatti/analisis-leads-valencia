# -*- coding: utf-8 -*-
import json, datetime, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "Panel_Captacion_Valencia.html")
data = json.load(open(os.path.join(HERE, "businesses.json"), encoding="utf-8"))
payload = json.dumps(data, ensure_ascii=False)
fecha = "23 de julio de 2026"

HTML = r"""<!DOCTYPE html>
<html lang="es" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Prospección Valencia · Panel de captación</title>
<style>
:root{
  --bg:#0a1620; --bg2:#0d1e2a; --panel:#102431; --panel2:#0f2028;
  --line:rgba(255,255,255,.08); --line2:rgba(255,255,255,.13);
  --tx:#e8f1ef; --mut:#8fa6ad; --mut2:#6d858d;
  --teal:#2dd4a7; --teal-d:#0f766e; --blue:#4cc2ff; --navy:#13324a;
  --gold:#e9c46a; --red:#f2657a; --amber:#f4a259;
  --grad:linear-gradient(135deg,#0f766e,#14b8a6 55%,#3aa7d6);
  --shadow:0 18px 40px -22px rgba(0,0,0,.7);
  --radius:18px;
}
html[data-theme="light"]{
  --bg:#eef3f2; --bg2:#e6edeb; --panel:#ffffff; --panel2:#f5f9f8;
  --line:rgba(12,40,44,.10); --line2:rgba(12,40,44,.16);
  --tx:#0c2530; --mut:#5c757d; --mut2:#7b929a;
  --teal:#0f9c7d; --teal-d:#0f766e; --blue:#1c7fb8; --navy:#dfeaf0;
  --gold:#b98a20; --red:#d63c58; --amber:#d17e2a;
  --grad:linear-gradient(135deg,#0f766e,#14b8a6 55%,#2b8fbf);
  --shadow:0 18px 44px -26px rgba(9,40,50,.4);
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  background:radial-gradient(1200px 700px at 82% -8%,rgba(45,212,167,.10),transparent 60%),
             radial-gradient(1000px 600px at -6% 4%,rgba(76,194,255,.09),transparent 55%),
             var(--bg);
  color:var(--tx);
  font-family:"Inter",system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  line-height:1.5; -webkit-font-smoothing:antialiased; min-height:100vh;
  transition:background .5s ease,color .3s ease;
}
.serif{font-family:Georgia,"Times New Roman","Iowan Old Style",serif}
.wrap{max-width:1240px;margin:0 auto;padding:26px 20px 80px}

/* ---------- header ---------- */
header.top{display:flex;justify-content:space-between;align-items:flex-start;gap:20px;flex-wrap:wrap;margin-bottom:26px}
.brand{display:flex;align-items:center;gap:14px}
.logo{width:46px;height:46px;border-radius:13px;background:var(--grad);display:grid;place-items:center;box-shadow:0 8px 22px -8px rgba(20,184,166,.6);flex:none}
.logo svg{width:26px;height:26px}
.brand h1{font-size:1.02rem;margin:0;letter-spacing:.02em;font-weight:600}
.brand .sub{color:var(--mut);font-size:.78rem;letter-spacing:.04em;text-transform:uppercase}
.tzone{display:flex;align-items:center;gap:10px}
.themebtn{background:var(--panel);border:1px solid var(--line2);color:var(--tx);width:42px;height:42px;border-radius:12px;cursor:pointer;display:grid;place-items:center;transition:.25s;font-size:1.1rem}
.themebtn:hover{border-color:var(--teal);transform:translateY(-2px)}

.hero{margin:6px 0 30px}
.eyebrow{color:var(--teal);font-weight:600;letter-spacing:.14em;text-transform:uppercase;font-size:.72rem;margin-bottom:10px}
.hero h2{font-size:clamp(1.9rem,4.6vw,3.05rem);line-height:1.06;margin:0 0 12px;font-weight:600;letter-spacing:-.01em}
.hero h2 em{font-style:normal;background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent}
.hero p{color:var(--mut);max-width:640px;margin:0;font-size:1.01rem}

/* ---------- KPIs ---------- */
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:30px}
.kpi{background:linear-gradient(180deg,var(--panel),var(--panel2));border:1px solid var(--line);border-radius:var(--radius);padding:20px 20px 18px;position:relative;overflow:hidden;box-shadow:var(--shadow)}
.kpi::before{content:"";position:absolute;inset:0 auto 0 0;width:4px;background:var(--grad)}
.kpi .k-lab{color:var(--mut);font-size:.74rem;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px}
.kpi .k-val{font-size:2.05rem;font-weight:600;letter-spacing:-.02em;line-height:1}
.kpi .k-sub{color:var(--mut2);font-size:.78rem;margin-top:7px}
.kpi .k-val small{font-size:1rem;color:var(--mut);font-weight:500}

/* ---------- panels ---------- */
.grid2{display:grid;grid-template-columns:1.05fr .95fr;gap:20px;margin-bottom:30px}
.card-panel{background:linear-gradient(180deg,var(--panel),var(--panel2));border:1px solid var(--line);border-radius:var(--radius);padding:22px;box-shadow:var(--shadow)}
.card-panel h3{margin:0 0 4px;font-size:1.04rem;font-weight:600}
.card-panel .ph{color:var(--mut);font-size:.82rem;margin-bottom:18px}

/* chart */
.bar-row{display:grid;grid-template-columns:120px 1fr 44px;align-items:center;gap:12px;margin-bottom:11px;font-size:.85rem}
.bar-row .bl{color:var(--mut);text-align:right;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bar-track{height:12px;background:var(--navy);border-radius:8px;overflow:hidden;position:relative}
.bar-fill{height:100%;width:0;background:var(--grad);border-radius:8px;transition:width 1.1s cubic-bezier(.22,1,.36,1)}
.bar-val{font-variant-numeric:tabular-nums;color:var(--tx);font-weight:600}

/* sector split */
.split{display:flex;flex-direction:column;gap:12px}
.srow{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:11px 13px;border:1px solid var(--line);border-radius:12px;background:var(--panel2)}
.srow .sl{display:flex;align-items:center;gap:10px;font-size:.9rem}
.dot{width:10px;height:10px;border-radius:50%;flex:none}
.srow .sv{font-weight:600;font-variant-numeric:tabular-nums}
.srow .savg{color:var(--mut);font-size:.78rem;margin-left:4px}

/* ---------- controls ---------- */
.controls{position:sticky;top:0;z-index:30;background:color-mix(in srgb,var(--bg) 82%,transparent);backdrop-filter:blur(14px);
  border:1px solid var(--line);border-radius:16px;padding:14px;margin-bottom:22px;display:flex;gap:12px;flex-wrap:wrap;align-items:center;box-shadow:var(--shadow)}
.search{flex:1;min-width:210px;position:relative}
.search input{width:100%;background:var(--panel2);border:1px solid var(--line2);color:var(--tx);padding:11px 13px 11px 38px;border-radius:11px;font-size:.9rem;outline:none;transition:.2s}
.search input:focus{border-color:var(--teal)}
.search svg{position:absolute;left:12px;top:50%;transform:translateY(-50%);width:16px;height:16px;color:var(--mut)}
select.ctl{background:var(--panel2);border:1px solid var(--line2);color:var(--tx);padding:11px 12px;border-radius:11px;font-size:.87rem;outline:none;cursor:pointer}
.chips{display:flex;gap:7px;flex-wrap:wrap}
.chip{border:1px solid var(--line2);background:var(--panel2);color:var(--mut);padding:8px 13px;border-radius:999px;font-size:.8rem;cursor:pointer;transition:.2s;white-space:nowrap}
.chip:hover{color:var(--tx);border-color:var(--teal)}
.chip.on{background:var(--grad);color:#04231d;border-color:transparent;font-weight:600}
html[data-theme="light"] .chip.on{color:#fff}
.count{color:var(--mut);font-size:.83rem;margin:0 2px 16px;font-weight:500}
.count b{color:var(--tx)}

/* ---------- cards ---------- */
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:18px}
.biz{background:linear-gradient(180deg,var(--panel),var(--panel2));border:1px solid var(--line);border-radius:var(--radius);padding:18px;display:flex;flex-direction:column;gap:12px;position:relative;box-shadow:var(--shadow);
  opacity:0;transform:translateY(14px);animation:rise .5s forwards}
@keyframes rise{to{opacity:1;transform:none}}
.biz.done{border-color:var(--teal-d)}
.biz.done::after{content:"✓ Llamada";position:absolute;top:14px;right:14px;background:var(--teal-d);color:#eafff8;font-size:.66rem;font-weight:700;padding:4px 9px;border-radius:999px;letter-spacing:.05em}
.b-top{display:flex;justify-content:space-between;align-items:flex-start;gap:12px}
.b-sector{font-size:.68rem;text-transform:uppercase;letter-spacing:.08em;color:var(--mut);font-weight:600;display:flex;align-items:center;gap:7px}
.b-name{font-size:1.16rem;font-weight:600;margin:4px 0 0;letter-spacing:-.01em;line-height:1.2}
.scorebadge{flex:none;width:52px;height:52px;border-radius:14px;display:grid;place-items:center;font-weight:700;font-size:1.15rem;font-variant-numeric:tabular-nums;
  background:conic-gradient(var(--sc) calc(var(--p)*1%),var(--navy) 0);position:relative}
.scorebadge span{position:absolute;inset:4px;border-radius:10px;background:var(--panel);display:grid;place-items:center;font-size:1.02rem}
.b-meta{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:.82rem;color:var(--mut)}
.b-meta .mi{display:flex;align-items:center;gap:5px}
.b-meta .mi b{color:var(--tx);font-weight:600}
.stars{color:var(--gold);letter-spacing:1px}
.b-act{font-size:.86rem;color:var(--tx);opacity:.92}
.b-sent{font-size:.82rem;color:var(--mut);border-left:2px solid var(--teal-d);padding-left:11px;line-height:1.45}
.tags{display:flex;flex-wrap:wrap;gap:6px}
.tag{font-size:.7rem;padding:4px 9px;border-radius:8px;border:1px solid var(--line2);color:var(--mut);display:flex;align-items:center;gap:5px}
.tag.ok{color:var(--teal);border-color:color-mix(in srgb,var(--teal) 40%,transparent)}
.tag.warn{color:var(--amber);border-color:color-mix(in srgb,var(--amber) 40%,transparent)}
.tag.chain{color:var(--red);border-color:color-mix(in srgb,var(--red) 40%,transparent)}
.actions{display:flex;gap:8px;flex-wrap:wrap}
.btn{flex:1;min-width:0;text-decoration:none;text-align:center;padding:9px 10px;border-radius:11px;font-size:.8rem;font-weight:600;border:1px solid var(--line2);color:var(--tx);background:var(--panel2);transition:.2s;display:flex;align-items:center;justify-content:center;gap:6px}
.btn:hover{border-color:var(--teal);transform:translateY(-1px)}
.btn.primary{background:var(--grad);color:#04231d;border-color:transparent}
html[data-theme="light"] .btn.primary{color:#fff}
.btn.disabled{opacity:.4;pointer-events:none}
.b-foot{border-top:1px solid var(--line);padding-top:12px;display:flex;flex-direction:column;gap:9px}
.callrow{display:flex;align-items:center;gap:9px;font-size:.84rem;cursor:pointer;user-select:none}
.callrow input{appearance:none;width:20px;height:20px;border:1.5px solid var(--line2);border-radius:6px;cursor:pointer;position:relative;flex:none;transition:.2s}
.callrow input:checked{background:var(--teal-d);border-color:var(--teal-d)}
.callrow input:checked::after{content:"✓";position:absolute;inset:0;display:grid;place-items:center;color:#fff;font-size:.8rem}
.notes{width:100%;background:var(--panel2);border:1px solid var(--line);border-radius:10px;color:var(--tx);padding:9px 11px;font-size:.82rem;font-family:inherit;resize:vertical;min-height:38px;outline:none;transition:.2s}
.notes:focus{border-color:var(--teal)}
.notes::placeholder{color:var(--mut2)}
.saved{font-size:.68rem;color:var(--teal);opacity:0;transition:.3s}
.saved.show{opacity:1}
.empty{text-align:center;color:var(--mut);padding:60px 20px}
#toast{position:fixed;left:50%;bottom:26px;transform:translateX(-50%) translateY(20px);background:var(--panel);border:1px solid var(--teal);color:var(--tx);padding:12px 18px;border-radius:12px;font-size:.85rem;font-weight:500;box-shadow:0 14px 34px -12px rgba(0,0,0,.6);z-index:100;opacity:0;pointer-events:none;transition:.3s;max-width:90vw}
#toast.show{opacity:1;transform:translateX(-50%) translateY(0)}

footer{margin-top:50px;padding-top:22px;border-top:1px solid var(--line);color:var(--mut2);font-size:.78rem;display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px}
footer a{color:var(--teal);text-decoration:none}

@media(max-width:900px){.grid2{grid-template-columns:1fr}.kpis{grid-template-columns:repeat(2,1fr)}}
@media(max-width:560px){.wrap{padding:18px 13px 60px}.kpi .k-val{font-size:1.7rem}.cards{grid-template-columns:1fr}.bar-row{grid-template-columns:96px 1fr 38px}}
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <div class="brand">
      <div class="logo"><svg viewBox="0 0 24 24" fill="none" stroke="#04231d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 11l19-9-9 19-2-8-8-2z"/></svg></div>
      <div>
        <h1 class="serif">Panel de Captación</h1>
        <div class="sub">Prospección comercial · Valencia</div>
      </div>
    </div>
    <div class="tzone">
      <button class="themebtn" id="themeBtn" title="Cambiar tema">◐</button>
    </div>
  </header>

  <section class="hero">
    <div class="eyebrow">Inteligencia de ventas</div>
    <h2 class="serif">Negocios locales de Valencia,<br><em>listos para llamar.</em></h2>
    <p>Radiografía de __TOTAL__ comercios de hostelería, moda, joyería, peluquería, clínicas dentales y fisioterapia en Valencia centro y alrededores. Cada ficha, leída y puntuada para priorizar a quién contactar primero.</p>
  </section>

  <section class="kpis" id="kpis"></section>

  <section class="grid2">
    <div class="card-panel">
      <h3>Reparto por zona</h3>
      <div class="ph">Concentración de oportunidades por barrio / población</div>
      <div id="chart"></div>
    </div>
    <div class="card-panel">
      <h3>Sectores y valoración media</h3>
      <div class="ph">Volumen de negocios y estrellas medias por sector</div>
      <div class="split" id="split"></div>
    </div>
  </section>

  <div class="controls">
    <div class="search">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4-4"/></svg>
      <input id="q" type="text" placeholder="Buscar negocio, zona o categoría…">
    </div>
    <select class="ctl" id="sort">
      <option value="score">Ordenar: puntuación ↓</option>
      <option value="score_asc">Puntuación ↑</option>
      <option value="reviews">Nº de reseñas ↓</option>
      <option value="rating">Valoración ↓</option>
      <option value="name">Nombre A–Z</option>
    </select>
    <select class="ctl" id="estado">
      <option value="all">Todas</option>
      <option value="pend">Pendientes</option>
      <option value="done">Llamadas hechas</option>
      <option value="email">Con email</option>
    </select>
  </div>
  <div class="chips" id="sectors" style="margin-bottom:16px"></div>

  <div class="count" id="count"></div>
  <section class="cards" id="cards"></section>
  <div class="empty" id="empty" style="display:none">No hay negocios que coincidan con el filtro.</div>

  <footer>
    <div>Panel generado el __FECHA__ · Datos públicos de Google Maps · __TOTAL__ negocios analizados</div>
    <div>Tus notas y llamadas se guardan en este navegador.</div>
  </footer>
</div>

<script>
const DATA = __PAYLOAD__;
const SECTOR_COLORS = {
  "Hostelería":"#2dd4a7","Tiendas de ropa":"#4cc2ff","Joyería":"#e9c46a",
  "Peluquería":"#c084fc","Clínica dental":"#5eead4","Fisioterapia":"#f4a259"
};
const LS = "prospeccion_valencia_v1";
let store = {};
try{ store = JSON.parse(localStorage.getItem(LS)||"{}"); }catch(e){ store={}; }
function save(){ localStorage.setItem(LS, JSON.stringify(store)); }
function rec(id){ return store[id] || (store[id]={done:false,notes:""}); }

/* ---- theme ---- */
const themeBtn = document.getElementById("themeBtn");
const savedTheme = localStorage.getItem("theme_pv") || "dark";
document.documentElement.setAttribute("data-theme", savedTheme);
themeBtn.onclick = ()=>{
  const t = document.documentElement.getAttribute("data-theme")==="dark"?"light":"dark";
  document.documentElement.setAttribute("data-theme", t);
  localStorage.setItem("theme_pv", t);
  renderChart();
};

/* ---- KPIs ---- */
function fmt(n){ return n.toLocaleString("es-ES"); }
const total = DATA.length;
const zonas = [...new Set(DATA.map(d=>d.zona))];
const reviewsSum = DATA.reduce((a,d)=>a+(d.resenas||0),0);
const avg = (DATA.reduce((a,d)=>a+(d.rating||0),0)/total);
document.getElementById("kpis").innerHTML = [
  ["Negocios analizados", fmt(total), "fichas leídas y puntuadas"],
  ["Zonas cubiertas", zonas.length, "barrios y poblaciones"],
  ["Reseñas sumadas", fmt(reviewsSum), "opiniones agregadas"],
  ["Valoración media", avg.toFixed(2).replace(".",",")+"<small> ★</small>", "sobre 5 estrellas"]
].map(k=>`<div class="kpi"><div class="k-lab">${k[0]}</div><div class="k-val">${k[1]}</div><div class="k-sub">${k[2]}</div></div>`).join("");

/* ---- chart by zone ---- */
function renderChart(){
  const counts = {};
  DATA.forEach(d=>counts[d.zona]=(counts[d.zona]||0)+1);
  const arr = Object.entries(counts).sort((a,b)=>b[1]-a[1]);
  const max = arr[0][1];
  document.getElementById("chart").innerHTML = arr.map(([z,c])=>`
    <div class="bar-row">
      <div class="bl" title="${z}">${z}</div>
      <div class="bar-track"><div class="bar-fill" data-w="${(c/max*100).toFixed(1)}"></div></div>
      <div class="bar-val">${c}</div>
    </div>`).join("");
  requestAnimationFrame(()=>{ setTimeout(()=>{
    document.querySelectorAll(".bar-fill").forEach(b=>b.style.width=b.dataset.w+"%");
  },60); });
}
renderChart();

/* ---- sector split ---- */
(function(){
  const by = {};
  DATA.forEach(d=>{ (by[d.sector]=by[d.sector]||[]).push(d); });
  const rows = Object.entries(by).sort((a,b)=>b[1].length-a[1].length).map(([s,list])=>{
    const av = (list.reduce((a,d)=>a+d.rating,0)/list.length).toFixed(2).replace(".",",");
    const col = SECTOR_COLORS[s]||"#2dd4a7";
    return `<div class="srow"><div class="sl"><span class="dot" style="background:${col}"></span>${s}</div>
      <div><span class="sv">${list.length}</span><span class="savg">· ${av}★</span></div></div>`;
  }).join("");
  document.getElementById("split").innerHTML = rows;
})();

/* ---- sector chips ---- */
const sectorList = [...new Set(DATA.map(d=>d.sector))];
let activeSector = "all";
const chipsEl = document.getElementById("sectors");
function renderChips(){
  chipsEl.innerHTML = `<div class="chip ${activeSector==='all'?'on':''}" data-s="all">Todos los sectores</div>` +
    sectorList.map(s=>`<div class="chip ${activeSector===s?'on':''}" data-s="${s}">${s}</div>`).join("");
  chipsEl.querySelectorAll(".chip").forEach(c=>c.onclick=()=>{ activeSector=c.dataset.s; renderChips(); render(); });
}
renderChips();

/* ---- helpers ---- */
function stars(r){ const f=Math.round(r); return "★".repeat(f)+"☆".repeat(5-f); }
function scoreColor(s){ return s>=75?"var(--teal)":s>=55?"var(--blue)":s>=40?"var(--amber)":"var(--red)"; }
function esc(t){ return (t||"").replace(/[&<>"]/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[m])); }

/* ---- render cards ---- */
/* ---- copiar + toast + email ---- */
function copyText(t){
  if(navigator.clipboard && navigator.clipboard.writeText){ return navigator.clipboard.writeText(t).catch(()=>fallbackCopy(t)); }
  return Promise.resolve(fallbackCopy(t));
}
function fallbackCopy(t){ try{const ta=document.createElement("textarea");ta.value=t;ta.style.position="fixed";ta.style.opacity="0";document.body.appendChild(ta);ta.select();document.execCommand("copy");document.body.removeChild(ta);}catch(e){} }
let toastT;
function toast(msg){
  let el=document.getElementById("toast");
  if(!el){ el=document.createElement("div"); el.id="toast"; document.body.appendChild(el); }
  el.textContent=msg; el.classList.add("show");
  clearTimeout(toastT); toastT=setTimeout(()=>el.classList.remove("show"),2600);
}
function copyToast(t,label){ copyText(t); toast((label||"Copiado")+": "+t); }
function emailAction(addr){
  copyText(addr);
  window.open("https://mail.google.com/mail/?view=cm&fs=1&to="+encodeURIComponent(addr),"_blank","noopener");
  toast("Email copiado y abriendo Gmail: "+addr);
}

const q = document.getElementById("q"), sortEl=document.getElementById("sort"), estadoEl=document.getElementById("estado");
function render(){
  let list = DATA.slice();
  const term = q.value.trim().toLowerCase();
  if(activeSector!=="all") list=list.filter(d=>d.sector===activeSector);
  const est = estadoEl.value;
  if(est==="pend") list=list.filter(d=>!rec(d.id).done);
  else if(est==="done") list=list.filter(d=>rec(d.id).done);
  else if(est==="email") list=list.filter(d=>d.email);
  if(term) list=list.filter(d=>(d.nombre+" "+d.zona+" "+(d.categoria||"")+" "+d.sector).toLowerCase().includes(term));
  const s=sortEl.value;
  const cmp={score:(a,b)=>b.score-a.score,score_asc:(a,b)=>a.score-b.score,
    reviews:(a,b)=>b.resenas-a.resenas,rating:(a,b)=>b.rating-a.rating,
    name:(a,b)=>a.nombre.localeCompare(b.nombre,"es")};
  list.sort(cmp[s]);

  document.getElementById("count").innerHTML = `Mostrando <b>${list.length}</b> de ${total} negocios`;
  const cards = document.getElementById("cards");
  document.getElementById("empty").style.display = list.length?"none":"block";
  cards.innerHTML = list.map((d,i)=>{
    const r=rec(d.id);
    const tel = d.telefono ? `<a class="btn" href="tel:${d.telefono.replace(/\s/g,'')}" onclick="copyToast('${d.telefono.replace(/\s/g,'')}','Teléfono copiado')">📞 ${esc(d.telefono)}</a>` : `<span class="btn disabled">Sin teléfono</span>`;
    const mail = d.email ? `<button type="button" class="btn" onclick="emailAction('${d.email}')">✉ Email</button>` : "";
    const col = SECTOR_COLORS[d.sector]||"#2dd4a7";
    const tags=[];
    tags.push(d.tiene_web?`<span class="tag ok">🌐 Con web</span>`:(d.red_social?`<span class="tag ok">📱 Redes</span>`:`<span class="tag warn">Sin web</span>`));
    if(d.email) tags.push(`<span class="tag ok">✉ Email</span>`);
    if(d.es_cadena) tags.push(`<span class="tag chain">Cadena/franquicia</span>`);
    return `<article class="biz ${r.done?'done':''}" style="animation-delay:${Math.min(i*28,420)}ms">
      <div class="b-top">
        <div>
          <div class="b-sector"><span class="dot" style="background:${col}"></span>${d.sector}</div>
          <h3 class="b-name serif">${esc(d.nombre)}</h3>
        </div>
        <div class="scorebadge" style="--sc:${scoreColor(d.score)};--p:${d.score}"><span>${d.score}</span></div>
      </div>
      <div class="b-meta">
        <span class="mi"><span class="stars">${stars(d.rating)}</span> <b>${(d.rating||0).toFixed(1).replace(".",",")}</b></span>
        <span class="mi">💬 <b>${fmt(d.resenas)}</b> reseñas</span>
        <span class="mi">📍 ${esc(d.zona)}</span>
        ${d.telefono?`<span class="mi">☎ ${esc(d.telefono)}</span>`:""}
      </div>
      <div class="b-act">${esc(d.actividad)}</div>
      <div class="b-sent">${esc(d.sentimiento)}</div>
      <div class="tags">${tags.join("")}</div>
      <div class="actions">
        <a class="btn primary" href="${d.maps_url}" target="_blank" rel="noopener">Ver en Maps ↗</a>
        ${tel}${mail}
      </div>
      <div class="b-foot">
        <label class="callrow"><input type="checkbox" data-done="${d.id}" ${r.done?'checked':''}> Marcar como llamada realizada</label>
        <textarea class="notes" data-notes="${d.id}" placeholder="Notas de la llamada: con quién hablé, objeciones, próximos pasos…">${esc(r.notes)}</textarea>
        <span class="saved" data-saved="${d.id}">✓ Guardado</span>
      </div>
    </article>`;
  }).join("");

  cards.querySelectorAll("[data-done]").forEach(cb=>cb.onchange=()=>{
    rec(cb.dataset.done).done=cb.checked; save();
    cb.closest(".biz").classList.toggle("done",cb.checked);
    if(estadoEl.value!=="all") render();
  });
  cards.querySelectorAll("[data-notes]").forEach(ta=>{
    let t; ta.oninput=()=>{ rec(ta.dataset.notes).notes=ta.value; clearTimeout(t);
      t=setTimeout(()=>{ save(); const s=cards.querySelector(`[data-saved="${ta.dataset.notes}"]`);
        if(s){s.classList.add("show");setTimeout(()=>s.classList.remove("show"),1200);} },400); };
  });
}
q.oninput=render; sortEl.onchange=render; estadoEl.onchange=render;
render();
</script>
</body>
</html>"""

HTML = (HTML.replace("__PAYLOAD__", payload)
            .replace("__TOTAL__", str(len(data)))
            .replace("__FECHA__", fecha))
open(OUT, "w", encoding="utf-8").write(HTML)
print("written", len(HTML), "bytes ->", os.path.abspath(OUT))
