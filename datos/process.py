# -*- coding: utf-8 -*-
import json, re, unicodedata

d = json.load(open("raw_data.json", encoding="utf-8"))

# ---------- zona / municipio ----------
ZONE_FIX = {
    "ensanche": "L'Eixample", "l'eixample": "L'Eixample", "eixample": "L'Eixample",
    "el llano del real": "El Pla del Real", "el pla del real": "El Pla del Real",
    "russafa": "Ruzafa", "ruzafa": "Ruzafa",
    "ciutat vella": "Ciutat Vella", "extramurs": "Extramurs", "la zaidia": "La Zaidía",
    "campanar": "Campanar", "patraix": "Patraix", "camins al grau": "Camins al Grau",
    "benicalap": "Benicalap", "algiros": "Algirós", "l'olivereta": "L'Olivereta",
    "rascanya": "Rascanya", "quatre carreres": "Quatre Carreres", "jesus": "Jesús",
    "poblats maritims": "Poblats Marítims", "el pla del remei": "L'Eixample",
}
def strip_ac(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()

def parse_loc(addr):
    if not addr: return ("València", None)
    parts = [p.strip() for p in addr.split(",")]
    idx = None
    for i, p in enumerate(parts):
        if re.match(r"46\d{3}\b", p): idx = i; break
    if idx is None:
        return ("València", None)
    muni = re.sub(r"^46\d{3}\s*", "", parts[idx]).strip()
    muni_norm = "València" if strip_ac(muni) in ("valencia",) else muni
    if strip_ac(muni) == "valencia" and idx > 0:
        barrio = parts[idx-1]
        key = strip_ac(barrio)
        if re.fullmatch(r"\d+", barrio.strip()) or len(barrio) < 3:
            barrio = "Ciutat Vella"; key = "ciutat vella"
        zone = ZONE_FIX.get(key, barrio)
        return (muni_norm, zone)
    return (muni_norm, muni_norm)

# ---------- cadena / franquicia ----------
CHAINS = [
    "toni&guy", "toni & guy", "marco aldany", "llongueras", "jean louis david", "cien x cien",
    "vitaldent", "dentix", "sanitas", "adeslas", "vithas", "quironsalud", "quiron", "asisa",
    "impress", "ruber", "clinica baviera", "dental company", "unidental", "caser",
    "tous", "pandora", "swarovski", "carrera y carrera", "rabat", "unode50", "aristocrazy",
    "vips", "100 montaditos", "cien montaditos", "la sureña", "rodilla", "telepizza", "domino",
    "starbucks", "mcdonald", "burger king", "foster's", "fosters hollywood", "ginos", "goiko",
    "tagliatella", "la tagliatella", "muerde la pasta", "tgb", "pans & company", "pans and company",
    "zara", "mango", "h&m", "bershka", "pull&bear", "pull and bear", "stradivarius", "massimo dutti",
    "springfield", "cortefiel", "women'secret", "oysho", "primark", "lefties", "c&a", "kiabi",
    "decathlon", "intimissimi", "calzedonia", "tezenis", "jack & jones", "guess", "levi's",
    "the north face", "nike", "adidas", "scalpers", "hollister", "desigual", "sfera", "cos ",
]
def is_chain(name, cat, reviews):
    n = strip_ac(name)
    for c in CHAINS:
        if strip_ac(c) in n:
            return True
    return False

# ---------- sentimiento desde reseñas reales ----------
POS = ["excelente","genial","increible","encanta","encanto","perfecto","perfecta","maravillos",
       "recomiend","mejor","delicios","impecable","profesional","atento","atenta","amable",
       "fantastic","estupend","buenisimo","riquisim","acierto","acertamos","calidad","trato inmejorable",
       "diez","fenomenal","espectacular","satisfech","volver","repetir","top","crack","bien","bueno","buena"]
NEG = ["peor","fatal","horrible","pesim","malisim","decepcion","decepion","nunca","estafa","caro",
       "carisimo","lenta","lento","tard","sucio","borde","maleducad","no vuelvo","no recomiend",
       "esperar","desastr","mala experiencia","frio","fría","error","problema","cobrar de mas"]

def sentiment(revs):
    p = n = 0
    for r in revs:
        t = strip_ac(r)
        p += sum(t.count(w) for w in POS)
        n += sum(t.count(w) for w in NEG)
    return p, n

def best_quote(revs):
    if not revs: return None
    scored = []
    for r in revs:
        t = strip_ac(r)
        s = sum(t.count(w) for w in POS) - sum(t.count(w) for w in NEG)
        scored.append((s, r))
    scored.sort(key=lambda x: -x[0])
    q = scored[0][1].replace("\n", " ").strip()
    q = re.sub(r"\s+", " ", q)
    if len(q) > 150: q = q[:147].rsplit(" ", 1)[0] + "…"
    return q

def fmt_int(x):
    return f"{x:,}".replace(",", ".")

def sentiment_text(rating, reviews, revs):
    p, n = sentiment(revs)
    if rating >= 4.7: tono = "Reputación excelente"
    elif rating >= 4.4: tono = "Muy bien valorada"
    elif rating >= 4.0: tono = "Bien valorada"
    elif rating >= 3.5: tono = "Valoración correcta con matices"
    else: tono = "Valoración floja"
    q = best_quote(revs)
    base = f"{tono}: {str(rating).replace('.',',')}★ sobre {fmt_int(reviews)} reseñas."
    if p and not n:
        base += " Reseñas positivas; clientes destacan trato y calidad."
    elif n and n >= p:
        base += " Opiniones mixtas: hay quejas puntuales entre las valoraciones."
    else:
        base += " Comentarios en general favorables."
    if q:
        base += f' «{q}»'
    return base

# ---------- actividad ----------
SECTOR_DESC = {
    "Peluqueria": "Salón local de corte, color, peinado y estética capilar.",
    "Clinica dental": "Clínica de odontología general, estética dental e implantes.",
    "Fisioterapia": "Centro de fisioterapia, rehabilitación y tratamiento del dolor.",
    "Joyeria": "Joyería y relojería con venta y arreglo de piezas y complementos.",
    "Tiendas de ropa": "Tienda de moda y complementos con atención personalizada.",
    "Hosteleria": "Establecimiento de restauración con cocina de producto y sala propia.",
}
def actividad(cat, desc, zone, sector):
    cat = cat or "Negocio local"
    zpart = f" en {zone}" if zone else " en Valencia"
    if desc:
        desc = re.sub(r"\s+", " ", desc).strip()
        return f"{cat}{zpart}. {desc}"
    return f"{cat}{zpart}. {SECTOR_DESC.get(sector, 'Comercio de proximidad de gestión independiente.')}"

# ---------- web / social ----------
SOCIAL_RX = re.compile(r"instagram|facebook|linktr|tiktok|linktree|beacons\.ai|wa\.me|whatsapp", re.I)
def web_class(w):
    if not w: return (False, None, None)          # has_web, real_url, social_url
    if SOCIAL_RX.search(w):
        return (False, None, w)
    return (True, w, None)

# ---------- score ----------
def score_business(rec):
    dt = rec["detail"]
    name = dt.get("name") or rec.get("name_feed") or ""
    rating = dt.get("rating") or 0
    reviews = dt.get("reviews") or 0
    email = rec.get("email")
    has_web, real_url, social_url = web_class(dt.get("website"))
    chain = is_chain(name, dt.get("category"), reviews)
    phone = dt.get("phone")

    s = 50.0
    reasons = []

    # rating (buenas reseñas = sube)
    if rating >= 4.8: s += 15; reasons.append("Valoración sobresaliente (+15)")
    elif rating >= 4.6: s += 12; reasons.append("Valoración excelente (+12)")
    elif rating >= 4.3: s += 8; reasons.append("Buena valoración (+8)")
    elif rating >= 4.0: s += 3; reasons.append("Valoración correcta (+3)")
    elif rating < 3.8 and rating > 0: s -= 6; reasons.append("Valoración baja (−6)")

    # tamaño por nº reseñas (pyme local con recorrido = sweet spot)
    if reviews == 0:
        s -= 2
    elif reviews < 25:
        s += 3; reasons.append("Negocio pequeño/nuevo (+3)")
    elif reviews <= 800:
        s += 14; reasons.append("Pyme local consolidada (+14)")
    elif reviews <= 2500:
        s += 6; reasons.append("Local con buena tracción (+6)")
    elif reviews <= 6000:
        s -= 4; reasons.append("Negocio grande/muy concurrido (−4)")
    else:
        s -= 12; reasons.append("Gran volumen/turístico, decisor lejano (−12)")

    # cadena / franquicia (baja fuerte)
    if chain:
        s -= 32; reasons.append("Cadena/franquicia: quien atiende no decide (−32)")

    # contactabilidad email-first
    if email:
        s += 13; reasons.append("Email localizado: contacto directo (+13)")
    if social_url:
        s += 7; reasons.append("Presencia en redes para contacto (+7)")
    if not email and not social_url:
        s -= 4; reasons.append("Sin email ni redes visibles (−4)")

    # desempate web real (peso mínimo)
    if has_web:
        s += 2
    if not phone and not email and not has_web and not social_url:
        s -= 10; reasons.append("Muy difícil de contactar (−10)")

    s = max(0, min(100, round(s)))
    return s, reasons, chain, has_web, real_url, social_url

# ---------- build ----------
out = []
for rec in d:
    dt = rec["detail"]
    muni, zone = parse_loc(dt.get("address"))
    score, reasons, chain, has_web, real_url, social_url = score_business(rec)
    name = dt.get("name") or rec.get("name_feed") or "—"
    out.append({
        "id": rec["pid"],
        "sector": rec["sector"],
        "nombre": name,
        "telefono": dt.get("phone"),
        "zona": zone or muni,
        "municipio": muni,
        "rating": dt.get("rating"),
        "resenas": dt.get("reviews") or 0,
        "email": rec.get("email"),
        "web": real_url,
        "tiene_web": has_web,
        "red_social": social_url,
        "maps_url": rec["href"],
        "categoria": dt.get("category"),
        "actividad": actividad(dt.get("category"), dt.get("description"), zone, rec["sector"]),
        "sentimiento": sentiment_text(dt.get("rating") or 0, dt.get("reviews") or 0, dt.get("reviews_text", [])),
        "es_cadena": chain,
        "score": score,
        "score_motivos": reasons,
    })

# sector display names
SECTOR_LABEL = {
    "Hosteleria": "Hostelería", "Tiendas de ropa": "Tiendas de ropa",
    "Joyeria": "Joyería", "Peluqueria": "Peluquería",
    "Clinica dental": "Clínica dental", "Fisioterapia": "Fisioterapia",
}
for o in out:
    o["sector"] = SECTOR_LABEL.get(o["sector"], o["sector"])

out.sort(key=lambda x: -x["score"])
json.dump(out, open("businesses.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# stats
from collections import Counter
total = len(out)
zonas = Counter(o["zona"] for o in out)
reviews_sum = sum(o["resenas"] for o in out)
avg = round(sum(o["rating"] for o in out) / total, 2)
print("total", total)
print("poblaciones/zonas", len(zonas))
print("reviews_sum", reviews_sum)
print("avg_rating", avg)
print("con_email", sum(1 for o in out if o["email"]))
print("cadenas", sum(1 for o in out if o["es_cadena"]))
print("score range", min(o["score"] for o in out), max(o["score"] for o in out))
print("top5:", [(o["nombre"][:25], o["score"]) for o in out[:5]])
print("bottom5:", [(o["nombre"][:25], o["score"]) for o in out[-5:]])
print("zonas:", zonas.most_common(12))
