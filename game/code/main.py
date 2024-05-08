from time import sleep
import pygame, keyboard
pygame.init()

from bgElement import BgTile, Background
from bgGeneration import generateBackground
from player import Player, AI
from AI import pathfinding
from textures import init_textures, UIElement
from gameElement import AnimatedElement, Ennemy

import datetime

TILES_SIZE = 40
BACKGROUND_HEIGHT = 18
BACKGROUND_WIDTH = 30

init_textures(TILES_SIZE)
window = pygame.display.set_mode([TILES_SIZE * BACKGROUND_WIDTH, TILES_SIZE * BACKGROUND_HEIGHT])
background = Background(window, BACKGROUND_WIDTH, BACKGROUND_HEIGHT, TILES_SIZE)

generateBackground(background, BACKGROUND_WIDTH, BACKGROUND_HEIGHT)

FPS = 60

player = Player(background, "wizard", TILES_SIZE)
AIPer = AI(background, "wizard", TILES_SIZE)
capaBar = UIElement(background, TILES_SIZE * (BACKGROUND_WIDTH - 1), TILES_SIZE * (BACKGROUND_HEIGHT - 5), "capaBar", "background", "cursor")
EnnemyBlob = Ennemy(background, 0, 0, "blob", TILES_SIZE, "idle")
capaField = UIElement(background, 0, 0, "capaField", "idle", None, False, 4*TILES_SIZE, 4*TILES_SIZE)
capaField.stickToElement(player)

stop = False
pathF = []
while not stop:
    time = datetime.datetime.now().timestamp()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            stop = True
    
    window.fill([0,0,0,0])
    background.reload()
    capaField.reload()
    background.reloadOverLayers(FPS)

    if (keyboard.is_pressed("m")):
        pathF = pathfinding(background, (0,0), (round((player.xpos/TILES_SIZE) + 0.5), round((player.ypos/TILES_SIZE) + 0.5)))
    
    if len(pathF) > 0:
        move = pathF.pop(0)
        player.xpos += move[0] * TILES_SIZE
        player.ypos += move[1] * TILES_SIZE

    player.move(FPS)
    AIPer.move(FPS)
    EnnemyBlob.move(FPS, [player, AIPer])
    
    player.reload(FPS)
    AIPer.reload(FPS)
    EnnemyBlob.reload()

    capaBar.reload()
    capaBar.cropOverLayer((( player.capaCurrCooldown / player.capaMaxCooldown )) * 5 * TILES_SIZE)
    
    pygame.display.flip()

    diff = datetime.datetime.now().timestamp() - time

    sleep(1/FPS)