import pytest

from rocket_simulator.entities import CorpoCeleste, Motor, Rocket, Tank

@pytest.fixture
def terra():
    return CorpoCeleste("Terra", 0, 0, 300, 40, (0, 0, 255), atmosfera=360)


def novo_foguete(combustivel=300):
    return Rocket(0, -(300 + Rocket.RAIO), [Motor(40, 2.5), Motor(40, 2.5)], Tank(300, combustivel))


def test_foguete_exige_motor():
    with pytest.raises(ValueError):
        Rocket(0, 0, [], Tank(10, 10))


def test_propulsor_decola(terra):
    f = novo_foguete()
    y0 = f.y
    for _ in range(60):
        f.update(1 / 60, 0, True, [terra])
    assert f.status == "FLYING" and f.y < y0


def test_sem_combustivel_nao_decola(terra):
    f = novo_foguete(combustivel=0)
    f.update(0.1, 0, True, [terra])
    assert f.status == "LANDED"


def test_motor_consome_combustivel(terra):
    f = novo_foguete()
    f.update(1.0, 0, True, [terra])
    assert f.tank.qtd_atual == pytest.approx(295)


def test_gravidade_puxa_para_o_planeta(terra):
    f = novo_foguete()
    f.status, f.x, f.y = "FLYING", 0, -1000
    f.update(0.5, 0, False, [terra])
    assert f.vy > 0


def test_pouso_suave(terra):
    f = novo_foguete()
    f.status, f.x, f.y, f.vy = "FLYING", 0, -312, 10
    assert f.update(0.5, 0, False, [terra]) == ("POUSO", terra)
    assert f.status == "LANDED"


def test_pouso_brusco_destroi(terra):
    f = novo_foguete()
    f.status, f.x, f.y, f.vy = "FLYING", 0, -312, 200
    assert f.update(0.1, 0, False, [terra]) == ("BATIDA", terra)
    assert f.status == "CRASHED"


def test_tres_danos_destroem(terra):
    f = novo_foguete()
    for _ in range(3):
        f.invulneravel = 0
        f.dano()
    assert f.status == "CRASHED"