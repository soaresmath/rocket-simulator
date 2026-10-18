"""Gera os sprites dos astros (pixel art, 1 pixel do sprite = 1 pixel do jogo).

Uso: python tools/gerar_planetas.py   ->   assets/planets/<nome>.png
"""
import os

import numpy as np
from PIL import Image

LUZ = np.array([-0.55, -0.5, 0.67])      # luz vindo do alto à esquerda (y para baixo)
LUZ = LUZ / np.linalg.norm(LUZ)
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0


def tons(base):
    """4 tons de uma cor: sombra, escuro, base, claro."""
    return np.array([np.clip(np.array(base) * f, 0, 255) for f in (0.42, 0.68, 1.0, 1.22)], dtype=np.uint8)


def ruido(u, v, escala, semente):
    tabela = np.random.default_rng(semente).random((256, 256))
    x, y = u * escala, v * escala
    x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
    fx, fy = x - x0, y - y0
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    x1, y1 = (x0 + 1) % 256, (y0 + 1) % 256
    x0, y0 = x0 % 256, y0 % 256
    a = tabela[y0, x0] * (1 - fx) + tabela[y0, x1] * fx
    b = tabela[y1, x0] * (1 - fx) + tabela[y1, x1] * fx
    return a * (1 - fy) + b * fy


def fbm(u, v, escala, semente, oitavas=5):
    total = soma = 0.0
    amp = 1.0
    for o in range(oitavas):
        total, soma = total + amp * ruido(u, v, escala * 2 ** o, semente + o), soma + amp
        amp *= 0.5
    return total / soma


class Esfera:
    """Geometria de um disco visto como esfera: coordenadas, lat/lon e tom de luz (0-3)."""

    def __init__(self, d):
        self.d = d
        ys, xs = np.mgrid[0:d, 0:d]
        r = d / 2
        self.x, self.y = (xs + 0.5 - r) / r, (ys + 0.5 - r) / r
        rr = self.x ** 2 + self.y ** 2
        self.rr, self.mask = rr, rr <= 1
        self.z = np.sqrt(np.clip(1 - rr, 0, 1))
        self.lat = np.arcsin(np.clip(-self.y, -1, 1))
        self.lon = np.arctan2(self.x, self.z)
        intensidade = self.x * LUZ[0] + self.y * LUZ[1] + self.z * LUZ[2]
        dither = (BAYER[ys % 4, xs % 4] - 0.5) * 0.18   # padrão de pontos na transição de luz
        self.luz = np.digitize(intensidade + dither, [0.0, 0.32, 0.62])

    def ruido(self, escala, semente, oitavas=5, dx=0.0, dy=0.0):
        return fbm(self.lon + dx, self.lat + dy, escala, semente, oitavas)

    def cratera(self, tom, n, semente, raio_min=0.04, raio_max=0.16):
        """Escurece o interior e clareia a borda de n crateras."""
        rng = np.random.default_rng(semente)
        tom = tom.copy()
        for _ in range(n):
            cx, cy = rng.uniform(-0.85, 0.85, 2)
            cr = rng.uniform(raio_min, raio_max)
            dist = np.hypot(self.x - cx, self.y - cy)
            dentro = dist < cr
            borda = (dist >= cr) & (dist < cr + 0.022)
            lado_luz = ((self.x - cx) * LUZ[0] + (self.y - cy) * LUZ[1]) < -0.25 * cr
            tom = np.where(dentro, tom - 1 - (dentro & lado_luz), tom)
            tom = np.where(borda & (self.x * 0 + (-(self.x - cx) * LUZ[0] - (self.y - cy) * LUZ[1]) < 0), tom + 1, tom)
        return np.clip(tom, 0, 3)


