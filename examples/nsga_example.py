from random import Random
from time import time
from ecspy import ec
from ecspy import emo
from ecspy import selectors
from ecspy import variators
from ecspy import observers
from ecspy import terminators


def generate_candidate(random, args):
    return [random.random()]

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
    final_pop = nsga.evolve(generator=generate_candidate, 
                            evaluator=evaluate_candidate, 
                            pop_size=100,
                            bounder=ec.bounder([0], [1]),
                            max_evaluations=1000)
    final_arc = nsga.archive
    
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
