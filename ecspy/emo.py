"""
    This module provides the framework for making multiobjective evolutionary computations.
    
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

from ecspy import ec
from ecspy import archivers


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
        
    
class EMO(ec.EvolutionaryComputation):
    """Evolutionary computation representing an evolutionary multiobjective optimization.
    
    This class represents a basic evolutionary multiobjective optimization
    algorithm. It only specifies that the Pareto archiver should be used.
    The remaining specifications (e.g., selection, variation, etc.) are 
    left for the designer to choose.
    
    """
    def __init__(self, random):
        ec.EvolutionaryComputation.__init__(self, random)
        self.archiver = archivers.pareto_archiver
