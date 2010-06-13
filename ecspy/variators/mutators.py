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
    and numeric. It performs Gaussian mutation.

    .. Arguments:
       random -- the random number generator object
       candidates -- the candidate solutions
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    - *mutation_rate* -- the rate at which mutation is performed (default 0.1)
    - *mutation_range* -- the variance used in the Gaussian function 
      (default 1.0)
    - *lower_bound* -- the lower bounds of the chromosome elements (default 0)
    - *upper_bound* -- the upper bounds of the chromosome elements (default 1)
    
    The lower and upper bounds can either be single values, which will
    be applied to all elements of a chromosome, or lists of values of 
    the same length as the chromosome.
    
    """
    mut_rate = args.setdefault('mutation_rate', 0.1)
    mut_range = args.setdefault('mutation_range', 1.0)
    lower_bound = args.setdefault('lower_bound', 0)
    upper_bound = args.setdefault('upper_bound', 1)
        
    try:
        iter(lower_bound)
    except TypeError:
        clen = max([len(x) for x in candidates])
        lower_bound = [lower_bound] * clen
        
    try:
        iter(upper_bound)
    except TypeError:
        clen = max([len(x) for x in candidates])
        upper_bound = [upper_bound] * clen
        
    cs_copy = list(candidates)
    for i, cs in enumerate(cs_copy):
        for j, c in enumerate(cs):
            if random.random() < mut_rate:
                c += random.gauss(0, mut_range) * (upper_bound[j] - lower_bound[j])
                c = max(min(c, upper_bound[j]), lower_bound[j])
                cs_copy[i][j] = c
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
