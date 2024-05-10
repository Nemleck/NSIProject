import json
import pygame, keyboard
from bgElement import Background
from utils import getProjectileEndPoint
from textures import Texture, AnimationPanel
from gameElement import Entity
from AI import *

class PartialPlayer(Entity):
    def __init__(self, background: "Background", character: str, tileSize):
        super().__init__(background, 0, 0, character, tileSize, "idle")

        with open(f"./data/characters/{character}.json") as f:
            data = json.load(f)
        
        self.attackDM = data["attackDM"]
        self.attackClicking = False
        
        self.capaMaxCooldown = data["capaCooldown"]
        self.capaCurrCooldown = self.capaMaxCooldown
        self.capaClicking = False
        self.mapCapaUsesWithFullBar = data["mapCapaUsesWithFullBar"]

        self.minSpeed = data["minSpeed"]
        self.maxSpeed = data["maxSpeed"]
        self.currentSpeed = self.minSpeed

        self.attackRange = data["attackRange"]
        self.capaDM = data["capaDM"]

        self.maxHealth = data["health"]
        self.health = self.maxHealth
        self.autoRegen = data["autoRegen"]

        self.mousePos = (0, 0)

        self.walkingSurface = Texture(self, self.character, "walk")

    def move(self, FPS, is_pressed, gameState):
        if (not self.moving):
            self.currentDirection = None
        
        result, distance = super().move(FPS, is_pressed, gameState)

        if (result[0] or result[1]):
            self.timeSinceNoMove = 0
        
        if (not self.moving):
            self.timeSinceNoMove += 1/FPS

            if self.timeSinceNoMove > 5:
                self.animPanel.launch_animation("sleep")
        
        if is_pressed["capacity"]:
            if not self.capaClicking and self.capaCurrCooldown >= self.capaMaxCooldown//self.mapCapaUsesWithFullBar:
                self.capaClicking = True
                self.capaCurrCooldown -= self.capaMaxCooldown / self.mapCapaUsesWithFullBar

                if (self.capaCurrCooldown < 0):
                    self.capaCurrCooldown = 0
                
                if (self.character == "wizard"):
                    self.background.addAnimatedElement("fireball", (self.xpos, self.ypos), self.mousePos, 1, "idle")
                
                elif (self.character == "knight"):
                    self.animPanel.launch_animation("attack")

                    self.attackAround(gameState)
                    self.swordedTreesAnimation()

                elif (self.character == "fletcher"):
                    endPos = getProjectileEndPoint()
                    self.background.addAnimatedElement("arrow", (self.xpos, self.ypos), self.mousePos, 1, "idle")
        else:
            self.capaClicking = False
        
        return result, distance

    def reload(self, FPS):
        if not self.dead:
            # Capa Bar

            self.capaCurrCooldown += 1/FPS
            if (self.capaCurrCooldown > self.capaMaxCooldown):
                self.capaCurrCooldown = self.capaMaxCooldown

            # Health Bar
            self.background.window.blit(self.healthBar.get_texture(), (self.xpos - self.tileSize//2, self.ypos - self.tileSize))

            # Graphics

            if (not self.moving):
                self.background.window.blit(self.animPanel.get_texture(self.lastDirection == "q"), (self.xpos - self.tileSize//2, self.ypos - self.tileSize//2))
            else:
                self.background.window.blit(self.walkingSurface.get_texture(self.lastDirection == "q"), (self.xpos - self.tileSize//2, self.ypos - self.tileSize//2))
    
    def swordedTreesAnimation(self):
        matPos = (self.xpos // self.tileSize, self.ypos // self.tileSize)
        for x in range(-1, 1+1, 1):
            for y in range(-1, 1+1, 1):
                tile = self.background.getAt(matPos[0]+x, matPos[1]+y)

                if tile and tile.overLayer:
                    tile.overLayer.launch_animation("sworded")

class Player(PartialPlayer):
    def move(self, FPS, gameState):
        space = keyboard.is_pressed("space")

        if space:
            self.mousePos = pygame.mouse.get_pos()

        super().move(FPS, {
            "d": keyboard.is_pressed("d"),
            "q": keyboard.is_pressed("q"),
            "z": keyboard.is_pressed("z"),
            "s": keyboard.is_pressed("s"),
            "attack": pygame.mouse.get_pressed() == 3,
            "capacity": space
        }, gameState)

class AI(PartialPlayer):
    def __init__(self, background: "Background", character: str, tileSize, brain):
        super().__init__(background, character, tileSize)
        
        self.path = pathfinding(background, (0,0), (background.width//2, background.height//2))
        self.distance = 0
        self.pressedKeys = {}
        self.brain = brain
        self.behavior = "noBehavior"
    
    def enableKey(self, key):
        self.pressedKeys[key] = True
    
    def setGoalTile(self, goal: tuple[int, int]):
        self.path = pathfinding(self.background, (self.xpos // self.tileSize, self.ypos // self.tileSize), goal)

    def move(self, FPS, gameState):
        self.pressedKeys = {
            "z": False,
            "s": False,
            "q": False,
            "d": False,
            "attack": False,
            "capacity": False
        }

        self.brain.checkNeurons(gameState, self)

        if len(self.path) > 1:
            if self.path[0][1] == -1:
                self.enableKey("z")
            if self.path[0][1] == 1:
                self.enableKey("s")
            if self.path[0][0] == -1:
                self.enableKey("q")
            if self.path[0][0] == 1:
                self.enableKey("d")

        _, result = super().move(FPS, self.pressedKeys, gameState)

        self.distance += result[0] + result[1]
        
        if len(self.path) > 1:
            if self.distance >= self.tileSize:
                self.path.pop(0)
                self.distance = 0