def manhattan_dist(tileSize, element1, element2):
    return ( abs(element1.xpos - element2.xpos) + abs(element1.ypos - element2.ypos) ) / tileSize