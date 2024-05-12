import pygame
from utils import teleportToRandom
from textures import Texture, AnimationPanel
from gameElement import AnimatedElement, GameObject

class Background:
    def __init__(self, window, width, height, tileSize):
        self.window = window
        self.tileSize = tileSize
        
        self.width = width
        self.height = height

        self.map: list[list["BgTile"]] = [[BgTile(self, "grass") for i in range(height)] for j in range(width)]
        self.elements: list["AnimatedElement"] = []
        self.objects: list["GameObject"] = []

        self.timeUntilNewObject = 0
    
    def move(self, FPS, gameState):
        self.timeUntilNewObject -= 1/FPS

        if self.timeUntilNewObject <= 0:
            heart = self.summonObject("heart", [0, 0])
            teleportToRandom(self, heart)

            self.timeUntilNewObject = gameState.timeLeft // 10

        for i in range(len(self.elements)):
            self.elements[i].move(FPS, gameState)

        for i in range(len(self.objects)):
            self.objects[i].move(FPS, gameState)

    def reload(self):
        # Graphics
        for x in range(len(self.map)):
            for y in range(len(self.map[x])):
                if self.map[x][y]:
                    self.window.blit(self.map[x][y].animPanel.get_texture(), (self.tileSize*x, self.tileSize*y))

    def reloadOverLayers(self):
        # Graphics
        for x in range(len(self.map)):
            for y in range(len(self.map[x])):
                if self.map[x][y]:
                    if self.map[x][y].overLayer:
                        self.window.blit(self.map[x][y].overLayer.get_texture(), (self.tileSize*x, self.tileSize*y))

        # Animated Elements Graphics
        for i in range(len(self.elements)):
            elm = self.elements[i]
            elm.reload()

        # Objects Graphics
        for i in range(len(self.objects)):
            obj = self.objects[i]
            obj.reload()
        
        # Delete Animated Elements
        diff = 0
        for i in range(len(self.elements)):
            # TODO : Fix several projectiles bug
            if (self.elements[i-diff].movingTo == None):
                if self.elements[i-diff].name == "fireball":
                    self.elements[i-diff].burnAround()
                
                self.elements.pop(i-diff)
                
                diff += 1
        
        diff = 0
        for i in range(len(self.objects)):
            if (self.objects[i-diff].isOnGround == False):
                self.objects.pop(i-diff)
                diff += 1

    def pushElement(self, x, y, *elms):
        self.map[x][y] = BgTile(self, *elms)
    
    def getAt(self, x, y) -> "BgTile":
        if (0 <= x < self.width and 0 <= y < self.height):
            return self.map[int(x)][int(y)]
        else:
            return None
    
    def getIntList(self):
        result = []
        
        for x in range(len(self.map)):
            result.append([])
            for y in range(len(self.map[x])):
                if self.map[x][y].collide:
                    result[-1].append(-1)
                else:
                    result[-1].append(0)
        
        return result

    def addAnimatedElement(self, name, startPos, endPos, duration, invoker, animation="idle", DM=0, opacityGrowth=0):
        elm = AnimatedElement(self, startPos[0], startPos[1], name, self.tileSize, invoker, animation, DM, opacityGrowth)
        self.elements.append(elm)
        self.elements[-1].move_to(endPos, duration, self.tileSize)

        return elm

    def summonObject(self, name, pos, animState="idle"):
        gameObject = GameObject(self, pos[0], pos[1], name, self.tileSize, animState)
        self.objects.append(gameObject)

        return gameObject

class BgTile:
    def __init__(self, background, type: str, collide=False, state="idle"):
        self.background: "Background" = background
        self.type = type
        
        self.collide = collide
        self.overLayer = None

        self.animPanel = AnimationPanel(self, type, state)
    
    def setOverLayer(self, name: str = None, overLayerRotation: int = 0, state="idle"):
        self.overLayer = AnimationPanel(self, name, state)
        self.overLayer.set_rotation(overLayerRotation)
    
    def setCollide(self, collide):
        self.collide = collide == True # Make sure it's bool