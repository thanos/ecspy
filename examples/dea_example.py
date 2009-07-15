from random import Random
from time import time
from ecspy import ec
from ecspy import terminators
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
dea = ec.DEA(rand)
dea.observer = observers.screen_observer
start = time()
final_pop = dea.evolve(evaluator=evaluate_real, 
                       generator=generate_real, 
                       terminator=terminators.fun_eval_termination,
                       pop_size=10, 
                       max_fun_evals=5000)
stop = time()
    
print('***********************************')
print('Total Execution Time: %0.5f seconds' % (stop - start))
for ind in final_pop:
    print(str(ind))
        