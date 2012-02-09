from time import time
from random import Random
import ecspy

def main(prng=None):
    if prng is None:
        prng = Random()
        prng.seed(time()) 
    
    problem = ecspy.benchmarks.Ackley(2)
    ea = ecspy.swarm.PSO(prng)
    ea.terminator = ecspy.terminators.evaluation_termination
    ea.topology = ecspy.topologies.ring_topology
    final_pop = ea.evolve(generator=problem.generator,
                          evaluator=problem.evaluator, 
                          pop_size=100,
                          bounder=problem.bounder,
                          maximize=problem.maximize,
                          max_evaluations=30000, 
                          neighborhood_size=5)
        
    best = max(final_pop) 
    print('%s Example (%s) Best Solution: \n%s' % (ea.__class__.__name__, problem.__class__.__name__, str(best)))
    return ea

if __name__ == '__main__':
    main()
