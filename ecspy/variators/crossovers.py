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


def crossover(cross):
    """Return an ecspy crossover function based on the given function.

    This function generator takes a function that operates on only
    two parent candidates to produce an iterable list of offspring
    (typically two). The generator handles the pairing of selected
    parents and collecting of all offspring.

    The generated function chooses every odd candidate as a 'mom' and
    every even as a 'dad' (discounting the last candidate if there is
    and odd number). For each mom-dad pair, offspring are produced via
    the `cross` function.

    The given function ``cross`` must have the following signature::

        offspring = cross(random, mom, dad, args)

    This function is most commonly used as a function decorator with
    the following usage::

        @crossover
        def cross(random, mom, dad, args):
            # Implementation of paired crossing

    The generated function also contains an attribute named
    ``single_crossover`` which holds the original crossover function.
    In this way, the original single-candidate function can be
    retrieved if necessary.

    """
    def ecspy_crossover(random, candidates, args):
        cand = list(candidates)
        if len(cand) % 2 == 1:
            cand = cand[:-1]
        moms = cand[::2]
        dads = cand[1::2]
        children = []
        for i, (mom, dad) in enumerate(zip(moms, dads)):
            cross.index = i
            offspring = cross(random, mom, dad, args)
            for o in offspring:
                children.append(o)
        return children
    ecspy_crossover.__name__ = cross.__name__
    ecspy_crossover.__dict__ = cross.__dict__
    ecspy_crossover.__doc__ = cross.__doc__
    ecspy_crossover.single_crossover = cross
    return ecspy_crossover


@crossover
def n_point_crossover(random, mom, dad, args):
    """Return the offspring of n-point crossover on the candidates.

    This function assumes that the candidate solutions are sliceable.
    It selects n random points without replacement at which to 'cut'
    the candidate solutions and recombine them.

    .. Arguments:
       random -- the random number generator object
       mom -- the first parent candidate
       dad -- the second parent candidate
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    - *crossover_rate* -- the rate at which crossover is performed 
      (default 1.0)
    - *num_crossover_points* -- the n crossover points used (default 1)
    
    """
    crossover_rate = args.setdefault('crossover_rate', 1.0)
    num_crossover_points = args.setdefault('num_crossover_points', 1)
    children = []
    if random.random() < crossover_rate:
        num_cuts = min(len(mom)-1, num_crossover_points)
        cut_points = random.sample(range(1, len(mom)), num_cuts)
        cut_points.sort()
        bro = copy.copy(dad)
        sis = copy.copy(mom)
        normal = True
        for i, (m, d) in enumerate(zip(mom, dad)):
            if i in cut_points:
                normal = not normal
            if not normal:
                bro[i] = m
                sis[i] = d
        children.append(bro)
        children.append(sis)
    else:
        children.append(mom)
        children.append(dad)
    return children


@crossover
def uniform_crossover(random, mom, dad, args):
    """Return the offspring of uniform crossover on the candidates.

    This function assumes that the candidate solutions are iterable.
    For each element of the parents, a biased coin is flipped to 
    determine whether the first offspring gets the 'mom' or the 
    'dad' element. An optional keyword argument in args, ``pux_bias``, 
    determines the bias.

    .. Arguments:
       random -- the random number generator object
       mom -- the first parent candidate
       dad -- the second parent candidate
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    - *crossover_rate* -- the rate at which crossover is performed 
      (default 1.0)
    - *pux_bias* -- the bias toward the first candidate in the crossover 
      (default 0.5)
    
    """
    pux_bias = args.setdefault('pux_bias', 0.5)
    crossover_rate = args.setdefault('crossover_rate', 1.0)
    children = []
    if random.random() < crossover_rate:
        bro = copy.copy(dad)
        sis = copy.copy(mom)
        for i, (m, d) in enumerate(zip(mom, dad)):
            if random.random() < pux_bias:
                bro[i] = m
                sis[i] = d
        children.append(bro)
        children.append(sis)
    else:
        children.append(mom)
        children.append(dad)
    return children


