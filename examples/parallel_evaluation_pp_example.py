from random import Random
from time import time
import ecspy
import math

# Define an additional "necessary" function for the evaluator
# to see how it must be handled when using pp.
def my_squaring_function(x):
    return x**2

def generate_rastrigin(random, args):
    size = args.get('num_inputs', 10)
    return [random.uniform(-5.12, 5.12) for i in xrange(size)]

def evaluate_rastrigin(candidates, args):
    fitness = []
    for cs in candidates:
        fit = 10 * len(cs) + sum([(my_squaring_function(x - 1) - 10 * math.cos(2 * math.pi * (x - 1))) for x in cs])
        fitness.append(fit)
    return fitness
    
def main(prng=None):    
    if prng is None:
        prng = Random()
        prng.seed(time()) 
        
    ea = ecspy.ec.ES(prng)
    ea.observer = ecspy.observers.screen_observer 
    ea.terminator = ecspy.terminators.evaluation_termination
    final_pop = ea.evolve(generator=generate_rastrigin, 
                          evaluator=ecspy.evaluators.parallel_evaluation_pp,
                          pp_evaluator=evaluate_rastrigin, 
                          pp_dependencies=(my_squaring_function,),
                          pp_modules=("math",),
                          pop_size=8, 
                          bounder=ecspy.ec.Bounder(-5.12, 5.12),
                          maximize=False,
                          max_evaluations=256,
                          mutation_rate=0.2,
                          use_one_fifth_rule=True,
                          num_inputs=3)
    best = max(final_pop) 
    print('%s Example (%s) Best Solution: \n%s' % (ea.__class__.__name__, "Rastrigin", str(best)))
    return ea
            
if __name__ == '__main__':
    main()