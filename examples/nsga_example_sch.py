import random
import time
from ecspy import emo
from ecspy import selectors
from ecspy import variators
from ecspy import observers
from ecspy import terminators

from ecspy.contrib.utils import round_fitness

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

def evaluate_sch(candidates, args):
    fitness = []
    for cs in candidates:
        x = cs[0]**2
        y = (cs[0]-2)**2 
        fitness.append(emo.Pareto([x, y]))
    return fitness

def converged_sch(population, num_generations, num_evaluations, args):
    pop = round_fitness(population, 1)
    return [0.0, 2.0] in pop

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
    
   
def main(do_plot=True, prng=None):
    if prng is None:
        prng = random.Random()
        prng.seed(time.time()) 

    nsga = emo.NSGA2(prng)
    nsga.variator = [variators.n_point_crossover, variators.gaussian_mutation]
    nsga.observer = my_observer
    final_arc = nsga.evolve(maximize=False,
                            generator=generate_candidate, 
                            evaluator=evaluate_sch, 
                            pop_size=100,
                            terminator=[terminators.evaluation_termination,converged_sch], 
                            max_evaluations=1e8,
                            lower_bound=-10e3,
                            upper_bound= 10e3
                            )
    
    print('*******************************')
    if do_plot:
        import pylab
        x = []
        y = []
        for f in final_arc:
            print(f)
            x.append(f.fitness[0])
            y.append(f.fitness[1])
        pylab.scatter(x, y, color='b')
        #pylab.show()
        pylab.savefig('nsga2-front.pdf', format='pdf')
    return nsga
        
if __name__ == '__main__':
    main()    
