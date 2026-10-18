class Tank:
    def __init__(self, capacidade, qtd_atual):
        if capacidade < 0:
            raise ValueError("A capacidade máxima não pode ser negativa")
        elif qtd_atual < 0:
            raise ValueError("A quantidade atual não pode ser negativa")
        elif qtd_atual > capacidade:
            raise ValueError("A quantidade atual não pode ser maior que a capacidade máxima do tanque")

        self.qtd_atual = qtd_atual
        self.capacidade = capacidade

    @property
    def fracao(self):
        return self.qtd_atual / self.capacidade if self.capacidade else 0

    def provide_fuel(self, qtd_desejada):
        if qtd_desejada > self.qtd_atual:
            raise ValueError("O tanque não tem a quantidade solicitada de combustível")

        self.qtd_atual = self.qtd_atual - qtd_desejada
        return qtd_desejada

    def refuel(self, qtd_desejada):
        if qtd_desejada <= 0:
            raise ValueError("A quantidade de abastecimento tem que ser maior que zero")

        espaco_disponivel = self.capacidade - self.qtd_atual
        combustivel = min(qtd_desejada, espaco_disponivel)
        self.qtd_atual = self.qtd_atual + combustivel

        return combustivel