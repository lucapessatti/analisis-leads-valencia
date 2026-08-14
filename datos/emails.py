import json, re, sys, io, concurrent.futures as cf
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
from scrapling.fetchers import Fetcher

EMAIL_RX = re.compile(r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}')
BAD = ('example.com','sentry.','wixpress.','godaddy','.png','.jpg','.gif','.webp','@2x','@3x','protonmail.com/support','domain.com','email.com','yourdomain','sentry.io','wix.com')
CONTACT_PATHS = ["", "/contacto", "/contact", "/contacta", "/aviso-legal", "/legal", "/es/contacto"]

def norm_url(w):
    w=w.strip()
    if not w.startswith("http"): w="https://"+w
    return w.rstrip("/")

def find_emails(base):
    found=set()
    for path in CONTACT_PATHS:
        url=base+path
        try:
            page=Fetcher.get(url, timeout=12, stealthy_headers=True)
            if page.status>=400: continue
            html=page.html_content
            for m in EMAIL_RX.findall(html):
                m=m.strip().lower()
                if any(b in m for b in BAD): continue
                if m.endswith(('.png','.jpg','.jpeg','.gif','.webp','.svg')): continue
                found.add(m)
            # also mailto
            for mt in re.findall(r'mailto:([^"\'>\s?]+)', html):
                mt=mt.strip().lower()
                if '@' in mt and not any(b in mt for b in BAD): found.add(mt)
            if found: break
        except Exception:
            continue
    # prefer domain-matching emails
    return sorted(found, key=lambda e: (0 if base.split('//')[-1].split('/')[0].replace('www.','') in e else 1, len(e)))

def process(rec):
    d=rec.get("detail",{})
    w=d.get("website")
    if not w: return rec["pid"], None
    try:
        emails=find_emails(norm_url(w))
    except Exception:
        emails=[]
    return rec["pid"], (emails[0] if emails else None)

def main():
    data=json.load(open("raw_data.json",encoding="utf-8"))
    with_web=[r for r in data if r.get("detail",{}).get("website")]
    print(f"{len(data)} records, {len(with_web)} with website", flush=True)
    emap={}
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        futs=[ex.submit(process,r) for r in with_web]
        for i,f in enumerate(cf.as_completed(futs),1):
            pid,email=f.result()
            if email: emap[pid]=email
            if i%10==0: print(f"  {i}/{len(with_web)} processed, {len(emap)} emails", flush=True)
    for r in data:
        r["email"]=emap.get(r["pid"])
    json.dump(data, open("raw_data.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"DONE. {len(emap)} emails found", flush=True)

if __name__=="__main__":
    main()
