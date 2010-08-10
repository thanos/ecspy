

from ecspy.contrib.cartesian_gp import CartesianGraphEncoding, CallableGraph

__author__ = 'henrik'

'''
Created on Jul 22, 2010

@author: henrik
'''
from random import Random
import random
from time import time
from ecspy import ec, observers, terminators, variators
import math
from itertools import *
from ecspy.selectors import truncation_selection, tournament_selection
matrix_size = (4, 3)
node_size = (2, 1)
n_inputs, n_outputs = 1, 1
n_args, output_args = 2, 1
levelsback = 2
encoding = CartesianGraphEncoding(n_inputs, matrix_size, node_size, n_outputs, levelsback)


def arithmetic(node, args, data):
    a, b = args
    op = data[0]
    op = int((op % 1) * 4)
    ops = [float.__add__, float.__sub__, float.__mul__, lambda a, b: a / (b or 1e-6)]
    val = ops[op](a,b)
    return val

target_function = lambda x: x + 1 - x*x



def fitness(candidates, args):
    fitness = []
    for cand in candidates:
        fit = 0.0

        evolved_function = CallableGraph(encoding.decode(cand), arithmetic)
        #sympy_exp = evolved_function([Symbol('x')])[0][0]
        diffs = [None] * 10
        prev_t = None
        prev_s = None
        for s in xrange(-10, 10):
            target = target_function(float(s))
            s = s / 5.
            #solution = sympy_exp.subs({'x':s})
            solution = evolved_function([s])[0][0]
            #if solution.__class__ in [NaN, NegativeInfinity, Infinity]:
            #    solution = 1e10


            fit += math.sqrt(abs(target - solution))
        fitness.append(fit)
    return fitness

def mutate_edge(v):
    return random.random()

def mutate_data(v):
    return random.randint(0,4)

def generate_data():
    return random.randint(0,4)

if __name__ == '__main__':

    prng = Random()
    prng.seed(time())

    mutator = encoding.mutator(0.1, mutate_edge=mutate_edge, mutate_data=mutate_data)
    generator = encoding.generator(random_edge=random.random, random_data=generate_data)
    ga = ec.GA(prng)

    ga.observer = [observers.screen_observer, observers.file_observer]
    ga.terminator = terminators.evaluation_termination
    ga.variator = [mutator]
    ga.selector = tournament_selection
    #ga.bounder = wrap_around(0., 1.)
    start = time()
    print "setup"
    final_pop = ga.evolve(evaluator=fitness,
                          generator=generator,
                          max_evaluations=10000,
                          num_elites=1,
                          pop_size=200,
                          mean=0.0, stdev=0.1,
                          mutation_rate=0.02,
                          tourn_size=4,
                          num_generations=1,
                          maximize=False)
    stop = time()
    stat_file.close()
    ind_file.close()

    print('***********************************')
    print('Total Execution Time: %0.5f seconds' % (stop - start))
    for ind in final_pop:
        print(str(ind))

    exps = []
    final_pop.sort(key=lambda c: c.fitness)

    #final_exps = [(create_function(c.candidate, decoder, sympy_arithmetic)([Symbol('x')]), c.fitness) for c in final_pop]
    #print final_exps
