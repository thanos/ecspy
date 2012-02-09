from random import Random
from time import time
import ecspy

def main(prng=None):
    if prng is None:
        prng = Random()
        prng.seed(time()) 
    
    problem = ecspy.benchmarks.Ackley(2)
    ea = ecspy.ec.EvolutionaryComputation(prng)
    ea.selector = ecspy.selectors.tournament_selection
    ea.variator = [ecspy.variators.uniform_crossover, ecspy.variators.gaussian_mutation]
    ea.replacer = ecspy.replacers.steady_state_replacement
    ea.terminator = ecspy.terminators.generation_termination
    final_pop = ea.evolve(generator=problem.generator,
                          evaluator=problem.evaluator,
                          pop_size=100, 
                          bounder=problem.bounder,
                          maximize=problem.maximize,
                          tourn_size=7,
                          num_selected=2, 
                          max_generations=300,
                          mutation_rate=0.2)
                          
    best = max(final_pop) 
    print('%s Example (%s) Best Solution: \n%s' % (ea.__class__.__name__, problem.__class__.__name__, str(best)))
    return ea

if __name__ == '__main__':
    main()
