import math
from random import randint

def manhattan_dist(tileSize, element1, element2):
    return ( abs(element1.xpos - element2.xpos) + abs(element1.ypos - element2.ypos) ) / tileSize

def get_distance_from_all_entities(gameState, selfPlayer):
    distances = {}
    
    for entity in gameState.getAllEntities():
        if entity != selfPlayer:
            distances[entity] = math.sqrt((entity.xpos - selfPlayer.xpos)**2 + (entity.ypos - selfPlayer.ypos)**2) / gameState.tileSize - 0.5
    
    # keys = distances.keys()
    # sorted_distances = sorted(keys)
    # sorted_distances = {key: distances[key] for key in keys}

    return distances

def teleportToRandom(background, entity):
    found = False
    i = 0
    while not found:
        pos = (randint(0, background.width-1), randint(0, background.height-1))
        tile = background.getAt(pos[0], pos[1])

        print(tile)

        if tile and not tile.collide:
            entity.xpos, entity.ypos =  ( pos[0] + 0.5 ) * background.tileSize, \
                                        ( pos[1] + 0.5 ) * background.tileSize
            return
        else:
            i += 1

            if i > 100:
                raise ValueError("Couldn't find any tile not colliding")

def getProjectileEndPoint(A, B, radius): # A is the entity pos, B the mouse pos
    # Searching B point

    AB = math.sqrt( ( B[0] - A[0] )**2 + ( B[1] - A[1] )**2 )
    xDiff = ( ( B[0] - A[0] ) * radius ) / AB # Thales's theorem
    yDiff = ( ( B[1] - A[1] ) * radius ) / AB

    return ( A[0] + xDiff, A[1] + yDiff )