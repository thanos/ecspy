import math
import itertools

def default_termination(population, num_generations, num_fun_evals, args):
    """Return True.
    
    This function acts as a default termination criterion for an EC.
    Arguments:
    population -- the population of Individuals
    num_generations -- the number of elapsed generations
    num_fun_evals -- the number of of used function evaluations
    
    """
    return True
    

def diversity_termination(population, num_generations, num_fun_evals, args):
    try:
        min_diversity = args['min_diversity']
    except KeyError:
        min_diversity = 0.001
    cart_prod = itertools.product(population, population)
    distance = []
    for (p, q) in cart_prod:
        d = 0
        for i in xrange(len(p.candidate)):
            d += (p.candidate[i] - q.candidate[i])**2
        distance.append(math.sqrt(d))
    return max(distance) < min_diversity

    
def avg_fitness_termination(population, num_generations, num_fun_evals, args):
    try:
        min_fitness_diff = args['min_fitness_diff']
    except KeyError:
        min_fitness_diff = 0.001
    avg_fit = sum([x.fitness for x in population]) / float(len(population))
    max_fit = max([x.fitness for x in population])
    return (max_fit - avg_fit) < min_fitness_diff


def fun_eval_termination(population, num_generations, num_fun_evals, args):
    try:
        max_fun_evals = args['max_fun_evals']
    except KeyError:
        max_fun_evals = len(population)
    return num_fun_evals >= max_fun_evals


def num_gen_termination(population, num_generations, num_fun_evals, args):
    try:
        max_generations = args['max_generations']
    except KeyError:
        max_generations = 1
    return num_generations >= max_generations

