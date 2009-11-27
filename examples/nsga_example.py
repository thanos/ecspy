import random
import time
from ecspy import emo
from ecspy import selectors
from ecspy import variators
from ecspy import observers
from ecspy import terminators
import pylab


def generate_candidate(random, args):
    try:
        lower_bound = args['lower_bound']
    except KeyError:
        lower_bound = 0
    try:
        upper_bound = args['upper_bound']
    except KeyError:
        upper_bound = 1
        
    return [random.random() * (upper_bound - lower_bound) + lower_bound]

def evaluate_candidate(candidates, args):
    fitness = []
    for cs in candidates:
        x = cs[0]**2
        y = (cs[0]-1)**2 
        fitness.append(emo.Pareto([x, y]))
    return fitness

def my_observer(population, num_generations, num_evaluations, args):
    try:
        archive = args['_archive']
    except KeyError:
        archive = []
    
    x = []
    y = []
    print('----------------------------')
    print('Gens: %d   Evals: %d' % (num_generations, num_evaluations))
    print('-----------')
    print('Population:')
    for p in population:
        print(p)
    print('-----------')
    print('Archive:')
    for a in archive:
        print(a)
    print('-----------')
    
   
   
prng = random.Random()
prng.seed(time.time())

nsga = emo.NSGA2(prng)
nsga.variator = variators.gaussian_mutation
nsga.observer = my_observer
final_pop = nsga.evolve(generator=generate_candidate, 
                        evaluator=evaluate_candidate, 
                        pop_size=100,
                        terminator=terminators.evaluation_termination, 
                        max_evaluations=1000,
                        lower_bound=0,
                        upper_bound=1)

print('*******************************')
x = []
y = []
for p in final_pop:
    print(p)
    x.append(p.fitness[0])
    y.append(p.fitness[1])
pylab.scatter(x, y, color='b')
#pylab.show()
pylab.savefig('nsga2-front.pdf', format='pdf')
    
    