# -*- coding: utf-8 -*-
import os, io, sys, json, re
if __name__=="__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
from playwright.sync_api import sync_playwright

SHELL = os.path.join(os.environ["LOCALAPPDATA"], "ms-playwright", "chromium_headless_shell-1228", "chrome-headless-shell-win64", "chrome-headless-shell.exe")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
RAW = "mega_raw.json"

# ---- category matrix (all sectors) ----
CATS = {
 "Hostelería": ["restaurantes","bares de tapas","cafeterías","pizzerías","hamburgueserías","arrocerías paella",
   "restaurante japonés","restaurante italiano","restaurante chino","kebab","marisquerías","heladerías",
   "cervecerías","gastrobar","brunch","restaurante vegetariano","comida rápida","bocaterías","vinotecas"],
 "Panadería y dulces": ["panaderías","pastelerías","churrerías","chocolaterías"],
 "Moda y complementos": ["tiendas de ropa","zapaterías","tienda de ropa infantil","lencería","ropa deportiva",
   "tiendas vintage ropa","bolsos y complementos"],
 "Joyería": ["joyerías","relojerías","bisutería"],
 "Belleza": ["peluquerías","barberías","centros de estética","manicura uñas","salones de belleza","spa",
   "estudios de tatuajes","centros de depilación"],
 "Salud": ["clínicas dentales","fisioterapia","clínicas veterinarias","farmacias","centros médicos",
   "psicólogos","podología","clínicas estéticas","ópticas","nutricionistas"],
 "Retail y hogar": ["perfumerías","librerías","jugueterías","tiendas de mascotas","floristerías","ferreterías",
   "tiendas de muebles","decoración hogar","tiendas de electrónica","telefonía móvil","tiendas de bicicletas",
   "tiendas de deporte","estancos","tiendas de regalos"],
 "Servicios profesionales": ["gimnasios","autoescuelas","inmobiliarias","asesorías gestorías","agencias de viajes",
   "abogados","talleres mecánicos","lavanderías","copisterías","academias de idiomas","fotógrafos","notarías"],
 "Ocio y alojamiento": ["hoteles","hostales","salas de escape","boleras"],
}

# ---- geographic anchors across Valencia city (lat,lng,label) ----
ANCHORS = [
 (39.4699,-0.3763,"Centro"),
 (39.4850,-0.3600,"Norte"),
 (39.4560,-0.3880,"Sur"),
 (39.4670,-0.3320,"Este-Marítim"),
 (39.4790,-0.4050,"Oeste-Campanar"),
 (39.4470,-0.3720,"Suroeste"),
]

def handle_consent(page):
    for label in ["Rechazar todo","Reject all","Aceptar todo","Accept all"]:
        try:
            btn=page.get_by_role("button",name=label)
            if btn.count()>0: btn.first.click(timeout=4000); page.wait_for_timeout(1200); return True
        except Exception: pass
    return False

FEED_JS = r'''() => {
  const feed=document.querySelector('div[role="feed"]');
  if(!feed) return [];
  const out=[];
  for(const card of feed.children){
    const a=card.querySelector('a[href*="/maps/place/"]');
    if(!a) continue;
    const t=card.innerText||'';
    if(/Patrocinado|Sponsored/.test(t)) continue;
    let rating=null, reviews=null;
    const rimg=card.querySelector('span[role="img"][aria-label*="estrella"], span[role="img"][aria-label*="star"]');
    if(rimg){const al=rimg.getAttribute('aria-label')||'';
      const rm=al.match(/([\d,\.]+)\s*(estrella|star)/); if(rm)rating=parseFloat(rm[1].replace(',','.'));
      const cm=al.match(/([\d\.\,]+)\s*(rese|review|opini)/i); if(cm)reviews=parseInt(cm[1].replace(/[\.\,]/g,''));
    }
    let website=false;
    for(const l of card.querySelectorAll('a')){const h=l.href||'';if(h&&!h.includes('google.')&&!h.includes('/aclk')){website=true;break;}}
    out.push({name:a.getAttribute('aria-label')||'', href:a.href, rating, reviews, website, text:t});
  }
  return out;
}'''

def parse_card(item):
    t = item.get("text","")
    lines = [l.strip() for l in t.split("\n") if l.strip() and l.strip()!="\xa0"]
    price=None; category=None; address=None; quote=None
    # price: pattern like 10-20 €, 30-50 €, €, €€, Menos de 10 €
    pm = re.search(r'(\d+\s?[-–]\s?\d+\s?€|Menos de \d+\s?€|Más de \d+\s?€|€{1,4}(?!\w))', t)
    if pm: price = pm.group(1).replace("–","-").strip()
    # find category+address line: the line containing ' · ' that comes after the rating token
    for i,l in enumerate(lines):
        if re.match(r'^\d[,\.]\d\(', l) or re.search(r'\(\d[\d.]*\)', l):
            # category line is usually next line with ' · '
            for j in range(i+1, min(i+3,len(lines))):
                if " · " in lines[j] or "·" in lines[j]:
                    segs=[s.strip() for s in re.split(r'·', lines[j]) if s.strip()]
                    # drop icon-only segs
                    segs=[s for s in segs if not re.fullmatch(r'[-\s]+', s)]
                    if segs:
                        category=segs[0]
                        address=segs[-1] if len(segs)>1 else None
                    break
            break
    # quote: a line wrapped in quotes
    for l in lines:
        if (l.startswith('"') and l.endswith('"')) or (l.startswith('«') and l.endswith('»')):
            quote=l.strip('"«» ').strip(); break
    return price, category, address, quote

