from random import Random
from time import time
import ecspy

def my_observer(population, num_generations, num_evaluations, args):
    best = max(pop)
    print("%6d -- %f : %s" % (num_generations, best.fitness, str(best.candidate)))

if __name__ == '__main__':
    prng = Random()
    prng.seed(time()) 
    
    problem = ecspy.benchmarks.Rosenbrock(2)
    ea = ecspy.ec.ES(prng)
    ea.observer = my_observer
    ea.terminator = ecspy.terminators.evaluation_termination
    final_pop = ea.evolve(generator=problem.generator, 
                          evaluator=problem.evaluator, 
                          pop_size=100, 
                          bounder=problem.bounder,
                          maximize=problem.maximize,
                          max_evaluations=30000,
                          mutation_rate=0.2,
                          use_one_fifth_rule=True)
    best = max(final_pop)
    print('%s Example (%s) Best Solution: \n%s' % (ea.__class__.__name__, problem.__class__.__name__, str(best)))
