import pandas as pd

df = pd.read_csv(r"C:\Claude Code\Prospeccion-Valencia\datos\valencia_negocios.csv")

# ¿Cómo se reparten las VALORACIONES?
print("--- RATING ---")
print(df["rating"].describe())

# ¿Y el nº de RESEÑAS? (con percentiles para ver dónde está "la mayoría")
print("\n--- RESEÑAS ---")
print(df["resenas"].describe(percentiles=[.25, .5, .75, .90, .95]))

CADENAS = [
    "mcdonald", "burger king", "kfc", "telepizza", "domino", "starbucks", "vips",
    "100 montaditos", "cien montaditos", "la sureña", "rodilla", "foster", "ginos",
    "tagliatella", "goiko", "pans",
    "zara", "mango", "h&m", "bershka", "pull", "stradivarius", "massimo dutti",
    "springfield", "primark", "lefties", "oysho", "cortefiel", "decathlon",
    "intimissimi", "calzedonia", "nike", "adidas", "sfera", "scalpers",
    "vitaldent", "dentix", "sanitas", "adeslas", "vithas", "quiron", "asisa", "impress",
    "clinica baviera", "dental company",
    "tous", "pandora", "swarovski", "aristocrazy", "unode50",
    "marco aldany", "llongueras", "jean louis david", "toni&guy", "cien x cien",
    "carrefour", "mercadona", "lidl", "consum", "aldi", "dia ",
    "mediamarkt", "worten", "fnac", "el corte ingles", "leroy merlin", "ikea",
    "phone house", "orange", "vodafone", "movistar", "yoigo",
    "norauto", "midas", "feu vert",
]

def es_cadena(nombre):
    nombre = str(nombre).lower()          # todo a minúsculas para comparar
    for c in CADENAS:
        if c in nombre:                   # ¿aparece el nombre de la cadena?
            return True
    return False

def puntuar(fila):
    score = 50
    r = fila["rating"]
    n = fila["resenas"]

    # Factor 1: reputación
    if pd.isna(r):     pass
    elif r >= 4.9:     score += 15
    elif r >= 4.6:     score += 10
    elif r >= 4.2:     score += 4
    elif r >= 4.0:     pass
    else:              score -= 8

    # Factor 2: pyme local
    if   n < 25:       score += 2
    elif n <= 300:     score += 14
    elif n <= 800:     score += 8
    elif n <= 1600:    pass
    else:              score -= 10

    # Factor 3: cadena / franquicia
    if es_cadena(fila["nombre"]):
        score -= 30

    # Factor 4: precio (matiz)
    if fila["precio_band"] in ("€€", "€€€"):
        score += 3

    score = max(0, min(100, score))   # nunca menos de 0 ni más de 100
    return score

df["score"] = df.apply(puntuar, axis=1)

cols = ["nombre", "sector", "rating", "resenas", "es_cadena_flag", "score"]
df["es_cadena_flag"] = df["nombre"].apply(es_cadena)   # columna extra para verlo

print("--- TOP 10 (mejores leads) ---")
print(df[cols].sort_values("score", ascending=False).head(10))

print("\n--- PEORES 10 ---")
print(df[cols].sort_values("score").head(10))

# Resumen general
print(df["score"].describe())

# ¿Cuántos leads hay en cada tramo? (pd.cut trocea el rango en cajones)
print("\nLeads por tramo:")
print(pd.cut(df["score"], bins=[0, 40, 55, 70, 85, 100]).value_counts().sort_index())

# ¿Qué sector concentra los mejores leads?
print("\nScore medio por sector:")
print(df.groupby("sector")["score"].mean().sort_values(ascending=False).round(1))

# Los leads que de verdad merece la pena llamar, en Valencia ciudad
leads = df[(df["score"] >= 75) & (df["nucleo_urbano"] == True)] \
          .sort_values("score", ascending=False)

print(f"{len(leads)} leads calientes en Valencia ciudad")

# Guardar el dataset completo YA puntuado en un CSV nuevo
df.to_csv(r"C:\Claude Code\Prospeccion-Valencia\datos\valencia_negocios_scored.csv",
          index=False, encoding="utf-8-sig")
