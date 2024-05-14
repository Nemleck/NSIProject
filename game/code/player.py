import json
import pygame, keyboard
from bgElement import Background
from utils import getProjectileEndPointAndAngle
from textures import Texture, AnimationPanel, UIElement
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
        self.capaUsing = False
        self.capaDuration = data["capaDuration"]
        self.capaTimeLeft = 0
        self.mapCapaUsesWithFullBar = data["mapCapaUsesWithFullBar"]

        self.minSpeed = data["minSpeed"]
        self.maxSpeed = data["maxSpeed"]
        self.currentSpeed = self.minSpeed

        self.attackRange = data["attackRange"]
        self.capaDM = data["capaDM"]

        self.maxHealth = data["health"]
        self.health = self.maxHealth
        self.autoRegen = data["autoRegen"]
        self.protectedTime = 0

        self.mousePos = (0, 0)

        self.walkingSurface = Texture(self, self.character, "walk")

        self.capaField = UIElement(background, 0, 0, "capaField", "idle", None, (2*self.attackRange+1)*tileSize, (2*self.attackRange+1)*tileSize)
        self.protectionField = UIElement(background, 0, 0, "capaField", "protection", None, (2*self.attackRange+1)*tileSize, (2*self.attackRange+1)*tileSize)
        self.capaField.stickToElement(self)
        self.protectionField.stickToElement(self)

    def move(self, FPS, is_pressed, gameState):
        # Protection

        if self.protectedTime > 0:
            self.protectedTime -= 1/FPS

        # Capa Bar

        self.capaCurrCooldown += 1/FPS
        if (self.capaCurrCooldown > self.capaMaxCooldown):
            self.capaCurrCooldown = self.capaMaxCooldown

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
                
                # Stats
                self.usedCapaTimes += 1
                self.points += 5

                if (self.capaCurrCooldown < 0):
                    self.capaCurrCooldown = 0
                
                if (self.character == "wizard"):
                    self.background.addAnimatedElement("fireball", (self.xpos, self.ypos), self.mousePos, 5, self, "idle", self.capaDM)
                
                elif (self.character == "knight"):
                    self.animPanel.launch_animation("attack")

                    self.attackAround(gameState)
                    self.swordedTreesAnimation()
                
                elif (self.character == "fletcher"):
                    self.capaUsing = True
                    self.capaTimeLeft = self.capaDuration
                    self.protectedTime = self.capaDuration

        else:
            self.capaClicking = False
            
        if is_pressed["attack"]:
            if not self.attackClicking:
                self.attackClicking = True

                if (self.character == "wizard"):
                    endPos, angle = getProjectileEndPointAndAngle((self.xpos, self.ypos), self.mousePos, self.attackRange, self.tileSize)
                    animatedElement = self.background.addAnimatedElement("magicBlast", (self.xpos, self.ypos), endPos, 10, self, "idle", self.attackDM, 255)
                    animatedElement.animPanel.set_rotation(angle / 90)

                elif (self.character == "fletcher"):
                    endPos, angle = getProjectileEndPointAndAngle((self.xpos, self.ypos), self.mousePos, self.attackRange, self.tileSize)
                    animatedElement = self.background.addAnimatedElement("arrow", (self.xpos, self.ypos), endPos, 10, self, "idle", self.attackDM)
                    animatedElement.animPanel.set_rotation(angle / 90)
        
        else:
            self.attackClicking = False

        if self.capaUsing:
            self.capaTimeLeft -= 1/FPS

            if self.capaTimeLeft <= 0:
                self.capaUsing = False
                self.capaTimeLeft = 0
        
        return result, distance

    def hurt(self, amount, attacker):
        if not self.protectedTime > 0:
            print(self.protectedTime)
            super().hurt(amount, attacker)
    
    def enableShield(self, time):
        self.protectedTime += time

    def reload(self):
        if not self.dead:
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
        attack = pygame.mouse.get_pressed()[0]

        if space or attack:
            self.mousePos = pygame.mouse.get_pos()

        super().move(FPS, {
            "d": keyboard.is_pressed("d"),
            "q": keyboard.is_pressed("q"),
            "z": keyboard.is_pressed("z"),
            "s": keyboard.is_pressed("s"),
            "attack": attack,
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

        self.capaAIClickingTime = 0
        self.attackAIClickingTime = 0
    
    def enableKey(self, key):
        self.pressedKeys[key] = True
    
    def disableKey(self, key):
        self.pressedKeys[key] = False
    
    def setGoalTile(self, goal: tuple[int, int], reversed=False):
        self.path = pathfinding(self.background, (self.xpos // self.tileSize, self.ypos // self.tileSize), goal)

        if reversed:
            for i in range(len(self.path)):
                self.path[i] = ( self.path[i][0] * -1, self.path[i][1] * -1 )

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

        # Clicking

        if self.capaAIClickingTime > 0:
            self.capaAIClickingTime -= 1/FPS
            self.disableKey("capacity")
        if self.attackAIClickingTime > 0:
            self.attackAIClickingTime -= 1/FPS
            self.disableKey("attack")
        
        oldCapaClicking = self.capaClicking
        oldAttackClicking = self.attackClicking

        # Pathfinding

        if len(self.path) > 0:
            if self.path[0][1] == -1:
                self.enableKey("z")
            if self.path[0][1] == 1:
                self.enableKey("s")
            if self.path[0][0] == -1:
                self.enableKey("q")
            if self.path[0][0] == 1:
                self.enableKey("d")

        # Call move from super

        _, result = super().move(FPS, self.pressedKeys, gameState)

        # Pathfinding

        self.distance += result[0] + result[1]
        
        if len(self.path) > 0:
            if self.distance >= self.tileSize:
                self.path.pop(0)
                self.distance = 0
        
        # Clicking time

        if self.capaClicking == True and oldCapaClicking == False:
            self.capaAIClickingTime = 0.5
        if self.attackClicking == True and oldAttackClicking == False:
            self.attackAIClickingTime = 0.5