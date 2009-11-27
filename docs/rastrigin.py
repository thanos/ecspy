#start_imports
from random import Random
from time import time
from math import cos
from math import pi
from ecspy import ec
from ecspy import terminators
#end_imports


def generate_rastrigin(random, args):
    try:
        size = args['num_inputs']
    except KeyError:
        size = 1
    try:
        lower = args['lower_bound']
    except KeyError:
        lower = 0
    try:
        upper = args['upper_bound']
    except KeyError:
        upper = 1
    return [random.uniform(lower, upper) for i in xrange(size)]

def evaluate_rastrigin(candidates, args):
    fitness = []
    for cs in candidates:
        fit = 10 * len(cs) + sum([((x - 1)**2 - 10 * cos(2 * pi * (x - 1))) for x in cs])
        fitness.append(-fit)
    return fitness

#start_main
rand = Random()
rand.seed(int(time()))
es = ec.ES(rand)
final_pop = es.evolve(generator=generate_rastrigin,
                      evaluator=evaluate_rastrigin,
                      terminator=terminators.evaluation_termination,
                      max_evaluations=20000,
                      mutation_rate=0.25,
                      lower_bound=-5.12,
                      upper_bound=5.12,
                      pop_size=100,
                      num_inputs=3)
# Print the best individual, who will be at index 0.
print(final_pop[0])
#end_main