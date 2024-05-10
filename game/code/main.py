from time import sleep
import pygame, keyboard
pygame.init()

from bgElement import BgTile, Background
from bgGeneration import generateBackground
from player import Player, AI
from AI import pathfinding
from AIBrain import GameState, load_brain
from textures import init_textures, UIElement
from gameElement import AnimatedElement, Enemy
from utils import *

import datetime

display_info = pygame.display.Info()

TILES_SIZE = 50
BACKGROUND_HEIGHT = int(display_info.current_h // TILES_SIZE) - 2
BACKGROUND_WIDTH = int(display_info.current_w // TILES_SIZE) - 1

print(BACKGROUND_WIDTH, BACKGROUND_HEIGHT)

# HEIGHT 18
# WIDTH 30
init_textures(TILES_SIZE)

window = pygame.display.set_mode([TILES_SIZE * BACKGROUND_WIDTH, TILES_SIZE * BACKGROUND_HEIGHT])
background = Background(window, BACKGROUND_WIDTH, BACKGROUND_HEIGHT, TILES_SIZE)

generateBackground(background, BACKGROUND_WIDTH, BACKGROUND_HEIGHT)

FPS = 60
newFPS = 60

player = Player(background, "fletcher", TILES_SIZE)
AIPer = AI(background, "fletcher", TILES_SIZE, load_brain("wizard"))
capaBar = UIElement(background, TILES_SIZE * (BACKGROUND_WIDTH - 1), TILES_SIZE * (BACKGROUND_HEIGHT - 5), "capaBar", "background", "cursor")
EnnemyBlob = Enemy(background, TILES_SIZE, TILES_SIZE, "blob", TILES_SIZE, "idle")
capaField = UIElement(background, 0, 0, "capaField", "idle", None, False, (player.attackRange+1)*TILES_SIZE, (player.attackRange+1)*TILES_SIZE)
capaField.stickToElement(player)

gameState = GameState(300, [AIPer, player], [EnnemyBlob], [], TILES_SIZE)

for entity in gameState.getAllEntities():
    teleportToRandom(background, entity)

def global_reload():
    window.fill([0,0,0,0])
    background.reload()
    capaField.reload()
    background.reloadOverLayers(newFPS)
    
    for entity in gameState.getAllEntities():
        entity.reload(newFPS)

    capaBar.reload()
    capaBar.cropOverLayer((1 - (player.capaCurrCooldown / player.capaMaxCooldown )) * 5 * TILES_SIZE)
    
    pygame.display.flip()

stop = False
pathF = []
while not stop:
    time = datetime.datetime.now().timestamp()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            stop = True

    for entity in gameState.getAllEntities():
        entity.move(newFPS, gameState)
    
    global_reload()

    diff = datetime.datetime.now().timestamp() - time

    # Includes execution time in FPS
    newFPS = 1/(1/FPS + diff)

    sleep(1/FPS)