def pathfinding(background, start_pos, end_pos):
    # A* algorithm

    start_pos = (int(start_pos[0]), int(start_pos[1]))
    end_pos = (int(end_pos[0]), int(end_pos[1]))

    if (start_pos[0] == end_pos[0] and start_pos[1] == end_pos[1]):
        return []

    bgMap = background.getIntList()
    
    toAnalyse = [start_pos]
    while len(toAnalyse) > 0:
        currX, currY = toAnalyse[0][0], toAnalyse[0][1]
        for direction in [(0,1), (0,-1), (1,0), (-1,0)]:
            x = direction[0]
            y = direction[1]
            
            newX = currX+x
            newY = currY+y
            
            if (0 <= newX < len(bgMap) and 0 <= newY < len(bgMap[newX])):
                if (bgMap[newX][newY] == 0 and not (newX == start_pos[0] and newY == start_pos[1])): #Dosn't collide
                    bgMap[newX][newY] = bgMap[currX][currY] + 1
                    toAnalyse.append((newX, newY))
        
        toAnalyse.pop(0)

    result = []
    curr_pos, curr_value = end_pos[:], bgMap[end_pos[0]][end_pos[1]]

    finished = False
    i = 0
    while not finished:
        for direction in [(0,1), (0,-1), (1,0), (-1,0)]:
            x = direction[0]
            y = direction[1]
            
            newX = curr_pos[0]+x
            newY = curr_pos[1]+y
            
            if (0 <= newX < len(bgMap) and 0 <= newY < len(bgMap[newX])):
                if ((bgMap[newX][newY] != -1 and bgMap[newX][newY] < curr_value)):
                    if (bgMap[newX][newY] == 0):
                        finished = True

                    result.append((-x, -y))
                    curr_pos, curr_value = (newX, newY), bgMap[newX][newY]
            
        i += 1
        if i > 500:
            return []
    
    result.reverse()
    return result

def printTab(tab):
    for y in range(len(tab[0])):
        for x in range(len(tab)):
            print(tab[x][y], end=" ")
            
            for i in range(2-len(str(tab[x][y]))):
                print(" ", end="")
        print()