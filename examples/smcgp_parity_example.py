'''
Created on Dec 13, 2010

@author: Henrik Rudstrom



`we evolve for two input bits. When a successful solution is found,
the fitness function requires that the program produces a two bit
circuit, followed by a three bit circuit. Then when a genotype has
been found that solves the two bit problem and on iteration solves
the three bit problem, the fitness function changes so that now in
addition to the previous behaviour the genotype, when iterated twice,
produces a phenotype that solves the four-bit problem. The process
continues in this way until we obtain a phenotype that correctly
implements the required function with 20 inputs. We refer to the
application of each parity or adder as a test case.
Fitness is computed as the number of correctly predicted bits over all
test cases. If the candidate solution fails to find a totally correct
solution for a given input size, it is not tested on other input sizes.
We evolve for 19 test cases (2 inputs to 20 inputs).`
-- "Developments in Cartesian Genetic Programming: self-modifying CGP",
   Harding Miller Banzhaf 2010


'''

import random
from random import Random
import time
#import pyximport;
#pyximport.install(pyximport, pyimport, build_dir, build_in_temp, setup_args, reload_support)
from ecspy import ec, terminators
from ecspy.contrib.smcgp.encoding import SMCGPEncoding
from ecspy.contrib.smcgp.phenotype import io_functions, SMCGPPhenotype
from ecspy.contrib.smcgp import modification_functions

def wrap(name, func):
    def f(g,a,b):
        return func(g,a,b)
    f.__name__ = name
    return f

user_functions = [
    wrap("BAND", lambda g,a,b: a and b), 
    wrap("BOR", lambda g,a,b: a or b),
    wrap("BNAND", lambda g,a,b: not  (a and b)),
    wrap("BXOR",  lambda g,a,b: (a and not  b) or (b and not  a)), 
    wrap("BNOR",  lambda g,a,b: not  (a or b)),
    wrap("BNOT", lambda g,a,b: not a),
    wrap("BIAND", lambda g,a,b: (not  a) and b), 
    wrap("BF0", lambda g,a,b: False),
    wrap("BF1", lambda g,a,b: (a and b)), 
    wrap("BF2", lambda g,a,b: a and (not  b)), 
    wrap("BF3", lambda g,a,b: (a and (not b))or(a and b)), 
    wrap("BF4", lambda g,a,b: (not  a) and b),
    wrap("BF5", lambda g,a,b: ((not a) and b) or (a and b)), 
    wrap("BF6", lambda g,a,b: ((not  a) and b) or (a and (not  b))), 
    wrap("BF7", lambda g,a,b: ((not  a) and b) or (a and not (b)) or (a and b)), 
    wrap("BF8", lambda g,a,b: ((not  a) and (not  b))),
    wrap("BF9", lambda g,a,b: ((not  a) and (not  b)) or (a and b)), 
    wrap("BF10", lambda g,a,b: ((not  a) and (not  b)) or (a and not  (b))), 
    wrap("BF11", lambda g,a,b: ((not a) and (not b) or a and (not b) or a and b)), 
    wrap("BF12", lambda g,a,b: ((not  a) and (not  b) or (not  a) and b)),
    wrap("BF13", lambda g,a,b: ((not a) and (not b) or (not a) and b or a and b)), 
    wrap("BF14", lambda g,a,b: ((not a) and (not b) or (not a) and b or a and (not b))), 
    wrap("BF15", lambda g,a,b: ((not a) and (not b) or (not a) and b or a and (not b) or a and b))
]

enc = SMCGPEncoding(length=25, max_arity=2, levelsback=15, min_outputs=1)
enc.set_functions(io_functions+user_functions+modification_functions.all_functions)


def int2bin(n, count=24):
    """returns the binary of integer n, using count number of digits"""
    return [(n >> y) & 1 for y in range(count-1, -1, -1)]

def get_test_cases(max_bits):
    return [[int2bin(i, bits) for i in xrange(2**bits)] for bits in xrange(2,max_bits+2)]

def get_targets(all_cases):
    return [[not sum(case) % 2 for case in cases] for cases in all_cases]

def select_test_cases(all_cases, all_targets, max_cases=100):
    cases = []
    targets = []
    for case, target in zip(all_cases, all_targets):
        if len(case) < max_cases:
            cases.append(case)
            targets.append(target)
        else:
            sel = list(xrange(len(case)))
            random.shuffle(sel)
            cases.append([case[s] for s in sel[:max_cases]])
            targets.append([target[s] for s in sel[:max_cases]])
    return cases, targets   


def test_test_cases():
    ac = get_test_cases(10)
    tac = get_targets(ac)
    lac = [len(c) for c in ac]
    print lac
    assert lac == [4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
    sac,stac = select_test_cases(ac, tac, 100)
    lsac = [len(c) for c in sac]
    print lsac
    assert lsac == [4, 8, 16, 32, 64, 100, 100, 100, 100, 100]
    for c,t in zip(sac, stac):
        assert len(c) % 2 == 0

test_test_cases()

all_cases = get_test_cases(10)
all_targets = get_targets(all_cases)
def fitness(candidates, args):
    sel_cases, sel_targets = select_test_cases(all_cases, all_targets, 100)
    fitness = []
    for cand in candidates:
        fit = 0
        func = SMCGPPhenotype(enc, cand)
        iii=0
        for cases, targets in zip(sel_cases, sel_targets):
            
            iii += 1
            func = func.get_modified()
            if not func.is_valid():
                break
            case_fit = 0
            for case, target in zip(cases, targets):
                solution = func(case)[0]
                if solution == target:
                    #print solution, target, case
                    case_fit += 1
            fit += case_fit
            if case_fit != len(cases):
                break
        #print "cases", iii
        fitness.append(fit)
    return fitness

            
            
def screen_observer(enc):
    def screen_observer(population, num_generations, num_evaluations, args):
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
        print('Current Population: (id,fitness,todo,2 bit solution)')
        print('----------------------------------------------------------------------------')
        for i, c in enumerate(population):
            #f = CGPPhenotype(enc, c.candidate)
            #exp = f([Symbol('x'), RealNumber(1.0)])
            pass
        for i, c in enumerate(population):
            #f = CGPPhenotype(enc, c.candidate)
            #exp = f([Symbol('x'), RealNumber(1.0)])
            phe = SMCGPPhenotype(enc, c.candidate)
            #print i, c.fitness, phe.todo_list, phe
            print i, c.fitness, [p.__name__ for p in phe.todo_list], phe.get_modified()
            
    return screen_observer        


if __name__ == '__main__':
    
    mutator = enc.mutator()
    generator = enc.generator()
    #seeds = generate_initial_population(generator, 500, 4, fitness_function)

    prng = Random()
    prng.seed(time.time())
    ga = ec.ES(prng)

    ga.observer = [screen_observer(enc)]
    ga.terminator = terminators.evaluation_termination
    ga.variator = [mutator]
    #ga.selector = tournament_selection
    start = time.time()
    #print "setup", seeds


    final_pop = ga.evolve(#seeds = seeds,
                          evaluator=fitness,
                          generator=generator,
                          max_evaluations=100000000,
                          pop_size=5,
                          mutation_rate=0.066,
                          maximize=True,
                          use_one_fifth_rule=True)
    stop = time.time()

    print('***********************************')
    print('Total Execution Time: %0.5f seconds' % (stop - start))



