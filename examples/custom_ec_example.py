from random import Random
from time import time
from ecspy import ec
from ecspy import terminators
from ecspy import selectors
from ecspy import replacers
from ecspy import variators
from ecspy import observers



def generate_real(random, args):
    size = args.get('chrom_size', 4)
    return [random.random() for i in xrange(size)]

def evaluate_real(candidates, args):
    fitness = []
    for cand in candidates:
        num = sum(cand)
        fitness.append(num)
    return fitness

def main(do_plot=True, prng=None):
    if prng is None:
        prng = Random()
        prng.seed(time()) 
    
    evocomp = ec.EvolutionaryComputation(prng)
    evocomp.selector = selectors.tournament_selection
    evocomp.variator = [variators.uniform_crossover, variators.gaussian_mutation]
    evocomp.replacer = replacers.steady_state_replacement
    evocomp.terminator = terminators.generation_termination
    
    if do_plot:
        evocomp.observer = observers.plot_observer 
    
    start = time()
    final_pop = evocomp.evolve(evaluator=evaluate_real, 
                               generator=generate_real, 
                               pop_size=100, 
                               tourn_size=7,
                               num_selected=2, 
                               max_generations=50,
                               mutation_rate=0.2)
    stop = time()
    
    
    print('***********************************')
    print('Total Execution Time: %0.5f seconds' % (stop - start))
    for ind in final_pop:
        print(str(ind))
    
    # This is required because, without it, the plotting produces
    # a runtime exception when the program ends. I'm not sure why.
    if do_plot:
        import pylab
        pylab.show()
    return evocomp

if __name__ == '__main__':
    main()
