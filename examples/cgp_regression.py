'''
Created on Jul 26, 2010

@author: henrik

symbolic regression of a 6th order polynominal
as described in original Cartesian genetic programming paper: Miller 2008 (GECCO Proceedings)

'''
__author__ = 'henrik'

from ecspy.contrib.cartesian_gp import CartesianGraphEncoding, CallableGraph
from sympy.core.symbol import Symbol
from sympy.core.numbers import RealNumber


from random import Random
import random
from time import time
from ecspy import ec, observers, terminators, variators
import math
from itertools import *
from ecspy.selectors import truncation_selection, tournament_selection


def div(num, den):
    '''
    return numerator if denominator is 0
    '''
    return num if den == 0.0 else num / den


ops = [float.__add__, float.__sub__, float.__mul__, div]

def arithmetic(node, args, data):
    a, b = args
    op = data[0]
    op = int((op % 1) * len(ops))
    val = ops[op](a,b)
    return val


def sympy_arithmetic(node, args, data):
    a, b = list(args)
    op = int((data[0] % 1) * 4)
    ops = [a.__add__, a.__sub__, a.__mul__, a.__div__]
    val = ops[op](b)
    return val

def get_fitness_function(target_function, constants):
    '''

    The fitness cases were 50 random values of X from the interval [-1.0, +1.0].
    These were fixed throughout the evolutionary run. The fitness of a program was
    defined as the sum over the 50 fitness cases of the sum of the absolute value of
    the error between the value returned by the program and that corresponding to the
    sixth order polynomial.
    --Miller
    '''
    def fitness(candidates, args):
        fitness = []
        sample_points = [random.random()*2-1 for _ in xrange(50)]
        for cand in candidates:
            fit = 0.0
            evolved_function = CallableGraph(encoding.decode(cand), arithmetic)

            for x in sample_points:
                x = random.random()*2 - 1
                target = target_function(x)
                solution = evolved_function([x]+constants)[0]
                fit += math.sqrt(abs(target - solution))
            fitness.append(fit)
        return fitness
    return fitness
def mutate_edge(v):
    return (v + random.random() * 0.4-0.2) % 1.0

def mutate_data(v):
    return (v + random.randint(-1,1)) % 4

def generate_data():
    return random.randint(0,4)



if __name__ == '__main__':

    #The population size chosen was 10. The number of generations was equal to 8000.
    #The crossover rate was 100% (entire population replaced by children). The mutation rate was 2%,
    #i.e. on average 2% of the all the genes in the population were mutated. Other parameters were
    #as follows: nr =1, nc =10, l =10.



    constants = [1.]


    matrix_size = 10, 1
    n_inputs, n_outputs = 2, 1
    node_size = 2, 1
    levelsback = 10
    encoding = CartesianGraphEncoding(n_inputs, matrix_size, node_size, n_outputs, levelsback)

    target = lambda x: x ** 6 - 2 * x ** 4 + x ** 2
    fitness_function = get_fitness_function(target, constants)


    mutator = encoding.mutator(0.1, mutate_edge=mutate_edge, mutate_data=mutate_data)
    generator = encoding.generator(random_edge=random.random, random_data=generate_data)


    prng = Random()
    prng.seed(time())    
    ga = ec.GA(prng)

    ga.observer = [observers.mini_screen_observer, observers.file_observer]
    ga.terminator = terminators.evaluation_termination
    ga.variator = [mutator]
    ga.selector = tournament_selection
    #ga.bounder = wrap_around(0., 1.)
    start = time()
    print "setup"
    final_pop = ga.evolve(evaluator=fitness_function,
                          generator=generator,
                          max_evaluations=120000,
                          num_elites=1,
                          pop_size=12,
                          mean=0.0, stdev=0.1,
                          mutation_rate=0.02,
                          tourn_size=4,
                          num_generations=1,
                          maximize=False)
    stop = time()
    #stat_file.close()
    #ind_file.close()

    print('***********************************')
    print('Total Execution Time: %0.5f seconds' % (stop - start))
    #for ind in final_pop:
    #    print(str(ind))

    exps = []
    final_pop.sort(key=lambda c: c.fitness)
    item = lambda c: [CallableGraph(encoding.decode(c.candidate), sympy_arithmetic)([Symbol('x'), RealNumber(1.)])]
    final_exps = [(c.fitness, item(c)[0][0]) for c in final_pop]
    for fit, exp in final_exps:
        print fit, exp