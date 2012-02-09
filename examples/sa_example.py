from random import Random
from time import time
import ecspy

def main(prng=None):    
    if prng is None:
        prng = Random()
        prng.seed(time()) 
        
    problem = ecspy.benchmarks.Sphere(2)
    ea = ecspy.ec.SA(prng)
    ea.terminator = ecspy.terminators.evaluation_termination
    final_pop = ea.evolve(evaluator=problem.evaluator, 
                          generator=problem.generator, 
                          maximize=problem.maximize,
                          bounder=problem.bounder,
                          max_evaluations=30000)
    best = max(final_pop)
    print('%s Example (%s) Best Solution: \n%s' % (ea.__class__.__name__, problem.__class__.__name__, str(best)))
    return ea
            
if __name__ == '__main__':
    main()
