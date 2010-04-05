from time import time
from random import Random
from ecspy import observers
from ecspy import terminators
from ecspy.swarm import PSO



def generate_real(random, args):
    try:
        size = args['particle_size']
    except KeyError:
        size = 4
    return [random.random() for i in xrange(size)]

def evaluate_real(candidates, args):
    fitness = []
    for cand in candidates:
        num = sum(cand)
        fitness.append(num)
    return fitness

def main(prng=None):
    if prng is None:
        prng = Random()
        prng.seed(time.time()) 
    
    pso = PSO(prng)
    pso.observer = observers.screen_observer
    
    start = time()
    final_pop = pso.swarm(evaluator=evaluate_real, 
                          generator=generate_real,
                          pop_size=20,
                          terminator=terminators.evaluation_termination,
                          max_evaluations=200,
                          topology='ring',
                          neighborhood_size=5,
                          use_constriction_coefficient=True,
                          particle_size=6)
    stop = time()
        
    print('***********************************')
    print('Total Execution Time: %0.5f seconds' % (stop - start))
    for ind in final_pop:
        print(str(ind))

if __name__ == '__main__':
    main()