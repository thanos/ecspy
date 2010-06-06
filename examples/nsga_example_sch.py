from random import Random
from time import time
from ecspy import emo, ec
from ecspy import selectors
from ecspy import variators
from ecspy import observers
from ecspy import terminators

from ecspy.contrib.utils import round_fitness

def generate_candidate(random, args):
    lower_bound = args.get('lower_bound', 0)
    upper_bound = args.get('upper_bound', 1)
    return [random.random() * (upper_bound - lower_bound) + lower_bound]

def evaluate_sch(candidates, args):
    fitness = []
    for cs in candidates:
        x = cs[0]**2
        y = (cs[0]-2)**2 
        fitness.append(emo.Pareto([x, y]))
    return fitness

def converged_sch(population, num_generations, num_evaluations, args):
    if num_generations < 20:
        return False
    pop = round_fitness(population, 1)
    return [0.0, 4.0] in pop

def my_observer(population, num_generations, num_evaluations, args):
    archive = args.get('_archive', [])   
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
        prng = Random()
        prng.seed(time()) 

    nsga = emo.NSGA2(prng)
    nsga.variator = [variators.gaussian_mutation, variators.blend_crossover]
    nsga.observer = my_observer
    nsga.terminator = [terminators.evaluation_termination, converged_sch]
    final_arc = nsga.evolve(maximize=False,
                            generator=generate_candidate, 
                            evaluator=evaluate_sch, 
                            pop_size=100,
                            max_evaluations=1e8,
                            lower_bound=-1000.,
                            upper_bound= 1000.,
                            #mut_range=1.
                            )
    
    print('*******************************')
    if do_plot:
        import pylab
        x = []
        y = []
        for f in final_arc[1:]:
            print(f)
            # filter out left over values in the archive...
            a,b = abs(f.fitness[0]), abs(f.fitness[1])
            if a>4 or b>4:
                continue 
            x.append(f.fitness[0])
            y.append(f.fitness[1])
        pylab.scatter(x, y, color='b')
        pylab.show()
        #pylab.savefig('nsga2-front.pdf', format='pdf')
    return nsga
        
if __name__ == '__main__':
    main()    
