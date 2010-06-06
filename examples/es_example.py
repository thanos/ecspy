from random import Random
from time import time
from ecspy import ec
from ecspy import terminators
from ecspy import observers
from ecspy import evaluators


def generate_real(random, args):
    size = args.get('chrom_size', 4)
    return [random.random() for i in xrange(size)]

def my_serial_evaluator(candidate):
    num = sum(candidate)
    return num

def main(prng=None):    
    if prng is None:
        prng = Random()
        prng.seed(time()) 
    es = ec.ES(prng)
    es.observer = observers.screen_observer
    es.terminator = [terminators.evaluation_termination, terminators.diversity_termination]
    start = time()
    final_pop = es.evolve(evaluator=evaluators.parallel_evaluation, 
                          generator=generate_real, 
                          pop_size=100, 
                          serial_evaluator=my_serial_evaluator,
                          max_evaluations=2000,
                          mutation_rate=0.2,
                          use_one_fifth_rule=True)
    stop = time()
        
    print('***********************************')
    print('Total Execution Time: %0.5f seconds' % (stop - start))
    for ind in final_pop:
        print(str(ind))
    return es
            
if __name__ == '__main__':
    main()