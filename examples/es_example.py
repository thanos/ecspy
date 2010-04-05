from random import Random
from time import time
from ecspy import ec
from ecspy import terminators
from ecspy import observers
from ecspy import evaluators


def generate_real(random, args):
    try:
        size = args['chrom_size']
    except KeyError:
        size = 4
    return [random.random() for i in xrange(size)]

def my_serial_evaluator(candidate):
    num = sum(candidate)
    return num

def main():    
    file = open('es_observer.txt', 'w')
    rand = Random()
    rand.seed(int(time()))
    es = ec.ES(rand)
    es.observer = [observers.screen_observer, observers.file_observer]
    start = time()
    final_pop = es.evolve(evaluator=evaluators.parallel_evaluation, 
                          generator=generate_real, 
                          pop_size=100, 
                          terminator=[terminators.evaluation_termination, terminators.diversity_termination],
                          serial_evaluator=my_serial_evaluator,
                          max_evaluations=2000,
                          mutation_rate=0.2,
                          use_one_fifth_rule=True,
                          observer_file=file)
    stop = time()
        
    print('***********************************')
    print('Total Execution Time: %0.5f seconds' % (stop - start))
    for ind in final_pop:
        print(str(ind))
    return es
            
if __name__ == '__main__':
    main()