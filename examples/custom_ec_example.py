from random import Random
from time import time
from ecspy import ec
from ecspy import terminators
from ecspy import selectors
from ecspy import replacers
from ecspy import variators
from ecspy import observers
from ecspy import benchmarks


def main(do_plot=True, prng=None):
    if prng is None:
        prng = Random()
        prng.seed(time()) 
    
    problem = benchmarks.Ackley(2)
    evocomp = ec.EvolutionaryComputation(prng)
    evocomp.selector = selectors.tournament_selection
    evocomp.variator = [variators.uniform_crossover, variators.gaussian_mutation]
    evocomp.replacer = replacers.steady_state_replacement
    evocomp.terminator = terminators.generation_termination
    final_pop = evocomp.evolve(generator=problem.generator,
                               evaluator=problem.evaluator,
                               pop_size=100, 
                               bounder=problem.bounder,
                               maximize=problem.maximize,
                               tourn_size=7,
                               num_selected=2, 
                               max_generations=300,
                               mutation_rate=0.2)
    if do_plot:
        best = max(final_pop) 
        print('Custom EC Example (Ackley) Best Solution: \n%s' % str(best))
        import itertools
        import pylab
        import mpl_toolkits.mplot3d.axes3d as axes3d
        num_points = 60
        points = []
        for lb, ub in zip(problem.bounder.lower_bound, problem.bounder.upper_bound):
            points.append([(i / float(num_points)) * (ub - lb) + lb for i in range(num_points)])
        points = itertools.product(*points)
        x = []
        y = []
        for p in points:
            x.append(p[0])
            y.append(p[1])
        z = problem.evaluator([[a, b] for a, b in zip(x, y)], {})
        fig = pylab.figure()
        ax = axes3d.Axes3D(fig)
        ax.scatter3D(x, y, z)
        ax.scatter3D([best.candidate[0]], [best.candidate[1]], [best.fitness], color='r')
        ax.scatter3D([problem.global_optimum[0]], [problem.global_optimum[1]], problem.evaluator([problem.global_optimum], {}), color='g')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Fitness')
        pylab.savefig('custom_ec_example_ackley.pdf', format='pdf')
        pylab.show()
    return evocomp

if __name__ == '__main__':
    main()
