# -*- coding: utf-8 -*-
import json, re, csv, math
from collections import Counter

SRC = "mega_raw.json"
raw = json.load(open(SRC, encoding="utf-8"))

# ---- approx Valencia districts by centroid ----
DISTRITOS = {
 "Ciutat Vella":(39.4750,-0.3770),"L'Eixample":(39.4630,-0.3720),"Extramurs":(39.4700,-0.3860),
 "Campanar":(39.4820,-0.4000),"La Zaidia":(39.4880,-0.3760),"El Pla del Real":(39.4770,-0.3630),
 "L'Olivereta":(39.4700,-0.4030),"Patraix":(39.4600,-0.3960),"Jesús":(39.4560,-0.3830),
 "Quatre Carreres":(39.4470,-0.3670),"Poblats Marítims":(39.4620,-0.3300),"Camins al Grau":(39.4590,-0.3480),
 "Algirós":(39.4720,-0.3450),"Benimaclet":(39.4880,-0.3620),"Rascanya":(39.4930,-0.3800),
 "Benicalap":(39.4950,-0.4000),
}
CENTER=(39.4699,-0.3763)
def hav(a,b):
    R=6371; la1,lo1=map(math.radians,a); la2,lo2=map(math.radians,b)
    dla=la2-la1; dlo=lo2-lo1
    x=math.sin(dla/2)**2+math.cos(la1)*math.cos(la2)*math.sin(dlo/2)**2
    return 2*R*math.asin(math.sqrt(x))
def distrito(lat,lng):
    if lat is None: return (None,None)
    best=None;bd=1e9
    for name,c in DISTRITOS.items():
        d=hav((lat,lng),c)
        if d<bd: bd=d;best=name
    dc=hav((lat,lng),CENTER)
    return best, round(dc,2)

def price_band(p):
    if not p: return (None,None,None)
    nums=[int(x) for x in re.findall(r'\d+', p)]
    if not nums:
        # €, €€, €€€ style
        e=p.count('€')
        return ({1:'€',2:'€€',3:'€€€',4:'€€€€'}.get(e,None), None, None)
    lo=min(nums); hi=max(nums); mid=round((lo+hi)/2,1)
    if mid<10: band='€'
    elif mid<=25: band='€€'
    elif mid<=45: band='€€€'
    else: band='€€€€'
    return (band, mid, f"{lo}-{hi} €")

# category consolidation for cleaner analysis
def clean_cat(c):
    if not c: return None
    return c.strip()

out=[]
seen=set()
for r in raw:
    if r["pid"] in seen: continue
    seen.add(r["pid"])
    lat,lng=r.get("lat"),r.get("lng")
    dist,dc=distrito(lat,lng)
    band,mid,rng=price_band(r.get("precio"))
    out.append({
        "id":r["pid"],"nombre":r.get("nombre"),"sector":r["sector"],
        "busqueda":r.get("cat_query"),"categoria":clean_cat(r.get("categoria")),
        "rating":r.get("rating"),"resenas":r.get("resenas") or 0,
        "precio_txt":r.get("precio"),"precio_band":band,"precio_medio_eur":mid,
        "distrito_aprox":dist,"dist_centro_km":dc,
        "nucleo_urbano": (dc is not None and dc<=6),
        "direccion":r.get("direccion"),"lat":lat,"lng":lng,
        "resena_destacada":r.get("resena_destacada"),"maps_url":r.get("maps_url"),
    })

# exports
json.dump(out, open("valencia_negocios.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
cols=["id","nombre","sector","busqueda","categoria","rating","resenas","precio_txt","precio_band",
      "precio_medio_eur","distrito_aprox","dist_centro_km","nucleo_urbano","direccion","lat","lng","resena_destacada","maps_url"]
with open("valencia_negocios.csv","w",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f, fieldnames=cols); w.writeheader()
    for o in out: w.writerow(o)

# summary
n=len(out)
print("TOTAL negocios:", n)
print("sectores:", dict(Counter(o["sector"] for o in out)))
print("con rating:", sum(1 for o in out if o["rating"]))
print("con precio:", sum(1 for o in out if o["precio_band"]))
print("distritos:", len(set(o["distrito_aprox"] for o in out if o["distrito_aprox"])))
print("reseñas totales:", sum(o["resenas"] for o in out))
rated=[o for o in out if o["rating"]]
print("rating medio:", round(sum(o["rating"] for o in rated)/len(rated),3) if rated else None)
print("dist top:", Counter(o["distrito_aprox"] for o in out if o["distrito_aprox"]).most_common(6))
