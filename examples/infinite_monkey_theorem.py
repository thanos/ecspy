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
    for p in population:
        if sum(abs(a-b) for a,b in zip(numeric_sentence, p)) == 0:
            return  True
    return False

def observer(population, num_generations, num_evaluations, args):
    '''
    '''
    best_fit = population[0].fitness
    print '*'*20
    print  ''.join(map(chr, best_fit))
    print '*'*20
    
def generate_sentence(random, args):
    s = [random.randint(0,100) for i in sentence]
    return s 
        
def evaluate_sentence(candidates, args):
    fitness = []
    for cand in candidates:
        fitt = [abs(a-b) for a,b in zip(cand, numeric_sentence)]
        fitness.append(fitt)
    return fitness

def main(prng=None): 
    prng = Random()
    prng.seed(time()) 
    ga = ec.GA(prng)
    ga.observer = observer
    ga.replacer = replacers.generational_replacement
    ga.selector = selectors.tournament_selection
    ga.variator = [variators.n_point_crossover, variators.gaussian_mutation]
    #ga.archiver = archivers.best_archiver
    final_pop = ga.evolve(evaluator=evaluate_sentence,
                          generator=generate_sentence,
                          terminator=terminators.evaluation_termination,
                          max_evaluations=10000000, 
                          pop_size=100,
                          #tourn_size=4,
                          num_selected=20,
                          num_crossover_points=1,
                          mutation_range=4,
                          mutation_rate=0.02,
                          crossover_rate=0.75,
                          maximize=False)
    final_sentence= ''.join(map(chr, final_pop[0]))
    print 'FINAL SENTENCE'
    print final_sentence
    return ga
            
if __name__ == '__main__':
    main()