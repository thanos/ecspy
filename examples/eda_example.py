from random import Random
from time import time
from ecspy import ec
from ecspy import terminators
from ecspy import observers


def generate_real(random, args):
    return [random.random() for i in xrange(4)]

def evaluate_real(candidates, args):
    fitness = []
    for cand in candidates:
        num = sum(cand)
        fitness.append(num)
    return fitness


def main(prng=None):
    if prng is None:
        prng = Random()
        prng.seed(time()) 
    
    eda = ec.EDA(prng)
    eda.terminator = terminators.evaluation_termination
    eda.observer = observers.screen_observer
    start = time()
    final_pop = eda.evolve(evaluator=evaluate_real, 
                           generator=generate_real, 
                           pop_size=10, 
                           bounder=ec.bounder(0, 1),
                           max_evaluations=5000,
                           num_selected=2,
                           num_elites=1)
    stop = time()
        
    print('***********************************')
    print('Total Execution Time: %0.5f seconds' % (stop - start))
    for ind in final_pop:
        print(str(ind))
    return eda
            
if __name__ == '__main__':
    main()