"""
    This module provides the framework for making multiobjective evolutionary computations.
    
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
from ecspy import ec
from ecspy import archivers
from ecspy import selectors
from ecspy import replacers
from ecspy import terminators
from ecspy import variators


class Pareto(object):
    """Represents a Pareto multiobjective solution.
    
    A Pareto solution is a multiobjective value that can be compared
    to other Pareto values using Pareto preference. This means that
    a solution dominates, or is better than, another solution if it is
    better than or equal to the other solution in all objectives and
    strictly better in at least one objective.
    
    """
    def __init__(self, values=[]):
        self.values = values
        
    def __len__(self):
        return len(self.values)
    
    def __getitem__(self, key):
        return self.values[key]
        
    def __iter__(self):
        return iter(self.values)
    
    def __lt__(self, other):
        if len(self.values) != len(other.values):
            return NotImplemented
        else:
            not_worse = True
            strictly_better = False
            for x, y in zip(self.values, other.values):
                if x > y:
                    not_worse = False
                elif y > x:
                    strictly_better = True
            return not_worse and strictly_better
            
    def __le__(self, other):
        return self < other or not other < self
        
    def __gt__(self, other):
        return other < self
        
    def __ge__(self, other):
        return other < self or not self < other
    
    def __str__(self):
        return str(self.values)
        
    def __repr__(self):
        return str(self.values)


def hypervolume(pareto_set, reference_point=None):
    """Calculates the hypervolume by slicing objectives (HSO).
    
    This function calculates the hypervolume (or S-measure) of a nondominated
    set using the Hypervolume by Slicing Objectives (HSO) procedure of While,
    et. al. The *pareto_set* should be a list of lists of objective values.
    The *reference_point* may be specified or it may be left as the default 
    value of None. In that case, the reference point is calculated to be the
    maximum value in the set for all objectives (the ideal point). As with 
    all other functions, this function assumes that objectives are to be
    maximized.
    
    Arguments:
    
    - *pareto_set* -- the list of objective values comprising the Pareto front
    - *reference_point* -- the reference point to be used (default None)
    
    """
    def dominates(p, q, k=None):
        if k is None:
            k = len(p)
        d = True
        while d and k < len(p):
            d = not (q[k] > p[k])
            k += 1
        return d
        
    def insert(p, k, pl):
        ql = []
        while pl and pl[0][k] > p[k]:
            ql.append(pl[0])
            pl = pl[1:]
        ql.append(p)
        while pl:
            if not dominates(p, pl[0], k):
                ql.append(pl[0])
            pl = pl[1:]
        return ql

    def slice(pl, k, ref):
        p = pl[0]
        pl = pl[1:]
        ql = []
        s = []
        while pl:
            ql = insert(p, k + 1, ql)
            p_prime = pl[0]
            s.append((math.fabs(p[k] - p_prime[k]), ql))
            p = p_prime
            pl = pl[1:]
        ql = insert(p, k + 1, ql)
        s.append((math.fabs(p[k] - ref[k]), ql))
        return s

    ps = pareto_set
    ref = reference_point
    n = min([len(p) for p in ps])
    if ref is None:
        ref = [max(ps, key=lambda x: x[o])[o] for o in xrange(n)]
    pl = ps[:]
    #pl.sort(key=lambda x: x[0], reverse=True)
    pl.sort(reverse=True)
    s = [(1, pl)]
    for k in xrange(n - 1):
        s_prime = []
        for x, ql in s:
            for x_prime, ql_prime in slice(ql, k, ref):
                s_prime.append((x * x_prime, ql_prime))
        s = s_prime
    vol = 0
    for x, ql in s:
        vol = vol + x * math.fabs(ql[0][n - 1] - ref[n - 1])
    return vol


class NSGA2(ec.EvolutionaryComputation):
    """Evolutionary computation representing the nondominated sorting genetic algorithm.
    
    This class represents the nondominated sorting genetic algorithm (NSGA-II)
    of Kalyanmoy Deb et al. It uses nondominated sorting with crowding for 
    replacement, binary tournament selection to produce *population size*
    children, and a Pareto archival strategy. The remaining operators take 
    on the typical default values but they may be specified by the designer.
    
    """
    def __init__(self, random):
        ec.EvolutionaryComputation.__init__(self, random)
        self.archiver = archivers.best_archiver
        self.replacer = replacers.nsga_replacement
        self.selector = selectors.tournament_selection
    
    def evolve(self, generator, evaluator, pop_size=100, seeds=[], terminator=terminators.default_termination, **args):
        try:
            args['num_selected']
        except KeyError:
            args['num_selected'] = pop_size
        try:
            args['tourn_size']
        except KeyError:
            args['tourn_size'] = 2
        return ec.EvolutionaryComputation.evolve(self, generator, evaluator, pop_size, seeds, terminator, **args)

    
class PAES(ec.EvolutionaryComputation):
    """Evolutionary computation representing the Pareto Archived Evolution Strategy.
    
    This class represents the Pareto Archived Evolution Strategy of Joshua
    Knowles and David Corne. It is essentially a (1+1)-ES with an adaptive
    grid archive that is used as a part of the replacement process. 
    
    """
    def __init__(self, random):
        ec.EvolutionaryComputation.__init__(self, random)
        self.archiver = archivers.adaptive_grid_archiver
        self.selector = selectors.default_selection
        self.variator = variators.gaussian_mutation
        self.replacer = replacers.paes_replacement  

    def evolve(self, generator, evaluator, pop_size=1, seeds=[], terminator=terminators.default_termination, **args):
        final_arc = ec.EvolutionaryComputation.evolve(self, generator, evaluator, pop_size, seeds, terminator, **args)
        try:
            del self.archiver.grid_population
        except AttributeError:
            pass
        try:
            del self.archiver.global_smallest
        except AttributeError:
            pass
        try:
            del self.archiver.global_largest
        except AttributeError:
            pass
        return final_arc
    

