from random import choice
from time import sleep
import pygame, keyboard
pygame.init()
pygame.font.init()

from bgElement import BgTile, Background
from bgGeneration import generateBackground
from player import Player, AI
from AI import pathfinding
from AIBrain import GameState, load_brain, create_new_brain
from textures import init_textures, UIElement
from gameElement import AnimatedElement, Enemy
from utils import *

import datetime

display_info = pygame.display.Info()

TILES_SIZE = 50
BACKGROUND_HEIGHT = int(display_info.current_h // TILES_SIZE) - 2
BACKGROUND_WIDTH = int(display_info.current_w // TILES_SIZE) - 1
GAME_DURATION = 180 # seconds

# HEIGHT 18
# WIDTH 30
init_textures(TILES_SIZE)

window = pygame.display.set_mode([TILES_SIZE * BACKGROUND_WIDTH, TILES_SIZE * BACKGROUND_HEIGHT])
background = Background(window, BACKGROUND_WIDTH, BACKGROUND_HEIGHT, TILES_SIZE)

generateBackground(background, BACKGROUND_WIDTH, BACKGROUND_HEIGHT)

FPS = 60
newFPS = 60

player = Player(background, "wizard", TILES_SIZE)
# AIPer = AI(background, "wizard", TILES_SIZE, load_brain("wizard"))
capaBar = UIElement(background, TILES_SIZE * (BACKGROUND_WIDTH - 1), TILES_SIZE * (BACKGROUND_HEIGHT - 5), "capaBar", "background", "cursor")
EnnemyBlob = Enemy(background, TILES_SIZE, TILES_SIZE, "blob", TILES_SIZE, "idle")

EnnemyBats = [Enemy(background, TILES_SIZE, TILES_SIZE, "bat", TILES_SIZE, "idle") for i in range(5)]

AIS = [
    AI(background, choice(["wizard", "fletcher", "knight"]), TILES_SIZE, create_new_brain(BACKGROUND_WIDTH, BACKGROUND_HEIGHT)) for i in range(10)
]

gameState = GameState(GAME_DURATION, AIS + [player], [EnnemyBlob] + EnnemyBats, [], TILES_SIZE)

for entity in gameState.getAllEntities():
    teleportToRandom(background, entity)

def global_reload():
    window.fill([0,0,0,0])
    background.reload()
    
    if player.character == "fletcher" and player.capaUsing:
        player.protectionField.reload()
    else:
        player.capaField.reload()

    background.reloadOverLayers()

    for entity in gameState.getAllEntities():
        entity.reload()

    capaBar.reload()
    capaBar.cropOverLayer((1 - (player.capaCurrCooldown / player.capaMaxCooldown )) * 5 * TILES_SIZE)
    
    background.window.blit(text_surface, (0, 0))

    pygame.display.flip()

background.summonObject("heart", [0, 0])

font = pygame.font.SysFont('Comic Sans MS', 30)

j = 0

stop = False
pathF = []
while not stop:
    time = datetime.datetime.now().timestamp()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            stop = True

    diff1 = datetime.datetime.now().timestamp() - time

    diffs = [diff1]
    global_diff = 0
    for entity in gameState.getAllEntities():
        entity.move(newFPS, gameState)
        
        currDiffs = datetime.datetime.now().timestamp() - ( time + global_diff )
        global_diff += currDiffs
        diffs.append(currDiffs)

    background.move(newFPS, gameState)
    
    diff2 = datetime.datetime.now().timestamp() - ( time + diff1 )

    gameState.timeLeft -= 1/newFPS
    text_surface = font.render(str(round(gameState.timeLeft)), False, (0, 0, 0))

    if True:
        # print("coucou")
        global_reload()

    diff3 = datetime.datetime.now().timestamp() - ( time + diff2 )

    diff = datetime.datetime.now().timestamp() - time

    # print("----------------------------------")
    # print()
    # print(f"Diff 1 : {diff1}")
    # print(f"Diff 2 : {diff2}")
    # for i in range(len(diffs)):
    #     print(f"    Diff 2-{i} : {diff2}")
    # print(f"Diff 3 : {diff3}")
    # print(f"Total Diff : {diff}")
    # print()
    # print("----------------------------------")

    # Includes execution time in FPS
    newFPS = 1/(1/FPS + diff)
    
    if True:
        sleep(1/FPS)
    
    if j % FPS == 0:
        print(gameState.timeLeft)
    
    j += 1

# TODO
# Traceback (most recent call last):
#   File "F:\Projects\ProjetNSI\game\code\main.py", line 81, in <module>
#     entity.move(newFPS, gameState)
#   File "F:\Projects\ProjetNSI\game\code\gameElement.py", line 241, in move
#     self.path = pathfinding(self.background, selfPos, playerPos)
#   File "F:\Projects\ProjetNSI\game\code\AI.py", line 30, in pathfinding
#     curr_pos, curr_value = end_pos[:], bgMap[end_pos[0]][end_pos[1]]
# IndexError: list index out of range