from random import Random
from time import time
import ecspy

def main(do_plot=True, prng=None):
    if prng is None:
        prng = Random()
        prng.seed(time()) 
        
    problem = ecspy.benchmarks.Kursawe(3)
    ea = ecspy.emo.PAES(prng)
    ea.terminator = ecspy.terminators.evaluation_termination
    final_pop = ea.evolve(generator=problem.generator, 
                          evaluator=problem.evaluator, 
                          bounder=problem.bounder,
                          maximize=problem.maximize,
                          max_evaluations=30000,
                          max_archive_size=100,
                          num_grid_divisions=4)
    
    if do_plot:
        final_arc = ea.archive
        print('%s Example (%s) Best Solutions: \n' % (ea.__class__.__name__, problem.__class__.__name__))
        for f in final_arc:
            print(f)
        import pylab
        x = []
        y = []
        for f in final_arc:
            x.append(f.fitness[0])
            y.append(f.fitness[1])
        pylab.scatter(x, y, color='b')
        pylab.savefig('%s Example (%s).pdf' % (ea.__class__.__name__, problem.__class__.__name__), format='pdf')
        pylab.show()
    return ea

if __name__ == '__main__':
    main()
