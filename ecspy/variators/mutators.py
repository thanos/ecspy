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
    
    
def mutator(mutate):
    """Return an ecspy mutator function based on the given function.
    
    This function generator takes a function that operates on only
    one candidate to produce a mutated candidate. The generator 
    handles the iteration over each candidate in the set of offspring.

    The given function ``mutate`` must have the following signature::
    
        mutant = mutate(random, candidate, args)
        
    This function is most commonly used as a function decorator with
    the following usage::
    
        @mutator
        def mutate(random, candidate, args):
            # Implementation of mutation
            
    The generated function also contains an attribute named
    ``single_mutation`` which holds the original mutation function.
    In this way, the original single-candidate function can be
    retrieved if necessary.
    
    """
    def ecspy_mutator(random, candidates, args):
        mutants = list(candidates)
        for i, cs in enumerate(mutants):
            mutants[i] = mutate(random, cs, args)
        return mutants
    ecspy_mutator.__name__ = mutate.__name__
    ecspy_mutator.__dict__ = mutate.__dict__
    ecspy_mutator.__doc__ = mutate.__doc__
    ecspy_mutator.single_mutation = mutate
    return ecspy_mutator
    

@mutator    
def gaussian_mutation(random, candidate, args):
    """Return the mutants created by Gaussian mutation on the candidates.

    This function assumes that the candidate solutions are indexable
    and numeric. It performs Gaussian mutation. This function also 
    makes use of the bounder function as specified in the EC's 
    ``evolve`` method.

    .. Arguments:
       random -- the random number generator object
       candidate -- the candidate solution
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
    bounder = args['_ec'].bounder
    for i, c in enumerate(candidate):
        if random.random() < mut_rate:
            candidate[i] += random.gauss(mean, stdev)
    candidate = bounder(candidate, args)
    return candidate


@mutator
def bit_flip_mutation(random, candidate, args):
    """Return the mutants produced by bit-flip mutation on the candidates.

    This function assumes that the candidate solution is made of binary 
    values. It performs bit-flip mutation. If a candidate solution contains
    non-binary values, this function leaves it unchanged.

    .. Arguments:
       random -- the random number generator object
       candidate -- the candidate solution
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    *mutation_rate* -- the rate at which mutation is performed (default 0.1)
    
    The mutation rate is applied on a bit by bit basis.
    
    """
    rate = args.setdefault('mutation_rate', 0.1)
    if len(candidate) == len([x for x in candidate if x in [0, 1]]):
        for i, c in enumerate(candidate):
            if random.random() < rate:
                candidate[i] = (c + 1) % 2
    return candidate

    
@mutator
def nonuniform_mutation(random, candidate, args):
    bounder = args['_ec'].bounder
    num_gens = args['_ec'].num_generations
    max_gens = args['max_generations']
    strength = args['mutation_strength']
    exponent = (1.0 - num_gens / max_gens) ^ strength
    mutant = copy.copy(candidate)
    for i, (c, lo, hi) in enumerate(zip(candidate, bounder.lower_bound, bounder.upper_bound)):
        if random.random() <= 0.5:
            new_value = c + (hi - c) * (1.0 - random.random() ^ exponent)
        else:
            new_value = c - (c - lo) * (1.0 - random.random() ^ exponent)
        mutant[i] = new_value
    return mutant

    
@mutator
def mptm_mutation(random, candidate, args):
    bounder = args['_ec'].bounder
    strength = args['mutation_strength']
    mutant = copy.copy(candidate)
    for i, (c, lo, hi) in enumerate(zip(candidate, bounder.lower_bound, bounder.upper_bound)):
        t = (c - lo) / (hi - c)
        r = random.random()
        if r < t:
            t_hat = t - t * ((t - r) / t) ^ strength
        elif r == t:
            t_hat = t
        else:
            t_hat = t + (1 - t) * ((r - t) / (1 - t)) ^ strength
        mutant[i] = (1 - t_hat) * lo + t_hat * hi
    return mutant





