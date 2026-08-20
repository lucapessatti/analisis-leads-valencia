# -*- coding: utf-8 -*-
import csv, os, json, re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "dashboard", "Analisis_Negocios_Valencia.html")

def _num(v):
    return float(v) if v not in (None, "") else None

with open(os.path.join(HERE, "..", "data", "valencia_negocios.csv"), encoding="utf-8-sig", newline="") as f:
    data = []
    for row in csv.DictReader(f):
        row["rating"] = _num(row["rating"])
        row["resenas"] = int(_num(row["resenas"]) or 0)
        row["lat"] = _num(row["lat"])
        row["lng"] = _num(row["lng"])
        row["nucleo_urbano"] = row["nucleo_urbano"] == "True"
        data.append(row)

SECTORS = ["Hostelería","Panadería y dulces","Moda y complementos","Joyería","Belleza",
           "Salud","Retail y hogar","Servicios profesionales","Ocio y alojamiento"]
DISTRITOS = sorted(set(x["distrito_aprox"] for x in data if x.get("distrito_aprox")))

def cid_from(pid):
    m = re.match(r'0x[0-9a-f]+:0x([0-9a-f]+)', pid or "")
    if m:
        try: return str(int(m.group(1),16))
        except Exception: return ""
    return ""

rows = []
for x in data:
    rows.append([
        x.get("nombre") or "",
        SECTORS.index(x["sector"]) if x["sector"] in SECTORS else -1,
        x.get("categoria") or "",
        x.get("rating") if x.get("rating") is not None else None,
        x.get("resenas") or 0,
        x.get("precio_band") or "",
        DISTRITOS.index(x["distrito_aprox"]) if x.get("distrito_aprox") in DISTRITOS else -1,
        round(x["lat"],5) if x.get("lat") is not None else None,
        round(x["lng"],5) if x.get("lng") is not None else None,
        1 if x.get("nucleo_urbano") else 0,
        cid_from(x.get("id")),
    ])

payload = json.dumps({"sectors":SECTORS,"distritos":DISTRITOS,"rows":rows}, ensure_ascii=False, separators=(",",":"))
fecha = "23 de julio de 2026"
total = len(rows)