def salvar(esf, rgb, caminho, aro=None):
    if aro is not None:  # anel fino de atmosfera na borda
        cor, forca = aro
        borda = (esf.rr > 0.93)[..., None]
        rgb = np.where(borda, (rgb * (1 - forca) + np.array(cor) * forca).astype(np.uint8), rgb)
    alpha = np.where(esf.mask, 255, 0).astype(np.uint8)
    Image.fromarray(np.dstack([rgb, alpha]), "RGBA").save(caminho)


def terra(d=600):
    e = Esfera(d)
    mar, terra_, deserto = tons((40, 100, 200)), tons((60, 150, 75)), tons((200, 170, 100))
    gelo, nuvem = tons((235, 240, 250)), tons((246, 248, 252))
    img = mar[e.luz]
    continente = e.ruido(2.2, 11) > 0.52
    img = np.where(continente[..., None], terra_[e.luz], img)
    seco = continente & (e.ruido(5, 7, 4) > 0.58) & (np.abs(e.lat) < 0.9)
    img = np.where(seco[..., None], deserto[e.luz], img)
    polo = np.abs(e.lat) > 1.2 + (e.ruido(6, 5, 3) - 0.5) * 0.25
    img = np.where(polo[..., None], gelo[e.luz], img)
    nuvens = e.ruido(3.0, 23, 5, dx=0.7) > 0.60
    img = np.where(nuvens[..., None], nuvem[e.luz], img)
    return e, img


def lua(d=240):
    e = Esfera(d)
    tom = e.luz.copy()
    tom = np.where(e.ruido(4, 31, 4) < 0.42, tom - 1, tom)      # mares escuros
    tom = e.cratera(np.clip(tom, 0, 3), 38, 5)
    return e, tons((165, 165, 172))[tom]


def marte(d=400):
    e = Esfera(d)
    claro, escuro, gelo = tons((196, 92, 52)), tons((135, 58, 40)), tons((240, 232, 230))
    img = claro[e.luz]
    img = np.where((e.ruido(3, 61, 5) > 0.55)[..., None], escuro[e.luz], img)
    tom = e.cratera(e.luz, 14, 9, 0.03, 0.09)
    img = np.where((tom != e.luz)[..., None], claro[tom], img)
    polo = np.abs(e.lat) > 1.38 + (e.ruido(7, 3, 3) - 0.5) * 0.2
    return e, np.where(polo[..., None], gelo[e.luz], img)


def jupiter(d=1000):
    e = Esfera(d)
    cores = [(232, 205, 160), (205, 160, 110), (160, 105, 65), (115, 70, 45), (210, 130, 70)]
    paleta = np.array([tons(c) for c in cores])                     # (faixas, tons, rgb)
    deforma = (e.ruido(3, 41, 4, dx=0.0) - 0.5) * 0.35
    onda = np.sin((e.lat + deforma) * 9.0) + 0.5 * np.sin((e.lat + deforma) * 23.0 + 1.3)
    faixa = np.digitize(onda, [-0.9, -0.2, 0.5, 1.0])
    img = paleta[faixa, e.luz]
    # grande mancha de tempestade
    turb = (e.ruido(8, 77, 3) - 0.5) * 0.25
    elipse = ((e.lon - 0.45) / 0.38) ** 2 + ((e.lat + 0.33) / 0.15) ** 2 + turb
    tempestade = tons((190, 70, 50))
    img = np.where((elipse < 1.0)[..., None], tempestade[e.luz], img)
    centro = tons((150, 45, 35))
    img = np.where((elipse < 0.35)[..., None], centro[e.luz], img)
    return e, img


def gerar_todos(pasta):
    os.makedirs(pasta, exist_ok=True)
    for nome, fn, aro in (("terra", terra, ((120, 180, 255), 0.45)), ("lua", lua, None),
                          ("marte", marte, ((255, 170, 120), 0.35)), ("jupiter", jupiter, None)):
        esf, rgb = fn()
        salvar(esf, rgb, os.path.join(pasta, f"{nome}.png"), aro)
        print("gerado", nome, esf.d)


if __name__ == "__main__":
    gerar_todos(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "planets"))