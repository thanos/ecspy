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


class Particle(ec.Individual):
    """Represents a particle in a swarm.
    
    An particle is an Individual that also contains a current location,
    with an associated fitness, and a velocity.
    
    Public Attributes:
    
    - *candidate* -- the candidate solution (the particle's personal best)
    - *fitness* -- the value of the candidate solution (personal best fitness)
    - *birthdate* -- the system time at which the individual was created
    - *x* -- the particle's current location
    - *xfitness* -- the fitness of the current location
    - *v* -- the particle's velocity
    
    """
    def __init__(self, candidate=None, maximize=True):
        ec.Individual.__init__(self, candidate, maximize)
        self.x = candidate
        self.xfitness = None
        self.v = [0.0] * len(candidate)
        
    def __setattr__(self, name, val):
        if name == 'x':
            self.__dict__[name] = val
            self.xfitness = None
        elif name == 'candidate':
            self.__dict__[name] = val
            self.fitness = None
        else:
            self.__dict__[name] = val

    def __str__(self):
        return '%s : %s' % (str(self.candidate), str(self.fitness))
        
    def __repr__(self):
        return 'x: %s : %s\np: %s : %s\nv: %s\n' % (str(self.x), str(self.xfitness), str(self.candidate), str(self.fitness), str(self.v))
        

