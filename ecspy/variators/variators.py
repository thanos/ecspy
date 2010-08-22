"""
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

import copy


def default_variation(random, candidates, args):
    """Return the set of candidates without variation.

    .. Arguments:
       random -- the random number generator object
       candidates -- the candidate solutions
       args -- a dictionary of keyword arguments
    
    """
    return candidates

    
def estimation_of_distribution_variation(random, candidates, args):
    """Return the offspring produced using estimation of distribution.

    This function assumes that the candidate solutions are iterable 
    objects containing real values. It creates a statistical model 
    based on the set of candidates. The offspring are then generated 
    from this model. This function also makes use of the bounder
    function as specified in the EC's ``evolve`` method.

    .. Arguments:
       random -- the random number generator object
       candidates -- the candidate solutions
       args -- a dictionary of keyword arguments
    
    Optional keyword arguments in args:
    
    - *num_offspring* -- the number of offspring to create (default 1)
    
    """
    num_offspring = args.setdefault('num_offspring', 1)
    bounder = args['_ec'].bounder
    
    cs_copy = list(candidates)
    num_genes = max([len(x) for x in cs_copy])
    genes = [[x[i] for x in cs_copy] for i in range(num_genes)] 
    mean = [float(sum(x)) / float(len(x)) for x in genes]
    stdev = [sum([(x - m)**2 for x in g]) / float(len(g) - 1) for g, m in zip(genes, mean)]
    offspring = []
    for _ in range(num_offspring):
        child = copy.copy(cs_copy[0])
        for i, (m, s) in enumerate(zip(mean, stdev)):
            child[i] = m + random.gauss(0, s)
        child = bounder(child, args)
        offspring.append(child)
        
    return offspring