@crossover
def blend_crossover(random, mom, dad, args):
    """Return the offspring of blend crossover on the candidates.

    This function assumes that the candidate solutions are iterable
    and composed of values on which arithmetic operations are defined.
    It performs blend crossover, which is similar to a generalized 
    averaging of the candidate elements. This function also 
    makes use of the bounder function as specified in the EC's 
    ``evolve`` method.

    .. Arguments:
       random -- the random number generator object
       mom -- the first parent candidate
       dad -- the second parent candidate
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    - *crossover_rate* -- the rate at which crossover is performed 
      (default 1.0)
    - *blx_alpha* -- the blending rate (default 0.1)
    
    """
    blx_alpha = args.setdefault('blx_alpha', 0.1)
    crossover_rate = args.setdefault('crossover_rate', 1.0)
    bounder = args['_ec'].bounder
    children = []
    if random.random() < crossover_rate:
        bro = copy.copy(dad)
        sis = copy.copy(mom)
        for i, (m, d) in enumerate(zip(mom, dad)):
            smallest = min(m, d)
            largest = max(m, d)
            delta = blx_alpha * (largest - smallest)
            bro[i] = smallest - delta + random.random() * (largest - smallest + 2 * delta)
            sis[i] = smallest - delta + random.random() * (largest - smallest + 2 * delta)
        bro = bounder(bro, args)
        sis = bounder(sis, args)
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
    rule used in particle swarm optimization. This function also 
    makes use of the bounder function as specified in the EC's 
    ``evolve`` method.

    .. Arguments:
       random -- the random number generator object
       candidates -- the candidate solutions
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    - *crossover_rate* -- the rate at which crossover is performed 
      (default 1.0)
    - *differential_phi* -- the amount of random change in the crossover 
      (default 0.1)
    
    """
    differential_phi = args.setdefault('differential_phi', 0.1)
    crossover_rate = args.setdefault('crossover_rate', 1.0)
    bounder = args['_ec'].bounder
        
    cand = list(candidates)
    if len(cand) % 2 == 1:
        cand = cand[:-1]
        
    # Since we don't have fitness information in the candidates, we need 
    # to make a dictionary containing the candidate and its corresponding 
    # individual in the population.
    population = args['_ec'].population[:]
    lookup = dict(zip([tuple(p.candidate) for p in population], population))
    
    moms = cand[::2]
    dads = cand[1::2]
    children = []
    for mom, dad in zip(moms, dads):
        if random.random() < crossover_rate:
            bro = copy.copy(dad)
            sis = copy.copy(mom)
            mom_is_better = lookup[tuple(mom)] > lookup[tuple(dad)]
            for i, (m, d) in enumerate(zip(mom, dad)):
                negpos = 1 if mom_is_better else -1
                val = d if mom_is_better else m
                bro[i] = val + differential_phi * random.random() * negpos * (m - d)
                sis[i] = val + differential_phi * random.random() * negpos * (m - d)
            bro = bounder(bro, args)
            sis = bounder(sis, args)
            children.append(bro)
            children.append(sis)
        else:
            children.append(mom)
            children.append(dad)
    return children
    

@crossover
def simulated_binary_crossover(random, mom, dad, args):
    """Return the offspring of simulated binary crossover on the candidates.
    
    This function performs simulated binary crosssover, following the 
    implementation in NSGA-II 
    `(Deb et al., ICANNGA 1999) <http://vision.ucsd.edu/~sagarwal/icannga.pdf>`_.
 
    .. Arguments:
       random -- the random number generator object
       mom -- the first parent candidate
       dad -- the second parent candidate
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    - *sbx_etac* -- the non-negative distribution index (default 10)
    
    A small value of the `sbx_etac` optional argument allows solutions 
    far away from parents to be created as children solutions, while a 
    large value restricts only near-parent solutions to be created as
    children solutions.
    
    """
    etac = args.setdefault('sbx_etac', 10)
    bounder = args['_bounder']
    bro = copy.copy(dad)
    sis = copy.copy(mom)
    for i, (m, d, lb, ub) in enumerate(zip(mom, dad, bounder.lower_bound, bounder.upper_bound)):
        try:
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
            bro[i] = bro_val
            sis[i] = sis_val
        except ZeroDivisionError:
            # The offspring already have legitimate values for every element,
            # so no need to take any special action here.
            pass
    return [bro, sis]


@crossover
def laplace_crossover(random, mom, dad, args):
    a = args.setdefault('laplace_a', 1)
    b = args.setdefault('laplace_b', 0)
    bro = copy.copy(dad)
    sis = copy.copy(mom)
    for i, (m, d) in enumerate(zip(mom, dad)):
        u = random.random()
        if random.random() <= 0.5:
            beta = a - b * math.log(u)
        else:
            beta = a + b * math.log(u)
        bro[i] = m + beta * math.abs(m - d)
        sis[i] = d + beta * math.abs(m - d)
    return [bro, sis]
    







