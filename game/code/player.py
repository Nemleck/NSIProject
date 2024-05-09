import pygame, keyboard
from bgElement import Background
from textures import Texture, AnimationPanel
from gameElement import Entity
from AI import *

class PartialPlayer(Entity):
    def __init__(self, background: "Background", character: str, tileSize):
        super().__init__(background, 0, 0, character, tileSize, "idle")
        
        self.capaMaxCooldown = 3.0
        self.capaCurrCooldown = 3.0
        self.capaClicking = False
        self.mapCapaUsesWithFullBar = 3

        self.mousePos = (0, 0)

        self.walkingSurface = Texture(self, self.character, "walk")
        
        self.lastAttacker: Entity | None = None
        self.lastAttackedTime: int | None = None

    def move(self, FPS, is_pressed):
        if (not self.moving):
            self.currentDirection = None
        
        result, distance = super().move(FPS, is_pressed)

        if (result[0] or result[1]):
            self.timeSinceNoMove = 0
        
        if (not self.moving):
            self.timeSinceNoMove += 1/FPS

            if self.timeSinceNoMove > 5:
                self.animPanel.launch_animation("sleep")
        
        if is_pressed["space"]:
            if not self.capaClicking and self.capaCurrCooldown > self.capaMaxCooldown//self.mapCapaUsesWithFullBar:
                self.capaClicking = True
                self.capaCurrCooldown -= self.capaMaxCooldown / self.mapCapaUsesWithFullBar

                if (self.capaCurrCooldown < 0):
                    self.capaCurrCooldown = 0
                
                self.background.addAnimatedElement("fireball", (self.xpos, self.ypos), self.mousePos, 1, "idle")
        else:
            self.capaClicking = False
        
        return result, distance

    def reload(self, FPS):
        # Capa Bar

        self.capaCurrCooldown += 1/FPS
        if (self.capaCurrCooldown > self.capaMaxCooldown):
            self.capaCurrCooldown = self.capaMaxCooldown

        # Graphics

        if (not self.moving):
            self.background.window.blit(self.animPanel.get_texture(self.lastDirection == "q"), (self.xpos, self.ypos))
        else:
            self.background.window.blit(self.walkingSurface.get_texture(self.lastDirection == "q"), (self.xpos, self.ypos))
    
class Player(PartialPlayer):
    def move(self, FPS):
        space = keyboard.is_pressed("space")

        if space:
            self.mousePos = pygame.mouse.get_pos()

        super().move(FPS, {
            "d": keyboard.is_pressed("d"),
            "q": keyboard.is_pressed("q"),
            "z": keyboard.is_pressed("z"),
            "s": keyboard.is_pressed("s"),
            "space": space
        })

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

    def move(self, FPS):
        self.pressedKeys = {
            "z": False,
            "s": False,
            "q": False,
            "d": False,
            "space": False
        }



        if self.distance >= self.tileSize:
            self.path.pop(0)
            self.distance = 0

        if len(self.path) > 0:
            if self.path[0][1] == -1:
                self.enableKey("z")
            if self.path[0][1] == 1:
                self.enableKey("s")
            if self.path[0][0] == -1:
                self.enableKey("q")
            if self.path[0][0] == 1:
                self.enableKey("d")

        _, result = super().move(FPS, self.pressedKeys)

        self.distance += result[0] + result[1]