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

    
file = open('es_observer.txt', 'w')
rand = Random()
rand.seed(int(time()))
es = ec.ES(rand)
es.observer = [observers.screen_observer, observers.file_observer]
start = time()
final_pop = es.evolve(evaluator=evaluate_real, 
                      generator=generate_real, 
                      terminator=[terminators.fun_eval_termination, terminators.diversity_termination],                                
                      pop_size=10, 
                      max_fun_evals=200,
                      mutation_rate=0.2,
                      use_one_fifth_rule=True,
                      observer_file=file)
stop = time()
    
print('***********************************')
print('Total Execution Time: %0.5f seconds' % (stop - start))
for ind in final_pop:
    print(str(ind))
        
