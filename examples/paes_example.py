import random
import time
from ecspy import emo
from ecspy import observers
from ecspy import terminators

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
        fitness.append(emo.Pareto(args['maximize'], [x, y]))
    return fitness

def my_observer(population, num_generations, num_evaluations, args):
    print('Gens: %d   Evals: %d' % (num_generations, num_evaluations))

def main(do_plot=True, prng=None):
    if prng is None:
        prng = random.Random()
        prng.seed(time.time()) 
    paes = emo.PAES(prng)
    paes.observer = my_observer
    final_arc = paes.evolve(generator=generate_candidate, 
                            evaluator=evaluate_candidate, 
                            pop_size=1,
                            terminator=terminators.evaluation_termination, 
                            max_evaluations=1000,
                            lower_bound=0,
                            upper_bound=1,
                            max_archive_size=20,
                            num_grid_divisions=1)
    
    front = []
    for f in final_arc:
        front.append(f.fitness)
    
    if do_plot:
        import pylab
        x = []
        y = []
        for f in front:
            print(f)
            x.append(f[0])
            y.append(f[1])
        pylab.scatter(x, y, color='b')
        #pylab.show()
        pylab.savefig('paes-front.pdf', format='pdf')
    return paes

if __name__ == '__main__':
    main()