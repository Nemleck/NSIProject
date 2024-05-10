import pygame
from AI import pathfinding
from textures import Texture, AnimationPanel
from utils import *

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
                tile = self.background.getAt(int(((self.xpos)//self.tileSize) + i), int((self.ypos)//self.tileSize) + j)
                
                if (tile and tile.overLayer):
                    tile.overLayer.launch_animation("burning")
    
    def reload(self):
        # Graphic
        self.background.window.blit(self.animPanel.get_texture(), (self.xpos - self.background.tileSize//2, self.ypos - self.background.tileSize//2))

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
    
        self.minSpeed = 1
        self.currentSpeed = self.minSpeed
        self.maxSpeed = 2
        self.moving = False
        self.timeSinceNoMove = 0
        self.currentDirection = None
        self.lastDirection = "d"

        self.attackRange = 1
        self.attackValue = 3

        self.character = name
        self.maxHealth = 50
        self.health = 50
        self.autoRegen = 1 # Health won per second
        self.dead = False

        self.lastAttacker: Entity | None = None
        self.lastAttackedTime: int | None = None

        self.healthBar = AnimationPanel(self, "healthBar", "idle")
    
    def attackAround(self, gameState):
        distances = get_distance_from_all_entities(gameState, self)
        
        amountHurt = 0
        for key in distances.keys():
            if distances[key] < self.attackRange:
                amountHurt += 1
                key.hurt(self.attackValue, self)
        
        return amountHurt
    
    def hurt(self, amount, attacker):
        self.health -= amount
        self.lastAttacker = attacker
        self.lastAttackedTime = 0
    
        if self.health <= 0:
            self.health = 0
            self.dead = True

    def reload(self, FPS):
        if not self.dead:
            # Reload health bar

            self.healthBar.set_size(self.tileSize * ( self.health / self.maxHealth ), None)

            super().reload()
            self.background.window.blit(self.healthBar.get_texture(), (self.xpos - self.tileSize//2, self.ypos - self.tileSize))

    def move(self, FPS, is_pressed, gameState):
        # Attacked time

        if self.lastAttacker:
            self.lastAttackedTime += 1

            if self.lastAttackedTime > 4000:
                self.lastAttacker = None

        # Adjust Health Bar

        self.health += self.autoRegen/FPS
        if self.health > self.maxHealth:
            self.health = self.maxHealth

        self.healthBar.set_size(self.tileSize * ( self.health / self.maxHealth ), None)

        # Move the entity

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
                    dist = 0.5/FPS * self.currentSpeed * self.tileSize
                else:
                    dist = 1/FPS * self.currentSpeed * self.tileSize
                
                goal = (self.xpos + goalDiff[0]*dist, self.ypos + goalDiff[1]*dist)
                goalTile = self.background.getAt(round((goal[0] + goalDiff[0] * self.tileSize//2) // self.tileSize), round((goal[1] + goalDiff[1] * self.tileSize//2) // self.tileSize))
                
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
        self.health = 50

        self.maxAttackCooldown = 3
        self.currAttackCooldown = 3
    
    def move(self, FPS, gameState):
        # Attack

        self.currAttackCooldown -= 1/FPS
        if self.currAttackCooldown <= 0:
            amounrHurt = self.attackAround(gameState)

            if amounrHurt:
                self.animPanel.launch_animation("attack")

            self.currAttackCooldown = self.maxAttackCooldown

        # Move

        selfPos = (self.xpos // self.tileSize, self.ypos // self.tileSize)

        if self.distance >= self.tileSize:
            self.path.pop(0)
            self.distance = 0

        for player in gameState.players:
            playerPos = (player.xpos // self.tileSize, player.ypos // self.tileSize)
            if (abs(selfPos[0] - playerPos[0]) + abs(selfPos[0] - playerPos[0]) <= self.targetDistance):
                if (len(self.path) == 0):
                    self.path = pathfinding(self.background, selfPos, playerPos)
                
                if (len(self.path) > 0):
                    _, result = super().move(FPS, {
                        "z": self.path[0][1] == -1,
                        "s": self.path[0][1] == 1,
                        "q": self.path[0][0] == -1,
                        "d": self.path[0][0] == 1,
                    }, gameState)

                    self.distance += result[0] + result[1]