from random import Random
from time import time
from ecspy import emo
from ecspy import variators
from ecspy import terminators
from ecspy import benchmarks

   
def main(do_plot=True, prng=None):
    if prng is None:
        prng = Random()
        prng.seed(time()) 

    problem = benchmarks.Kursawe(3)
    nsga = emo.NSGA2(prng)
    nsga.variator = [variators.blend_crossover, variators.gaussian_mutation]
    nsga.terminator = terminators.generation_termination
    final_pop = nsga.evolve(generator=problem.generator, 
                            evaluator=problem.evaluator, 
                            pop_size=100,
                            maximize=problem.maximize,
                            bounder=problem.bounder,
                            max_generations=80)
    
    if do_plot:
        final_arc = nsga.archive
        print('NSGA Example (Kursawe) Best Solutions:')
        for f in final_arc:
            print(f)
        import pylab
        x = []
        y = []
        for f in final_arc:
            x.append(f.fitness[0])
            y.append(f.fitness[1])
        pylab.scatter(x, y, color='b')
        pylab.savefig('nsga_example_kursawe.pdf', format='pdf')
        pylab.show()
    return nsga
        
if __name__ == '__main__':
    main()    
