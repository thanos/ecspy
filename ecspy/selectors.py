"""
    This module provides pre-defined selectors for evolutionary computations.

    All selector functions have the following arguments:
    
    - *random* -- the random number generator object
    - *population* -- the population of individuals
    - *args* -- a dictionary of keyword arguments
    
    Each selector function returns the list of selected individuals.
    
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


def default_selection(random, population, args):
    """Return the population.
    
    This function acts as a default selection scheme for an EC.
    It simply returns the entire population as having been 
    selected.
    
    .. Arguments:
       random -- the random number generator object
       population -- the population of individuals
       args -- a dictionary of keyword arguments
    
    """
    return population


def truncation_selection(random, population, args):
    """Selects the best individuals from the population.
    
    This function performs truncation selection, which means that only
    the best individuals from the current population are selected. This
    is a completely deterministic selection mechanism.
    
    .. Arguments:
       random -- the random number generator object
       population -- the population of individuals
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    *num_selected* -- the number of individuals to be selected 
    (default len(population))
    
    """
    num_selected = args.setdefault('num_selected', len(population))
    pool = list(population)
    pool.sort(reverse=True)
    return pool[:num_selected]

    
def uniform_selection(random, population, args):
    """Return a uniform sampling of individuals from the population.
    
    This function performs uniform selection by randomly choosing
    members of the population with replacement.
    
    .. Arguments:
       random -- the random number generator object
       population -- the population of individuals
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    *num_selected* -- the number of individuals to be selected 
    (default 1)
    
    """
    num_selected = args.setdefault('num_selected', 1)
    pop = list(population)
    selected = []
    for _ in range(num_selected):
        selected.append(pop[random.randint(0, len(pop)-1)])
    return selected


def fitness_proportionate_selection(random, population, args):
    """Return fitness proportionate sampling of individuals from the population.

    .. Arguments:
       random -- the random number generator object
       population -- the population of individuals
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    *num_selected* -- the number of individuals to be selected (default 1)
    
    """
    num_selected = args.setdefault('num_selected', 1)
    pop = list(population)
    len_pop = len(pop)
    psum = [i for i in range(len_pop)]
    pop_max_fit = (max(pop)).fitness
    pop_min_fit = (min(pop)).fitness
    
    # If we're actually doing minimimization,
    # fitness proportionate selection is not defined.
    if pop_max_fit < pop_min_fit:
        raise ValueError('Fitness proportionate selection is not valid for minimization.')
    
    # Set up the roulette wheel
    if pop_max_fit == pop_min_fit:
        psum = [(index + 1) / float(len_pop) for index in range(len_pop)]
    elif (pop_max_fit > 0 and pop_min_fit >= 0) or (pop_max_fit <= 0 and pop_min_fit < 0):
        pop.sort(reverse=True)
        psum[0] = pop[0].fitness
        for i in range(1, len_pop):
            psum[i] = pop[i].fitness + psum[i-1]
        for i in range(len_pop):
            psum[i] /= float(psum[len_pop-1])
            
    # Select the individuals
    selected = []
    for _ in range(num_selected):
        cutoff = random.random()
        lower = 0
        upper = len_pop - 1
        while(upper >= lower):
            mid = (lower + upper) // 2
            if psum[mid] > cutoff: 
                upper = mid - 1
            else: 
                lower = mid + 1
        lower = max(0, min(len_pop-1, lower))
        selected.append(pop[lower])
    return selected


def rank_selection(random, population, args):
    """Return a rank-based sampling of individuals from the population.
    
    .. Arguments:
       random -- the random number generator object
       population -- the population of individuals
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    *num_selected* -- the number of individuals to be selected (default 1)
    
    """
    num_selected = args.setdefault('num_selected', 1)

    # Set up the roulette wheel
    pop = list(population)
    len_pop = len(pop)
    pop.sort()
    psum = range(len_pop)
    den = (len_pop * (len_pop + 1)) / 2.0
    for i in range(len_pop):
        psum[i] = (i + 1) / den
    for i in range(1, len_pop):
        psum[i] += psum[i-1]
        
    # Select the individuals
    selected = []
    for _ in range(num_selected):
        cutoff = random.random()
        lower = 0
        upper = len_pop - 1
        while(upper >= lower):
            mid = (lower + upper) // 2
            if psum[mid] > cutoff: 
                upper = mid - 1
            else: 
                lower = mid + 1
        lower = max(0, min(len_pop-1, lower))
        selected.append(pop[lower])
    return selected


def tournament_selection(random, population, args):
    """Return a tournament sampling of individuals from the population.
    
    .. Arguments:
       random -- the random number generator object
       population -- the population of individuals
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    - *num_selected* -- the number of individuals to be selected (default 1)
    - *tourn_size* -- the tournament size (default 2)
    
    """
    num_selected = args.setdefault('num_selected', 1)
    tourn_size = args.setdefault('tourn_size', 2)
    pop = list(population)
    selected = []
    for _ in range(num_selected):
        tourn = random.sample(pop, tourn_size)
        selected.append(max(tourn))
    return selected


