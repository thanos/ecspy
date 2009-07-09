"""
    This module provides capabilities for creating swarm intelligence algorithms.
    
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


import math
import copy
import ec
import observers
import terminators



class Particle(ec.Individual):
    def __init__(self, candidate = None):
        ec.Individual.__init__(self, candidate)
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
        return "%s : %s" % (str(self.candidate), str(self.fitness))
        
    def __repr__(self):
        return "x: %s : %s \nv: %s \np: %s : %s\n" % (str(self.x), str(self.xfitness), str(self.v), str(self.candidate), str(self.fitness))
        

class PSO(object):
    def __init__(self, random):
        self._random = random
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

    def _move(self, population, args):
        try:
            lower_bound = args['lower_bound']
        except KeyError:
            lower_bound = 0.0
            args['lower_bound'] = lower_bound
        try:
            upper_bound = args['upper_bound']
        except KeyError:
            upper_bound = 1.0
            args['upper_bound'] = upper_bound
        try:
            cognitive_rate = args['cognitive_rate']
        except KeyError:
            cognitive_rate = 2.1
            args['cognitive_rate'] = cognitive_rate
        try:
            social_rate = args['social_rate']
        except KeyError:
            social_rate = 2.1
            args['social_rate'] = social_rate
        try:
            topology = args['topology']
        except KeyError:
            topology = 'star'
            args['topology'] = topology
        try:
            neighborhood_size = args['neighborhood_size']
        except KeyError:
            neighborhood_size = None
            args['neighborhood_size'] = neighborhood_size
        try:
            use_constriction_coefficient = args['use_constriction_coefficient']
        except KeyError:
            use_constriction_coefficient = False
            args['use_constriction_coefficient'] = use_constriction_coefficient
                
        K = 1.0
        if(use_constriction_coefficient):
            phi = cognitive_rate + social_rate
            K = 2.0 / abs(2.0 - phi - math.sqrt(phi**2 - (4.0 * phi)))
                    
        for index, particle in enumerate(population):
            if topology == 'ring' and neighborhood_size is not None and neighborhood_size > 0:
                if index < neighborhood_size / 2:
                    start = len(population) - neighborhood_size / 2 + index
                else:
                    start = index - neighborhood_size / 2
                gbest = population[start]
                for i in xrange(1, neighborhood_size):
                    hood_i = (start + i) % len(population)
                    if population[hood_i] > gbest:
                        gbest = population[hood_i]
            else: # star topology
                gbest = population[0]
                for p in population:
                    if p > gbest:
                        gbest = p
                        
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

    def swarm(self, pop_size=100, seeds=[], generator=None, evaluator=None, terminator=terminators.default_termination, **args):
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
            particle = Particle(cs)
            particle.fitness = fit
            particle.x = cs
            particle.xfitness = fit
            population.append(particle)
            
        num_fun_evals = len(initial_fit)
        num_generations = 0
        
        population.sort(key=lambda x: x.fitness, reverse=True)
        
        try:
            for obs in self.observer:
                obs(population=population, num_generations=num_generations, num_fun_evals=num_fun_evals, args=self._kwargs)
        except TypeError:
            self.observer(population=population, num_generations=num_generations, num_fun_evals=num_fun_evals, args=self._kwargs)
            
        while not self._should_terminate(terminator, population, num_generations, num_fun_evals):            
            population = self._move(population, self._kwargs)

            updated_candidates = [p.x for p in population]
            updated_fitness = evaluator(candidates=updated_candidates, args=self._kwargs)
            for particle, fitness in zip(population, updated_fitness):
                particle.xfitness = fitness
                if particle.xfitness > particle.fitness:
                    particle.candidate = copy.deepcopy(particle.x)
                    particle.fitness = copy.deepcopy(particle.xfitness)
                    
            population.sort(key=lambda x: x.fitness, reverse=True)
            num_fun_evals += len(updated_fitness)
            num_generations += 1
            
            try:
                for obs in self.observer:
                    obs(population=population, num_generations=num_generations, num_fun_evals=num_fun_evals, args=self._kwargs)
            except TypeError:
                self.observer(population=population, num_generations=num_generations, num_fun_evals=num_fun_evals, args=self._kwargs)        
            
        return population
