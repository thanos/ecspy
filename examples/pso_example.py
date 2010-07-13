from time import time
from random import Random
from ecspy import observers
from ecspy import terminators
from ecspy import topologies
from ecspy.swarm import PSO
from ecspy import ec



def generate_real(random, args):
    size = args.get('particle_size', 4)
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
        prng.seed(time()) 
    
    pso = PSO(prng)
    pso.observer = observers.screen_observer
    pso.terminator = terminators.evaluation_termination
    pso.topology = topologies.ring_topology
    
    start = time()
    final_pop = pso.evolve(evaluator=evaluate_real, 
                          generator=generate_real,
                          pop_size=20,
                          maximize=True,
                          bounder=ec.bounder(0, 1),
                          max_evaluations=400, 
                          neighborhood_size=5,
                          particle_size=6)
    stop = time()
        
    final_pop.sort(reverse=True)
    print('***********************************')
    print('Total Execution Time: %0.5f seconds' % (stop - start))
    for ind in final_pop:
        print(str(ind))
    return pso

if __name__ == '__main__':
    main()