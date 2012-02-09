from random import Random
from time import time
import ecspy

def my_archiver(random, population, archive, args):
    worst_in_pop = min(population)
    if len(archive) > 0:
        worst_in_arc = min(archive)
        if worst_in_pop < worst_in_arc:
            return [worst_in_pop]
        else:
            return archive
    else:
        return [worst_in_pop]

if __name__ == '__main__':
    prng = Random()
    prng.seed(time()) 
    
    problem = ecspy.benchmarks.Rosenbrock(2)
    ea = ecspy.ec.ES(prng)
    ea.observer = [ecspy.observers.stats_observer, ecspy.observers.archive_observer]
    ea.archiver = my_archiver
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