TEMPLATE = r"""<!DOCTYPE html>
<html lang="es" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Análisis de Negocios · Valencia</title>
<style>
:root{
  --bg:#0e1b24;--bg2:#0c1820;--panel:#132633;--panel2:#0f2029;
  --line:rgba(255,255,255,.08);--line2:rgba(255,255,255,.13);
  --tx:#e8eef2;--mut:#95a6ad;--mut2:#6d828a;
  --teal:#e8b45c;--teal-d:#a8752a;--blue:#7fa8c9;--navy:#182f3d;
  --gold:#e9c46a;--red:#f2657a;--amber:#e8b45c;--purple:#c8a97a;--pink:#d8a48f;--lime:#c9b568;
  --grad:linear-gradient(135deg,#cf8a2c,#e8b45c 55%,#f3cd84);
  --shadow:0 18px 40px -22px rgba(0,0,0,.7);--radius:18px;
}
html[data-theme="light"]{
  --bg:#f4f5f6;--bg2:#ececee;--panel:#ffffff;--panel2:#f8f9fa;
  --line:rgba(20,30,35,.10);--line2:rgba(20,30,35,.16);
  --tx:#1f2a30;--mut:#5c6b72;--mut2:#8a969c;
  --teal:#bd7f26;--teal-d:#9a6a20;--blue:#3d7ea6;--navy:#e7ebee;
  --gold:#b8860b;--red:#d63c58;--amber:#bd7f26;--purple:#8a7a52;--pink:#b07a6a;--lime:#9a8a2a;
  --grad:linear-gradient(135deg,#e0a94f,#e8b45c 55%,#d18f2c);
  --shadow:0 18px 44px -26px rgba(30,42,48,.18);
}
*{box-sizing:border-box}html,body{margin:0;padding:0}
body{background:radial-gradient(1200px 700px at 82% -8%,rgba(232,180,92,.12),transparent 60%),radial-gradient(1000px 600px at -6% 4%,rgba(232,180,92,.06),transparent 55%),var(--bg);
  color:var(--tx);font-family:"Inter",system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;line-height:1.5;-webkit-font-smoothing:antialiased;min-height:100vh;transition:background .5s,color .3s}
.serif{font-family:Georgia,"Times New Roman",serif}
.wrap{max-width:1280px;margin:0 auto;padding:26px 20px 80px}
header.top{display:flex;justify-content:space-between;align-items:flex-start;gap:20px;flex-wrap:wrap;margin-bottom:24px}
.brand{display:flex;align-items:center;gap:14px}
.logo{width:46px;height:46px;border-radius:13px;background:var(--grad);display:grid;place-items:center;box-shadow:0 8px 22px -8px rgba(20,184,166,.6);flex:none}
.logo svg{width:26px;height:26px}
.brand h1{font-size:1.02rem;margin:0;letter-spacing:.02em;font-weight:600}
.brand .sub{color:var(--mut);font-size:.78rem;letter-spacing:.04em;text-transform:uppercase}
.themebtn{background:var(--panel);border:1px solid var(--line2);color:var(--tx);width:42px;height:42px;border-radius:12px;cursor:pointer;font-size:1.1rem}
.themebtn:hover{border-color:var(--teal)}
.hero{margin:6px 0 26px}
.eyebrow{color:var(--teal);font-weight:600;letter-spacing:.14em;text-transform:uppercase;font-size:.72rem;margin-bottom:10px}
.hero h2{font-size:clamp(1.9rem,4.6vw,3.05rem);line-height:1.06;margin:0 0 12px;font-weight:600;letter-spacing:-.01em}
.hero h2 em{font-style:normal;background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent}
.hero p{color:var(--mut);max-width:680px;margin:0;font-size:1.01rem}
.toolbar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:20px 0 24px}
.seg{display:flex;background:var(--panel2);border:1px solid var(--line2);border-radius:12px;padding:4px;gap:2px}
.seg button{background:none;border:none;color:var(--mut);padding:8px 15px;border-radius:9px;cursor:pointer;font-size:.85rem;font-weight:600;transition:.2s}
.seg button.on{background:var(--grad);color:#04231d}
html[data-theme="light"] .seg button.on{color:#3a2a0e}
.dl{margin-left:auto;display:flex;gap:8px}
.dl a{text-decoration:none;background:var(--panel);border:1px solid var(--line2);color:var(--tx);padding:9px 14px;border-radius:11px;font-size:.82rem;font-weight:600;transition:.2s}
.dl a:hover{border-color:var(--teal);transform:translateY(-1px)}
.kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-bottom:26px}
.kpi{background:linear-gradient(180deg,var(--panel),var(--panel2));border:1px solid var(--line);border-radius:var(--radius);padding:18px;position:relative;overflow:hidden;box-shadow:var(--shadow)}
.kpi::before{content:"";position:absolute;inset:0 auto 0 0;width:4px;background:var(--grad)}
.kpi .k-lab{color:var(--mut);font-size:.72rem;text-transform:uppercase;letter-spacing:.07em;margin-bottom:7px}
.kpi .k-val{font-size:1.75rem;font-weight:600;letter-spacing:-.02em;line-height:1}
.kpi .k-val small{font-size:.9rem;color:var(--mut)}
.kpi .k-sub{color:var(--mut2);font-size:.74rem;margin-top:6px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:18px}
.panel{background:linear-gradient(180deg,var(--panel),var(--panel2));border:1px solid var(--line);border-radius:var(--radius);padding:22px;box-shadow:var(--shadow);min-width:0}
.panel h3{margin:0 0 3px;font-size:1.02rem;font-weight:600}
.panel .ph{color:var(--mut);font-size:.8rem;margin-bottom:18px}
.span2{grid-column:1/-1}
.bar-row{display:grid;grid-template-columns:150px 1fr 52px;align-items:center;gap:11px;margin-bottom:9px;font-size:.84rem}
.bar-row .bl{color:var(--mut);text-align:right;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bar-track{height:13px;background:var(--navy);border-radius:8px;overflow:hidden}
.bar-fill{height:100%;width:0;border-radius:8px;transition:width 1s cubic-bezier(.22,1,.36,1)}
.bar-val{font-variant-numeric:tabular-nums;color:var(--tx);font-weight:600;text-align:right}
.hist{display:flex;align-items:flex-end;gap:6px;height:170px;padding-top:10px}
.hist .hb{flex:1;background:var(--grad);border-radius:6px 6px 0 0;position:relative;min-height:2px;transition:height 1s cubic-bezier(.22,1,.36,1);height:0}
.hist .hb span{position:absolute;top:-18px;left:0;right:0;text-align:center;font-size:.68rem;color:var(--mut);font-variant-numeric:tabular-nums}
.hist-x{display:flex;gap:6px;margin-top:7px}
.hist-x div{flex:1;text-align:center;font-size:.68rem;color:var(--mut2)}
canvas{width:100%;height:auto;display:block;border-radius:12px}
.legend{display:flex;flex-wrap:wrap;gap:10px 16px;margin-top:14px}
.legend .li{display:flex;align-items:center;gap:6px;font-size:.76rem;color:var(--mut)}
.legend .dot{width:10px;height:10px;border-radius:50%}
table{width:100%;border-collapse:collapse;font-size:.83rem}
th,td{padding:9px 10px;text-align:left;border-bottom:1px solid var(--line)}
th{color:var(--mut);font-weight:600;font-size:.74rem;text-transform:uppercase;letter-spacing:.04em;cursor:pointer;user-select:none;white-space:nowrap}
th:hover{color:var(--teal)}
td{color:var(--tx)}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
tr.biz:hover td{background:var(--panel2)}
.pill{display:inline-block;padding:2px 8px;border-radius:7px;font-size:.7rem;font-weight:600;color:#04231d}
.stars{color:var(--gold)}
.tlink{color:var(--teal);text-decoration:none;font-weight:600}
.exp-controls{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px}
.exp-controls input,.exp-controls select{background:var(--panel2);border:1px solid var(--line2);color:var(--tx);padding:10px 12px;border-radius:11px;font-size:.85rem;outline:none}
.exp-controls input{flex:1;min-width:180px}
.exp-controls input:focus,.exp-controls select:focus{border-color:var(--teal)}
.pager{display:flex;justify-content:space-between;align-items:center;margin-top:14px;color:var(--mut);font-size:.82rem}
.pager button{background:var(--panel);border:1px solid var(--line2);color:var(--tx);padding:8px 14px;border-radius:10px;cursor:pointer;font-weight:600}
.pager button:disabled{opacity:.35;cursor:default}
.tbl-scroll{overflow-x:auto}
footer{margin-top:44px;padding-top:22px;border-top:1px solid var(--line);color:var(--mut2);font-size:.78rem}
footer b{color:var(--mut)}
.method{background:linear-gradient(180deg,var(--panel),var(--panel2));border:1px solid var(--line);border-radius:var(--radius);padding:22px;box-shadow:var(--shadow);margin-top:18px;font-size:.85rem;color:var(--mut)}
.method h3{color:var(--tx);margin:0 0 10px;font-size:1rem}
.method ul{margin:0;padding-left:18px}.method li{margin-bottom:6px}
@media(max-width:920px){.grid{grid-template-columns:1fr}.kpis{grid-template-columns:repeat(2,1fr)}}
@media(max-width:560px){.wrap{padding:18px 13px 60px}.bar-row{grid-template-columns:110px 1fr 44px}.dl{margin-left:0;width:100%}}
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <div class="brand">
      <div class="logo"><svg viewBox="0 0 24 24" fill="none" stroke="#04231d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 14l4-4 3 3 5-6"/></svg></div>
      <div><h1 class="serif">Análisis de Negocios</h1><div class="sub">Mercado local · Valencia</div></div>
    </div>
    <button class="themebtn" id="themeBtn" title="Tema">◐</button>
  </header>

  <section class="hero">
    <div class="eyebrow">Estudio de mercado · Datos de Google Maps</div>
    <h2 class="serif">El tejido comercial de Valencia,<br><em>en __TOTAL__ negocios.</em></h2>
    <p>Censo de comercios y servicios de Valencia y su entorno urbano a lo largo de 9 grandes sectores y 81 categorías: valoración, reseñas, precio, distribución por distrito y geolocalización. Un retrato del mercado local para análisis y toma de decisiones.</p>
  </section>

  <div class="toolbar">
    <div class="seg" id="scopeSeg">
      <button data-scope="nucleo" class="on">Valencia ciudad</button>
      <button data-scope="all">+ Área metropolitana</button>
    </div>
    <div class="dl">
      <a href="../data/valencia_negocios.csv" download>⬇ Censo (CSV)</a>
      <a href="../data/valencia_negocios_scored.csv" download>⬇ Con score (CSV)</a>
    </div>
  </div>

  <section class="kpis" id="kpis"></section>

  <div class="grid">
    <div class="panel"><h3>Negocios por sector</h3><div class="ph">Volumen de comercios censados en cada gran sector</div><div id="chSector"></div></div>
    <div class="panel"><h3>Valoración media por sector</h3><div class="ph">Estrellas medias de Google (0–5)</div><div id="chRatSector"></div></div>
  </div>
  <div class="grid">
    <div class="panel"><h3>Negocios por distrito</h3><div class="ph">Concentración por distrito (aprox. según coordenadas)</div><div id="chDistrito"></div></div>
    <div class="panel">
      <h3>Distribución de valoraciones</h3><div class="ph">Cuántos negocios caen en cada tramo de estrellas</div>
      <div class="hist" id="chHist"></div>
      <div class="hist-x" id="chHistX"></div>
    </div>
  </div>
  <div class="grid">
    <div class="panel"><h3>Reparto por nivel de precio</h3><div class="ph">Sólo negocios donde Maps indica precio (€ a €€€€)</div><div id="chPrecio"></div></div>
    <div class="panel"><h3>Categorías más numerosas</h3><div class="ph">Top 12 categorías por número de negocios</div><div id="chCat"></div></div>
  </div>

  <div class="panel span2" style="margin-bottom:18px">
    <h3>Mapa del comercio de Valencia</h3><div class="ph">Cada punto es un negocio, coloreado por sector · <span id="mapCount"></span></div>
    <canvas id="map" width="1180" height="620"></canvas>
    <div class="legend" id="mapLegend"></div>
  </div>

  <div class="grid">
    <div class="panel"><h3>Top 12 más reseñados</h3><div class="ph">Los negocios con más opiniones acumuladas</div><div class="tbl-scroll"><table id="tMost"></table></div></div>
    <div class="panel"><h3>Top 12 mejor valorados</h3><div class="ph">Rating más alto con ≥ 300 reseñas (relevancia estadística)</div><div class="tbl-scroll"><table id="tBest"></table></div></div>
  </div>

  <div class="panel span2">
    <h3>Explorador de negocios</h3><div class="ph">Busca y filtra entre los __TOTAL__ negocios del censo</div>
    <div class="exp-controls">
      <input id="q" placeholder="Buscar por nombre o categoría…">
      <select id="fSector"><option value="">Todos los sectores</option></select>
      <select id="fDist"><option value="">Todos los distritos</option></select>
      <select id="fSort">
        <option value="resenas">Orden: más reseñas</option>
        <option value="rating">Mejor valoración</option>
        <option value="nombre">Nombre A–Z</option>
      </select>
    </div>
    <div class="tbl-scroll"><table id="tExp"></table></div>
    <div class="pager"><button id="prev">← Anterior</button><span id="pgInfo"></span><button id="next">Siguiente →</button></div>
  </div>

  <div class="method">
    <h3>Metodología y notas</h3>
    <ul>
      <li><b>Fuente:</b> fichas públicas de Google Maps, recogidas el __FECHA__ mediante scraping automatizado (81 búsquedas por categoría × anclas geográficas por toda la ciudad).</li>
      <li><b>Cobertura:</b> __TOTAL__ negocios únicos; <b id="mNuc"></b> dentro del núcleo urbano de Valencia (≤6 km del centro) y el resto en el área metropolitana colindante.</li>
      <li><b>Distrito aproximado</b> asignado por cercanía de coordenadas al centroide de cada distrito; no es el límite administrativo exacto.</li>
      <li><b>Precio:</b> Google sólo muestra rango de precio en parte de los negocios (sobre todo hostelería), por eso el análisis de precio usa un subconjunto.</li>
      <li><b>Uso:</b> datos orientativos para estudio de mercado. Las valoraciones y reseñas reflejan el momento de la captura.</li>
    </ul>
  </div>

  <footer>Panel de análisis generado el __FECHA__ · <b>__TOTAL__ negocios</b> · Datos públicos de Google Maps · Descarga el dataset completo en CSV/JSON arriba.</footer>
</div>

<script>
const DB = __PAYLOAD__;
const S = DB.sectors, D = DB.distritos, ROWS = DB.rows;
// index map: 0 nombre,1 sectorIdx,2 cat,3 rating,4 resenas,5 precioBand,6 distIdx,7 lat,8 lng,9 nucleo,10 cid
const SC = ["#e8b45c","#c9a227","#e08a5f","#b0895f","#a3b18a","#7fa8c9","#c98a9b","#8d9db0","#9c8fb0"];
let scope = "nucleo";
function active(){ return scope==="nucleo" ? ROWS.filter(r=>r[9]===1) : ROWS; }
function fmt(n){ return (n||0).toLocaleString("es-ES"); }
function mapsLink(r){ return r[10] ? "https://www.google.com/maps?cid="+r[10] : "https://www.google.com/maps/search/"+encodeURIComponent(r[0]+" Valencia"); }

/* theme */
const tb=document.getElementById("themeBtn");
const st=localStorage.getItem("theme_an")||"dark"; document.documentElement.setAttribute("data-theme",st);
tb.onclick=()=>{const t=document.documentElement.getAttribute("data-theme")==="dark"?"light":"dark";document.documentElement.setAttribute("data-theme",t);localStorage.setItem("theme_an",t);drawMap();};

function barChart(el, entries, opts={}){
  const max=Math.max(...entries.map(e=>e[1]),1);
  el.innerHTML=entries.map((e,i)=>{
    const col=opts.color?opts.color(e,i):"var(--grad)";
    const val=opts.fmtVal?opts.fmtVal(e[1]):fmt(e[1]);
    return `<div class="bar-row"><div class="bl" title="${e[0]}">${e[0]}</div>
      <div class="bar-track"><div class="bar-fill" data-w="${(e[1]/max*100).toFixed(1)}" style="background:${col}"></div></div>
      <div class="bar-val">${val}</div></div>`;
  }).join("");
  requestAnimationFrame(()=>setTimeout(()=>el.querySelectorAll(".bar-fill").forEach(b=>b.style.width=b.dataset.w+"%"),50));
}

function render(){
  const rows=active();
  // KPIs
  const rated=rows.filter(r=>r[3]!=null);
  const avg=rated.reduce((a,r)=>a+r[3],0)/(rated.length||1);
  const revSum=rows.reduce((a,r)=>a+r[4],0);
  const dists=new Set(rows.filter(r=>r[6]>=0).map(r=>r[6])).size;
  const cats=new Set(rows.map(r=>r[2]).filter(Boolean)).size;
  document.getElementById("kpis").innerHTML=[
    ["Negocios",fmt(rows.length),"comercios censados"],
    ["Sectores",S.length,"grandes sectores"],
    ["Distritos",dists,"zonas cubiertas"],
    ["Reseñas",fmt(revSum),"opiniones sumadas"],
    ["Valoración media",avg.toFixed(2).replace(".",",")+'<small> ★</small>',"sobre 5 estrellas"],
  ].map(k=>`<div class="kpi"><div class="k-lab">${k[0]}</div><div class="k-val">${k[1]}</div><div class="k-sub">${k[2]}</div></div>`).join("");

  // by sector
  const bySec=S.map((s,i)=>[s,rows.filter(r=>r[1]===i).length]).sort((a,b)=>b[1]-a[1]);
  barChart(document.getElementById("chSector"),bySec,{color:(e)=>SC[S.indexOf(e[0])%SC.length]});
  // rating by sector
  const ratSec=S.map((s,i)=>{const rs=rows.filter(r=>r[1]===i&&r[3]!=null);return [s, rs.length?rs.reduce((a,r)=>a+r[3],0)/rs.length:0];}).sort((a,b)=>b[1]-a[1]);
  barChart(document.getElementById("chRatSector"),ratSec,{color:(e)=>SC[S.indexOf(e[0])%SC.length],fmtVal:v=>v.toFixed(2).replace(".",",")});
  // by district
  const byDist=D.map((d,i)=>[d,rows.filter(r=>r[6]===i).length]).filter(e=>e[1]>0).sort((a,b)=>b[1]-a[1]);
  barChart(document.getElementById("chDistrito"),byDist);
  // histogram of ratings 3.0..5.0 in 0.25 buckets
  const buckets={}; const edges=[];
  for(let x=3.0;x<5.001;x+=0.25){edges.push(+x.toFixed(2));}
  const counts=edges.map(()=>0);
  rated.forEach(r=>{let idx=Math.floor((r[3]-3.0)/0.25);if(r[3]<3)idx=0;if(idx<0)idx=0;if(idx>counts.length-1)idx=counts.length-1;counts[idx]++;});
  const hmax=Math.max(...counts,1);
  document.getElementById("chHist").innerHTML=counts.map(c=>`<div class="hb" data-h="${(c/hmax*100).toFixed(1)}"><span>${c?fmt(c):""}</span></div>`).join("");
  document.getElementById("chHistX").innerHTML=edges.map((e,i)=>i%2===0?`<div>${e.toFixed(1).replace(".",",")}</div>`:`<div></div>`).join("");
  requestAnimationFrame(()=>setTimeout(()=>document.querySelectorAll("#chHist .hb").forEach(b=>b.style.height=b.dataset.h+"%"),50));
  // precio
  const pOrder=["€","€€","€€€","€€€€"];
  const byP=pOrder.map(p=>[p,rows.filter(r=>r[5]===p).length]).filter(e=>e[1]>0);
  barChart(document.getElementById("chPrecio"),byP,{color:()=>"var(--gold)"});
  // categorias top12
  const catC={}; rows.forEach(r=>{if(r[2])catC[r[2]]=(catC[r[2]]||0)+1;});
  const topCat=Object.entries(catC).sort((a,b)=>b[1]-a[1]).slice(0,12);
  barChart(document.getElementById("chCat"),topCat,{color:()=>"var(--blue)"});

  // tables
  const most=[...rows].sort((a,b)=>b[4]-a[4]).slice(0,12);
  const best=[...rows].filter(r=>r[4]>=300&&r[3]!=null).sort((a,b)=>b[3]-a[3]||b[4]-a[4]).slice(0,12);
  const trow=r=>`<tr class="biz"><td><a class="tlink" href="${mapsLink(r)}" target="_blank" rel="noopener">${escapeHtml(r[0])}</a><br><span style="color:var(--mut2);font-size:.72rem">${escapeHtml(r[2]||S[r[1]]||"")}</span></td><td class="num"><span class="stars">★</span> ${r[3]!=null?r[3].toFixed(1).replace(".",","):"–"}</td><td class="num">${fmt(r[4])}</td></tr>`;
  document.getElementById("tMost").innerHTML=`<tr><th>Negocio</th><th class="num">Rating</th><th class="num">Reseñas</th></tr>`+most.map(trow).join("");
  document.getElementById("tBest").innerHTML=`<tr><th>Negocio</th><th class="num">Rating</th><th class="num">Reseñas</th></tr>`+best.map(trow).join("");

  document.getElementById("mNuc").textContent=fmt(ROWS.filter(r=>r[9]===1).length);
  drawMap();
  buildExplorer();
}

function escapeHtml(t){return (t||"").replace(/[&<>"]/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[m]));}

/* ---- canvas map ---- */
function drawMap(){
  const rows=active().filter(r=>r[7]!=null);
  const cv=document.getElementById("map"); const ctx=cv.getContext("2d");
  const W=cv.width,H=cv.height; ctx.clearRect(0,0,W,H);
  // bounds (Valencia core, clip metro extremes for readability)
  const latMin=39.42,latMax=39.52,lngMin=-0.43,lngMax=-0.30;
  const px=(lng)=>((lng-lngMin)/(lngMax-lngMin))*W;
  const py=(lat)=>H-((lat-latMin)/(latMax-latMin))*H;
  const light=document.documentElement.getAttribute("data-theme")==="light";
  document.getElementById("mapCount").textContent=fmt(rows.length)+" negocios geolocalizados";
  for(const r of rows){
    if(r[7]<latMin||r[7]>latMax||r[8]<lngMin||r[8]>lngMax) continue;
    ctx.beginPath();
    ctx.fillStyle=SC[r[1]%SC.length];
    ctx.globalAlpha=light?0.55:0.7;
    ctx.arc(px(r[8]),py(r[7]),1.7,0,6.283);
    ctx.fill();
  }
  ctx.globalAlpha=1;
  document.getElementById("mapLegend").innerHTML=S.map((s,i)=>`<div class="li"><span class="dot" style="background:${SC[i%SC.length]}"></span>${s}</div>`).join("");
}

/* ---- explorer ---- */
let page=0; const PER=25; let filtered=[];
function buildExplorer(){
  const fS=document.getElementById("fSector"), fD=document.getElementById("fDist");
  if(fS.options.length<=1) S.forEach((s,i)=>fS.add(new Option(s,i)));
  if(fD.options.length<=1) D.forEach((d,i)=>fD.add(new Option(d,i)));
  applyExp();
}
function applyExp(){
  const rows=active();
  const term=document.getElementById("q").value.trim().toLowerCase();
  const si=document.getElementById("fSector").value, di=document.getElementById("fDist").value;
  const sort=document.getElementById("fSort").value;
  filtered=rows.filter(r=>{
    if(si!==""&&r[1]!=si) return false;
    if(di!==""&&r[6]!=di) return false;
    if(term&&!(r[0]+" "+(r[2]||"")).toLowerCase().includes(term)) return false;
    return true;
  });
  const cmp={resenas:(a,b)=>b[4]-a[4],rating:(a,b)=>(b[3]||0)-(a[3]||0)||b[4]-a[4],nombre:(a,b)=>a[0].localeCompare(b[0],"es")};
  filtered.sort(cmp[sort]);
  page=0; renderExp();
}
function renderExp(){
  const t=document.getElementById("tExp");
  const start=page*PER, slice=filtered.slice(start,start+PER);
  t.innerHTML=`<tr><th>Negocio</th><th>Sector</th><th>Distrito</th><th class="num">Rating</th><th class="num">Reseñas</th><th>€</th></tr>`+
    slice.map(r=>`<tr class="biz"><td><a class="tlink" href="${mapsLink(r)}" target="_blank" rel="noopener">${escapeHtml(r[0])}</a><br><span style="color:var(--mut2);font-size:.72rem">${escapeHtml(r[2]||"")}</span></td>
      <td><span class="pill" style="background:${SC[r[1]%SC.length]}">${S[r[1]]}</span></td>
      <td>${r[6]>=0?D[r[6]]:"–"}</td>
      <td class="num"><span class="stars">★</span> ${r[3]!=null?r[3].toFixed(1).replace(".",","):"–"}</td>
      <td class="num">${fmt(r[4])}</td><td>${r[5]||"–"}</td></tr>`).join("");
  const pages=Math.max(1,Math.ceil(filtered.length/PER));
  document.getElementById("pgInfo").textContent=`${fmt(filtered.length)} negocios · página ${page+1} de ${fmt(pages)}`;
  document.getElementById("prev").disabled=page<=0;
  document.getElementById("next").disabled=page>=pages-1;
}
document.getElementById("prev").onclick=()=>{if(page>0){page--;renderExp();}};
document.getElementById("next").onclick=()=>{if((page+1)*PER<filtered.length){page++;renderExp();}};
["q","fSector","fDist","fSort"].forEach(id=>document.getElementById(id).addEventListener("input",applyExp));

/* scope toggle */
document.querySelectorAll("#scopeSeg button").forEach(b=>b.onclick=()=>{
  document.querySelectorAll("#scopeSeg button").forEach(x=>x.classList.remove("on"));
  b.classList.add("on"); scope=b.dataset.scope; render();
});
render();
</script>
</body>
</html>"""

html = (TEMPLATE.replace("__PAYLOAD__", payload)
                .replace("__TOTAL__", f"{total:,}".replace(",", "."))
                .replace("__FECHA__", fecha))
open(OUT, "w", encoding="utf-8").write(html)
print("written", round(len(html)/1024/1024,2), "MB ->", os.path.abspath(OUT))
