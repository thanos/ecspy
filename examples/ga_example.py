from random import Random
from time import time
from ecspy import ec
from ecspy import terminators
from ecspy import observers


def generate_binary(random, args):
    bits = args.get('num_bits', 8)
    return [random.choice([0, 1]) for i in xrange(bits)]
        
def evaluate_binary(candidates, args):
    fitness = []
    base = args.get('base', 2)
    for cand in candidates:
        num = 0
        exp = len(cand) - 1
        for c in cand:
            num += c * (base ** exp)
            exp -= 1
        fitness.append(num)
    return fitness

def main(prng=None): 
    stat_file = open('ga_statistics.csv', 'w')
    ind_file = open('ga_individuals.csv', 'w')

    if prng is None:
        prng = Random()
        prng.seed(time()) 
    
    ga = ec.GA(prng)
    ga.observer = [observers.screen_observer, observers.file_observer]
    ga.terminator = terminators.evaluation_termination
    start = time()
    final_pop = ga.evolve(evaluator=evaluate_binary,
                          generator=generate_binary,
                          max_evaluations=1000, 
                          statistics_file=stat_file,
                          individuals_file=ind_file,
                          num_elites=1,
                          pop_size=100,
                          num_bits=10)
    stop = time()
    stat_file.close()
    ind_file.close()
            
    print('***********************************')
    print('Total Execution Time: %0.5f seconds' % (stop - start))
    for ind in final_pop:
        print(str(ind))
    return ga
            
if __name__ == '__main__':
    main()