from random import Random
from time import time
from ecspy import ec
from ecspy import terminators, observers, replacers, selectors, variators, archivers


sentence = """
'Just living is not enough,' said the butterfly,
'one must have sunshine, freedom, and a little flower.'
"""
numeric_sentence = map(ord, sentence)

def evaluation_termination(population, num_generations, num_evaluations, args):
    if sum([abs(a-b) for a,b in zip(population[0].candidate, numeric_sentence)]) == 0:
        return  True
    return False

def observer(population, num_generations, num_evaluations, args):
    '''
    '''
    best_fit = population[0].candidate
    print '*'*20
    print  ''.join(map(chr, best_fit))
    print 'fitnesses:',
    #for p in population: print p.fitness
    
def generate_sentence(random, args):
    s = [random.randint(0,100) for i in sentence]
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
    try:
        mut_rate = args['mutation_rate']
    except KeyError:
        mut_rate = 0.1
        args['mutation_rate'] = mut_rate
    try:
        mut_range = args['mutation_range']
    except KeyError:
        mut_range = 1.0
        args['mutation_range'] = mut_range
    try:
        lower_bound = args['lower_bound']
    except KeyError:
        lower_bound = 0
        args['lower_bound'] = lower_bound
    try:
        upper_bound = args['upper_bound']
    except KeyError:
        upper_bound = 1
        args['upper_bound'] = upper_bound
        
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
                c = max(min(c, upper_bound[j]), lower_bound[j])
                cs_copy[i][j] = c
    return cs_copy


def main(prng=None): 
    prng = Random()
    prng.seed(time()) 
    ga = ec.GA(prng)
    ga.observer = observer
    ga.replacer = replacers.steady_state_replacement
    ga.selector = selectors.tournament_selection
    ga.variator = [variators.uniform_crossover, gaussian_mutation]
    #ga.archiver = archivers.best_archiver
    final_pop = ga.evolve(evaluator=evaluate_sentence,
                          generator=generate_sentence,
                          terminator=evaluation_termination,
                          max_evaluations=10000000, 
                          pop_size=100,
                          tourn_size=2,
                          #num_selected=20,
                          num_crossover_points=1,
                          mutation_range=4,
                          mutation_rate=0.02,
                          crossover_rate=0.9,
                          upper_bound=max(numeric_sentence),
                          lower_bound =min(numeric_sentence),
                          maximize=False)
    final_sentence= ''.join(map(chr, final_pop[0].candidate))
    print 'FINAL SENTENCE'
    print final_sentence
    return ga
            
if __name__ == '__main__':
    main()