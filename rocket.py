import math

class Rocket:
    def __init__(self, x: int | float, y: int | float, destino_x: int | float, destino_y: int | float, peso: int, motors: list, tank):
        if not len(motors):
            raise ValueError(f"Crie ao menos um motor primeiramente para criar um foguete")
        elif not isinstance(x, (int, float)):
            raise TypeError(f"O campo x deve ser inteiro ou float")
        elif not isinstance(y, (int, float)):
            raise TypeError(f"O campo y deve ser inteiro ou float")
        elif not isinstance(destino_x, (int, float)):
            raise TypeError(f"O campo x deve ser inteiro ou float")
        elif not isinstance(destino_y, (int, float)):
            raise TypeError(f"O campo y deve ser inteiro ou float")            
        else:
            self.x = x
            self.y = y
            self.destino_x = destino_x
            self.destino_y = destino_y
            self.status = "NOT-LAUNCHED"
            self.velocidade = 0
            self.peso = peso
            self.motors = motors
            self.tank = tank

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
            if motor.status == "RUNNING":
                total_acceleration = total_acceleration + motor.aceleracao

        return total_acceleration

    def update_velocity(self, segundos):
        if self.status == "LAUNCHED":

            self.consume_fuel(segundos)

            total_acceleration = self.calculate_total_acceleration()

            self.velocidade = self.velocidade + (total_acceleration * segundos)

            return self.velocidade
        else:
            raise RuntimeError(f"O foguete não pode atualizar a velocidade, pois está {self.status}")

    def consume_fuel(self, segundos):
        list_fuel_delivery = {}

        for motor in self.motors:
            try:
                fuel_delivery = motor.request_fuel(self.tank, segundos)

                list_fuel_delivery[motor] = {"success":True, "fuel": fuel_delivery, "error": None}
            except ValueError as erro:
                list_fuel_delivery[motor] = {"success":False, "fuel": 0, "error": erro}

        return list_fuel_delivery

    def calculate_distance_to_destination(self):
        variacao_x = self.destino_x - self.x
        variacao_y = self.destino_y - self.y

        distancia = (variacao_x**2 + variacao_y**2) ** 0.5

        return distancia

    def calculate_direction_to_destination(self):
        variacao_x = self.destino_x - self.x
        variacao_y = self.destino_y - self.y

        angulo_direcao = math.atan2(variacao_y, variacao_x)

        return angulo_direcao

    def calculate_velocity_components(self):
        angulo = self.calculate_direction_to_destination()

        velocidade_x = self.velocidade * math.cos(angulo)
        velocidade_y = self.velocidade * math.sin(angulo)

        return velocidade_x, velocidade_y

    def update_position(self, segundos):
        if self.status != "LAUNCHED":
            raise RuntimeError(f"O foguete não pode atualizar sua posição, pois está {self.status}")
        
        velocidade_componentes = self.calculate_velocity_components()

        velocidade_componente_x = velocidade_componentes[0]
        velocidade_componentes_y = velocidade_componentes[1]

        nova_posicao_x = self.x + (velocidade_componente_x * segundos)
        nova_posicao_y = self.y + (velocidade_componentes_y * segundos)

        distancia_destino = self.calculate_distance_to_destination()
        distancia_percorrida = self.velocidade * segundos
        
        if distancia_percorrida >= distancia_destino:
            self.x = self.destino_x
            self.y = self.destino_y

            self.status = "LANDED"
        else:
            self.x = nova_posicao_x
            self.y = nova_posicao_y
        
        
        