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
    
    problem = benchmarks.Ackley(2)
    
    def generate_binary(random, args):
        bits = args.get('num_bits', 8)
        return [random.choice([0, 1]) for i in xrange(bits)]
            
    def evaluate_binary(candidates, args):
        bits = args.get('num_bits', 8)
        real_candidates = []
        for cand in candidates:
            real_values = []
            for half, lb, ub in zip([cand[:bits//2], cand[bits//2:]], problem.bounder.lower_bound, problem.bounder.upper_bound):
                num = 0
                exp = len(half) - 1
                for h in half:
                    num += h * (2**exp)
                    exp -= 1
                num = num / float(2**(len(half)) - 1)
                real_values.append(num * (ub - lb) + lb)
            real_candidates.append(real_values)
        return problem.evaluator(real_candidates, args)

    stat_file = open('ga_statistics.csv', 'w')
    ind_file = open('ga_individuals.csv', 'w')

    ga = ec.GA(prng)
    ga.observer = observers.file_observer
    ga.terminator = terminators.evaluation_termination
    final_pop = ga.evolve(generator=generate_binary,
                          evaluator=evaluate_binary,
                          pop_size=100,
                          maximize=problem.maximize,
                          max_evaluations=30000, 
                          statistics_file=stat_file,
                          individuals_file=ind_file,
                          num_elites=1,
                          num_bits=20)
    stat_file.close()
    ind_file.close()
    best = max(final_pop)
    print('GA Example (Ackley) Best Solution: \n%s' % str(best))
        
    if do_plot:
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
        pylab.savefig('ga_example_ackley.pdf', format='pdf')
        pylab.show()
    return ga
            
if __name__ == '__main__':
    main()