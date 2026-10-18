import math


class Rocket:
    RAIO = 5
    GIRO = 140            # graus por segundo
    ARRASTO = 0.5         # multiplicado pela densidade do ar
    VEL_POUSO = 30        # acima disso o pouso vira batida
    VEL_TOQUE = 8         # abaixo disso o contato nunca destrói
    ALINHAMENTO_MIN = 0.8 # ~37 graus de inclinação máxima no pouso

    def __init__(self, x, y, motors, tank):
        if not motors:
            raise ValueError("Crie ao menos um motor para criar um foguete")
        for nome, valor in (("x", x), ("y", y)):
            if not isinstance(valor, (int, float)):
                raise TypeError(f"O campo {nome} deve ser inteiro ou float")

        self.x, self.y = x, y
        self.vx = self.vy = 0.0
        self.angulo = 0.0           # 0 = apontando para cima, positivo = horário
        self.status = "LANDED"      # LANDED, FLYING ou CRASHED
        self.corpo = None           # corpo onde está pousado
        self.integridade = 3
        self.invulneravel = 0.0
        self.motors = motors
        self.tank = tank

    @property
    def velocidade(self):
        return math.hypot(self.vx, self.vy)

    def direcao(self):
        a = math.radians(self.angulo)
        return math.sin(a), -math.cos(a)

    def calculate_total_acceleration(self):
        return sum(m.aceleracao for m in self.motors if m.status == "RUNNING")

    def consume_fuel(self, ligado, segundos):
        for motor in self.motors:
            if not ligado:
                motor.desligar()
                continue
            try:
                motor.request_fuel(self.tank, segundos)
            except ValueError:
                pass
        return self.calculate_total_acceleration()

    def dano(self):
        if self.invulneravel > 0 or self.status == "CRASHED":
            return False
        self.integridade -= 1
        self.invulneravel = 1.2
        if self.integridade <= 0:
            self.status = "CRASHED"
        return True

    def update(self, dt, giro, ligado, corpos):
        """Avança a física. Retorna ("POUSO", corpo), ("BATIDA", corpo) ou None."""
        if self.status == "CRASHED":
            return None

        self.invulneravel = max(0.0, self.invulneravel - dt)
        self.angulo += giro * self.GIRO * dt
        aceleracao = self.consume_fuel(ligado, dt)

        if self.status == "LANDED":
            if aceleracao <= 0:
                return None
            self.status, self.corpo = "FLYING", None

        dx, dy = self.direcao()
        ax, ay = dx * aceleracao, dy * aceleracao
        for c in corpos:
            gx, gy = c.atracao(self.x, self.y)
            ax, ay = ax + gx, ay + gy

        k = self.ARRASTO * max(c.densidade(self.x, self.y) for c in corpos)
        ax, ay = ax - self.vx * k, ay - self.vy * k

        self.vx += ax * dt
        self.vy += ay * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

        return self._checar_colisao(corpos)

    def _checar_colisao(self, corpos):
        for c in corpos:
            dist = c.distancia(self.x, self.y)
            limite = c.raio + self.RAIO
            if dist > limite:
                continue

            nx, ny = (self.x - c.x) / dist, (self.y - c.y) / dist
            if self.vx * nx + self.vy * ny >= 0 and dist > limite - 1:
                continue  # está se afastando (decolagem)

            dx, dy = self.direcao()
            alinhado = dx * nx + dy * ny >= self.ALINHAMENTO_MIN
            toque_leve = self.velocidade <= self.VEL_TOQUE  # raspão lento não destrói
            if (self.velocidade <= self.VEL_POUSO and alinhado) or toque_leve:
                self.x, self.y = c.x + nx * limite, c.y + ny * limite
                self.vx = self.vy = 0.0
                self.status, self.corpo = "LANDED", c
                return ("POUSO", c)

            self.status = "CRASHED"
            return ("BATIDA", c)
        return None

    def prever_trajetoria(self, corpos, passos=90, dt=0.4):
        """Pontos futuros se os motores forem desligados agora (só gravidade)."""
        x, y, vx, vy = self.x, self.y, self.vx, self.vy
        pontos = []
        for _ in range(passos):
            ax = ay = 0.0
            for c in corpos:
                gx, gy = c.atracao(x, y)
                ax, ay = ax + gx, ay + gy
            vx, vy = vx + ax * dt, vy + ay * dt
            x, y = x + vx * dt, y + vy * dt
            if any(c.distancia(x, y) <= c.raio for c in corpos):
                break
            pontos.append((x, y))
        return pontos