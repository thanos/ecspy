from time import time
from random import Random
from ecspy import terminators
from ecspy import topologies
from ecspy import swarm
from ecspy import ec
from ecspy import benchmarks


def main(do_plot=True, prng=None):
    if prng is None:
        prng = Random()
        prng.seed(time()) 
    
    problem = benchmarks.Sphere(2)
    pso = swarm.PSO(prng)
    pso.terminator = terminators.evaluation_termination
    pso.topology = topologies.ring_topology
    final_pop = pso.evolve(generator=problem.generator,
                           evaluator=problem.evaluator, 
                           pop_size=100,
                           bounder=problem.bounder,
                           maximize=problem.maximize,
                           max_evaluations=30000, 
                           neighborhood_size=5)
        
    if do_plot:
        best = max(final_pop)
        print('PSO Example (Sphere) Best Solution: \n%s' % str(best))
        import itertools
        import pylab
        import mpl_toolkits.mplot3d.axes3d as axes3d
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
        z = problem.evaluator([[a, b] for a, b in zip(x, y)], {})
        fig = pylab.figure()
        ax = axes3d.Axes3D(fig)
        ax.scatter3D(x, y, z)
        ax.scatter3D([best.candidate[0]], [best.candidate[1]], [best.fitness], color='r')
        ax.scatter3D([problem.global_optimum[0]], [problem.global_optimum[1]], problem.evaluator([problem.global_optimum], {}), color='g')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Fitness')
        pylab.savefig('pso_example_sphere.pdf', format='pdf')
        pylab.show()
    return pso

if __name__ == '__main__':
    main()