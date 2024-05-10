import pygame
from random import randint
from bgElement import Background, BgTile

def generateBackground(background: "Background", WIDTH, HEIGHT):
    generateRiver(background, WIDTH, HEIGHT)
    generateElement(background, "decorative_flower", WIDTH*HEIGHT//15, WIDTH, HEIGHT, False)
    generateElement(background, "tree", WIDTH*HEIGHT//5, WIDTH, HEIGHT)

    for i in range(WIDTH):
        tile = background.getAt(i, HEIGHT//2)
        if tile.type == "river":
            tile.setOverLayer("bridge", 0)
            tile.setCollide(False)

            leftTile = background.getAt(i-1, HEIGHT//2)
            rightTile = background.getAt(i+1, HEIGHT//2)
            if (leftTile and leftTile.type == "river"):
                if (rightTile and rightTile.type == "river"):
                    tile.overLayer.launch_animation("high")
                else:
                    tile.overLayer.flip()

def generateRiver(background: "Background", WIDTH, HEIGHT):
    tocheckpos = []

    for repeat in range(randint(1, 2)):
        a,b,c = randint(-60, 60)/100, randint(-1*(HEIGHT//2), HEIGHT//2), randint(-1*(WIDTH//2), WIDTH//2)
        for loop in range(-10 * (WIDTH//2), WIDTH*10, 1):
            x = loop/10
            fx = round(a*x*x + b*x + c)

            xBg = round(x + (WIDTH//2))
            for i in range(-1, 1, 1):
                for j in range(-1, 1, 1):
                    if 0 <= xBg+i < WIDTH and 0 <= fx+j < HEIGHT:
                        tocheckpos.append((xBg+i, fx+j))
                        background.pushElement(xBg+i, fx+j, "river")
                        background.getAt(xBg+i, fx+j).setCollide(True)

    for pos in tocheckpos:
        if pos[1]-1 > 0 and background.getAt(pos[0], pos[1]-1).type == "grass":
            background.map[pos[0]][pos[1]].setOverLayer("grassOverLayer", 0)

        if pos[0]-1 >= 0 and background.map[pos[0]-1][pos[1]].type == "grass":
            background.map[pos[0]][pos[1]].setOverLayer("grassOverLayer", 1)

        if pos[0]+1 < WIDTH and background.map[pos[0]+1][pos[1]].type == "grass":
            background.map[pos[0]][pos[1]].setOverLayer("grassOverLayer", 3)

        if pos[1]+1 < HEIGHT and background.map[pos[0]][pos[1]+1].type == "grass":
            background.map[pos[0]][pos[1]].setOverLayer("grassOverLayer", 2)

def generateElement(background: "Background", element: "BgTile", nbr, WIDTH, HEIGHT, collide=True):
    for i in range(nbr):
        randomPos = ( randint(0, WIDTH-1), randint(0, HEIGHT-1) )

        elementAt: "BgTile" = background.getAt(*randomPos)
        if (elementAt.type == "grass"):
            elementAt.setOverLayer(element, 0)
            elementAt.setCollide(collide)