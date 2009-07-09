"""
    This module provides the framework for making evolutionary computations.
    
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

import time
import copy
import selectors
import variators
import replacers
import migrators
import terminators
import observers


class Individual(object):
    def __init__(self, candidate = None):
        self.candidate = candidate
        self.fitness = None
        self.birthdate = time.time()
    
    def __setattr__(self, name, val):
        if name == 'candidate':
            self.__dict__[name] = val
            self.fitness = None
        else:
            self.__dict__[name] = val
    
    def __str__(self):
        return "%s : %s" % (str(self.candidate), str(self.fitness))
        
    def __repr__(self):
        return "%s : %s" % (str(self.candidate), str(self.fitness))
        
    def __cmp__(self, other):
        if self.fitness is not None and other.fitness is not None:
            return cmp(self.fitness, other.fitness)
        else:
            raise Exception("fitness is not defined")


class EvolutionEngine(object):
    def __init__(self, random):
        self._random = random
        self.selector = selectors.default_selection
        self.variator = variators.default_variation
        self.replacer = replacers.default_replacement
        self.migrator = migrators.default_migration
        self.operators = [self.selector,
                          self.variator, 
                          self.replacer,
                          self.migrator]
        self.observer = observers.default_observer
        self._kwargs = dict()
        
    def _should_terminate(self, terminator, pop, ng, fe):
        terminate = False
        try:
            for clause in terminator:
                terminate = terminate or clause(population=pop, num_generations=ng, num_fun_evals=fe, args=self._kwargs)
        except TypeError:
            terminate = terminator(population=pop, num_generations=ng, num_fun_evals=fe, args=self._kwargs)
        return terminate
        
    
    def evolve(self, pop_size=100, seeds=[], generator=None, evaluator=None, terminator=terminators.default_termination, **args):
        self._kwargs = args
        try:
            iter(seeds)
        except TypeError:
            seeds = [seeds]
        initial_cs = list(seeds)
        num_generated = max(pop_size - len(seeds), 0)
        for _ in xrange(num_generated):
            cs = generator(random=self._random, args=self._kwargs)
            initial_cs.append(cs)
        initial_fit = evaluator(candidates=initial_cs, args=self._kwargs)
        
        population = []
        for cs, fit in zip(initial_cs, initial_fit):
            ind = Individual(cs)
            ind.fitness = fit
            population.append(ind)
            
        num_fun_evals = len(initial_fit)
        num_generations = 0
        
        population.sort(key=lambda x: x.fitness, reverse=True)
        
        try:
            for obs in self.observer:
                obs(population=population, num_generations=num_generations, num_fun_evals=num_fun_evals, args=self._kwargs)
        except TypeError:
            self.observer(population=population, num_generations=num_generations, num_fun_evals=num_fun_evals, args=self._kwargs)
        while not self._should_terminate(terminator, population, num_generations, num_fun_evals):
            pop_copy = list(population)
            parents = self.selector(random=self._random, population=pop_copy, args=self._kwargs)
            
            # Sort the parents just before taking out the candidate so that relative fitness
            # can be determined in the variators (e.g., differential crossover).
            parents.sort(key=lambda x: x.fitness, reverse=True)
            parent_cs = [copy.deepcopy(i.candidate) for i in parents]
            offspring_cs = parent_cs
            try:
                for op in self.variator:
                    offspring_cs = op(random=self._random, candidates=offspring_cs, args=self._kwargs)
            except TypeError:
                offspring_cs = self.variator(random=self._random, candidates=offspring_cs, args=self._kwargs)
            offspring_fit = evaluator(candidates=offspring_cs, args=self._kwargs)
            offspring = []
            for cs, fit in zip(offspring_cs, offspring_fit):
                off = Individual(cs)
                off.fitness = fit
                offspring.append(off)
            
            num_fun_evals += len(offspring_fit)
            pop_copy = self.replacer(random=self._random, population=pop_copy, parents=parents, offspring=offspring, args=self._kwargs)
            population = self.migrator(random=self._random, population=pop_copy, args=self._kwargs)
            population.sort(key=lambda x: x.fitness, reverse=True)
            num_generations += 1
            try:
                for obs in self.observer:
                    obs(population=population, num_generations=num_generations, num_fun_evals=num_fun_evals, args=self._kwargs)
            except TypeError:
                self.observer(population=population, num_generations=num_generations, num_fun_evals=num_fun_evals, args=self._kwargs)        
        return population
        

class GA(EvolutionEngine):
    def __init__(self, random):
        EvolutionEngine.__init__(self, random)
        self.selector = selectors.roulette_wheel_selection
        self.variator = [variators.n_point_crossover, variators.bit_flip_mutation]
        self.replacer = replacers.generational_replacement
        self.operators = [self.selector,
                          self.variator,
                          self.replacer]
        self.observer = observers.default_observer
        
    def evolve(self, pop_size=100, seeds=[], generator=None, evaluator=None, terminator=terminators.default_termination, **args):
        try:
            args['num_selected']
        except KeyError:
            args['num_selected'] = pop_size
        return EvolutionEngine.evolve(self, pop_size, seeds, generator, evaluator, terminator, **args)


class ES(EvolutionEngine):
    def __init__(self, random):
        EvolutionEngine.__init__(self, random)
        self.selector = selectors.default_selection
        self.variator = variators.gaussian_mutation
        self.replacer = replacers.plus_replacement
        self.operators = [self.selector,
                          self.variator,
                          self.replacer]
        self.observer = observers.default_observer
        
