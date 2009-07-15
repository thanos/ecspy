from random import Random
from time import time
from ecspy import ec
from ecspy import terminators
from ecspy import selectors
from ecspy import replacers
from ecspy import variators
from ecspy import observers


def generate_real(random, args):
    try:
        size = args['chrom_size']
    except KeyError:
        size = 4
    return [random.random() for i in xrange(size)]

def evaluate_real(candidates, args):
    fitness = []
    for cand in candidates:
        num = sum(cand)
        fitness.append(num)
    return fitness

    
rand = Random()
rand.seed(int(time()))
evocomp = ec.EvolutionaryComputation(rand)
evocomp.selector = selectors.tournament_selection
evocomp.variator = [variators.uniform_crossover, variators.gaussian_mutation]
evocomp.replacer = replacers.steady_state_replacement
evocomp.observer = observers.screen_observer

start = time()
final_pop = evocomp.evolve(evaluator=evaluate_real, 
                           generator=generate_real, 
                           terminator=terminators.num_gen_termination,
                           pop_size=100, 
                           tourn_size=7,
                           num_selected=2, 
                           max_generations=100,
                           mutation_rate=0.2)
stop = time()

print('***********************************')
print('Total Execution Time: %0.5f seconds' % (stop - start))
for ind in final_pop:
    print(str(ind))
