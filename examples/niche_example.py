import random
import time
import math
import itertools
from ecspy import ec
from ecspy import selectors
from ecspy import terminators
from ecspy import variators
from ecspy import replacers
from ecspy import observers


def my_distance(x, y):
    return sum([math.fabs(a - b) for a, b in zip(x, y)])

def generate(random, args):
    lower = args.get('lower_bound', 0)
    upper = args.get('upper_bound', 1)
    return [random.uniform(lower, upper) for _ in xrange(1)]
    

def evaluate(candidates, args):
    fitness = []
    for cand in candidates:
        fit = sum([math.sin(c) for c in cand])
        fitness.append(fit)
    return fitness


def main(do_plot=True, prng=None):
    if prng is None:
        prng = Random()
        prng.seed(time.time()) 
    
    ga = ec.EvolutionaryComputation(prng)
    ga.selector = selectors.tournament_selection
    ga.replacer = replacers.crowding_replacement
    ga.variator = variators.gaussian_mutation
    ga.observer = observers.screen_observer
    ga.terminator = terminators.evaluation_termination

    final_pop = ga.evolve(generate, evaluate, pop_size=20,
                          max_evaluations=5000,
                          num_selected=20,
                          upper_bound=26,
                          lower_bound=0,
                          mutation_rate=1.0,
                          crowding_distance=10,
                          distance_function=my_distance,
                          mutation_range=0.1)
                          
    if do_plot:
        import pylab
        x = []
        y = []
        for p in final_pop:
            x.append(p.candidate[0])
            y.append(math.sin(p.candidate[0]))
        pylab.scatter(x, y)
        pylab.axis([0, 26, 0, 1.1])
        pylab.show()

    return ga

if __name__ == '__main__':
    main()




    
    
    