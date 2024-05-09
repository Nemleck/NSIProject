from AIBrain import *

WIDTH = 10
HEIGHT = 8

GENERATIONS_NUM = 3
POPULATION_NUM = 10
BESTS_NUM = 2

def play_game(brains: list[Brain]):
    return [
        {
            "total_points": randint(100, 300),
            "neurons_points": [ randint(0, 10) for j in range(len(brains[i].neurons)) ],
            "brain": brains[i]
        } for i in range(len(brains))
    ]

def get_points(brain):
    return brain["total_points"]

def mutate(brain):
    return brain

# Generations
brains = [create_new_brain(WIDTH, HEIGHT) for i in range(POPULATION_NUM)]
for gen in range(GENERATIONS_NUM):
    result = play_game(brains)
    result.sort(key=get_points, reverse=True)

    # Delete worse and mutate bests
    brains = brains[0:BESTS_NUM]

    for i in range(POPULATION_NUM - BESTS_NUM):
        brains.append(mutate(brains[i % POPULATION_NUM]))
    
    # print([r["total_points"] for r in result])

save_brains([brains[0]], ["wizard"])