from dataclasses import dataclass
import dataclasses
import json
from random import choice, randint
import sys
from typing import Literal

import yaml

from gameElement import Enemy
from utils import getAngleFromEntities, getMousePosFromAngle, manhattan_dist
from player import PartialPlayer, AI

BEHAVIORS = ["noBehavior", "collaborator", "bourin", "sniper", "coward", "armorer", "simpleAttacker"]
OBJECTS = ["bomb", "armor", "sword"]
MAX_TIME = 300
CAPA_STATES = ["charging", "using", "ready", "fullBar"]
KEYS = ["s", "z", "q", "d"]

def load_brain(filename) -> "Brain":
    with open(f"./data/IA/{filename}.json", "r") as f:
        data = json.load(f)

    neurons = []
    for neur_data in data["neurons"]:
        inputs = []
        for inp_data in neur_data["inputs"]:
            inputs.append(getattr(sys.modules[__name__], inp_data["type"])(*inp_data.values()))
        
        output = getattr(sys.modules[__name__], neur_data["output"]["type"])(*neur_data["output"].values())
        
        neuron = Neuron(inputs, output, 0)
        neurons.append(neuron)
    
    brain = Brain(neurons)

    return brain

def create_new_brain(WIDTH, HEIGHT):
    coef = 0.5
    neurons = []
    for i in range(10):
        inputs: list[Input] = []

        for j in range(randint(1, 3)):
            inputType = randint(0, 6)

            if (inputType == 0):
                distance = randint(1, HEIGHT * 50) / 100

                pvMin = None
                if randint(0, (1 - coef) * 10) == 0:
                    pvMin = randint(1, 100)
                
                character = None
                if randint(0, (1 - coef) * 10) == 0:
                    character = choice(["wizard", "knight"])
                
                capaState = None
                if randint(0, (1 - coef) * 10) == 0:
                    capaState = choice(["charging", "using", "ready", "fullBar"])

                input = PlayerDistance("PlayerDistance", distance, pvMin, character, capaState)
            
            elif (inputType == 1):
                distance = randint(1, HEIGHT * 50) / 100

                kind = None
                if randint(0, (1 - coef) * 10) == 0:
                    kind = choice(OBJECTS)

                input = NearestObject("NearestObject", distance, kind)
            
            elif (inputType == 2):
                minTime = randint(0, MAX_TIME-1)
                maxTime = randint(minTime, MAX_TIME)

                input = TimeLeft("TimeLeft", maxTime, minTime)
            
            elif (inputType == 3):
                distance = randint(1, HEIGHT * 50) / 100

                pvMin = None
                if randint(0, (1 - coef) * 10) == 0:
                    pvMin = randint(1, 100)
                
                character = None
                if randint(0, (1 - coef) * 10) == 0:
                    character = choice(["blob"])

                input = EnemyDistance("EnemyDistance", distance, pvMin, character)
            
            elif (inputType == 4):
                entityType = None
                if randint(0, (1 - coef) * 10) == 0:
                    entityType = choice(["enemy", "player"])

                input = AttackingEntity("AttackingEntity", randint(0, MAX_TIME), entityType)
            
            elif (inputType == 5):
                input = OwnCapacityState("OwnCapacityState", choice(CAPA_STATES))
            
            else:
                input = OwnHealthPercentage("OwnHealthPercentage", randint(0, 100), randint(0, 100))
            
            inputs.append(input)
        
        outputType = randint(0, 4)

        if outputType == 0:
            output = Behavior("Behavior", choice(BEHAVIORS))
        
        elif outputType == 1:
            goal = (0,0)
            if randint(0, 1) == 0:
                goal = "inputData"

            output = GoalTile("GoalTile", goal, randint(0, 2) != 0)
        
        elif outputType == 2:
            output = Capacity("Capacity")
        
        elif outputType == 3:
            output = Attack("Attack")
        
        else:
            output = SimpleKey("SimpleKey", choice(KEYS))
        
        neurons.append(Neuron(inputs, output))
    
    return Brain(neurons)

def mixInputDatas(inputDatas):
    result = InputData(0, 0, 0)
    
    for inputData in inputDatas:
        attrs = inputData.__dict__
        for attr in attrs.keys():
            if attrs[attr]:
                setattr(result, attr, attrs[attr])
    
    return result