def place_id(href):
    m=re.search(r'!1s(0x[0-9a-f]+:0x[0-9a-f]+)', href)
    if m: return m.group(1)
    m=re.search(r'/maps/place/([^/@]+)', href)
    return m.group(1) if m else href

def coords(href):
    m=re.search(r'!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)', href)
    if m: return float(m.group(1)), float(m.group(2))
    m=re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', href)
    if m: return float(m.group(1)), float(m.group(2))
    return None, None

def scroll_feed(page, target=120, max_rounds=20):
    prev=0; stag=0
    for i in range(max_rounds):
        n=page.evaluate('''()=>{const f=document.querySelector('div[role="feed"]');return f?[...f.children].filter(c=>c.querySelector('a[href*="/maps/place/"]')).length:0;}''')
        end=page.evaluate('''()=>document.body.innerText.includes('Has llegado al final')||document.body.innerText.includes('reached the end')''')
        if n>=target or end: break
        if n==prev: stag+=1
        else: stag=0
        if stag>=4: break
        prev=n
        page.evaluate('''()=>{const f=document.querySelector('div[role="feed"]');if(f)f.scrollTo(0,f.scrollHeight);}''')
        page.wait_for_timeout(1500)

def run_query(page, cat, lat, lng, zoom=14):
    url=f"https://www.google.com/maps/search/{cat.replace(' ','+')}/@{lat},{lng},{zoom}z?hl=es"
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(2200); handle_consent(page)
    try: page.wait_for_selector('div[role="feed"]', timeout=12000)
    except Exception: return []
    page.wait_for_timeout(1200)
    scroll_feed(page)
    return page.evaluate(FEED_JS)

def make_record(item, sector, cat, anchor):
    pid=place_id(item["href"])
    lat,lng=coords(item["href"])
    price,category,address,quote=parse_card(item)
    return {"pid":pid,"sector":sector,"cat_query":cat,"anchor":anchor,
            "nombre":item["name"],"rating":item["rating"],"resenas":item["reviews"],
            "precio":price,"categoria":category,"direccion":address,"resena_destacada":quote,
            "lat":lat,"lng":lng,"maps_url":item["href"]}

PROG = "mega_progress.json"

def load_state():
    data={}; done=set()
    if os.path.exists(RAW):
        try:
            for r in json.load(open(RAW,encoding="utf-8")): data[r["pid"]]=r
        except Exception: pass
    if os.path.exists(PROG):
        try: done=set(json.load(open(PROG,encoding="utf-8")))
        except Exception: pass
    return data, done

def save_state(data, done):
    json.dump(list(data.values()), open(RAW,"w",encoding="utf-8"), ensure_ascii=False)
    json.dump(sorted(done), open(PROG,"w",encoding="utf-8"), ensure_ascii=False)

if __name__=="__main__":
    mode = sys.argv[1] if len(sys.argv)>1 else "full"
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path=SHELL, headless=True, args=["--window-size=1360,900","--no-sandbox"])
        ctx=b.new_context(locale="es-ES", user_agent=UA, viewport={"width":1360,"height":900})
        page=ctx.new_page()

        if mode=="test":
            items=run_query(page, "restaurantes", *ANCHORS[0][:2])
            print("got", len(items), "items")
            b.close(); sys.exit(0)

        data, done = load_state()
        print(f"resume: {len(data)} businesses, {len(done)} queries done", flush=True)
        qi=0
        total_cats=sum(len(v) for v in CATS.values())
        for sector, cats in CATS.items():
            for cat in cats:
                qi+=1
                key=f"{cat}|BASE"
                if key in done:
                    continue
                # base wide query (city-wide zoom 13, center)
                try:
                    items=run_query(page, cat, ANCHORS[0][0], ANCHORS[0][1], zoom=13)
                except Exception as e:
                    print(f"[{qi}/{total_cats}] {cat} BASE ERR {e}", flush=True); items=[]
                added=0
                for it in items:
                    r=make_record(it, sector, cat, "Centro")
                    if r["pid"] not in data: data[r["pid"]]=r; added+=1
                done.add(key)
                saturated = len(items)>=100
                print(f"[{qi}/{total_cats}] {sector} · {cat}: {len(items)} res, +{added} (tot {len(data)}){' [DENSA→zonas]' if saturated else ''}", flush=True)
                # dense category: dig into each anchor at tighter zoom
                if saturated:
                    for lat,lng,lab in ANCHORS[1:]:
                        akey=f"{cat}|{lab}"
                        if akey in done: continue
                        try:
                            aitems=run_query(page, cat, lat, lng, zoom=15)
                        except Exception as e:
                            print(f"     {cat}@{lab} ERR {e}", flush=True); aitems=[]
                        aadd=0
                        for it in aitems:
                            r=make_record(it, sector, cat, lab)
                            if r["pid"] not in data: data[r["pid"]]=r; aadd+=1
                        done.add(akey)
                        print(f"     {cat}@{lab}: {len(aitems)} res, +{aadd} (tot {len(data)})", flush=True)
                        save_state(data, done)
                save_state(data, done)
        b.close()
    print(f"DONE. {len(data)} unique businesses", flush=True)
