import pytest

from rocket import Rocket
from motor import Motor
from tank import Tank
from simulation import run_simulation

"""
Testes
"""
@pytest.fixture
def rocket():
    motorv1 = Motor(100,50)
    motorv2 = Motor(100,50)

    tanque = Tank(200, 200)

    foguete = Rocket(0,0,400,500,10000,[motorv1, motorv2],tanque)

    return foguete

@pytest.fixture
def rocket_with_enough_fuel():
    motorv1 = Motor(100, 50)
    motorv2 = Motor(100, 50)

    tanque = Tank(1000, 1000)

    foguete = Rocket(
        0, 0,
        400, 500,
        10000,
        [motorv1, motorv2],
        tanque
    )

    return foguete

def test_rocket_not_lauch(rocket):

    with pytest.raises(RuntimeError):
        rocket.move(2)


def test_rocket_lauch(rocket):

    rocket.launch()

    posicao_inical = rocket.x

    rocket.move(2)

    assert rocket.x != posicao_inical

def test_rocket_velocity(rocket):

    rocket.launch()

    rocket.move(2)

    velocidade_final_code = rocket.velocidade

    assert velocidade_final_code == 400

def test_rocket_lands_when_reaches_destination(rocket_with_enough_fuel):
    rocket_with_enough_fuel.launch()

    rocket_with_enough_fuel.move(3)

    assert rocket_with_enough_fuel.status == "LANDED"

    assert rocket_with_enough_fuel.x == rocket_with_enough_fuel.destino_x
    assert rocket_with_enough_fuel.y == rocket_with_enough_fuel.destino_y

def test_simulation_reaches_destination(rocket_with_enough_fuel):
    resultado = run_simulation(rocket_with_enough_fuel)

    assert resultado.status == "LANDED"

    assert resultado.x == resultado.destino_x
    assert resultado.y == resultado.destino_y
