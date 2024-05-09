import pygame
from AI import pathfinding
from textures import Texture, AnimationPanel

class GameElement:
    def __init__(self, background, xpos, ypos, name, tileSize, animState="idle"):
        self.name = name
        self.animPanel = AnimationPanel(self, name, animState)

        self.background = background
        self.tileSize = tileSize
        self.xpos = xpos
        self.ypos = ypos
    
    def burnAround(self):
        for i in range(-1, 1+1, 1):
            for j in range(-1, 1+1, 1):
                tile = self.background.getAt(int(((self.xpos + self.tileSize//2)//self.tileSize) + i), int((self.ypos + self.tileSize//2)//self.tileSize) + j)
                
                if (tile and tile.overLayer):
                    tile.overLayer.launch_animation("burning")
    
    def reload(self):
        # Graphic
        self.background.window.blit(self.animPanel.get_texture(), (self.xpos, self.ypos))

class AnimatedElement(GameElement):
    def __init__(self, background, xpos, ypos, name, tileSize, state="idle"):
        super().__init__(background, xpos, ypos, name, tileSize, state)

        self.movingTo = None
        self.timeLeft = 0
        self.animDuration = 0
    
    def move_to(self, pos, duration):
        self.movingTo = pos
        self.timeLeft = duration
        self.speed = duration
    
    def reload(self, FPS):
        if (self.movingTo):
            self.xpos += ( self.movingTo[0] - self.xpos ) / ( self.timeLeft * FPS )
            self.ypos += ( self.movingTo[1] - self.ypos ) / ( self.timeLeft * FPS )

            self.timeLeft -= 1/FPS
            if (self.timeLeft <= 0):
                self.movingTo = None
        
        super().reload()

class Entity(GameElement):
    def __init__(self, background, xpos, ypos, name, tileSize, animState="idle"):
        super().__init__(background, xpos, ypos, name, tileSize, animState)
    
        self.minSpeed = 180
        self.currentSpeed = self.minSpeed
        self.maxSpeed = 360
        self.moving = False
        self.timeSinceNoMove = 0
        self.currentDirection = None
        self.lastDirection = "d"

        self.character = name
        self.health = 50

    def move(self, FPS, is_pressed):
        if (not self.moving):
            self.currentDirection = None
        
        result, distance, goalDiff = [0, 0], [0, 0], [0, 0]

        self.moving = False
        for key in ["d", "q", "z", "s"]:
            if is_pressed[key]:
                if key in ["q", "d"]:
                    self.currentDirection = key
                    self.lastDirection = key
                
                goalDiff = [0, 0]
                if key == "d":
                    goalDiff[0] += 1
                if key == "q":
                    goalDiff[0] -= 1
                if key == "z":
                    goalDiff[1] -= 1
                if key == "s":
                    goalDiff[1] += 1

                if (self.currentDirection and self.currentDirection != key and is_pressed[self.currentDirection]):
                    dist = 0.5/FPS * self.currentSpeed
                else:
                    dist = 1/FPS * self.currentSpeed
                
                goal = (self.xpos + goalDiff[0]*dist, self.ypos + goalDiff[1]*dist)
                goalTile = self.background.getAt(round((goal[0] + (1 + goalDiff[0]) * self.tileSize//2) // self.tileSize), round((goal[1] + (1 + goalDiff[1 ]) * self.tileSize//2) // self.tileSize))
                
                distance[0] += abs(goalDiff[0] * dist)
                distance[1] += abs(goalDiff[1] * dist)
                if (goalTile and not goalTile.collide):
                    self.moving = True

                    if self.animPanel.get_animation() == "sleep":
                        self.animPanel.launch_animation("idle")

                    result[0] += goalDiff[0] * dist
                    result[1] += goalDiff[1] * dist

                    self.xpos, self.ypos = goal[0], goal[1]
            
        if (self.moving and self.currentSpeed < self.maxSpeed):
            self.currentSpeed *= 1 + 1/FPS
        if (not self.moving and self.currentSpeed > self.minSpeed):
            self.currentSpeed *= 1 - 5/FPS
        
        return result, distance

class Enemy(Entity):
    def __init__(self, background, xpos, ypos, name, tileSize, animState="idle"):
        super().__init__(background, xpos, ypos, name, tileSize, animState)

        self.path = []
        self.distance = 0
        self.targetDistance = 10
    
    def move(self, FPS, players):
        selfPos = (self.xpos // self.tileSize + 0.5, self.ypos // self.tileSize + 0.5)

        if self.distance >= self.tileSize:
            self.path.pop(0)
            self.distance = 0
            # print("Removed")

        for player in players:
            playerPos = (player.xpos // self.tileSize + 0.5, player.ypos // self.tileSize + 0.5)
            if (abs(selfPos[0] - playerPos[0]) + abs(selfPos[0] - playerPos[0]) <= self.targetDistance):
                if (len(self.path) == 0):
                    # print("Found New Path")
                    self.path = pathfinding(self.background, selfPos, playerPos)
                
                # print(self.path, len(self.path), self.distance)
                if (len(self.path) > 0):
                    # print("Found Path")
                    _, result = super().move(FPS, {
                        "z": self.path[0][1] == -1,
                        "s": self.path[0][1] == 1,
                        "q": self.path[0][0] == -1,
                        "d": self.path[0][0] == 1,
                    })

                    self.distance += result[0] + result[1]