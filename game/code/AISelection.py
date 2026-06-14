from AIBrain import *
from main import play
import inspect

WIDTH = 10
HEIGHT = 8

GENERATIONS_NUM = 5
POPULATION_NUM = 5
BESTS_NUM = 2

def play_game(brains: list[Brain]):
    points = play(False, brains, False)

    print()
    print("POINTS :", [p[0] for p in points])

    return [
        {
            "total_points": points[i][0],
            "neurons_points": points[i][1],
            "brain": brains[i],
        } for i in range(len(brains))
    ]

def get_points(brain):
    return brain["total_points"]

def mutate(brain):
    neuron = choice(brain.neurons)
    nInput = choice(neuron.inputs+[neuron.output])
    
    allAttributes = [key for key in nInput.__dict__.keys() if not ("__" in key or key=="type")]
    if len(allAttributes):
        attr = choice(allAttributes)
    else:
        return mutate(brain)

    newValue = generate_property(attr, getattr(nInput, attr))

    setattr(nInput, attr, newValue)

    return brain

# Generations
brains = [create_new_brain(WIDTH, HEIGHT) for i in range(POPULATION_NUM)]
for gen in range(GENERATIONS_NUM):
    print("-----------------------------------")
    print(f"Génération {gen+1}/{GENERATIONS_NUM}")
    print("-----------------------------------")
    print()

    result = play_game(brains)
    result.sort(key=get_points, reverse=True)

    # Delete worse and mutate bests
    brains = brains[0:BESTS_NUM]

    for i in range(POPULATION_NUM - BESTS_NUM):
        brains.append(mutate(brains[i % POPULATION_NUM]))
    
    print()

save_brains([brains[0]], ["wizard"])