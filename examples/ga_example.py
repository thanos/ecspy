from random import Random
from time import time
import ecspy

def main(prng=None): 
    if prng is None:
        prng = Random()
        prng.seed(time()) 
    
    problem = ecspy.benchmarks.Binary(ecspy.benchmarks.Schwefel(2), dimension_bits=30)
    ea = ecspy.ec.GA(prng)
    #ea.observer = ecspy.observers.stats_observer
    ea.terminator = ecspy.terminators.evaluation_termination
    final_pop = ea.evolve(generator=problem.generator,
                          evaluator=problem.evaluator,
                          pop_size=100,
                          maximize=problem.maximize,
                          bounder=problem.bounder,
                          max_evaluations=30000, 
                          num_elites=1)
                          
    # Note that the Scwefel function is a minimization problem,
    # but the max of the final population is the "best" individual, 
    # which in this case means the individual with the smallest fitness.
    best = max(final_pop)
    print('%s Example (%s) Best Solution: \n%s' % (ea.__class__.__name__, problem.__class__.__name__, str(best)))
    return ea
            
if __name__ == '__main__':
    main()
