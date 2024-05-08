import pygame
from textures import Texture, AnimationPanel
from gameElement import AnimatedElement

class Background:
    def __init__(self, window, width, height, tileSize):
        self.window = window
        self.tileSize = tileSize
        
        self.width = width
        self.height = height

        self.map: list[list["BgTile"]] = [[BgTile(self, "grass") for i in range(height)] for j in range(width)]
        self.elements: list["AnimatedElement"] = []

    def reload(self):
        # Graphics
        for x in range(len(self.map)):
            for y in range(len(self.map[x])):
                if self.map[x][y]:
                    self.window.blit(self.map[x][y].animPanel.get_texture(), (self.tileSize*x, self.tileSize*y))

    def reloadOverLayers(self, FPS):
        # Graphics
        for x in range(len(self.map)):
            for y in range(len(self.map[x])):
                if self.map[x][y]:
                    if self.map[x][y].overLayer:
                        self.window.blit(self.map[x][y].overLayer.get_texture(), (self.tileSize*x, self.tileSize*y))

        # Animated Elements Graphics
        for i in range(len(self.elements)):
            elm = self.elements[i]
            elm.reload(FPS)
        
        # Delete Animated Elements
        diff = 0
        for i in range(len(self.elements)):
            # TODO : Fix several projectiles bug
            if (self.elements[i-diff].movingTo == None):
                diff += 1
                
                self.elements[i-diff].burnAround()
                del self.elements[i-diff]

    def pushElement(self, x, y, *elms):
        self.map[x][y] = BgTile(self, *elms)
    
    def getAt(self, x, y) -> "BgTile":
        if (0 <= x < self.width and 0 <= y < self.height):
            return self.map[x][y]
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

    def addAnimatedElement(self, name, startPos, endPos, duration, animation="idle"):
        self.elements.append(AnimatedElement(self, startPos[0], startPos[1], name, self.tileSize, animation))
        self.elements[-1].move_to(endPos, duration)

class BgTile:
    def __init__(self, background, type: str, collide=False, state="idle"):
        self.background: "Background" = background
        self.type = type
        
        self.collide = collide
        self.overLayer = None

        self.animPanel = AnimationPanel(self, type, state)
    
    def setOverLayer(self, name: str = None, overLayerRotation: int = 0):
        self.overLayer = AnimationPanel(self, name)
        self.overLayer.set_rotation(overLayerRotation)
    
    def setCollide(self, collide):
        self.collide = collide == True # Make sure it's bool