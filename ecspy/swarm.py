"""
    This module provides capabilities for creating swarm intelligence algorithms.
    
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
from ecspy import ec
from ecspy import archivers
from ecspy import observers
from ecspy import terminators
from ecspy import topologies



class PSO(ec.EvolutionaryComputation):
    """Represents a basic particle swarm optimization algorithm.
    
    This class is built upon the ``EvolutionaryComputation`` class making
    use of an external archive and maintaining the population at the previous
    timestep, rather than a velocity. This approach was outlined in 
    (Deb and Padhye, "Development of Efficient Particle Swarm Optimizers by
    Using Concepts from Evolutionary Algorithms", GECCO 2010, pp. 55--62).
    
    Public Attributes:
    
    - *topology* -- the neighborhood topology (default topologies.star_topology)
    
    Optional keyword arguments in ``evolve`` args parameter:
    
    - *inertia* -- the inertia constant to be used in the particle 
      updating
    - *cognitive_rate* -- the rate at which the particle's current 
      position influences its movement (default 2.1)
    - *social_rate* -- the rate at which the particle's neighbors 
      influence its movement (default 2.1)
    
    """
    def __init__(self, random):
        ec.EvolutionaryComputation.__init__(self, random)
        self.topology = topologies.star_topology
        self._previous_population = []
        self.selector = self._swarm_selector
        self.replacer = self._swarm_replacer
        self.variator = self._swarm_variator
        
    def _swarm_archiver(self, random, population, archive, args):
        if len(archive) == 0:
            return population[:]
        else:
            new_archive = []
            for i, (p, a) in enumerate(zip(population[:], archive[:])):
                if p < a:
                    new_archive.append(a)
                else:
                    new_archive.append(p)
            return new_archive
        
    def _swarm_variator(self, random, candidates, args):
        inertia = args.setdefault('inertia', 0.5)
        cognitive_rate = args.setdefault('cognitive_rate', 1.0)
        social_rate = args.setdefault('social_rate', 1.0)
        if len(self.archive) == 0:
            self.archive = self.population[:]
        if len(self._previous_population) == 0:
            self._previous_population = self.population[:]
        neighbors = self.topology(self._random, self.archive, args)
        offspring = []
        for x, xprev, pbest, hood in zip(self.population, self._previous_population, self.archive, neighbors):
            nbest = max(hood)
            particle = []
            for xi, xpi, pbi, nbi in zip(x.candidate, xprev.candidate, pbest.candidate, nbest.candidate):
                value = xi + inertia * (xi - xpi) + cognitive_rate * random.random() * (pbi - xi) + social_rate * random.random() * (nbi - xi)
                particle.append(value)
            particle = self.bounder(particle, args)
            offspring.append(particle)
        return offspring
        
    def _swarm_selector(self, random, population, args):
        return population
        
    def _swarm_replacer(self, random, population, parents, offspring, args):
        self._previous_population = population[:]
        return offspring

    
