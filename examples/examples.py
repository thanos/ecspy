from random import Random
from time import time
from ecspy import ec
from ecspy import terminators
from ecspy import selectors
from ecspy import replacers
from ecspy import variators
from ecspy import observers


def generate(random, args):
    try:
        bits = args['num_bits']
    except KeyError:
        bits = 8
    return [random.choice([0, 1]) for i in xrange(bits)]
        
def evaluate(candidates, args):
    fitness = []
    try:
        base = args['base']
    except KeyError:
        base = 2
    for cand in candidates:
        num = 0
        exp = len(cand) - 1
        for c in cand:
            num += c * (base ** exp)
            exp -= 1
        fitness.append(num)
    return fitness
    

    
if __name__ == '__main__': 
    run_times = []
    for i in xrange(1):
        rand = Random()
        rand.seed(1324567)
        ga = ec.GA(rand)
        ga.observer = observers.screen_observer
#        ga.variator = [variators.uniform_crossover, variators.bit_flip_mutation]
        start = time()
        final_pop = ga.evolve(evaluator=evaluate,
                              generator=generate,
                              terminator=terminators.fun_eval_termination,
                              max_fun_evals=100,
                              num_elites=1,
                              pop_size=10,
                              num_bits=10)
        stop = time()
        
        # es = ec.ES(rand)
        # es.observer = observers.screen_observer
        # start = time()
        # final_pop = es.evolve(evaluator=evaluate, 
                                  # generator=generate, 
                                  # terminator=[terminators.fun_eval_termination], #, terminators.diversity_termination, terminators.fun_eval_termination, terminators.num_gen_termination],
                                  # pop_size=10, 
                                  # max_fun_evals=50,
                                  # max_generations=5,
                                  # mutation_rate=0.2,
                                  # use_one_fifth_rule=True,
                                  # num_bits=10)
        # stop = time()
        
        # engine = ec.EvolutionEngine(rand)
        # engine.selector = selectors.roulette_wheel_selection
        # engine.variator = [variators.uniform_crossover, variators.bit_flip_mutation]
        # engine.replacer = replacers.comma_replacement
        # engine.observer = observers.screen_observer
        
        # start = time()
        # final_pop = engine.evolve(evaluator=evaluate, 
                                  # generator=generate, 
                                  # terminator=[terminators.fun_eval_termination], #, terminators.diversity_termination, terminators.fun_eval_termination, terminators.num_gen_termination],
                                  # pop_size=10, 
                                  # num_selected=10, 
                                  # num_elites=1, 
                                  # max_fun_evals=50,
                                  # max_generations=5,
                                  # mutation_rate=0.5,
                                  # use_one_fifth_rule=True,
                                  # num_bits=10)
        # stop = time()
        
        print('***********************************')
        print('Total Execution Time: %0.5f seconds' % (stop - start))
        for ind in final_pop:
            print(str(ind))
        
