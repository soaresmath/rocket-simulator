class Motor:
    """Status: OFF (desligado), RUNNING (queimando) ou OUT_OF_FUEL (tanque vazio)."""

    def __init__(self, aceleracao, consumo_combustivel):
        self.aceleracao = aceleracao
        self.consumo_combustivel = consumo_combustivel
        self.status = "OFF"

    def request_fuel(self, tank, segundos):
        try:
            combustivel_recebido = tank.provide_fuel(self.consumo_combustivel * segundos)
            self.status = "RUNNING"
            return combustivel_recebido
        except ValueError:
            self.status = "OUT_OF_FUEL"
            raise

    def desligar(self):
        self.status = "OFF"