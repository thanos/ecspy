from random import Random
from time import time
from ecspy import ec
from ecspy import terminators
from ecspy import observers


def generate_binary(random, args):
    try:
        bits = args['num_bits']
    except KeyError:
        bits = 8
    return [random.choice([0, 1]) for i in xrange(bits)]
        
def evaluate_binary(candidates, args):
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

    
file = open('ga_observer.txt', 'w')
rand = Random()
rand.seed(int(time()))
ga = ec.GA(rand)
ga.observer = [observers.screen_observer, observers.file_observer]
start = time()
final_pop = ga.evolve(evaluator=evaluate_binary,
                      generator=generate_binary,
                      terminator=terminators.fun_eval_termination,
                      max_fun_evals=1000,
                      num_elites=1,
                      pop_size=100,
                      num_bits=10,
                      observer_file=file)
stop = time()
        
print('***********************************')
print('Total Execution Time: %0.5f seconds' % (stop - start))
for ind in final_pop:
    print(str(ind))
        
