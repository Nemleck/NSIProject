import json
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
    def __init__(self, background, xpos, ypos, name, tileSize, invoker, state="idle", DM=0, opacityGrowth=0):
        super().__init__(background, xpos, ypos, name, tileSize, state)

        self.movingTo = None
        self.timeLeft = 0
        self.animDuration = 0
        self.DM = DM
        self.invoker = invoker
        self.touching = []

        self.opacityGrowth = opacityGrowth
        self.currentOpacity = 100
    
    def move_to(self, pos, speed, tileSize):
        self.movingTo = pos
        self.timeLeft = math.sqrt(( pos[0] - self.xpos )**2 + ( pos[1] - self.ypos )**2) / ( speed * tileSize )
        self.speed = speed
    
    def move(self, FPS, gameState):
        self.currentOpacity += self.opacityGrowth/FPS

        if (self.movingTo):
            self.xpos += ( self.movingTo[0] - self.xpos ) / ( self.timeLeft * FPS )
            self.ypos += ( self.movingTo[1] - self.ypos ) / ( self.timeLeft * FPS )

            self.timeLeft -= 1/FPS
            if (self.timeLeft <= 0):
                self.movingTo = None
        
        tile = self.background.getAt(self.xpos // gameState.tileSize, self.ypos // gameState.tileSize)
        if not tile or tile.collide:
            self.movingTo = None
            
            if tile and tile.overLayer:
                tile.overLayer.launch_animation("sworded")
        
        if self.movingTo:
            for entity in gameState.getAllEntities():
                if self.invoker != entity and manhattan_dist(gameState.tileSize, self, entity) < 1:
                    if not entity in self.touching:
                        self.touching.append(entity)
                        entity.hurt(self.DM, self)

                elif entity in self.touching:
                    self.touching.remove(entity)

    def reload(self):
        if self.opacityGrowth > 0:
            self.animPanel.set_opacity(self.currentOpacity)
        
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
    
    def regenerate(self, amount):
        self.health += amount
        
        if self.health > self.maxHealth:
            self.health = self.maxHealth

    def reload(self):
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

        with open(f"./data/enemies/{name}.json", "r") as f:
            data = json.load(f)
        
        self.walkingPanel = AnimationPanel(self, "livingTree", "walk")
        self.walking = False

        self.path = []
        self.distance = 0

        self.detectionRange = data["detectionRange"]
        self.health = data["health"]
        self.maxHealth = self.health
        self.autoRegen = data["autoRegen"]

        self.maxAttackCooldown = data["attackCooldown"]
        self.currAttackCooldown = self.maxAttackCooldown
        self.attackValue = data["attackDM"]

        self.minSpeed = data["minSpeed"]
        self.maxSpeed = data["maxSpeed"]
    
    def move(self, FPS, gameState):
        # Attack

        self.currAttackCooldown -= 1/FPS
        if self.currAttackCooldown <= 0:
            amountHurt = self.attackAround(gameState)

            if amountHurt:
                self.animPanel.launch_animation("attack")

            self.currAttackCooldown = self.maxAttackCooldown

        # Move

        selfPos = (self.xpos // self.tileSize, self.ypos // self.tileSize)

        if self.distance >= self.tileSize:
            self.path.pop(0)
            self.distance = 0

        for player in gameState.players:
            playerPos = (player.xpos // self.tileSize, player.ypos // self.tileSize)
            if (abs(selfPos[0] - playerPos[0]) + abs(selfPos[0] - playerPos[0]) <= self.detectionRange):
                if (len(self.path) == 0):
                    self.path = pathfinding(self.background, selfPos, playerPos)
                
                if (len(self.path) > 0):
                    actualDist, result = super().move(FPS, {
                        "z": self.path[0][1] == -1,
                        "s": self.path[0][1] == 1,
                        "q": self.path[0][0] == -1,
                        "d": self.path[0][0] == 1,
                    }, gameState)

                    if actualDist[0] or actualDist[1]:
                        self.walking = True
                    else:
                        self.walking = False

                    self.distance += result[0] + result[1]
    
    def reload(self):
        if self.walking:
            self.background.window.blit(self.walkingPanel.get_texture(self.lastDirection == "q"), (self.xpos, self.ypos))
        else:
            super().reload()

class GameObject(GameElement):
    def __init__(self, background, xpos, ypos, name, tileSize, animState="idle"):
        super().__init__(background, (xpos+0.5)*tileSize, (ypos+0.5)*tileSize, name, tileSize, animState)

        self.isOnGround = True

    def move(self, FPS: float, gameState):
        if self.isOnGround:
            for player in gameState.players:
                if manhattan_dist(gameState.tileSize, self, player) < 1:
                    print("C TCHAO")
                    self.isOnGround = False
                    
                    # Touches the object

                    if self.name == "heart":
                        player.regenerate(50)
    
    def reload(self):
        if self.isOnGround:
            super().reload()