from random import Random
from time import time
from ecspy import ec
from ecspy import observers
from ecspy import terminators
from ecspy import benchmarks


def main(do_plot=True, prng=None): 
    if prng is None:
        prng = Random()
        prng.seed(time()) 
    
    problem = benchmarks.Binary(benchmarks.Schwefel(2), dimension_bits=30)
    
    stat_file = open('ga_statistics.csv', 'w')
    ind_file = open('ga_individuals.csv', 'w')

    ea = ec.GA(prng)
    ea.observer = observers.file_observer
    ea.terminator = terminators.evaluation_termination
    final_pop = ea.evolve(generator=problem.generator,
                          evaluator=problem.evaluator,
                          pop_size=100,
                          maximize=problem.maximize,
                          bounder=problem.bounder,
                          max_evaluations=30000, 
                          statistics_file=stat_file,
                          individuals_file=ind_file,
                          num_elites=1)
    stat_file.close()
    ind_file.close()
    
        
    if do_plot:
        best = max(final_pop)
        print('%s Example (%s) Best Solution: \n%s' % (ea.__class__.__name__, problem.__class__.__name__, str(best)))
        realbest = problem.binary_to_real(best.candidate)
        realfit = best.fitness
        print('Converted as --> %s : %f' % (str(realbest), realfit))
        
        import itertools
        import pylab
        import mpl_toolkits.mplot3d.axes3d as axes3d
        from ecspy import analysis
        
        # Create the points using the original Ackley function.
        num_points = 40
        points = []
        for lb, ub in zip(problem.bounder.lower_bound, problem.bounder.upper_bound):
            points.append([(i / float(num_points)) * (ub - lb) + lb for i in range(num_points)])
        points = itertools.product(*points)
        x = []
        y = []
        for p in points:
            x.append(p[0])
            y.append(p[1])
        z = problem.benchmark.evaluator([[a, b] for a, b in zip(x, y)], {})
        
        fig = pylab.figure()
        ax = axes3d.Axes3D(fig)
        ax.scatter3D(x, y, z)
        ax.scatter3D([realbest[0]], [realbest[1]], [realfit], color='r')
        realopt = problem.benchmark.global_optimum
        ax.scatter3D([realopt[0]], [realopt[1]], problem.benchmark.evaluator([realopt], {}), color='g')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Fitness')
        pylab.savefig('%s Example (%s).pdf' % (ea.__class__.__name__, problem.__class__.__name__), format='pdf')
        analysis.generation_plot('ga_statistics.csv', errorbars=False)
    return ea
            
if __name__ == '__main__':
    main()