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
GRAPHIC_MODE = True

# HEIGHT 18
# WIDTH 30
init_textures(TILES_SIZE)

window = pygame.display.set_mode([TILES_SIZE * BACKGROUND_WIDTH, TILES_SIZE * BACKGROUND_HEIGHT])
background = Background(window, BACKGROUND_WIDTH, BACKGROUND_HEIGHT, TILES_SIZE)

generateBackground(background, BACKGROUND_WIDTH, BACKGROUND_HEIGHT)

FPS = 60
newFPS = 60

player = Player(background, "fletcher", TILES_SIZE)
capaBar = UIElement(background, TILES_SIZE * (BACKGROUND_WIDTH - 1), TILES_SIZE * (BACKGROUND_HEIGHT - 5), "capaBar", "background", "cursor", TILES_SIZE, 5*TILES_SIZE)

AIS = [
    AI(background, choice(["wizard", "fletcher", "knight"]), TILES_SIZE, load_brain("wizard")) for i in range(5)
]

endScreen = UIElement(background, 0, 0, "endScreen", "idle", None, TILES_SIZE*BACKGROUND_WIDTH, TILES_SIZE*BACKGROUND_HEIGHT)

gameState = GameState(GAME_DURATION, AIS + [player], background.ennemies, background.objects, TILES_SIZE)

for player in gameState.getAllEntities():
    teleportToRandom(background, player)

def global_reload():
    window.fill([0,0,0,0])
    background.reload()
    
    if player.protectedTime > 0:
        player.protectionField.reload()
    else:
        player.capaField.reload()

    background.reloadOverLayers()

    for entity in gameState.getAllEntities():
        entity.reload()

    capaBar.reload()
    capaBar.cropOverLayer((1 - (player.capaCurrCooldown / player.capaMaxCooldown )) * 5 * TILES_SIZE)

    if gameState.timeLeft < 0:
        endScreen.reload()

        background.window.blit(end_of_game_surface, end_of_game_pos)
        
        for i in range(len(texts)):
            background.window.blit(stats_surfaces[i], stats_pos[i])
    else:
        text_surface = font.render(str(round(gameState.timeLeft)), False, (0, 0, 0))
        background.window.blit(text_surface, (0, 0))


    pygame.display.flip()

font = pygame.font.SysFont('Comic Sans MS', 30)

rendered_final_texts = False

stop = False
pathF = []
while not stop:
    time = datetime.datetime.now().timestamp()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            stop = True

    diff1 = datetime.datetime.now().timestamp() - time

    # While the game is still on, let all entities move
    if gameState.timeLeft > 0:
        diffs = [diff1]
        global_diff = 0
        for player in gameState.getPlayers():
            if not player.dead:
                player.move(newFPS, gameState)
                
                currDiffs = datetime.datetime.now().timestamp() - ( time + global_diff )
                global_diff += currDiffs
                diffs.append(currDiffs)

        background.move(newFPS, gameState)

    if player.dead:
        gameState.timeLeft = 0
    
    diff2 = datetime.datetime.now().timestamp() - ( time + diff1 )

    gameState.timeLeft -= 1/newFPS

    if gameState.timeLeft <= 0 and not rendered_final_texts:
        end_of_game_surface = font.render("Partie terminée !", False, (0, 0, 0))
        end_of_game_pos = (background.width*TILES_SIZE//2 - end_of_game_surface.get_width()//2, background.height*TILES_SIZE * 0.25)

        texts = [f"Ennemis tués : {player.killedEnemies},", f"Adversaires tués: {player.killedPlayers},", f"Capacité utilisée : {player.usedCapaTimes} fois,", f"Objets ramassés : {player.pickedObjects}", f"Points totaux: {player.points},"]
        stats_surfaces = [font.render(text, False, (0, 0, 0)) for text in texts]
        stats_pos = [(BACKGROUND_WIDTH*TILES_SIZE//2 - stats_surfaces[i].get_width()//2, BACKGROUND_HEIGHT*TILES_SIZE//2 + (i - len(texts)//2) * stats_surfaces[i].get_height()) for i in range(len(texts))]

    if GRAPHIC_MODE:
        global_reload()

    diff = datetime.datetime.now().timestamp() - time

    # print("----------------------------------")
    # print()
    # print(f"Diff 1 : {diff1}")
    # print(f"Diff 2 : {diff2}")
    # for i in range(len(diffs)):
    #     print(f"    Diff 2-{i} : {diff2}")
    # print(f"Total Diff : {diff}")
    # print()
    # print("----------------------------------")

    # Includes execution time in FPS
    newFPS = 1/(1/FPS + diff)
    
    if GRAPHIC_MODE:
        sleep(1/FPS)

# TODO
# Traceback (most recent call last):
#   File "F:\Projects\ProjetNSI\game\code\main.py", line 81, in <module>
#     entity.move(newFPS, gameState)
#   File "F:\Projects\ProjetNSI\game\code\gameElement.py", line 241, in move
#     self.path = pathfinding(self.background, selfPos, playerPos)
#   File "F:\Projects\ProjetNSI\game\code\AI.py", line 30, in pathfinding
#     curr_pos, curr_value = end_pos[:], bgMap[end_pos[0]][end_pos[1]]
# IndexError: list index out of range