class PSO(object):
    """Represents a basic particle swarm optimization algorithm.
    
    This class encapsulates the components of a particle swarm
    optimization. These components are the selection mechanism, the
    variation operators, the replacement mechanism, the migration
    scheme, and the observers.
    
    Public Attributes:
    
    - *archiver* -- the archival operator
    - *observer* -- the (possibly list of) observer(s)
    - *terminator* -- the (possibly list of) terminator(s)
    - *topology* -- the neighborhood topology (default topologies.star_topology)
    
    Protected Attributes:
    
    - *_random* -- the random number generator object
    - *_kwargs* -- the dictionary of keyword arguments initialized
      from the *args* parameter in the *swarm* method
    
    Public Methods:
    
    - ``swarm`` -- performs the swarming and returns the final
      archive of particles
    
    """
    def __init__(self, random):
        self._random = random
        self.observer = observers.default_observer
        self.archiver = archivers.default_archiver
        self.terminator = terminators.default_termination
        self.topology = topologies.star_topology
        self._kwargs = dict()

    def _should_terminate(self, pop, ng, ne):
        terminate = False
        fname = ''
        try:
            for clause in self.terminator:
                terminate = terminate or clause(population=pop, num_generations=ng, num_evaluations=ne, args=self._kwargs)
                if terminate:
                    fname = clause.__name__
                    break
        except TypeError:
            terminate = self.terminator(population=pop, num_generations=ng, num_evaluations=ne, args=self._kwargs)
            fname = self.terminator.__name__
        if terminate:
            print('TERMINATED DUE TO %s' % fname)
        return terminate

    def _move(self, population, args):
        lower_bound = args.setdefault('lower_bound', 0.0)
        upper_bound = args.setdefault('upper_bound', 1.0)
        cognitive_rate = args.setdefault('cognitive_rate', 2.1)
        social_rate = args.setdefault('social_rate', 2.1)
        use_constriction_coefficient = args.setdefault('use_constriction_coefficient', False)
                
        K = 1.0
        if(use_constriction_coefficient):
            phi = cognitive_rate + social_rate
            K = 2.0 / abs(2.0 - phi - math.sqrt(phi**2 - (4.0 * phi)))

        neighbors = self.topology(self._random, population, args)
        for index, (particle, neighborhood) in enumerate(zip(population, neighbors)):
            gbest = neighborhood[0]
            for neighbor in neighborhood:
                if neighbor > gbest:
                    gbest = neighbor
                        
            for i, (x, v, p, g) in enumerate(zip(particle.x, particle.v, particle.candidate, gbest.candidate)):
                r1 = self._random.random()
                r2 = self._random.random()
                v = K * (v + cognitive_rate * r1 * (p - x) + social_rate * r2 * (g - x))
                x = x + v
                if x < lower_bound or x > upper_bound:
                    x = max(min(x, upper_bound), lower_bound)
                    v = 0.0
                particle.v[i] = v
                particle.x[i] = x
        
        return population

    def swarm(self, generator, evaluator, 
              pop_size=100, 
              seeds=[], 
              maximize=True,
              **args):
        """Perform the swarming.
        
        This function creates a swarm and allows the particles to fly around
        the search space until the terminator is satisfied. The function 
        returns the particles in the final archive (which, by default, is
        just the final population).
        
        Arguments:
        
        - *generator* -- the function to be used to generate candidate solutions 
        - *evaluator* -- the function to be used to evaluate candidate solutions
        - *pop_size* -- the number of Individuals in the population (default 100)
        - *seeds* -- an iterable collection of candidate solutions to include
          in the initial population (default [])
        - *maximize* -- Boolean value stating use of maximization (default True)
        - *args* -- a dictionary of keyword arguments

        Optional keyword arguments in args:
        
        - *lower_bound* -- the lower bounds of the chromosome elements 
          (default 0)
        - *upper_bound* -- the upper bounds of the chromosome elements 
          (default 1)
        - *cognitive_rate* -- the rate at which the particle's current 
          position influences its movement (default 2.1)
        - *social_rate* -- the rate at which the particle's neighbors 
          influence its movement (default 2.1)
        - *use_constriction_coefficient* -- whether Clerc's constriction 
          coefficient should be used (default False)
        
        Note that the *_kwargs* class variable will be initialized to the args 
        parameter here. It will also be modified to include the following 'built-in' 
        keyword arguments (each preceded by an underscore) unless these arguments 
        are already present (which shouldn't be the case):
        
        - *_generator* -- the generator used for creating candidate solutions
        - *_evaluator* -- the evaluator used for evaluating solutions
        - *_population_size* -- the size of the population
        - *_num_generations* -- the number of generations that have elapsed
        - *_num_evaluations* -- the number of evaluations that have been completed
        - *_population* -- the current population
        - *_archive* -- the current archive
        - *_evolutionary_computation* -- the evolutionary computation (this object)
        
        """
        self._kwargs = args
        # Add entries to the keyword arguments dictionary
        # if they're not already present.
        self._kwargs.setdefault('_generator', generator)
        self._kwargs.setdefault('_evaluator', evaluator)
        self._kwargs.setdefault('_population_size', pop_size)
        self._kwargs.setdefault('_evolutionary_computation', self)

        try:
            iter(seeds)
        except TypeError:
            seeds = [seeds]
        initial_cs = list(seeds)
        num_generated = max(pop_size - len(seeds), 0)
        for _ in range(num_generated):
            cs = generator(random=self._random, args=self._kwargs)
            initial_cs.append(cs)
        initial_fit = evaluator(candidates=initial_cs, args=self._kwargs)
        
        population = []
        archive = []
        for cs, fit in zip(initial_cs, initial_fit):
            particle = Particle(cs, maximize=maximize)
            particle.fitness = fit
            particle.x = cs
            particle.xfitness = fit
            population.append(particle)
            
        num_evaluations = len(initial_fit)
        num_generations = 0
        self._kwargs['_num_generations'] = num_generations
        self._kwargs['_num_evaluations'] = num_evaluations
        
        population.sort(reverse=True)
        self._kwargs['_population'] = population
        
        pop_copy = list(population)
        arc_copy = list(archive)
        archive = self.archiver(random=self._random, population=pop_copy, archive=arc_copy, args=self._kwargs)
        self._kwargs['_archive'] = archive
        
        if isinstance(self.observer, (list, tuple)):
            for obs in self.observer:
                obs(population=population, num_generations=num_generations, num_evaluations=num_evaluations, args=self._kwargs)
        else:
            self.observer(population=population, num_generations=num_generations, num_evaluations=num_evaluations, args=self._kwargs)
            
        while not self._should_terminate(population, num_generations, num_evaluations):
            population = self._move(population, self._kwargs)

            updated_candidates = [p.x for p in population]
            updated_fitness = evaluator(candidates=updated_candidates, args=self._kwargs)
            for particle, fitness in zip(population, updated_fitness):
                particle.xfitness = fitness
                if maximize:
                    if particle.xfitness > particle.fitness:
                        particle.candidate = copy.deepcopy(particle.x)
                        particle.fitness = copy.deepcopy(particle.xfitness)
                else:
                    if particle.xfitness < particle.fitness:
                        particle.candidate = copy.deepcopy(particle.x)
                        particle.fitness = copy.deepcopy(particle.xfitness)
                    
            population.sort(reverse=True)
            num_evaluations += len(updated_fitness)
            num_generations += 1
            self._kwargs['_population'] = population
            self._kwargs['_num_evaluations'] = num_evaluations
            self._kwargs['_num_generations'] = num_generations
            # Archive individuals.
            pop_copy = list(population)
            arc_copy = list(archive)
            archive = self.archiver(random=self._random, archive=arc_copy, population=pop_copy, args=self._kwargs)
            self._kwargs['_archive'] = archive
            
            if isinstance(self.observer, (list, tuple)):
                for obs in self.observer:
                    obs(population=population, num_generations=num_generations, num_evaluations=num_evaluations, args=self._kwargs)
            else:
                self.observer(population=population, num_generations=num_generations, num_evaluations=num_evaluations, args=self._kwargs)
            
        return archive
