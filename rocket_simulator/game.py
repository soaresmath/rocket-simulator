import math
import os
import random

import pygame

from rocket_simulator.entities import Combustivel, CorpoCeleste, Meteoro, Missao, Motor, Rocket, Tank

LARG, ALT, ZOOM = 320, 180, 4   # desenha em 320x180 e amplia 4x => pixel art
ESPACO = (4, 6, 14)

SPRITE = [
    "...W...",
    "..WWW..",
    "..WBW..",
    "..WBW..",
    "..WWW..",
    ".WWWWW.",
    ".WWWWW.",
    "RWWWWWR",
    "R.WWW.R",
    "..RRR..",
]
CORES = {"W": (225, 230, 240), "B": (80, 170, 255), "R": (230, 70, 70)}


PASTA_PLANETAS = PASTA_PLANETAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "planets")

ARQUIVOS = {"Terra": "terra", "Lua": "lua", "Marte": "marte", "Júpiter": "jupiter"}


def carregar_texturas():
    """Carrega assets/planets/<astro>.png; gera os que faltarem (precisa de numpy e pillow)."""
    faltando = [a for a in ARQUIVOS.values() if not os.path.exists(os.path.join(PASTA_PLANETAS, f"{a}.png"))]
    if faltando:
        print(f"[aviso] texturas ausentes em {PASTA_PLANETAS}: {faltando}. Tentando gerar...")
        try:
            from tools.gerar_planetas import gerar_todos
            gerar_todos(PASTA_PLANETAS)
        except Exception as erro:  # sem numpy/pillow ou sem a pasta tools
            print(f"[aviso] não foi possível gerar ({erro}); os astros serão círculos.")
    texturas = {}
    for nome, arquivo in ARQUIVOS.items():
        caminho = os.path.join(PASTA_PLANETAS, f"{arquivo}.png")
        if os.path.exists(caminho):
            texturas[nome] = pygame.image.load(caminho).convert_alpha()
    return texturas


def criar_sprite():
    surf = pygame.Surface((7, len(SPRITE)), pygame.SRCALPHA)
    for j, linha in enumerate(SPRITE):
        for i, ch in enumerate(linha):
            if ch in CORES:
                surf.set_at((i, j), CORES[ch])
    return surf


