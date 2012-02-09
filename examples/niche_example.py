import random
import time
import math
import itertools
import ecspy

def my_distance(x, y):
    return sum([abs(a - b) for a, b in zip(x, y)])

def generate(random, args):
    return [random.uniform(0, 26)]
    
def evaluate(candidates, args):
    fitness = []
    for cand in candidates:
        fit = sum([math.sin(c) for c in cand])
        fitness.append(fit)
    return fitness

def main(do_plot=True, prng=None):
    if prng is None:
        prng = random.Random()
        prng.seed(time.time()) 
    
    ea = ecspy.ec.EvolutionaryComputation(prng)
    ea.selector = ecspy.selectors.tournament_selection
    ea.replacer = ecspy.replacers.crowding_replacement
    ea.variator = ecspy.variators.gaussian_mutation
    ea.terminator = ecspy.terminators.evaluation_termination

    final_pop = ea.evolve(generate, evaluate, pop_size=20, bounder=ecspy.ec.Bounder(0, 26),
                          max_evaluations=5000,
                          num_selected=20,
                          mutation_rate=1.0,
                          crowding_distance=10,
                          distance_function=my_distance)
                          
    if do_plot:
        import pylab
        x = []
        y = []
        for p in final_pop:
            x.append(p.candidate[0])
            y.append(math.sin(p.candidate[0]))
        t = [(i / 1000.0) * 26.0 for i in range(1000)]
        s = [math.sin(a) for a in t]
        pylab.plot(t, s, color='b')
        pylab.scatter(x, y, color='r')
        pylab.axis([0, 26, 0, 1.1])
        pylab.savefig('niche_example.pdf', format='pdf')
        pylab.show()
    return ea

if __name__ == '__main__':
    main()




    
    
    
