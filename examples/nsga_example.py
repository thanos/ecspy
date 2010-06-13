from random import Random
from time import time
from ecspy import emo
from ecspy import selectors
from ecspy import variators
from ecspy import observers
from ecspy import terminators


def generate_candidate(random, args):
    lower_bound = args.get('lower_bound', 0)
    upper_bound = args.get('upper_bound', 1)
    return [random.random() * (upper_bound - lower_bound) + lower_bound]

def evaluate_candidate(candidates, args):
    fitness = []
    for cs in candidates:
        x = cs[0]**2
        y = (cs[0]-1)**2 
        fitness.append(emo.Pareto([x, y]))
    return fitness

  
def main(do_plot=True, prng=None):
    if prng is None:
        prng = Random()
        prng.seed(time()) 

    nsga = emo.NSGA2(prng)
    nsga.variator = [variators.uniform_crossover, variators.gaussian_mutation]
    nsga.observer = observers.archive_observer
    nsga.terminator = terminators.evaluation_termination
    final_arc = nsga.evolve(generator=generate_candidate, 
                            evaluator=evaluate_candidate, 
                            pop_size=100,
                            max_evaluations=1000,
                            lower_bound=0.,
                            upper_bound=1.)
    
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
