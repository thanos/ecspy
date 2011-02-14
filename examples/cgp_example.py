'''
Created on Jul 26, 2010

symbolic regression of a 6th order polynominal using cartesian genetic programming

'''
__author__ = 'Henrik Rudstrom'
from ecspy.variators.crossovers import n_point_crossover
from ecspy.contrib.cgp import CGPPhenotype, CGPEncoding


import ecspy
from sympy.core.symbol import Symbol
from sympy.core.numbers import RealNumber, Number


from random import Random
import random
from time import time
from ecspy import ec, terminators
import math
from ecspy.selectors import tournament_selection



#Node functions
def add(a,b):
    return a + b
def sub(a,b):
    return a - b
def mul(a,b):
    return a * b
def div(a,b):
    '''
    return numerator if denominator is 0
    '''
    return a if b == 0.0 else a / b


def get_fitness_function(target_function, constants):
    '''

    The fitness cases were 50 random values of X from the interval [-1.0, +1.0].
    These were fixed throughout the evolutionary run. The fitness of a program was
    defined as the sum over the 50 fitness cases of the sum of the absolute value of
    the error between the value returned by the program and that corresponding to the
    sixth order polynomial.
    --Miller
    '''
    sample_points = list([random.random()*2-1 for _ in xrange(50)])
    def fitness(candidates, args):
        fitness = []
         #sample_points = list([random.random()*2-1 for _ in xrange(50)])
        for cand in candidates:
            fit = 0.0
            func = CGPPhenotype(encoding, cand)
               
            for x in sample_points:
                target = target_function(x)
                
                solution = func([x]+constants)[0]
                fit += math.sqrt(abs(target - solution))

            fitness.append(fit)
        return fitness
    return fitness

def screen_observer(enc):
    def screen_observer(population, num_generations, num_evaluations, args):
        """Print the output of the EC to the screen.
        
        This function displays the results of the evolutionary computation
        to the screen. The output includes the generation number, the current
        number of evaluations, the average fitness, the maximum fitness, and 
        the full population.
        
        .. Arguments:
           population -- the population of Individuals
           num_generations -- the number of elapsed generations
           num_evaluations -- the number of candidate solution evaluations
           args -- a dictionary of keyword arguments
        
        """
        import numpy
        
        population = list(population)
        population.sort(reverse=True)
        worst_fit = population[-1].fitness
        best_fit = population[0].fitness
        med_fit = numpy.median([p.fitness for p in population])
        avg_fit = numpy.mean([p.fitness for p in population])
        std_fit = numpy.std([p.fitness for p in population], ddof=1)
        if(num_generations % 50 != 0):
            return
        print('Generation Evaluation Worst      Best       Median     Average    Std Dev   ')
        print('---------- ---------- ---------- ---------- ---------- ---------- ----------')
        print('{0:10} {1:10} {2:10} {3:10} {4:10} {5:10} {6:10}\n'.format(num_generations, num_evaluations, worst_fit, best_fit, med_fit, avg_fit, std_fit))
        print('Current Population:')
        print('----------------------------------------------------------------------------')
        for i, c in enumerate(population):
            f = CGPPhenotype(enc, c.candidate)
            exp = f([Symbol('x'), RealNumber(1.0)])
            print i, c.fitness, exp 
            
    return screen_observer   
        
def generate_initial_population(generator, n, sel, fitness_function):
    indexes = list(xrange(n))
    candidates = [generator(None, None) for _ in indexes]
    fitness = fitness_function(candidates, {})
    indexes.sort(key=lambda i: fitness[i])
    return [candidates[i] for i in indexes][:sel]
        
            
if __name__ == '__main__':
    constants = [1.]
    encoding = CGPEncoding(10, 2, 10, [add, sub, mul, div], 1)

    target = lambda x: x ** 6 - 2 * x ** 4 + x ** 2
    fitness_function = get_fitness_function(target, constants)


    mutator = encoding.mutator()
    generator = encoding.generator()
    seeds = generate_initial_population(generator, 500, 4, fitness_function)

    prng = Random()
    prng.seed(time())    
    ga = ec.ES(prng)

    ga.observer = [screen_observer(encoding)]
    ga.terminator = terminators.evaluation_termination
    ga.variator = [mutator]
    #ga.selector = tournament_selection
    start = time()
    print "setup", seeds

    
    final_pop = ga.evolve(seeds = seeds,
                          evaluator=fitness_function,
                          generator=generator,
                          max_evaluations=80000, 
                          pop_size=5,
                          mutation_rate=0.2,
                          maximize=False,
                          use_one_fifth_rule=True)
    stop = time()

    print('***********************************')
    print('Total Execution Time: %0.5f seconds' % (stop - start))
