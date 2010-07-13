from random import Random
from time import time
from ecspy import ec
from ecspy import terminators
from ecspy import observers
from ecspy import evaluators


def generate_real(random, args):
    return [random.random() for i in xrange(4)]

def evaluate_real(candidates, args):
    fitness = []
    for candidate in candidates:
        num = sum(candidate)
        fitness.append(num)
    return fitness

def main(prng=None):    
    if prng is None:
        prng = Random()
        prng.seed(time()) 
    sa = ec.SA(prng)
    sa.observer = observers.screen_observer
    sa.terminator = terminators.evaluation_termination
    start = time()
    final_pop = sa.evolve(evaluator=evaluate_real, 
                          generator=generate_real, 
                          pop_size=10, 
                          maximize=False,
                          bounder=ec.bounder([0] * 4, [1] * 4),
                          max_evaluations=400)
    stop = time()
        
    print('***********************************')
    print('Total Execution Time: %0.5f seconds' % (stop - start))
    for ind in final_pop:
        print(str(ind))
    return sa
            
if __name__ == '__main__':
    main()