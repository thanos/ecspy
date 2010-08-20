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

def optimal_termination(population, num_generations, num_evaluations, args):
    if any([i.fitness==0 for i in population]):
        return  True
    return False

def observer(population, num_generations, num_evaluations, args):
    if num_generations % 100 == 0:
        population = list(population)
        population.sort(reverse=True)
        best_fit = population[0].candidate
        print '*'*20
        print  ''.join(map(chr, best_fit))
        print 'fitnesses:',
        print 'n archive:', len(args['_ec'].archive)
        print 'n population:', len(population)
        print 'n evals:', num_evaluations
    
def generate_sentence(random, args):
    s = [random.randint(0, max_ord) for i in sentence]
    return s 
    
def evaluate_sentence(candidates, args):
    fitness = []
    for cand in candidates:
        fitt = sum([abs(a-b) for a,b in zip(cand, numeric_sentence)])
        fitness.append(fitt)
    return fitness

def integer_mutation(random, candidates, args):
    mut_rate = args.setdefault('mutation_rate', 0.1)
    step = args.setdefault('mutation_step', 3)
    cands = list(candidates)
    for i, cs in enumerate(cands):
        for j, c in enumerate(cs):
            if random.random() < mut_rate:
                s = random.randint(0, 2 * step + 1) - step
                cands[i][j] = c + s
    return cands


def main(prng=None):
    if prng is None:
        prng = Random()
        prng.seed(time())
            
    ta = time()
    ea = ec.EvolutionaryComputation(prng)
    ea.observer = observer
    ea.selector = selectors.tournament_selection
    ea.variator = [variators.uniform_crossover, integer_mutation]
    ea.replacer = replacers.comma_replacement
    ea.archiver = archivers.best_archiver
    ea.terminator = [optimal_termination, terminators.evaluation_termination]
    final_pop = ea.evolve(evaluator=evaluate_sentence,
                          generator=generate_sentence,
                          max_evaluations=100000, 
                          pop_size=60,
                          tourn_size=20,
                          num_selected=60, 
                          mutation_rate=0.01,
                          crossover_rate=1.0,
                          maximize=False)
    final_pop.sort(reverse=True)
    final_sentence= ''.join(map(chr, final_pop[0].candidate))
    print 'FINAL SENTENCE'
    print final_sentence
    print 'n generations:',ea.num_generations
    print 'n archive:', len(ea.archive)
    print 'n population:', len(ea.population)
    print 'evolution took:', time() - ta
    return ea
            
if __name__ == '__main__':
    TEST_PERFORMANCE = False
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
        
    
