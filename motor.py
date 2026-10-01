class Motor:
    def __init__(self, aceleracao, consumo_combustivel):
        self.aceleracao = aceleracao
        self.consumo_combustivel = consumo_combustivel
        self.status = "NOT_STARTED"

    def request_fuel(self, tank, segundos):
        try:
            combustivel = self.consumo_combustivel
            combustivel_tempo = combustivel * segundos
            
            combustivel_recebido = tank.provide_fuel(combustivel_tempo)

            self.status = "RUNNING"

            return combustivel_recebido
        
        except ValueError:
            self.status = "OUT_OF_FUEL"
            raise