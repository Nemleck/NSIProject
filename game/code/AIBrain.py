from dataclasses import dataclass
import dataclasses
import json
from random import choice, randint
from typing import Literal

import yaml

from utils import manhattan_dist
from player import PartialPlayer, AI

BEHAVIORS = ["collaborator", "bourin", "sniper", "coward", "armorer", "simpleAttacker"]
OBJECTS = ["bomb", "armor", "sword"]
MAX_TIME = 300
CAPA_STATES = ["charging", "using", "ready"]

def load_brain(filename) -> "Brain":
    with open(f"../data/IA/{filename}.yaml", "r") as f:
        brain = yaml.safe_load(f)
    return brain

def create_new_brain(WIDTH, HEIGHT):
    coef = 0.5
    neurons = []
    for i in range(10):
        inputs: list[Input] = []

        for i in range(randint(1, 3)):
            inputType = randint(0, 5)

            if (inputType == 0):
                distance = randint(1, HEIGHT * 50) / 100

                pvMin = None
                if randint(0, (1 - coef) * 10) == 0:
                    pvMin = randint(1, 100)
                
                character = None
                if randint(0, (1 - coef) * 10) == 0:
                    character = choice(["wizard"])
                
                capaState = None
                if randint(0, (1 - coef) * 10) == 0:
                    capaState = choice(["charging", "using", "ready"])

                input = PlayerDistance("playerDistance", distance, pvMin, character, capaState)
            
            elif (inputType == 1):
                distance = randint(1, HEIGHT * 50) / 100

                kind = None
                if randint(0, (1 - coef) * 10) == 0:
                    kind = choice(OBJECTS)

                input = NearestObject("nearestObject", distance, kind)
            
            elif (inputType == 2):
                input = TimeLeft("timeLeft", randint(1, MAX_TIME))
            
            elif (inputType == 3):
                distance = randint(1, HEIGHT * 50) / 100

                pvMin = None
                if randint(0, (1 - coef) * 10) == 0:
                    pvMin = randint(1, 100)
                
                character = None
                if randint(0, (1 - coef) * 10) == 0:
                    character = choice(["blob"])

                input = EnemyDistance("enemyDistance", distance, pvMin, character)
            
            elif (inputType == 4):
                entityType = None
                if randint(0, (1 - coef) * 10) == 0:
                    entityType = choice(["enemy", "player"])

                input = AttackingEntity("attackingEntity", randint(0, MAX_TIME), entityType)
            
            else:
                input = OwnCapacityState("ownCapacityState", choice(CAPA_STATES))
            
            inputs.append(input)
        
        outputType = randint(0, 2)

        if outputType == 0:
            output = Behavior("behavior", choice(BEHAVIORS))
        
        elif outputType == 1:
            relative = randint(0, 1) == 0

            output = GoalTile("goalTile", relative, (0, 0))
        
        else:
            output = Capacity("capacity")
        
        neurons.append(Neuron(inputs, output))
    
    return Brain(neurons)

@dataclass
class GameState:
    timeLeft: int
    players: list[PartialPlayer]
    chests: list
    tileSize: int

@dataclass
class InputData:
    distance: float | None
    pos: tuple[int, int] | None

@dataclass
class Brain:
    neurons: list["Neuron"]

@dataclass
class Neuron:
    inputs: list["Input"]
    output: "Output"

    def isChecked(self):
        checked = True
        for inp in self.inputs:
            if not inp.isChecked():
                checked = False
                break
        
        return checked

@dataclass
class Input:
    inputData = InputData(None, None)

    def isChecked(self):
        return False
    
    def getInputData(self):
        self.inputData

@dataclass
class PlayerDistance(Input):
    type: Literal['playerDistance']
    distance: float # matrice
    pvMin: int | None
    character: Literal["wizard"] | None
    capaState: Literal["charging", "using", "ready"] | None

@dataclass
class NearestObject(Input):
    type: Literal['nearestObject']
    distance: int
    kind: Literal["bomb", "armor", "sword"] | None

@dataclass
class TimeLeft(Input):
    type: Literal['timeLeft']
    maxTime: int

    def isChecked(self, gameState: GameState, selfAI: AI):
        return gameState.timeLeft <= self.maxTime

@dataclass
class EnemyDistance(Input):
    type: Literal['enemyDistance']
    distance: float
    pvMin: int | None
    character: Literal["blob"] | None

    def isChecked(self, gameState: GameState, selfAI: AI):
        nearest = None
        nearestDist = 0
        for player in gameState.players:
            if player != selfAI:
                distance = manhattan_dist(gameState.tileSize, player, selfAI)
                if ( not nearest and distance < self.distance ) or ( distance <= nearestDist ):

                    # Check optionnal values
                    if  ( self.pvMin == None or ( player.health < self.pvMin ) ) and\
                        ( self.character == None or ( player.character == self.character ) ):
                        
                        nearest = player
                        nearestDist = distance
        
        # Update input data
        if (nearest):
            self.inputData.distance = distance
            self.inputData.pos = (nearest.xpos // gameState.tileSize, nearest.ypos // gameState.tileSize)
        
        return nearest != None

@dataclass
class AttackingEntity(Input):
    type: Literal['attackingEntity']
    maxTime: int
    entityType: Literal["player", "enemy"] | None

    def isChecked(self, gameState: GameState, selfAI: AI):
        if selfAI.lastAttacker and selfAI.lastAttackedTime <= self.maxTime and \
            ( not self.entityType or type(self.lastAttacker) ):
            pass # TODO HERE REVIENS STP

@dataclass
class OwnCapacityState(Input):
    type: Literal['ownCapacityState']
    state: Literal["charging", "using", "ready"]

@dataclass
class Output:
    pass
@dataclass
class Behavior(Output):
    type: Literal["behavior"]
    behavior: Literal["collaborator", "bourin", "sniper", "coward", "armorer", "simpleAttacker"]

@dataclass
class GoalTile(Output):
    type: Literal["goalTile"]
    relative: bool
    coords: tuple[int, int] | Literal["inputData"]

@dataclass
class Capacity(Output):
    type: Literal["capacity"]

def save_brains(brains, files):
    for i in range(len(brains)):
        with open(f"../data/IA/{files[i]}.yaml", "w") as f:
            yaml.dump(brains[i], f)

        with open(f"../data/IA/{files[i]}.json", "w") as f:
            json.dump(dataclasses.asdict(brains[i]), f)