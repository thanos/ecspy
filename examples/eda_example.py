from random import Random
from time import time
import ecspy

def main(prng=None):
    if prng is None:
        prng = Random()
        prng.seed(time()) 
    
    problem = ecspy.benchmarks.Rastrigin(2)
    ea = ecspy.ec.EDA(prng)
    #ea.observer = ecspy.observers.stats_observer
    ea.terminator = ecspy.terminators.evaluation_termination
    final_pop = ea.evolve(evaluator=problem.evaluator, 
                          generator=problem.generator, 
                          pop_size=1000, 
                          bounder=problem.bounder,
                          maximize=problem.maximize,
                          max_evaluations=30000,
                          num_selected=500,
                          num_offspring=1000,
                          num_elites=1)
        
    best = max(final_pop) 
    print('%s Example (%s) Best Solution: \n%s' % (ea.__class__.__name__, problem.__class__.__name__, str(best)))
    return ea
            
if __name__ == '__main__':
    main()
