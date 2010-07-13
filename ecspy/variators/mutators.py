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
    
def gaussian_mutation(random, candidates, args):
    """Return the mutants created by Gaussian mutation on the candidates.

    This function assumes that the candidate solutions are indexable
    and numeric. It performs Gaussian mutation. This function also 
    makes use of the bounder function as specified in the EC's 
    ``evolve`` method.

    .. Arguments:
       random -- the random number generator object
       candidates -- the candidate solutions
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    - *mutation_rate* -- the rate at which mutation is performed (default 0.1)
    - *mean* -- the mean used in the Gaussian function (default 0)
    - *stdev* -- the standard deviation used in the Gaussian function
      (default 1.0)
    
    """
    mut_rate = args.setdefault('mutation_rate', 0.1)
    mean = args.setdefault('mean', 0.0)
    stdev = args.setdefault('stdev', 1.0)
    bounder = args['_evolutionary_computation'].bounder
        
    cs_copy = list(candidates)
    for i, cs in enumerate(cs_copy):
        for j, c in enumerate(cs):
            if random.random() < mut_rate:
                c += random.gauss(mean, stdev)
                cs_copy[i][j] = c
        cs_copy[i] = bounder(cs_copy[i], args)
    return cs_copy


def bit_flip_mutation(random, candidates, args):
    """Return the mutants produced by bit-flip mutation on the candidates.

    This function assumes that the candidate solutions are binary values.
    It performs bit-flip mutation. If a candidate solution contains
    non-binary values, this function leaves it unchanged.

    .. Arguments:
       random -- the random number generator object
       candidates -- the candidate solutions
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    *mutation_rate* -- the rate at which mutation is performed (default 0.1)
    
    The mutation rate is applied on a bit by bit basis.
    
    """
    rate = args.setdefault('mutation_rate', 0.1)
    cs_copy = list(candidates)
    for i, cs in enumerate(cs_copy):
        if len(cs) == len([x for x in cs if x in [0, 1]]):
            for j, c in enumerate(cs):
                if random.random() < rate:
                    cs_copy[i][j] = (c + 1) % 2
    return cs_copy
