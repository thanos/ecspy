"""
    This module provides pre-defined replacers for evolutionary computations.
    
    Copyright (C) 2009  Inspired Intelligence Initiative

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


def default_replacement(random, population, parents, offspring, args):
    """Replaces entire population with offspring.
    
    Arguments:
    random -- the random number generator object
    population -- the population of Individuals
    parents -- the list of parent individuals
    offspring -- the list of offspring individuals
    args -- a dictionary of keyword arguments
    
    """
    return offspring

    
def truncation_replacement(random, population, parents, offspring, args):
    """Replaces population with the best of the population and offspring.
    
    This function performs truncation replacement, which means that
    the entire existing population is replaced by the best from among
    the current population and offspring, keeping the existing population
    size fixed. This is similar to so called 'plus' replacement in the 
    evolution strategies literature, except that 'plus' replacement 
    considers only parents and offspring for survival. However, if the
    entire population are parents (which is often the case in ES), then
    truncation replacement and plus-replacement are equivalent approaches.
    Arguments:
    random -- the random number generator object
    population -- the population of Individuals
    parents -- the list of parent individuals
    offspring -- the list of offspring individuals
    args -- a dictionary of keyword arguments
    
    """
    pool = list(population)
    pool.extend(list(offspring))
    pool.sort(key=lambda x: x.fitness, reverse=True)
    return pool[:len(population)]

    
def steady_state_replacement(random, population, parents, offspring, args):
    """Performs steady-state replacement for the offspring.
    
    This function performs steady-state replacement, which means that
    the offspring replace the least fit individuals in the existing
    population, even if those offspring are less fit than the individuals
    that they replace.
    Arguments:
    random -- the random number generator object
    population -- the population of Individuals
    parents -- the list of parent individuals
    offspring -- the list of offspring individuals
    args -- a dictionary of keyword arguments
    
    """
    off = list(offspring)
    pop = list(population)
    pop.sort(key=lambda x: x.fitness)
    num_to_replace = min(len(off), len(pop))
    pop[:num_to_replace] = off[:num_to_replace]
    return pop


def generational_replacement(random, population, parents, offspring, args):
    """Performs generational replacement with optional weak elitism.
    
    This function performs generational replacement, which means that
    the entire existing population is replaced by the offspring,
    truncating to the population size if the number of offspring is 
    larger. Weak elitism may also be specified through the num_elites
    keyword argument in args. If this is used, the best num_elites
    individuals in the current population are allowed to survive if
    they are better than the worst num_elites offspring.
    Arguments:
    random -- the random number generator object
    population -- the population of Individuals
    parents -- the list of parent individuals
    offspring -- the list of offspring individuals
    args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    num_elites -- number of elites to consider (default 0)
    
    """
    try:
        num_elites = args['num_elites']
    except KeyError:
        num_elites = 0
        args['num_elites'] = num_elites
    off = list(offspring)
    pop = list(population)
    pop.sort(key=lambda x: x.fitness, reverse=True)
    off.extend(pop[:num_elites])
    off.sort(key=lambda x: x.fitness, reverse=True)
    survivors = off[:len(population)]
    return survivors


def random_replacement(random, population, parents, offspring, args):
    """Performs random replacement with optional weak elitism.
    
    This function performs random replacement, which means that
    the offspring replace random members of the population, keeping
    the population size constant. Weak elitism may also be specified 
    through the num_elites keyword argument in args. If this is used, 
    the best num_elites individuals in the current population are 
    allowed to survive if they are better than the worst num_elites 
    offspring.
    Arguments:
    random -- the random number generator object
    population -- the population of Individuals
    parents -- the list of parent individuals
    offspring -- the list of offspring individuals
    args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    num_elites -- number of elites to consider (default 0)
    
    """
    try:
        num_elites = args['num_elites']
    except KeyError:
        num_elites = 0
        args['num_elites'] = num_elites
    off = list(offspring)
    pop = list(population)
    pop.sort(key=lambda x: x.fitness, reverse=True)
    num_to_replace = min(len(off), len(pop) - num_elites) 
    valid_indices = range(num_elites, len(pop))
    rep_index = random.sample(valid_indices, num_to_replace)
    for i in xrange(len(off)):
        pop[rep_index[i]] = off[i]
    return pop


def plus_replacement(random, population, parents, offspring, args):
    """Performs 'plus' replacement with optional adaptive mutation.
    
    This function performs 'plus' replacement, which means that
    the entire existing population is replaced by the best
    population-many elements from the combined set of parents and 
    offspring. Adaptive mutation can also be specified here through 
    the use_one_fifth_rule keyword argument in args. This adaptive
    mutation attempts to keep the rate of viable offspring near 20%.
    If the number of successful offspring is below 20%, the mutation
    rate is reduced by 20% (to allow more exploitation). If the 
    number of successful offspring is above 20%, the mutation rate
    is increased by 20% (to allow more exploration).
    Arguments:
    random -- the random number generator object
    population -- the population of Individuals
    parents -- the list of parent individuals
    offspring -- the list of offspring individuals
    args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    use_one_fifth_rule -- whether the 1/5 rule should be used (default False)
    
    """
    try:
        use_one_fifth_rule = args['use_one_fifth_rule']
    except KeyError:
        use_one_fifth_rule = False
        args['use_one_fifth_rule'] = use_one_fifth_rule
    pool = list(parents)
    pool.extend(list(offspring))
    pool.sort(key=lambda x: x.fitness, reverse=True)
    survivors = pool[:len(population)]
    if use_one_fifth_rule:
        count = len([x for x in offspring if x in survivors])
        rate = count / float(len(offspring))
        if rate < 0.2:
            try:
                args['mutation_rate'] = args['mutation_rate'] * 0.8
            except KeyError:
                args['use_one_fifth_rule'] = False
        elif rate > 0.2:
            try:
                args['mutation_rate'] = args['mutation_rate'] * 1.2
            except KeyError:
                args['use_one_fifth_rule'] = False            
    return survivors


def comma_replacement(random, population, parents, offspring, args):
    """Performs 'comma' replacement.
    
    This function performs 'comma' replacement, which means that
    the entire existing population is replaced by the best
    population-many elements from the offspring. This function
    makes the assumption that the size of the offspring is at 
    least as large as the original population. Otherwise, the
    population size will not be constant.
    Arguments:
    random -- the random number generator object
    population -- the population of Individuals
    parents -- the list of parent individuals
    offspring -- the list of offspring individuals
    args -- a dictionary of keyword arguments
    
    """
    pool = list(offspring)
    pool.sort(key=lambda x: x.fitness, reverse=True)
    survivors = pool[:len(population)]
    return survivors
