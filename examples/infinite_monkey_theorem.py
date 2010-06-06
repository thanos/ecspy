from random import Random
from time import time
from ecspy import ec
from ecspy import terminators, observers, replacers, selectors, variators, archivers

#sentence = """
#Methinks it is like a weasel.
#It is backed like a weasel.
#Or like a whale?
#Very like a whale
#"""

sentence = """
'Just living is not enough,' said the butterfly,
'one must have sunshine, freedom, and a little flower.'
"""

ddd = map(ord, sentence)
max_ord = max(ddd)
min_ord = min(ddd)
numeric_sentence = map(ord, sentence)

def evaluation_termination(population, num_generations, num_evaluations, args):
    if any([i.fitness==0 for i in population]):
        return  True
    return False

def observer(population, num_generations, num_evaluations, args):
    '''
    '''
    if args['_num_generations']%100 == 0:
        best_fit = population[0].candidate
        print '*'*20
        print  ''.join(map(chr, best_fit))
        print 'fitnesses:',
        print 'n archive:', len(args['_archive'])
        print 'n population:', len(args['_population'])
        print 'n evals:', args['_num_evaluations']
    
def generate_sentence(random, args):
    s = [random.randint(0,max_ord) for i in sentence]
    return s 
    
def evaluate_sentence(candidates, args):
    fitness = []
    for cand in candidates:
        fitt = sum([abs(a-b) for a,b in zip(cand, numeric_sentence)])
        fitness.append(fitt)
    return fitness

def gaussian_mutation(random, candidates, args):
    """Return the mutants created by Gaussian mutation on the candidates.

    This function assumes that the candidate solutions are indexable
    and numeric. It performs Gaussian mutation.

    .. Arguments:
       random -- the random number generator object
       candidates -- the candidate solutions
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    - *mutation_rate* -- the rate at which mutation is performed (default 0.1)
    - *mutation_range* -- the variance used in the Gaussian function 
      (default 1.0)
    - *lower_bound* -- the lower bounds of the chromosome elements (default 0)
    - *upper_bound* -- the upper bounds of the chromosome elements (default 1)
    
    The lower and upper bounds can either be single values, which will
    be applied to all elements of a chromosome, or lists of values of 
    the same length as the chromosome.
    
    """
    mut_rate = args.setdefault('mutation_rate', 0.1)
    mut_range = args.setdefault('mutation_range', 1.0)
    lower_bound = args.setdefault('lower_bound', 0)
    upper_bound = args.setdefault('upper_bound', 1)
        
    try:
        iter(lower_bound)
    except TypeError:
        clen = max([len(x) for x in candidates])
        lower_bound = [lower_bound] * clen
        
    try:
        iter(upper_bound)
    except TypeError:
        clen = max([len(x) for x in candidates])
        upper_bound = [upper_bound] * clen
        
    cs_copy = list(candidates)
    for i, cs in enumerate(cs_copy):
        for j, c in enumerate(cs):
            if random.random() < mut_rate:
                c += random.gauss(0, mut_range) * (upper_bound[j] - lower_bound[j])
                c = int(c)
                c = max(min(c, upper_bound[j]), lower_bound[j])
                cs_copy[i][j] = c
    return cs_copy


def main(prng=None):
    ta = time()
    prng = Random()
    prng.seed(time()) 
    ga = ec.GA(prng)
    ga.observer = observer
    ga.replacer = replacers.comma_replacement
    ga.variator = [variators.uniform_crossover, gaussian_mutation]
    ga.archiver = archivers.best_archiver
    ga.selector = selectors.tournament_selection
    ga.variator = [variators.uniform_crossover, gaussian_mutation]
    ga.terminator = evaluation_termination
    final_pop = ga.evolve(evaluator=evaluate_sentence,
                          generator=generate_sentence,
                          max_evaluations=100000, 
                          pop_size=60,
                          tourn_size=20,
                          num_crossover_points=1,
                          mutation_range=0.05,
                          mutation_rate=0.01,
                          crossover_rate=1.0,
                          upper_bound=max_ord,
                          lower_bound=min_ord,
                          mu=1,
                          sigma=4,
                          maximize=False)
    final_sentence= ''.join(map(chr, final_pop[0].candidate))
    print 'FINAL SENTENCE'
    print final_sentence
    print 'n generations:',ga._kwargs['_num_generations']
    print 'n archive:', len(ga._kwargs['_archive'])
    print 'n population:', len(ga._kwargs['_population'])
    print 'evolution took:', time() - ta
    return ga
            
if __name__ == '__main__':
    TEST_PERFORMANCE = True
    if not TEST_PERFORMANCE:
        try:
            # 3 fold speed up!
            import psyco; psyco.full()
        except ImportError:
            pass
        main()
    else:
        import hotshot, hotshot.stats, test.pystone
        prof = hotshot.Profile("inf_monkey.prof")
        prof.runcall( main )
        prof.close()
        stats = hotshot.stats.load("inf_monkey.prof")
        stats.strip_dirs()
        stats.sort_stats('time', 'calls')
        stats.print_stats(20)
    

#===============================================================================
# 2760600/25800    4.394    0.000    7.778    0.000 copy.py:144(deepcopy)
#    25800    2.113    0.000    7.679    0.000 copy.py:223(_deepcopy_list)
#      430    1.471    0.003    1.495    0.003 variators.py:122(uniform_crossover)
#      430    1.329    0.003    1.401    0.003 infinite_monkey_theorem.py:43(gaussian_mutation)
#      431    1.261    0.003    1.261    0.003 infinite_monkey_theorem.py:36(evaluate_sentence)
#  1108827    0.978    0.000    0.978    0.000 copy.py:260(_keep_alive)
#   756271    0.709    0.000    0.709    0.000 ec.py:64(__lt__)
#    25800    0.700    0.000    0.700    0.000 random.py:264(sample)
#      430    0.431    0.001    1.985    0.005 selectors.py:208(tournament_selection)
#   491042    0.382    0.000    0.855    0.000 ec.py:76(__gt__)
#  1083027    0.293    0.000    0.293    0.000 copy.py:197(_deepcopy_atomic)
#        1    0.257    0.257   14.810   14.810 ec.py:167(evolve)
#    25860    0.091    0.000    0.167    0.000 ec.py:45(__init__)
# 155160/129300    0.087    0.000    0.087    0.000 ec.py:51(__setattr__)
#      430    0.079    0.000    0.182    0.000 replacers.py:223(comma_replacement)
#      431    0.073    0.000    0.134    0.000 archivers.py:48(best_archiver)
#    27186    0.073    0.000    0.073    0.000 random.py:516(gauss)
#    36167    0.027    0.000    0.027    0.000 ec.py:82(__eq__)
#      430    0.025    0.000    0.025    0.000 random.py:250(shuffle)
#     6360    0.015    0.000    0.015    0.000 random.py:147(randrange)
#===============================================================================
        
    
