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
            raise NotImplementedError
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
    
    def evolve(self, generator, evaluator, pop_size=100, seeds=[], terminator=terminators.default_termination, maximize=True, **args):
        try:
            args['num_selected']
        except KeyError:
            args['num_selected'] = pop_size
        try:
            args['tourn_size']
        except KeyError:
            args['tourn_size'] = 2
        return ec.EvolutionaryComputation.evolve(self, generator, evaluator, pop_size, seeds, terminator, maximize, **args)

    
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

    def evolve(self, generator, evaluator, pop_size=1, seeds=[], terminator=terminators.default_termination, maximize=True, **args):
        final_arc = ec.EvolutionaryComputation.evolve(self, generator, evaluator, pop_size, seeds, terminator, maximize, **args)
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
    