print("Guardado: valencia_negocios_scored.csv")

import matplotlib.pyplot as plt

# 1. Los datos: score medio por sector, ordenado de menor a mayor
medias = df.groupby("sector")["score"].mean().sort_values()

# 2. Preparamos el lienzo
plt.figure(figsize=(9, 5))

# 3. Barras horizontales (mejor para nombres largos de sector)
plt.barh(medias.index, medias.values, color="#14b8a6")

# 4. Etiquetas y título
plt.xlabel("Score medio de lead")
plt.title("¿Qué sectores tienen los mejores leads? — Valencia")

# 5. Escribimos el valor al final de cada barra
for i, v in enumerate(medias.values):
    plt.text(v + 0.3, i, f"{v:.1f}", va="center")

# 6. Ajustar, guardar y mostrar
plt.tight_layout()
plt.savefig(r"C:\Claude Code\Prospeccion-Valencia\datos\score_por_sector.png", dpi=150)
plt.show()

import numpy as np
import matplotlib.pyplot as plt
import contextily as ctx

ciudad = df[df["nucleo_urbano"] == True].dropna(subset=["lat", "lng"])
leads  = ciudad[ciudad["score"] >= 75]

R = 6378137.0
def a_mercator(lng, lat):
    x = np.radians(lng) * R
    y = np.log(np.tan(np.pi/4 + np.radians(lat)/2)) * R
    return x, y

x_ciudad, y_ciudad = a_mercator(ciudad["lng"], ciudad["lat"])
x_leads,  y_leads  = a_mercator(leads["lng"],  leads["lat"])

fig, ax = plt.subplots(figsize=(10, 10))
fig.patch.set_facecolor("#0e1b24")

# Fríos: azul grisáceo tenue → contexto que no distrae
ax.scatter(x_ciudad, y_ciudad, s=4, c="#8fa3b0", alpha=0.22,
           label="Leads fríos (resto)")
# Calientes: ámbar suave → acento cálido y legible, sin ser neón
ax.scatter(x_leads, y_leads, s=15, c="#e8b45c", alpha=0.85, edgecolors="none",
           label="Leads calientes (≥ 75)")

# Mapa real de Valencia, versión oscura y SIN etiquetas (más limpio)
ctx.add_basemap(ax, source=ctx.providers.CartoDB.DarkMatterNoLabels)

ax.set_title(f"Distribución de leads en Valencia — {len(leads)} calientes",
             color="#e6edf2", fontsize=13)
ax.set_axis_off()
ax.legend(loc="upper right", facecolor="#16303d", edgecolor="none",
          labelcolor="#e6edf2", framealpha=0.85)

plt.tight_layout()
plt.savefig(r"C:\Claude Code\Prospeccion-Valencia\datos\mapa_leads.png",
            dpi=150, bbox_inches="tight", facecolor="#0e1b24")
plt.show()

import matplotlib.pyplot as plt

# leads = Valencia ciudad con score >= 75
leads = df[(df["nucleo_urbano"] == True) & (df["score"] >= 75)]

# contamos leads por sector y ordenamos
por_sector = leads["sector"].value_counts().sort_values()

fig, ax = plt.subplots(figsize=(9, 5.5))
fig.patch.set_facecolor("#0e1b24")
ax.set_facecolor("#0e1b24")

ax.barh(por_sector.index, por_sector.values, color="#e8b45c")

# número al final de cada barra
for i, v in enumerate(por_sector.values):
    ax.text(v + 3, i, str(v), va="center", color="#e6edf2", fontsize=10)

ax.set_title(f"Leads calientes por sector — {len(leads)} en Valencia ciudad",
             color="#e6edf2", fontsize=13)
ax.set_xlabel("Nº de leads", color="#c2d0d8")
ax.tick_params(colors="#c2d0d8")            # color de las etiquetas de los ejes
for spine in ax.spines.values():
    spine.set_visible(False)                # quita el recuadro → más limpio

plt.tight_layout()
plt.savefig(r"C:\Claude Code\Prospeccion-Valencia\datos\leads_por_sector.png",
            dpi=150, bbox_inches="tight", facecolor="#0e1b24")
plt.show()