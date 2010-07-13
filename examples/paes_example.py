from random import Random
from time import time
from ecspy import emo
from ecspy import observers
from ecspy import terminators
from ecspy import ec

def generate_candidate(random, args):
    return [random.random()]

def evaluate_candidate(candidates, args):
    fitness = []
    for cs in candidates:
        x = cs[0]**2
        y = (cs[0]-1)**2
        fitness.append(emo.Pareto([x, y]))
    return fitness

def my_observer(population, num_generations, num_evaluations, args):
    print('Gens: %d   Evals: %d' % (num_generations, num_evaluations))

def main(do_plot=True, prng=None):
    if prng is None:
        prng = Random()
        prng.seed(time()) 
    paes = emo.PAES(prng)
    paes.observer = my_observer
    paes.terminator = terminators.evaluation_termination
    final_pop = paes.evolve(generator=generate_candidate, 
                            evaluator=evaluate_candidate, 
                            pop_size=1,
                            bounder=ec.bounder([0], [1]),
                            max_evaluations=1000,
                            max_archive_size=20,
                            num_grid_divisions=2)
    
    final_arc = paes.archive
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
