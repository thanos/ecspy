import math
import itertools

def default_termination(population, num_generations, num_fun_evals, args):
    """Return True.
    
    This function acts as a default termination criterion for an EC.
    Arguments:
    population -- the population of Individuals
    num_generations -- the number of elapsed generations
    num_fun_evals -- the number of of used function evaluations
    args -- a dictionary of keyword arguments
    
    """
    return True
    

def diversity_termination(population, num_generations, num_fun_evals, args):
    """Return True if population diversity is less than a minimum diversity.
    
    This function calculates the Euclidean distance between every pair of
    individuals in the population. It then compares the maximum of those
    distances with a specified minimum required diversity. This terminator 
    is really only well-defined for candidate solutions which are List 
    types of numeric values. 
    Arguments:
    population -- the population of Individuals
    num_generations -- the number of elapsed generations
    num_fun_evals -- the number of of used function evaluations
    args -- a dictionary of keyword arguments
    
    Optional keyword arguments in args:
    min_diversity -- the minimum population diversity allowed (default 0.001)
    
    """
    try:
        min_diversity = args['min_diversity']
    except KeyError:
        min_diversity = 0.001
    cart_prod = itertools.product(population, population)
    distance = []
    for (p, q) in cart_prod:
        d = 0
        for x, y in zip(p.candidate, q.candidate):
            d += (x - y)**2
        distance.append(math.sqrt(d))
    return max(distance) < min_diversity

    
def avg_fitness_termination(population, num_generations, num_fun_evals, args):
    """Return True if the population's average fitness is near its maximum fitness.
    
    This function calculates the average fitness of the population as well
    as the maximum (i.e., best) fitness. If the difference between those values
    is less than a specified minimum, the function returns True. 
    Arguments:
    population -- the population of Individuals
    num_generations -- the number of elapsed generations
    num_fun_evals -- the number of of used function evaluations
    args -- a dictionary of keyword arguments
    
    Optional keyword arguments in args:
    min_fitness_diff -- the minimum allowable difference between 
                        average and maximum fitness (default 0.001)
    
    """
    try:
        min_fitness_diff = args['min_fitness_diff']
    except KeyError:
        min_fitness_diff = 0.001
    avg_fit = sum([x.fitness for x in population]) / float(len(population))
    max_fit = max([x.fitness for x in population])
    return (max_fit - avg_fit) < min_fitness_diff


def fun_eval_termination(population, num_generations, num_fun_evals, args):
    """Return True if the number of function evaluations meets or exceeds a maximum.
    
    This function compares the number of function evaluations that have been 
    generated with a specified maximum. It returns True if the maximum is met
    or exceeded.
    Arguments:
    population -- the population of Individuals
    num_generations -- the number of elapsed generations
    num_fun_evals -- the number of of used function evaluations
    args -- a dictionary of keyword arguments
    
    Optional keyword arguments in args:
    max_fun_evals -- the maximum function evaluations (default len(population)) 
    
    """
    try:
        max_fun_evals = args['max_fun_evals']
    except KeyError:
        max_fun_evals = len(population)
    return num_fun_evals >= max_fun_evals


def num_gen_termination(population, num_generations, num_fun_evals, args):
    """Return True if the number of generations meets or exceeds a maximum.
    
    This function compares the number of generations with a specified 
    maximum. It returns True if the maximum is met or exceeded.
    Arguments:
    population -- the population of Individuals
    num_generations -- the number of elapsed generations
    num_fun_evals -- the number of of used function evaluations
    args -- a dictionary of keyword arguments
    
    Optional keyword arguments in args:
    max_generations -- the maximum generations (default 1) 
    
    """
    try:
        max_generations = args['max_generations']
    except KeyError:
        max_generations = 1
    return num_generations >= max_generations

