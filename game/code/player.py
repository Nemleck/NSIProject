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

        self.walkingSurface = Texture(self, self.character, "walk")

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
        
        if keyboard.is_pressed("space"):
            if not self.capaClicking and self.capaCurrCooldown > self.capaMaxCooldown//3:
                self.capaClicking = True
                self.capaCurrCooldown -= self.capaMaxCooldown / 3

                if (self.capaCurrCooldown < 0):
                    self.capaCurrCooldown = 0
                
                mousePos = pygame.mouse.get_pos()
                self.background.addAnimatedElement("fireball", (self.xpos, self.ypos), mousePos, 1, "idle")
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
        super().move(FPS, {
            "d": keyboard.is_pressed("d"),
            "q": keyboard.is_pressed("q"),
            "z": keyboard.is_pressed("z"),
            "s": keyboard.is_pressed("s")
        })

class AI(PartialPlayer):
    def __init__(self, background: "Background", character: str, tileSize):
        super().__init__(background, character, tileSize)
        
        self.path = pathfinding(background, (0,0), (background.width//2, background.height//2))
        self.distance = 0

    def move(self, FPS):
        if self.distance >= self.tileSize:
            self.path.pop(0)
            self.distance = 0

        if len(self.path) > 0:
            _, result = super().move(FPS, {
                "z": self.path[0][1] == -1,
                "s": self.path[0][1] == 1,
                "q": self.path[0][0] == -1,
                "d": self.path[0][0] == 1,
            })

            self.distance += result[0] + result[1]