@dataclass
class GameState:
    timeLeft: int
    players: list[PartialPlayer]
    enemies: list[Enemy]
    objects: list
    tileSize: int

    def getAllEntities(self):
        return [entity for entity in self.players + self.enemies if not entity.dead]

@dataclass
class InputData:
    distance: float | None
    angle: float | None
    pos: tuple[int, int] | None

@dataclass
class Brain:
    neurons: list["Neuron"]

    def checkNeurons(self, gameState: GameState, selfAI):
        for neuron in self.neurons:
            neuron.checkNeuron(gameState, selfAI)

@dataclass
class Neuron:
    inputs: list["Input"]
    output: "Output"
    points: int = 0

    def checkNeuron(self, gameState: GameState, selfAI: AI):
        checked = True
        for inp in self.inputs:
            if not inp.isChecked(gameState, selfAI):
                checked = False
                break
        
        if checked:
            self.output.performAction(mixInputDatas([input.getInputData() for input in self.inputs]), selfAI)

@dataclass
class Input:
    inputData = InputData(None, None, None)

    def isChecked(self, gameState, selfAI):
        return False
    
    def getInputData(self):
        return self.inputData

@dataclass
class PlayerDistance(Input):
    type: Literal["PlayerDistance"]
    distance: float # matrice
    pvMin: int | None
    character: Literal["wizard", "knight"] | None
    capaState: Literal["charging", "using", "ready", "fullBar"] | None

    def isChecked(self, gameState: GameState, selfAI: AI):
        nearest = None
        nearestDist = 0
        for player in gameState.players:
            if player != selfAI:
                distance = manhattan_dist(gameState.tileSize, player, selfAI)
                if ( not nearest and distance <= self.distance ) or ( distance <= nearestDist ):

                    # Check optionnal values
                    if  ( self.pvMin == None or ( player.health < self.pvMin ) ) and\
                        ( self.character == None or ( player.character == self.character ) ):
                        
                        angle = getAngleFromEntities(selfAI, player)
                        nearest = player
                        nearestDist = distance
        
        # Update input data
        if (nearest):
            self.inputData.distance = distance
            self.inputData.pos = (nearest.xpos // gameState.tileSize, nearest.ypos // gameState.tileSize)
            self.inputData.angle = angle
        
        return nearest != None

@dataclass
class NearestObject(Input):
    type: Literal["NearestObject"]
    distance: int
    kind: Literal["bomb", "armor", "sword"] | None

    def isChecked(self, gameState, selfAI):
        nearest = None
        nearestDist = 0

        for obj in gameState.objects:
            distance = manhattan_dist(gameState.tileSize, obj, selfAI)
            if distance < self.distance:
                if ( not nearest and distance < self.distance ) or ( distance <= nearestDist ):
                    # Optionnal values
                    if ( not self.kind or obj.name == self.kind ):
                        angle = getAngleFromEntities(selfAI, obj)
                        nearest = obj
                        nearestDist = distance
        
        # Input data
        if nearest:
            self.inputData.distance = distance
            self.inputData.pos = (nearest.xpos // gameState.tileSize, nearest.ypos // gameState.tileSize)
            self.inputData.angle = angle
        
        return nearest != None

@dataclass
class TimeLeft(Input):
    type: Literal['TimeLeft']
    maxTime: int | None
    minTime: int | None

    def isChecked(self, gameState: GameState, selfAI: AI):
        return ( self.minTime == None or gameState.timeLeft >= self.minTime ) and ( self.maxTime == None or gameState.timeLeft <= self.maxTime )

@dataclass
class EnemyDistance(Input):
    type: Literal["EnemyDistance"]
    distance: float
    pvMin: int | None
    character: Literal["blob"] | None

    def isChecked(self, gameState: GameState, selfAI: AI):
        nearest = None
        nearestDist = 0
        for enemy in gameState.enemies:
            distance = manhattan_dist(gameState.tileSize, enemy, selfAI)
            if ( not nearest and distance < self.distance ) or ( distance <= nearestDist ):

                # Check optionnal values
                if  ( self.pvMin == None or ( enemy.health < self.pvMin ) ) and\
                    ( self.character == None or ( enemy.character == self.character ) ):
                    
                    nearest = enemy
                    nearestDist = distance
                    angle = getAngleFromEntities(selfAI, enemy)
        
        # Update input data
        if (nearest):
            self.inputData.distance = distance
            self.inputData.pos = (nearest.xpos // gameState.tileSize, nearest.ypos // gameState.tileSize)
            self.inputData.angle = angle
        
        return nearest != None

@dataclass
class AttackingEntity(Input):
    type: Literal["AttackingEntity"]
    maxTime: int
    entityType: Literal["player", "enemy"] | None

    def isChecked(self, gameState: GameState, selfAI: AI):
        return selfAI.lastAttacker and selfAI.lastAttackedTime <= self.maxTime and \
            ( not self.entityType or \
                ( self.entityType == "player" and issubclass(selfAI.lastAttacker.__class__, PartialPlayer) or \
                    self.entityType == "enemy" and type(selfAI.lastAttacker) is Enemy) )

@dataclass
class OwnCapacityState(Input):
    type: Literal["OwnCapacityState"]
    state: Literal["charging", "using", "ready", "fullBar"]

    def isChecked(self, gameState: GameState, selfAI: AI):
        if self.state == "charging":
            return selfAI.capaCurrCooldown < selfAI.capaMaxCooldown / selfAI.mapCapaUsesWithFullBar
        elif self.state == "using":
            return selfAI.capaUsing
        elif self.state == "ready":
            return selfAI.capaCurrCooldown >= selfAI.capaMaxCooldown / selfAI.mapCapaUsesWithFullBar
        else:
            return selfAI.capaCurrCooldown >= selfAI.capaMaxCooldown

@dataclass
class OwnHealthPercentage(Input):
    type: Literal["OwnHealthPercentage"]
    minPercentage: int | None
    maxPercentage: int | None

    def isChecked(self, gameState, selfAI):
        ratio = ( selfAI.health / selfAI.maxHealth ) * 100
        return ( self.minPercentage == None or ratio >= self.minPercentage ) and ( self.maxPercentage == None or ratio <= self.maxPercentage )

@dataclass
class Output:
    def performAction(self, inputData: InputData, selfAI: AI):
        print("Doing nothing...")

@dataclass
class Behavior(Output):
    type: Literal["Behavior"]
    behavior: Literal["noBehavior", "collaborator", "bourin", "sniper", "coward", "armorer", "simpleAttacker"]

    def performAction(self, inputData: InputData, selfAI: AI):
        selfAI.behavior = self.behavior

@dataclass
class GoalTile(Output):
    type: Literal["GoalTile"]
    coords: tuple[int, int] | Literal["inputData"]
    reversed: bool
    
    def performAction(self, inputData: InputData, selfAI: AI):
        if self.coords == "inputData":
            if inputData.pos:
                selfAI.setGoalTile(inputData.pos, self.reversed)
            else:
                print("no inputData")
        else:
            selfAI.setGoalTile(self.coords, self.reversed)

@dataclass
class Capacity(Output):
    type: Literal["Capacity"]

    def performAction(self, inputData, selfAI: AI):
        selfAI.enableKey("capacity")

        if inputData.angle:
            selfAI.mousePos = getMousePosFromAngle((selfAI.xpos, selfAI.ypos), inputData.angle)

@dataclass
class Attack(Output):
    type: Literal["Attack"]

    def performAction(self, inputData: InputData, selfAI: AI):
        selfAI.enableKey("attack")
        if inputData.angle:
            selfAI.mousePos = getMousePosFromAngle((selfAI.xpos, selfAI.ypos), inputData.angle)
@dataclass
class SimpleKey(Output):
    type: Literal["SimpleKey"]
    key: Literal["z", "s", "q", "d", "capacity", "attack"]

    def performAction(self, inputData: InputData, selfAI: AI):
        selfAI.enableKey(self.key)

def save_brains(brains, files):
    for i in range(len(brains)):
        with open(f"../data/IA/{files[i]}.yaml", "w") as f:
            yaml.dump(brains[i], f)

        with open(f"../data/IA/{files[i]}.json", "w") as f:
            json.dump(dataclasses.asdict(brains[i]), f)