def misturar(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


class Jogo:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARG * ZOOM, ALT * ZOOM))
        pygame.display.set_caption("Rocket Simulator")
        self.canvas = pygame.Surface((LARG, ALT))
        self.fonte = pygame.font.Font(None, 14)
        self.relogio = pygame.time.Clock()
        self.sprite = criar_sprite()
        self.texturas = carregar_texturas()
        rng = random.Random(7)
        self.estrelas = [(rng.randrange(LARG), rng.randrange(ALT), rng.choice([90, 150, 230]),
                          rng.choice([0.15, 0.3])) for _ in range(70)]
        self.resetar()

    # ------------------------------------------------------------------
    def resetar(self):
        self.terra = CorpoCeleste(
            "Terra", 0, 0, 300, 25, (40, 110, 200), atmosfera=360, cor_ceu=(90, 160, 235),
            cor_mancha=(50, 150, 70), seed=1,
            camadas=[(60, "Troposfera"), (140, "Estratosfera"), (240, "Mesosfera"), (360, "Termosfera")])
        lua = CorpoCeleste("Lua", 5000, -900, 120, 8, (170, 170, 180), seed=2)
        marte = CorpoCeleste("Marte", 12000, 1500, 200, 12, (200, 90, 50),
                             atmosfera=120, cor_ceu=(170, 110, 80), seed=3)
        jupiter = CorpoCeleste("Júpiter", 21000, -2000, 500, 22, (205, 160, 110),
                               cor_mancha=(160, 110, 70), seed=4)
        self.corpos = [self.terra, lua, marte, jupiter]
        self.missao = Missao(self.corpos)

        self.foguete = Rocket(0, -(self.terra.raio + Rocket.RAIO),
                              [Motor(20, 4), Motor(20, 4)], Tank(300, 300))
        self.foguete.corpo = self.terra

        self.meteoros, self.itens = [], self.missao.gerar_itens()
        self.acumulado = self.t = self.tempo_msg = 0.0
        self.msg, self.fim = "", None
        self.zoom = self.z = 1.0
        self.cache_texturas = {}
        self.checkpoint = None
        self.salvar_checkpoint(self.terra)

    # ------------------------------------------------------------------
    def avisar(self, texto, segundos=3.0):
        self.msg, self.tempo_msg = texto, segundos

    def salvar_checkpoint(self, corpo):
        """Guarda onde o foguete pousou, a etapa da missão e o combustível."""
        f = self.foguete
        self.checkpoint = {"corpo": corpo, "dx": f.x - corpo.x, "dy": f.y - corpo.y,
                           "etapa": self.missao.etapa, "combustivel": f.tank.qtd_atual}

    def voltar_checkpoint(self):
        if self.missao.concluida:
            return self.resetar()
        cp, f = self.checkpoint, self.foguete
        corpo = cp["corpo"]
        f.x, f.y = corpo.x + cp["dx"], corpo.y + cp["dy"]
        f.vx = f.vy = 0.0
        f.angulo = math.degrees(math.atan2(cp["dx"], -cp["dy"]))  # bico para fora do astro
        f.status, f.corpo = "LANDED", corpo
        f.integridade, f.invulneravel = 3, 0.0
        for motor in f.motors:
            motor.desligar()
        # piso de 100 de combustível para não voltar preso sem poder decolar
        f.tank.qtd_atual = min(f.tank.capacidade, max(cp["combustivel"], 100))
        self.missao.etapa = cp["etapa"]
        self.itens, self.meteoros, self.acumulado, self.fim = self.missao.gerar_itens(), [], 0.0, None
        self.zoom = self.z = 1.0
        self.avisar(f"VOLTOU AO CHECKPOINT: {corpo.nome}")

    def tratar_evento(self, evento):
        tipo, corpo = evento
        if tipo == "BATIDA":
            self.fim = ("FOGUETE DESTRUÍDO", f"Pouso brusco em {corpo.nome}")
        elif corpo is self.missao.alvo:
            self.foguete.tank.refuel(120)
            self.missao.avancar()
            self.itens = self.missao.gerar_itens()
            if self.missao.concluida:
                self.fim = ("MISSÃO CUMPRIDA!", "Todas as entregas foram feitas")
            else:
                self.avisar(f"ENTREGA CONCLUÍDA: {corpo.nome}! Próximo: {self.missao.alvo.nome}")
            self.salvar_checkpoint(corpo)
        else:
            self.salvar_checkpoint(corpo)
            self.avisar(f"CHECKPOINT: {corpo.nome}")

    def spawn_meteoro(self):
        f = self.foguete
        base = math.atan2(f.vy, f.vx) if f.velocidade > 30 else random.uniform(0, 6.28)
        ang = base + random.uniform(-1.2, 1.2)
        dist_spawn = max(210, 190 / self.z)   # nasce fora da tela, mesmo com zoom
        px, py = f.x + math.cos(ang) * dist_spawn, f.y + math.sin(ang) * dist_spawn
        tx = f.x + f.vx * 1.5 + random.uniform(-110, 110)
        ty = f.y + f.vy * 1.5 + random.uniform(-110, 110)
        dist = math.hypot(tx - px, ty - py) or 1
        vel = random.uniform(40, 90)
        self.meteoros.append(Meteoro(px, py, (tx - px) / dist * vel, (ty - py) / dist * vel,
                                     random.randint(3, 7)))

    def atualizar(self, dt):
        if self.fim:
            return
        f = self.foguete
        alt_ref = min(c.altitude(f.x, f.y) for c in self.corpos)
        alvo_zoom = 1.0 if alt_ref <= 70 else max(0.18, 70 / alt_ref)   # recua ao se afastar, mantendo o astro na tela
        self.zoom += (alvo_zoom - self.zoom) * min(1.0, 3 * dt)
        k = pygame.key.get_pressed()
        giro = (k[pygame.K_RIGHT] or k[pygame.K_d]) - (k[pygame.K_LEFT] or k[pygame.K_a])
        ligado = k[pygame.K_SPACE] or k[pygame.K_UP] or k[pygame.K_w]

        self.t += dt
        self.tempo_msg -= dt
        evento = f.update(dt, giro, ligado, self.corpos)
        if evento:
            self.tratar_evento(evento)

        if f.status == "LANDED" and f.corpo is self.terra and f.tank.fracao < 1:
            f.tank.refuel(40 * dt)  # base de reabastecimento
        elif f.status == "LANDED" and f.tank.qtd_atual < 0.5 and not self.fim:
            self.fim = ("SEM COMBUSTÍVEL", f"Preso em {f.corpo.nome}")

        # meteoros: só no espaço (a atmosfera os queima)
        dens = max(c.densidade(f.x, f.y) for c in self.corpos)
        if f.status == "FLYING" and dens < 0.2 and len(self.meteoros) < 18:
            self.acumulado += dt * (0.35 + 0.1 * self.missao.etapa)
            while self.acumulado >= 1:
                self.acumulado -= 1
                self.spawn_meteoro()

        for m in self.meteoros[:]:
            m.update(dt)
            dist = math.hypot(m.x - f.x, m.y - f.y)
            if dist < m.raio + Rocket.RAIO and f.status == "FLYING":
                self.meteoros.remove(m)
                if f.dano():
                    self.avisar("IMPACTO!", 1.0)
            elif dist > max(350, 330 / self.z):
                self.meteoros.remove(m)

        for item in self.itens[:]:
            if math.hypot(item.x - f.x, item.y - f.y) < max(Combustivel.RAIO + Rocket.RAIO + 3, 8 / self.z):
                self.itens.remove(item)
                f.tank.refuel(Combustivel.QTD)
                self.avisar("+ COMBUSTÍVEL", 1.0)

        if f.status == "CRASHED" and not self.fim:
            self.fim = ("FOGUETE DESTRUÍDO", "Casco danificado por meteoros")

    # ------------------------------------------------------------------
    def texto(self, s, x, y, cor=(235, 240, 250), centro=False):
        img = self.fonte.render(s, False, cor)
        sombra = self.fonte.render(s, False, (0, 0, 0))
        if centro:
            x -= img.get_width() // 2
        self.canvas.blit(sombra, (x + 1, y + 1))
        self.canvas.blit(img, (x, y))

    def desenhar_estrelas(self, cam, vis):
        if vis < 0.1:
            return
        for x, y, b, p in self.estrelas:
            v = int(b * vis)
            self.canvas.set_at((int((x - cam[0] * p) % LARG), int((y - cam[1] * p) % ALT)), (v, v, v))

    def para_tela(self, x, y):
        """Converte coordenadas do mundo em pixels, com o foguete no centro e o zoom atual."""
        f = self.foguete
        return int(LARG / 2 + (x - f.x) * self.z), int(ALT / 2 + (y - f.y) * self.z)

    def textura_escalada(self, corpo):
        base = self.texturas.get(corpo.nome)
        if base is None:
            return None
        nivel = max(1, round(self.z * 32))
        if nivel >= 32:
            return base
        chave = (corpo.nome, nivel)
        if chave not in self.cache_texturas:
            lado = max(2, base.get_width() * nivel // 32)
            self.cache_texturas[chave] = pygame.transform.smoothscale(base, (lado, lado))
        return self.cache_texturas[chave]

    def desenhar_corpo(self, corpo, ceu):
        z, c = self.z, self.canvas
        sx, sy = self.para_tela(corpo.x, corpo.y)
        alcance = (corpo.raio + corpo.atmosfera) * z
        if sx + alcance < 0 or sx - alcance > LARG or sy + alcance < 0 or sy - alcance > ALT:
            return
        if corpo.atmosfera:
            pygame.draw.circle(c, misturar(ceu, corpo.cor_ceu, 0.3), (sx, sy), max(1, int(alcance)))
            for limite, _ in corpo.camadas:
                pygame.draw.circle(c, misturar(ceu, corpo.cor_ceu, 0.6), (sx, sy),
                                   max(1, int((corpo.raio + limite) * z)), 1)
        textura = self.textura_escalada(corpo)
        if textura:
            c.blit(textura, (sx - textura.get_width() // 2, sy - textura.get_height() // 2))
            return
        pygame.draw.circle(c, corpo.cor, (sx, sy), max(1, int(corpo.raio * z)))
        for dx, dy, r, cor in corpo.manchas:
            pygame.draw.circle(c, cor, (int(sx + dx * z), int(sy + dy * z)), max(1, int(r * z)))

    def desenhar_rota(self):
        alvo = self.missao.alvo
        if alvo is None:
            return
        o = self.missao.origem
        n = max(1, int(math.hypot(alvo.x - o.x, alvo.y - o.y) / 30))
        for i in range(n + 1):
            px, py = self.para_tela(o.x + (alvo.x - o.x) * i / n, o.y + (alvo.y - o.y) * i / n)
            if 0 <= px < LARG and 0 <= py < ALT:
                pygame.draw.rect(self.canvas, (70, 210, 200), (px, py, 2, 2))

    def desenhar_foguete(self):
        f, c = self.foguete, self.canvas
        sx, sy = LARG // 2, ALT // 2
        if f.status == "CRASHED":
            pygame.draw.circle(c, (255, 140, 40), (sx, sy), 9)
            pygame.draw.circle(c, (255, 230, 90), (sx, sy), 5)
            return
        if f.invulneravel > 0 and int(f.invulneravel * 10) % 2:
            return
        dx, dy = f.direcao()
        if any(m.status == "RUNNING" for m in f.motors):
            tamanho = random.randint(2, 4)
            for i in range(tamanho):
                cor = (255, 230, 90) if i == 0 else (255, 140, 40) if i < tamanho - 1 else (200, 60, 30)
                pygame.draw.rect(c, cor, (int(sx - dx * (6 + i * 2)) - 1, int(sy - dy * (6 + i * 2)) - 1, 2, 2))
        img = pygame.transform.rotate(self.sprite, -f.angulo)
        c.blit(img, img.get_rect(center=(sx, sy)))

    def desenhar_seta(self):
        alvo, f = self.missao.alvo, self.foguete
        if alvo is None:
            return
        ang = math.atan2(alvo.y - f.y, alvo.x - f.x)
        ux, uy = math.cos(ang), math.sin(ang)
        cx, cy = LARG / 2 + ux * 28, ALT / 2 + uy * 28
        pontos = [(cx + ux * 6, cy + uy * 6),
                  (cx - ux * 3 - uy * 4, cy - uy * 3 + ux * 4),
                  (cx - ux * 3 + uy * 4, cy - uy * 3 - ux * 4)]
        pygame.draw.polygon(self.canvas, (255, 215, 60), pontos)

    def desenhar_hud(self):
        f = self.foguete
        ref = min(self.corpos, key=lambda c: c.altitude(f.x, f.y))
        alt = ref.altitude(f.x, f.y)
        self.texto(ref.camada(alt), 4, 3, (255, 215, 60))
        rel = (255, 90, 90) if f.velocidade > Rocket.VEL_POUSO else (120, 255, 140)
        self.texto(f"ALT {alt:.0f}", 4, 14)
        self.texto(f"VEL {f.velocidade:.0f}", 4, 25, rel)
        alvo = self.missao.alvo
        if alvo:
            self.texto(f"ALVO {alvo.nome} {alvo.altitude(f.x, f.y):.0f}", 4, 36, (70, 210, 200))
            self.texto(f"ENTREGA {self.missao.etapa + 1}/{len(self.corpos) - 1}", 4, 47)
        pygame.draw.rect(self.canvas, (40, 40, 60), (4, 60, 62, 6))
        cor = (80, 220, 110) if f.tank.fracao > 0.25 else (240, 80, 70)
        pygame.draw.rect(self.canvas, cor, (5, 61, int(60 * f.tank.fracao), 4))
        for i in range(f.integridade):
            pygame.draw.rect(self.canvas, (230, 70, 70), (4 + i * 9, 70, 7, 5))
        self.texto(f"SAVE {self.checkpoint['corpo'].nome}", 4, 79, (170, 180, 200))

        if self.tempo_msg > 0:
            self.texto(self.msg, LARG // 2, ALT - 22, (255, 255, 255), centro=True)
        if self.t < 10:
            self.texto("A/D: girar   ESPACO: propulsor   R: checkpoint   N: novo jogo",
                       LARG // 2, ALT - 11, (170, 180, 200), centro=True)
        if self.fim:
            veu = pygame.Surface((LARG, ALT), pygame.SRCALPHA)
            veu.fill((0, 0, 0, 150))
            self.canvas.blit(veu, (0, 0))
            self.texto(self.fim[0], LARG // 2, ALT // 2 - 14, (255, 215, 60), centro=True)
            self.texto(self.fim[1], LARG // 2, ALT // 2, centro=True)
            ajuda = "N para novo jogo" if self.missao.concluida else "R: voltar ao checkpoint   N: novo jogo"
            self.texto(ajuda, LARG // 2, ALT // 2 + 16, (170, 180, 200), centro=True)

    def desenhar(self):
        c, f = self.canvas, self.foguete
        self.z = max(1, round(self.zoom * 32)) / 32   # zoom em degraus (cache das texturas)

        dens, ref = 0.0, None
        for corpo in self.corpos:
            d = corpo.densidade(f.x, f.y)
            if d > dens:
                dens, ref = d, corpo
        ceu = misturar(ESPACO, ref.cor_ceu, dens) if ref else ESPACO
        c.fill(ceu)
        self.desenhar_estrelas((f.x * self.z, f.y * self.z), 1 - dens)

        for corpo in self.corpos:
            self.desenhar_corpo(corpo, ceu)
        self.desenhar_rota()

        if f.status == "FLYING":
            for i, (x, y) in enumerate(f.prever_trajetoria(self.corpos)):
                px, py = self.para_tela(x, y)
                if i % 2 == 0 and 0 <= px < LARG and 0 <= py < ALT:
                    c.set_at((px, py), (210, 235, 255))

        for item in self.itens:
            px, py = self.para_tela(item.x, item.y)
            if -10 < px < LARG + 10 and -10 < py < ALT + 10:
                pygame.draw.rect(c, (30, 120, 60), (px - 3, py - 4, 6, 8))
                pygame.draw.rect(c, (90, 255, 130), (px - 2, py - 3, 4, 6))
        for m in self.meteoros:
            px, py = self.para_tela(m.x, m.y)
            r = max(2, round(m.raio * (0.5 + 0.5 * self.z)))
            if -10 < px < LARG + 10 and -10 < py < ALT + 10:
                pygame.draw.circle(c, (120, 100, 90), (px, py), r)
                pygame.draw.circle(c, (80, 66, 60), (px - 1, py - 1), max(1, r // 3))

        self.desenhar_foguete()
        self.desenhar_seta()
        self.desenhar_hud()

        pygame.transform.scale(c, self.tela.get_size(), self.tela)
        pygame.display.flip()

    # ------------------------------------------------------------------
    def rodar(self):
        rodando = True
        while rodando:
            dt = min(self.relogio.tick(60) / 1000, 0.05)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    rodando = False
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        rodando = False
                    elif e.key == pygame.K_r:
                        self.voltar_checkpoint()
                    elif e.key == pygame.K_n:
                        self.resetar()
            self.atualizar(dt)
            self.desenhar()
        pygame.quit()


if __name__ == "__main__":
    Jogo().rodar()