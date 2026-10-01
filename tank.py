class Tank:
    def __init__(self, capacidade, qtd_atual):
        if capacidade < 0:
            raise ValueError(f"A capacidade maxima não pode ser negativa")
        elif qtd_atual < 0:
            raise ValueError(f"A quantidade atual não pode ser negativa")
        elif qtd_atual > capacidade:
            raise ValueError(f"A quantidade atual não pode ser maior que a capacidade máxima do tanque")

        self.qtd_atual = qtd_atual
        self.capacidade = capacidade

    def provide_fuel(self, qtd_desejada):
        if qtd_desejada > self.qtd_atual:
            raise ValueError(f"O tank não tem a quantidade solicitada de combustivel")
        
        self.qtd_atual = self.qtd_atual - qtd_desejada
        return qtd_desejada