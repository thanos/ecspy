"""
    This module provides pre-defined variators for evolutionary computations.
    
    All variator functions have the following arguments:
    
    - *random* -- the random number generator object
    - *candidates* -- the candidate solutions
    - *args* -- a dictionary of keyword arguments
    
    Each variator function returns the list of modified individuals.
    
    These variators may make some limited assumptions about the type of
    candidate solutions on which they operate. These assumptions are noted
    in the table below.
    
    +--------------------------------------+----------+-----------+-----------+----------+---------+------+--------+
    | Variator                             | Iterable | Indexable | Sliceable | Listable | Lenable | Real | Binary |
    +======================================+==========+===========+===========+==========+=========+======+========+
    | bit_flip_mutation                    |    X     |     X     |           |          |    X    |      |    X   |
    +--------------------------------------+----------+-----------+-----------+----------+---------+------+--------+
    | blend_crossover                      |    X     |           |           |          |    X    |   X  |        |
    +--------------------------------------+----------+-----------+-----------+----------+---------+------+--------+
    | default_variation                    |          |           |           |          |         |      |        |
    +--------------------------------------+----------+-----------+-----------+----------+---------+------+--------+
    | differential_crossover               |          |           |           |          |    X    |      |        |
    +--------------------------------------+----------+-----------+-----------+----------+---------+------+--------+
    | estimation_of_distribution_variation |          |     X     |           |          |    X    |   X  |        |
    +--------------------------------------+----------+-----------+-----------+----------+---------+------+--------+
    | gaussian_mutation                    |    X     |     X     |           |          |    X    |   X  |        |
    +--------------------------------------+----------+-----------+-----------+----------+---------+------+--------+
    | n_point_crossover                    |          |           |     X     |     X    |    X    |      |        |
    +--------------------------------------+----------+-----------+-----------+----------+---------+------+--------+
    | uniform_crossover                    |    X     |           |           |          |         |      |        |
    +--------------------------------------+----------+-----------+-----------+----------+---------+------+--------+
    
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
import copy


def default_variation(random, candidates, args):
    """Return the set of candidates without variation.

    .. Arguments:
       random -- the random number generator object
       candidates -- the candidate solutions
       args -- a dictionary of keyword arguments
    
    """
    return candidates


def n_point_crossover(random, candidates, args):
    """Return the offspring of n-point crossover on the candidates.

    This function assumes that the candidate solutions are sliceable.
    It selects n random points without replacement at which to 'cut'
    the candidate solutions and recombine them.

    .. Arguments:
       random -- the random number generator object
       candidates -- the candidate solutions
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    - *crossover_rate* -- the rate at which crossover is performed 
      (default 1.0)
    - *num_crossover_points* -- the n crossover points used (default 1)
    
    """
    crossover_rate = args.setdefault('crossover_rate', 1.0)
    num_crossover_points = args.setdefault('num_crossover_points', 1)
    cand = list(candidates)
    if len(cand) % 2 == 1:
        cand = cand[:-1]
    random.shuffle(cand)
    moms = cand[::2]
    dads = cand[1::2]
    children = []
    for mom, dad in zip(moms, dads):
        if random.random() < crossover_rate:
            bro = list(mom)
            sis = list(dad)
            num_cuts = min(len(mom)-1, num_crossover_points)
            cut_points = random.sample(range(1, len(mom)), num_cuts)
            cut_points.sort()
            for p in cut_points:
                bro[p:] = dad[p:]
                sis[:p] = mom[:p]
            children.append(bro)
            children.append(sis)
        else:
            children.append(mom)
            children.append(dad)            
    return children


def uniform_crossover(random, candidates, args):
    """Return the offspring of uniform crossover on the candidates.

    This function assumes that the candidate solutions are iterable.
    It chooses every odd candidate as a 'mom' and every even as a 'dad'.
    For each mom-dad pair, two offspring are produced. For each element
    of the parents, a biased coin is flipped to determine whether the 
    first offspring gets the 'mom' or the 'dad' element. An optional
    keyword argument in args, pux_bias, determines the bias.

    .. Arguments:
       random -- the random number generator object
       candidates -- the candidate solutions
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    - *crossover_rate* -- the rate at which crossover is performed 
      (default 1.0)
    - *pux_bias* -- the bias toward the first candidate in the crossover 
      (default 0.5)
    
    """
    pux_bias = args.setdefault('pux_bias', 0.5)
    crossover_rate = args.setdefault('crossover_rate', 1.0)
    cand = list(candidates)
    if len(cand) % 2 == 1:
        cand = cand[:-1]
    random.shuffle(cand)
    moms = cand[::2]
    dads = cand[1::2]
    children = []
    for mom, dad in zip(moms, dads):
        if random.random() < crossover_rate:
            bro = []
            sis = []
            for m, d in zip(mom, dad):
                if random.random() < pux_bias:
                    bro.append(m)
                    sis.append(d)
                else:
                    bro.append(d)
                    sis.append(m)
            children.append(bro)
            children.append(sis)
        else:
            children.append(mom)
            children.append(dad)
    return children

    
def blend_crossover(random, candidates, args):
    """Return the offspring of blend crossover on the candidates.

    This function assumes that the candidate solutions are iterable
    and composed of values on which arithmetic operations are defined.
    It performs blend crossover, which is similar to a generalized 
    averaging of the candidate elements.

    .. Arguments:
       random -- the random number generator object
       candidates -- the candidate solutions
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    - *crossover_rate* -- the rate at which crossover is performed 
      (default 1.0)
    - *blx_alpha* -- the blending rate (default 0.1)
    - *lower_bound* -- the lower bounds of the chromosome elements (default 0)
    - *upper_bound* -- the upper bounds of the chromosome elements (default 1)
    
    The lower and upper bounds can either be single values, which will
    be applied to all elements of a chromosome, or lists of values of 
    the same length as the chromosome.
    
    """
    blx_alpha = args.setdefault('blx_alpha', 0.1)
    crossover_rate = args.setdefault('crossover_rate', 1.0)
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
        
    cand = list(candidates)
    if len(cand) % 2 == 1:
        cand = cand[:-1]
    random.shuffle(cand)
    moms = cand[::2]
    dads = cand[1::2]
    children = []
    for mom, dad in zip(moms, dads):
        if random.random() < crossover_rate:
            bro = []
            sis = []
            for index, (m, d) in enumerate(zip(mom, dad)):
                smallest = min(m, d)
                largest = max(m, d)
                delta = blx_alpha * (largest - smallest)
                bro_val = smallest - delta + random.random() * (largest - smallest + 2 * delta)
                sis_val = smallest - delta + random.random() * (largest - smallest + 2 * delta)
                bro_val = max(min(bro_val, upper_bound[index]), lower_bound[index])
                sis_val = max(min(sis_val, upper_bound[index]), lower_bound[index])
                bro.append(bro_val)
                sis.append(sis_val)
            children.append(bro)
            children.append(sis)
        else:
            children.append(mom)
            children.append(dad)
    return children
    
def differential_crossover(random, candidates, args):
    """Return the offspring of differential crossover on the candidates.

    This function assumes that the candidate solutions are iterable
    and composed of values on which arithmetic operations are defined.
    It performs differential crossover, which is similar to the update
    rule used in particle swarm optimization.

    .. Arguments:
       random -- the random number generator object
       candidates -- the candidate solutions
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    - *crossover_rate* -- the rate at which crossover is performed 
      (default 1.0)
    - *differential_phi* -- the amount of random change in the crossover 
      (default 0.1)
    - *lower_bound* -- the lower bounds of the chromosome elements (default 0)
    - *upper_bound* -- the upper bounds of the chromosome elements (default 1)
    
    The lower and upper bounds can either be single values, which will
    be applied to all elements of a chromosome, or lists of values of 
    the same length as the chromosome.
    
    """
    differential_phi = args.setdefault('differential_phi', 0.1)
    crossover_rate = args.setdefault('crossover_rate', 1.0)
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
        
    # Be careful shuffling the candidates so that 
    # we will know which is better. 
    cand = list(candidates)
    if len(cand) % 2 == 1:
        cand = cand[:-1]
    cand_pair = [(pos, ind) for pos, ind in enumerate(cand)]
    random.shuffle(cand_pair)
    moms = cand_pair[::2]
    dads = cand_pair[1::2]
    children = []
    for mom, dad in zip(moms, dads):
        if random.random() < crossover_rate:
            bro = []
            sis = []
            for index, (m, d) in enumerate(zip(mom[1], dad[1])):
                if mom[0] > dad[0]:
                    negpos = 1
                    val = d
                else:
                    negpos = -1
                    val = m
                bro_val = val + differential_phi * random.random() * negpos * (m - d)
                sis_val = val + differential_phi * random.random() * negpos * (m - d)
                bro_val = max(min(bro_val, upper_bound[index]), lower_bound[index])
                sis_val = max(min(sis_val, upper_bound[index]), lower_bound[index])
                bro.append(bro_val)
                sis.append(sis_val)
            children.append(bro)
            children.append(sis)
        else:
            children.append(mom[1])
            children.append(dad[1])
    return children
    
def simulated_binary_crossover(random, candidates, args):
    """
    Adapted from pyevolve's implementation by Amit Saha
    
    Experimental SBX Implementation -- Follows the implementation in NSGA-II (Deb, et.al)
 
    Some implementation `reference <http://vision.ucsd.edu/~sagarwal/icannga.pdf>`_.
 
    warning:: This crossover method is Data Type Dependent, which means that
    must be used for 1D genome of real values.
    """
    # SBX specifix
    eta_c = args.setdefault('sbx_etac', 10)
    EPS = args.setdefault('sbx_eps', 1.0e-14)

    # general
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
        
    
    cand = list(candidates)
    if len(cand) % 2 == 1:
        cand = cand[:-1]
    random.shuffle(cand)
    moms = cand[::2]
    dads = cand[1::2]
    
    sister = copy.deepcopy(moms)
    brother = copy.deepcopy(dads)
    
    children = []
    for i in range(0,len(moms)):
        for j in range(len(moms[i])):
            if math.fabs(moms[i][j]-dads[i][j]) > EPS:
                lb, ub = lower_bound[j], upper_bound[j]
                if moms[i][j] > dads[i][j]:
                    #swap
                    temp = moms[i][j]
                    moms[i][j] = dads[i][j]
                    dads[i][j] = temp
    
                #random number betwn. 0 & 1
                u = random.random() 
                beta = 1.0 + 2*(moms[i][j] - lb)/(1.0*(dads[i][j]-moms[i][j]))
                alpha = 2.0 - beta**(-(eta_c+1.0))
    
                if u <= (1.0/alpha):
                    beta_q = (u*alpha)**(1.0/((eta_c + 1.0)*1.0))
                else:
                    beta_q = (1.0/(2.0-u*alpha))**(1.0/(1.0*(eta_c + 1.0)))
        
                brother[i][j] = 0.5*((moms[i][j] + dads[i][j]) - beta_q*(dads[i][j]-moms[i][j]))
        
                beta = 1.0 + 2.0*(ub - dads[i][j])/(1.0*(dads[i][j]-moms[i][j]))
                alpha = 2.0 - beta**(-(eta_c+1.0))
        
                if u <= (1.0/alpha):
                    beta_q = (u*alpha)**(1.0/((eta_c + 1)*1.0))
                else:
                    beta_q = (1.0/(2.0-u*alpha))**(1.0/(1.0*(eta_c + 1.0)))
        
                sister[i][j] = 0.5*((moms[i][j] + dads[i][j]) + beta_q*(dads[i][j]-moms[i][j]))
    
                if brother[i][j] > ub:
                    brother[i][j] = ub
                if brother[i][j] < lb:
                    brother[i][j] = lb
        
                if sister[i][j] > ub:
                    sister[i][j] = ub
                if sister[i][j] < lb:
                    sister[i][j] = lb
    
                if random.random() > 0.5:
                    # Swap
                    temp = sister[i][j]
                    sister[i][j] = brother[i][j]
                    brother[i][j] = temp
            else:
                sister[i][j] = moms[i][j]
                brother[i][j] = dads[i][j]
        children.append(brother[i])
        children.append(sister[i])
    return children
            
        
    
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

    
def estimation_of_distribution_variation(random, candidates, args):
    """Return the offspring produced using estimation of distribution.

    This function assumes that the candidate solutions are iterable 
    objects containing real values. It creates a statistical model 
    based on the set of candidates. The offspring are then generated 
    from this model.

    .. Arguments:
       random -- the random number generator object
       candidates -- the candidate solutions
       args -- a dictionary of keyword arguments
    
    Optional keyword arguments in args:
    
    - *num_offspring* -- the number of offspring to create (default 1)
    - *lower_bound* -- the lower bounds of the chromosome elements (default 0)
    - *upper_bound* -- the upper bounds of the chromosome elements (default 1)
    
    The lower and upper bounds can either be single values, which will
    be applied to all elements of a chromosome, or lists of values of 
    the same length as the chromosome.
    
    """
    num_offspring = args.setdefault('num_offspring', 1)
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
    num_genes = max([len(x) for x in cs_copy])
    genes = [[x[i] for x in cs_copy] for i in range(num_genes)] 
    mean = [float(sum(x)) / float(len(x)) for x in genes]
    stdev = [max(sum([(x - m)**2 for x in g]) / float(len(g) - 1), 0.001) for g, m in zip(genes, mean)]
    offspring = []
    for _ in range(num_offspring):
        child = []
        for m, s, hi, lo in zip(mean, stdev, upper_bound, lower_bound):
            value = m + random.gauss(0, s);
            value = max(min(value, hi), lo)
            child.append(value)
        offspring.append(child)
        
    return offspring
