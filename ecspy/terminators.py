"""
    This module provides pre-defined terminators for evolutionary computations.
    
    All terminator functions have the following arguments:
    
    - *population* -- the population of Individuals
    - *num_generations* -- the number of elapsed generations
    - *num_evaluations* -- the number of candidate solution evaluations
    - *args* -- a dictionary of keyword arguments
    
    .. Copyright (C) 2009  Inspired Intelligence Initiative

    .. This program is free software: you can redistribute it and/or modify
       it under the terms of the GNU General Public License as published by
       the Free Software Foundation, either version 3 of the License, or
       (at your option) any later version.

    .. This program is distributed in the hope that it will be useful,
       but WITHOUT ANY WARRANTY; without even the implied warranty of
       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
       GNU General Public License for more details.

    .. You should have received a copy of the GNU General Public License
       along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import math
import itertools


def default_termination(population, num_generations, num_evaluations, args):
    """Return True.
    
    This function acts as a default termination criterion for an EC.
    
    .. Arguments:
       population -- the population of Individuals
       num_generations -- the number of elapsed generations
       num_evaluations -- the number of candidate solution evaluations
       args -- a dictionary of keyword arguments
    
    """
    return True
    

def diversity_termination(population, num_generations, num_evaluations, args):
    """Return True if population diversity is less than a minimum diversity.
    
    This function calculates the Euclidean distance between every pair of
    individuals in the population. It then compares the maximum of those
    distances with a specified minimum required diversity. This terminator 
    is really only well-defined for candidate solutions which are List 
    types of numeric values. 
    
    .. Arguments:
       population -- the population of Individuals
       num_generations -- the number of elapsed generations
       num_evaluations -- the number of candidate solution evaluations
       args -- a dictionary of keyword arguments
    
    Optional keyword arguments in args:
    
    *min_diversity* -- the minimum population diversity allowed (default 0.001)
    
    """
    min_diversity = args.setdefault('min_diversity', 0.001)
    cart_prod = itertools.product(population, population)
    distance = []
    for (p, q) in cart_prod:
        d = 0
        for x, y in zip(p.candidate, q.candidate):
            d += (x - y)**2
        distance.append(math.sqrt(d))
    if max(distance) < min_diversity:
        return True
    return False

    
def avg_fitness_termination(population, num_generations, num_evaluations, args):
    """Return True if the population's average fitness is near its maximum fitness.
    
    This function calculates the average fitness of the population as well
    as the maximum (i.e., best) fitness. If the difference between those values
    is less than a specified minimum, the function returns True. 
    
    .. Arguments:
       population -- the population of Individuals
       num_generations -- the number of elapsed generations
       num_evaluations -- the number of candidate solution evaluations
       args -- a dictionary of keyword arguments
    
    Optional keyword arguments in args:
    
    *min_fitness_diff* -- the minimum allowable difference between 
    average and maximum fitness (default 0.001)
    
    """
    min_fitness_diff = args.setdefault('min_fitness_diff', 0.001)
    avg_fit = sum([x.fitness for x in population]) / float(len(population))
    max_fit = max([x.fitness for x in population])
    if (max_fit - avg_fit) < min_fitness_diff:
        return True
    return False


def evaluation_termination(population, num_generations, num_evaluations, args):
    """Return True if the number of function evaluations meets or exceeds a maximum.
    
    This function compares the number of function evaluations that have been 
    generated with a specified maximum. It returns True if the maximum is met
    or exceeded.
    
    .. Arguments:
       population -- the population of Individuals
       num_generations -- the number of elapsed generations
       num_evaluations -- the number of candidate solution evaluations
       args -- a dictionary of keyword arguments
    
    Optional keyword arguments in args:
    
    *max_evaluations* -- the maximum candidate solution evaluations (default len(population)) 
    
    """
    max_evaluations = args.setdefault('max_evaluations', len(population))
    if num_evaluations >= max_evaluations:
        return True
    return False


def generation_termination(population, num_generations, num_evaluations, args):
    """Return True if the number of generations meets or exceeds a maximum.
    
    This function compares the number of generations with a specified 
    maximum. It returns True if the maximum is met or exceeded.
    
    .. Arguments:
       population -- the population of Individuals
       num_generations -- the number of elapsed generations
       num_evaluations -- the number of candidate solution evaluations
       args -- a dictionary of keyword arguments
    
    Optional keyword arguments in args:
    
    *max_generations* -- the maximum generations (default 1) 
    
    """
    max_generations = args.setdefault('max_generations', 1)
    if num_generations >= max_generations:
        return True
    return False

