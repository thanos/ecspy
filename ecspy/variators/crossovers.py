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

import math
import copy


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
    """Return the offspring of simulated binary crossover on the candidates.
    
    This function performs simulated binary crosssover. It was adapted 
    from pyevolve's implementation by Amit Saha, which follows the 
    implementation in NSGA-II 
    `(Deb, et. al, ICANNGA 1999) <http://vision.ucsd.edu/~sagarwal/icannga.pdf>`_.
 
    .. Arguments:
       random -- the random number generator object
       candidates -- the candidate solutions
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    - *sbx_etac* -- the non-negative distribution index (default 10)
    - *lower_bound* -- the lower bounds of the chromosome elements (default 0)
    - *upper_bound* -- the upper bounds of the chromosome elements (default 1)
    
    The lower and upper bounds can either be single values, which will
    be applied to all elements of a chromosome, or lists of values of 
    the same length as the chromosome.
    
    A small value of the `sbx_etac` optional argument allows solutions 
    far away from parents to be created as children solutions, while a 
    large value restricts only near-parent solutions to be created as
    children solutions.
    
    """

    etac = args.setdefault('sbx_etac', 10)
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
        bro = []
        sis = []
        for index, (m, d) in enumerate(zip(mom, dad)):
            try:
                lb, ub = lower_bound[index], upper_bound[index]
                if m > d:
                    m, d = d, m
                beta = 1.0 + 2 * min(m - lb, ub - d) / float(d - m)
                alpha = 2.0 - 1.0 / beta**(eta_c + 1.0)
                u = random.random() 
                if u <= (1.0 / alpha):
                    beta_q = (u * alpha)**(1.0 / float(eta_c + 1.0))
                else:
                    beta_q = (1.0 / (2.0 - u * alpha))**(1.0 / float(eta_c + 1.0))
                bro_val = 0.5 * ((m + d) - beta_q * (d - m))
                bro_val = max(min(bro_val, ub), lb)        
                sis_val = 0.5 * ((m + d) + beta_q * (d - m))
                sis_val = max(min(sis_val, ub), lb)
                if random.random() > 0.5:
                    bro_val, sis_val = sis_val, bro_val
                bro.append(bro_val)
                sis.append(sis_val)
            except ZeroDivisionError:
                sis.append(m)
                bro.append(d)
        children.append(bro)
        children.append(sis)
    return children

