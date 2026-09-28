class Rocket:
    def __init__(self, localizao, peso, motors):
        if not len(motors):
            raise ValueError(f"Crie ao menos um motor primeiramente para criar um foguete")
        else:
            self.status = "NOT-LAUNCHED"
            self.velocidade = 0
            self.localizao = localizao
            self.peso = peso
            self.motors = motors

    def launch(self):
        if self.status == "NOT-LAUNCHED":
            self.status = "LAUNCHED"
            return f"O foguete foi lançado"
        
        elif self.status == "LANDED":
            return f"O foguete já foi pousado"

        else:
            return f"O foguete já foi lançado"

    def land(self):
        if self.status == "LAUNCHED":
            self.status = "LANDED"
            return f"O foguete pousou"
        else:
            return f"Foguete não pode pousar, pois seu status é: {self.status}"

    def calculate_total_acceleration(self):
        total_acceleration = 0

        for motor in self.motors:
            total_acceleration = total_acceleration + motor.aceleracao

        return total_acceleration

    def update_velocity(self, segundos):
        if self.status == "LAUNCHED":
            total_acceleration = self.calculate_total_acceleration()

            self.velocidade = self.velocidade + (total_acceleration * segundos)

            return self.velocidade
        else:
            raise RuntimeError(f"O foguete não pode atualizar a velocidade, pois está {self.status}")
