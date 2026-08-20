# -*- coding: utf-8 -*-
"""Quita el fondo negro de un logo con relleno por inundación desde los bordes,
con transición suave en el borde antialiaseado (sin halo ni recorte brusco)."""
from PIL import Image
import numpy as np
from collections import deque
import sys, os

SRC = r"C:\Users\Luca Pessatti\Pictures\Screenshots\Captura de pantalla 2026-08-20 134731.png"
OUT_FULL = r"C:\Claude Code\Prospeccion-Valencia\branding\logo_sin_fondo.png"
OUT_CROP = r"C:\Claude Code\Prospeccion-Valencia\branding\logo_sin_fondo_recortado.png"

LOW, HIGH = 18, 70  # umbrales de "negrura" (brillo máx. de canal)

im = Image.open(SRC).convert("RGBA")
arr = np.array(im).astype(np.int32)
h, w = arr.shape[0], arr.shape[1]
brightness = arr[:, :, :3].max(axis=2)  # 0 = negro puro

# --- flood fill (BFS) desde todos los píxeles del borde que sean muy oscuros ---
visited = np.zeros((h, w), dtype=bool)
q = deque()
for x in range(w):
    for y in (0, h - 1):
        if brightness[y, x] < LOW and not visited[y, x]:
            visited[y, x] = True
            q.append((x, y))
for y in range(h):
    for x in (0, w - 1):
        if brightness[y, x] < LOW and not visited[y, x]:
            visited[y, x] = True
            q.append((x, y))

while q:
    x, y = q.popleft()
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h and not visited[ny, nx] and brightness[ny, nx] < HIGH:
            visited[ny, nx] = True
            q.append((nx, ny))

# --- alpha: 0 dentro de la región de fondo oscura, rampa suave en el borde ---
alpha = arr[:, :, 3].copy()
region_b = brightness[visited]
ramp = np.clip((region_b - LOW) / (HIGH - LOW), 0, 1) * 255
alpha[visited] = ramp.astype(np.int32)

out = arr.copy()
out[:, :, 3] = alpha
out_im = Image.fromarray(out.astype(np.uint8), mode="RGBA")
out_im.save(OUT_FULL)
print("guardado (tamaño original):", OUT_FULL)

# --- recorte al contenido con un margen pequeño ---
alpha_mask = out[:, :, 3] > 5
ys, xs = np.where(alpha_mask)
pad = 10
x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad, w)
y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad, h)
cropped = out_im.crop((x0, y0, x1, y1))
cropped.save(OUT_CROP)
print("guardado (recortado):", OUT_CROP, "tamaño:", cropped.size)
