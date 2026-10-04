import pygame
from rocket import Rocket
from motor import Motor
from tank import Tank

pygame.init()

motor1 = Motor(100,8)
motor2 = Motor(50,8)

tank = Tank(200, 50)

foguete = Rocket(0,0,300,400,1000,[motor1,motor2],tank)

WIDTH = 1280
HEIGHT = 720



destino_screen_x = foguete.destino_x
destino_screen_y = HEIGHT - foguete.destino_y

screen = pygame.display.set_mode((WIDTH, HEIGHT))

running = True

ultimo_tempo = pygame.time.get_ticks()

foguete.launch()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((0, 0, 0))

    tempo_atual = pygame.time.get_ticks()


    if tempo_atual - ultimo_tempo >= 1000:
        foguete.move(1)
        ultimo_tempo = tempo_atual

    foguete_screen_x = foguete.x
    foguete_screen_y = HEIGHT - foguete.y

    pygame.draw.circle(
        screen,
        (255, 0, 0),
        (destino_screen_x, destino_screen_y),
        10
    )

    if foguete.status == "LAUNCHED":
        pygame.draw.circle(
            screen,
            (255,0,0),
            (foguete_screen_x, foguete_screen_y),
            10
        )

    pygame.display.flip()

pygame.quit()