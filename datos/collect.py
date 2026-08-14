import os, io, sys, json, time, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
from playwright.sync_api import sync_playwright

SHELL = os.path.join(os.environ["LOCALAPPDATA"], "ms-playwright", "chromium_headless_shell-1228", "chrome-headless-shell-win64", "chrome-headless-shell.exe")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
RAW = "raw_data.json"

QUERIES = [
    ("Hosteleria", "restaurantes Valencia centro", 16),
    ("Hosteleria", "bares de tapas Valencia Ruzafa", 14),
    ("Hosteleria", "cafeterias Valencia centro", 12),
    ("Tiendas de ropa", "tiendas de ropa Valencia centro", 16),
    ("Tiendas de ropa", "boutiques moda Valencia Ruzafa", 12),
    ("Joyeria", "joyerias Valencia centro", 16),
    ("Peluqueria", "peluquerias Valencia centro", 14),
    ("Peluqueria", "peluquerias Valencia Ruzafa", 12),
    ("Clinica dental", "clinicas dentales Valencia centro", 16),
    ("Fisioterapia", "clinicas fisioterapia Valencia centro", 16),
]

def handle_consent(page):
    for label in ["Rechazar todo","Reject all","Aceptar todo","Accept all"]:
        try:
            btn=page.get_by_role("button",name=label)
            if btn.count()>0:
                btn.first.click(timeout=4000); page.wait_for_timeout(1500); return True
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
    const sponsored=/Patrocinado|Sponsored/.test(t);
    let rating=null;
    const rimg=card.querySelector('span[role="img"][aria-label*="estrella"], span[role="img"][aria-label*="star"]');
    if(rimg){const al=rimg.getAttribute('aria-label')||'';const rm=al.match(/([\d,\.]+)/);if(rm)rating=parseFloat(rm[1].replace(',','.'));}
    let website=false;
    for(const l of card.querySelectorAll('a')){const h=l.href||'';if(h&&!h.includes('google.')&&!h.includes('/aclk')){website=true;}}
    out.push({name:a.getAttribute('aria-label')||'', href:a.href, sponsored, rating_feed:rating, website_hint:website});
  }
  return out;
}'''

DETAIL_JS = r'''() => {
  const q=(s)=>document.querySelector(s);
  const txt=(el)=>el?el.textContent.trim():null;
  const r={};
  r.name=txt(q('h1'));
  const rd=q('div.F7nice');
  if(rd){const m=rd.innerText.match(/([\d,\.]+)/);if(m)r.rating=parseFloat(m[1].replace(',','.'));
    const rm=rd.innerText.match(/\(([\d\.\,]+)\)/);if(rm)r.reviews=parseInt(rm[1].replace(/[\.\,]/g,''));}
  if(r.reviews==null){const bm=document.body.innerText.match(/([\d\.\,]+)\s*rese[nñ]as/i);if(bm)r.reviews=parseInt(bm[1].replace(/[\.\,]/g,''));}
  const cat=q('button[jsaction*="category"]'); r.category=txt(cat);
  const info={};
  document.querySelectorAll('[data-item-id]').forEach(b=>{const id=b.getAttribute('data-item-id');const al=b.getAttribute('aria-label')||b.innerText||'';info[id]=al.trim();});
  for(const k in info){
    if(k==='address') r.address=info[k].replace(/^Direcci[oó]n:\s*/i,'');
    if(k.startsWith('phone')) r.phone=info[k].replace(/^Tel[eé]fono:\s*/i,'').replace(/^Phone:\s*/i,'');
    if(k==='authority') r.website=info[k].replace(/^Sitio web:\s*/i,'').replace(/^Website:\s*/i,'');
  }
  const ed=q('div.PYvSYb'); r.description=txt(ed);
  const revs=[]; document.querySelectorAll('span.wiI7pd').forEach(s=>{const t=s.textContent.trim();if(t)revs.push(t);});
  r.reviews_text=revs.slice(0,8);
  return r;
}'''

def place_id(href):
    m=re.search(r'!1s(0x[0-9a-f]+:0x[0-9a-f]+)', href)
    if m: return m.group(1)
    m=re.search(r'/maps/place/([^/@]+)', href)
    return m.group(1) if m else href

def scroll_feed(page, target=16, max_rounds=16):
    prev=0; stagnant=0
    for i in range(max_rounds):
        cards=page.evaluate('''()=>{const f=document.querySelector('div[role="feed"]');return f?[...f.children].filter(c=>c.querySelector('a[href*="/maps/place/"]')).length:0;}''')
        end=page.evaluate('''()=>document.body.innerText.includes('Has llegado al final')||document.body.innerText.includes('reached the end')''')
        if cards>=target or end: break
        if cards==prev: stagnant+=1
        else: stagnant=0
        if stagnant>=3: break
        prev=cards
        page.evaluate('''()=>{const f=document.querySelector('div[role="feed"]');if(f)f.scrollTo(0,f.scrollHeight);}''')
        page.wait_for_timeout(1700)

def collect_feed(page, query, target):
    url=f"https://www.google.com/maps/search/{query.replace(' ','+')}/?hl=es"
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(2500); handle_consent(page)
    try: page.wait_for_selector('div[role="feed"]', timeout=15000)
    except Exception: return []
    page.wait_for_timeout(1500)
    scroll_feed(page, target=target)
    return page.evaluate(FEED_JS)

def get_detail(page, href):
    page.goto(href, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(1500); handle_consent(page)
    try: page.wait_for_selector('h1', timeout=12000)
    except Exception: pass
    page.wait_for_timeout(1500)
    # scroll left panel to load review snippets
    try:
        for _ in range(3):
            page.mouse.move(360,500); page.mouse.wheel(0,1500); page.wait_for_timeout(700)
    except Exception: pass
    return page.evaluate(DETAIL_JS)

def main():
    # load existing
    done={}
    if os.path.exists(RAW):
        try:
            for r in json.load(open(RAW,encoding="utf-8")): done[r["pid"]]=r
        except Exception: pass
    print(f"resume: {len(done)} already done", flush=True)

    with sync_playwright() as p:
        b=p.chromium.launch(executable_path=SHELL, headless=True, args=["--window-size=1360,900","--no-sandbox"])
        ctx=b.new_context(locale="es-ES", user_agent=UA, viewport={"width":1360,"height":900})
        page=ctx.new_page()

        # Phase A: gather candidate list
        candidates={}  # pid -> {sector, href, name, rating_feed, website_hint}
        for sector, query, target in QUERIES:
            try:
                feed=collect_feed(page, query, target)
            except Exception as e:
                print("FEED ERR", query, e); continue
            organic=[f for f in feed if not f["sponsored"]]
            n=0
            for f in organic:
                pid=place_id(f["href"])
                if pid in candidates: continue
                candidates[pid]={"pid":pid,"sector":sector,"query":query,"href":f["href"],
                                 "name_feed":f["name"],"rating_feed":f["rating_feed"],"website_hint":f["website_hint"]}
                n+=1
            print(f"[A] {sector} / {query}: {len(organic)} organic, +{n} new (total {len(candidates)})", flush=True)

        print(f"TOTAL candidates: {len(candidates)}", flush=True)

        # Phase B: details
        results=list(done.values())
        seen={r["pid"] for r in results}
        i=0
        for pid,c in candidates.items():
            i+=1
            if pid in seen: continue
            try:
                d=get_detail(page, c["href"])
            except Exception as e:
                print(f"[B] {i}/{len(candidates)} ERR {c['name_feed']}: {e}", flush=True); d={}
            rec={**c, **{"detail":d}}
            results.append(rec); seen.add(pid)
            nm=(d.get("name") or c.get("name_feed") or "?")
            print(f"[B] {i}/{len(candidates)} {nm} | rating={d.get('rating')} reviews={d.get('reviews')} web={bool(d.get('website'))} revs={len(d.get('reviews_text',[]))}", flush=True)
            # incremental save
            json.dump(results, open(RAW,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
        b.close()
    print("DONE. total records:", len(results), flush=True)

if __name__=="__main__":
    main()
