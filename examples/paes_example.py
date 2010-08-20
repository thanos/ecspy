from random import Random
from time import time
from ecspy import ec
from ecspy import emo
from ecspy import terminators
from ecspy import benchmarks


def main(do_plot=True, prng=None):
    if prng is None:
        prng = Random()
        prng.seed(1000)#time()) 
        
    problem = benchmarks.Kursawe(3)
    paes = emo.PAES(prng)
    paes.terminator = terminators.evaluation_termination
    final_pop = paes.evolve(generator=problem.generator, 
                            evaluator=problem.evaluator, 
                            pop_size=1,
                            bounder=problem.bounder,
                            maximize=problem.maximize,
                            max_evaluations=8000,
                            max_archive_size=20,
                            num_grid_divisions=2)
    
    if do_plot:
        final_arc = paes.archive
        print('PAES Example (Kursawe) Best Solutions:')
        for f in final_arc:
            print(f)
        import pylab
        x = []
        y = []
        for f in final_arc:
            print(f)
            x.append(f.fitness[0])
            y.append(f.fitness[1])
        pylab.scatter(x, y, color='b')
        pylab.savefig('paes_example_kursawe.pdf', format='pdf')
        pylab.show()
    return paes

if __name__ == '__main__':
    main()
