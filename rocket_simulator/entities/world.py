import math
import random


class CorpoCeleste:
    """Planeta/lua: atrai o foguete (gravidade) e pode ter atmosfera em camadas."""

    def __init__(self, nome, x, y, raio, g_superficie, cor, atmosfera=0,
                 cor_ceu=(0, 0, 0), cor_mancha=None, camadas=None, seed=1):
        self.nome, self.x, self.y, self.raio = nome, x, y, raio
        self.cor, self.atmosfera, self.cor_ceu = cor, atmosfera, cor_ceu
        self.gm = g_superficie * raio ** 2
        self.camadas = camadas or [(atmosfera, f"Atmosfera de {nome}")]

        rng = random.Random(seed)
        cor_mancha = cor_mancha or tuple(int(v * 0.75) for v in cor)
        self.manchas = []
        for _ in range(14):
            ang, dist = rng.uniform(0, 2 * math.pi), rng.uniform(0, 0.7) * raio
            self.manchas.append((math.cos(ang) * dist, math.sin(ang) * dist,
                                 rng.uniform(0.08, 0.22) * raio, cor_mancha))

    def distancia(self, x, y):
        return math.hypot(x - self.x, y - self.y)

    def altitude(self, x, y):
        return self.distancia(x, y) - self.raio

    def atracao(self, x, y):
        d = max(self.distancia(x, y), self.raio)
        forca = self.gm / d ** 2
        return (self.x - x) / d * forca, (self.y - y) / d * forca

    def densidade(self, x, y):
        if not self.atmosfera:
            return 0.0
        return max(0.0, min(1.0, 1 - self.altitude(x, y) / self.atmosfera))

    def camada(self, altitude):
        for limite, nome in self.camadas:
            if altitude < limite:
                return nome
        return "Espaço"


class Meteoro:
    def __init__(self, x, y, vx, vy, raio):
        self.x, self.y, self.vx, self.vy, self.raio = x, y, vx, vy, raio

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt


class Combustivel:
    RAIO = 6
    QTD = 60

    def __init__(self, x, y):
        self.x, self.y = x, y


class Missao:
    """Rota de entregas: cada etapa leva a carga do corpo atual ao próximo."""

    def __init__(self, rota):
        self.rota = rota
        self.etapa = 0

    @property
    def origem(self):
        return self.rota[self.etapa]

    @property
    def alvo(self):
        return self.rota[self.etapa + 1] if not self.concluida else None

    @property
    def concluida(self):
        return self.etapa >= len(self.rota) - 1

    def avancar(self):
        self.etapa += 1

    def gerar_itens(self, qtd=6):
        if self.alvo is None:
            return []
        o, a = self.origem, self.alvo
        itens = []
        for i in range(1, qtd + 1):
            t = i / (qtd + 1)
            ang, dist = random.uniform(0, 2 * math.pi), random.uniform(40, 220)
            itens.append(Combustivel(o.x + (a.x - o.x) * t + math.cos(ang) * dist,
                                     o.y + (a.y - o.y) * t + math.sin(ang) * dist))
        return itens
