from dataclasses import dataclass
import dataclasses
import json
from random import choice, randint
import sys
from typing import Literal, get_args, _GenericAlias

from gameElement import Enemy
from utils import getAngleFromEntities, getMousePosFromAngle, manhattan_dist
from player import PartialPlayer, AI

BEHAVIORS = ["noBehavior", "collaborator", "bourin", "sniper", "coward", "armorer", "simpleAttacker"]
OBJECTS = ["bomb", "armor", "sword"]
PLAYER_CHARS = ["wizard", "fletcher", "knight"]
ENEMIES = ["blob", "bat", "livingTree"]
MAX_TIME = 300
CAPA_STATES = ["charging", "using", "ready", "fullBar"]
KEYS = ["s", "z", "q", "d"]
TILE_TYPES = ["grass", "river"]
WIDTH = 10
HEIGHT = 8

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
            inputType = choice([PlayerDistance, NearestObject, TimeLeft, EnemyDistance, AttackingEntity, OwnCapacityState, OwnHealthPercentage, TilesAround])

            annots = inputType.__annotations__
            args = [
                generate_property(prop, None, is_nullable(annots[prop])) for prop in annots.keys() if prop != "type"
            ]
            
            inputs.append(inputType(inputType.__name__, *args))
        
        outputType = choice([GoalTile, Capacity, SimpleKey, Attack])

        annots = outputType.__annotations__
        args = [
            generate_property(prop, None, is_nullable(annots[prop])) for prop in annots.keys() if prop != "type"
        ]
        
        output = outputType(outputType.__name__, *args)
        
        neurons.append(Neuron(inputs, output))
    
    return Brain(neurons)

def is_nullable(propType):
    return isinstance(propType, _GenericAlias) and type(None) in propType.__args__

def generate_property(property: str, value, nullable=False):
    property = property.lower()

    if nullable and randint(0, 3) == 0:
        return None

    result = value
    i = 0
    while result == value:
        i += 1
        if "pv" in property:
            if value:
                result = value + randint(-10, 10)
            else:
                result = randint(0, 200)
        elif "character" in property:
            result = choice(PLAYER_CHARS)
        elif property == "capastate":
            result = choice(CAPA_STATES)
        elif property == "objkind":
            result = choice(OBJECTS)
        elif "time" in property:
            if value:
                result = value + randint(-20, 20)
            else:
                result = randint(1, MAX_TIME)
        elif property == "enemychar":
            result = choice(ENEMIES)
        elif property == "entitytype":
            result = choice(["player", "enemy"])
        elif "percentage" in property:
            if value:
                result = result + randint(-30, 30)
                if result > 100:
                    result = 100
                elif result < 0:
                    result = 0
            else:
                result = randint(1, 100)
        elif property == "relativepos":
            if value:
                result = [value[0] + randint(-2, 2), value[1] + randint(-2, 2)]
            else:
                result = [randint(-2, 2), randint(-2, 2)]
        elif property in ["globalpos", "coords"]:
            if property == "coords" and randint(0, 5) != 0:
                if value and not type(value) is str:
                    result = [value[0] + randint(-5, 5), value[1] + randint(-5, 5)]
                else:
                    result = [randint(0, WIDTH), randint(0, HEIGHT)]
            else:
                result = "inputData"

            # TODO : Put map limit here
        elif "tiletype" in property:
            result = choice(TILE_TYPES)
        elif property in ["tilecollision", "reversed"]:
            result = randint(0, 1) == 0
        elif "key" in property:
            result = choice(KEYS)
        elif "behavior" in property:
            result = choice(BEHAVIORS)
        elif "distance" in property:
            if value:
                result = value + randint(-30, 30) / 100
                if result < 0:
                    result = 0
            else:
                result = randint(0, 300) / 100
        else:
            print("DIDN'T FIND :", property)
        
        if i > 10:
            break
    
    return result

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
    
    def getPlayers(self):
        return [player for player in self.players if not player.dead]

@dataclass
class InputData:
    distance: float | None
    angle: float | None
    pos: tuple[int, int] | None

@dataclass
class Brain:
    neurons: list["Neuron"]

    def checkNeurons(self, gameState: GameState, selfAI):
        result = []
        for neuron in self.neurons:
            enabled = neuron.checkNeuron(gameState, selfAI)
            if enabled:
                result.append(neuron)
        
        return result

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
        
        return checked

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
        for player in gameState.getPlayers():
            if player != selfAI:
                distance = manhattan_dist(gameState.tileSize, player, selfAI)
                if ( not nearest and distance <= self.distance ) or ( distance <= nearestDist ):
                    # Check optionnal values
                    if  ( self.pvMin == None or ( player.health < self.pvMin ) ) and\
                        ( self.character == None or ( player.character == self.character ) ):
                        # print("Checked !")
                        
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
    objKind: Literal["bomb", "armor", "sword"] | None

    def isChecked(self, gameState, selfAI):
        nearest = None
        nearestDist = 0

        for obj in gameState.objects:
            distance = manhattan_dist(gameState.tileSize, obj, selfAI)
            if distance < self.distance:
                if ( not nearest and distance < self.distance ) or ( distance <= nearestDist ):
                    # Optionnal values
                    if ( not self.objKind or obj.name == self.objKind ):
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
    enemyChar: Literal["blob", "bat", "livingTree"] | None

    def isChecked(self, gameState: GameState, selfAI: AI):
        nearest = None
        nearestDist = 0
        for enemy in gameState.enemies:
            distance = manhattan_dist(gameState.tileSize, enemy, selfAI)
            if ( not nearest and distance < self.distance ) or ( distance <= nearestDist ):

                # Check optionnal values
                if  ( self.pvMin == None or ( enemy.health < self.pvMin ) ) and\
                    ( self.enemyChar == None or ( enemy.character == self.enemyChar ) ):
                    
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
    capaState: Literal["charging", "using", "ready", "fullBar"]

    def isChecked(self, gameState: GameState, selfAI: AI):
        if self.capaState == "charging":
            return selfAI.capaCurrCooldown < selfAI.capaMaxCooldown / selfAI.mapCapaUsesWithFullBar
        elif self.capaState == "using":
            return selfAI.capaUsing
        elif self.capaState == "ready":
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
class TilesAround(Input):
    type: Literal["TilesAround"]
    relativePos: tuple[int, int]
    tileType: str | None
    tileCollision: bool | None

    def isChecked(self, gameState: GameState, selfAI: AI):
        tile = selfAI.background.getAt(selfAI.xpos//gameState.tileSize + self.relativePos[0], selfAI.ypos//gameState.tileSize + self.relativePos[1])
        
        if not tile:
            return self.tileCollision == True # If a collision is needed and there is no tile, return True, False otherwise

        return ( not self.tileType or self.tileType == tile.type ) and ( self.tileCollision == tile.doesCollide(selfAI.zIndex) )

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
            # else:
            #     print("no inputData")
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
        # with open(f"./data/IA/{files[i]}.yaml", "w") as f:
        #     yaml.dump(brains[i], f)

        with open(f"./data/IA/{files[i]}.json", "w") as f:
            json.dump(dataclasses.asdict(brains[i]), f)