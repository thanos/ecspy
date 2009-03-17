# TO DO
# Add additional selection/replacement/variation schemes
# Create off-the-shelf ECs (like GA, EDA, etc.) that can be used
# Add the comment strings to all functions/methods/classes


import time
import types
import terminators
import selectors
import replacers
import variators
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
        return str(self.candidate) + " : " + str(self.fitness)
        
    def __repr__(self):
        return str(self.candidate) + " : " + str(self.fitness)
        
    def __cmp__(self, other):
        if self.fitness is not None and other.fitness is not None:
            return cmp(self.fitness, other.fitness)
        else:
            raise Exception("fitness is not defined")


class EvolutionEngine(object):
    def __init__(self, prng):
        self._random = prng
        self.selector = selectors.default_selection
        self.variator = variators.default_variation
        self.replacer = replacers.default_replacement
        self.operators = [self.selector,
                          self.variator, 
                          self.replacer]
        self.observer = observers.default_observer
        self._kwargs = dict()
        
    def _should_terminate(self, terminator, pop, ng, fe):
        terminate = False
        if isinstance(terminator, types.ListType):
            for clause in terminator:
                terminate = terminate or clause(population=pop, num_generations=ng, num_fun_evals=fe, args=self._kwargs)
        else:
            terminate = terminator(population=pop, num_generations=ng, num_fun_evals=fe, args=self._kwargs)
        return terminate
        
    
    def evolve(self, pop_size=100, seeds=[], generator=None, evaluator=None, terminator=terminators.default_termination, **args):
        self._kwargs = args
        initial_cs = list(seeds)
        num_generated = max(pop_size - len(seeds), 0)
        for i in xrange(num_generated):
            cs = generator(random=self._random, args=self._kwargs)
            initial_cs.append(cs)
        initial_fit = evaluator(candidates=initial_cs, args=self._kwargs)
        
        population = []
        for i in xrange(len(initial_cs)):
            ind = Individual(initial_cs[i])
            ind.fitness = initial_fit[i]
            population.append(ind)
            
        num_fun_evals = len(population)
        num_generations = 0
        
        population.sort(key=lambda x: x.fitness, reverse=True)
        
        self.observer(population=population, num_generations=num_generations, num_fun_evals=num_fun_evals, args=self._kwargs)
        
        while not self._should_terminate(terminator, population, num_generations, num_fun_evals):
            pop_copy = list(population)
            parents = self.selector(random=self._random, population=pop_copy, args=self._kwargs)
            parent_cs = [list(i.candidate) for i in parents]
            offspring_cs = parent_cs
            if isinstance(self.variator, types.ListType):
                for op in self.variator:
                    offspring_cs = op(random=self._random, candidates=offspring_cs, args=self._kwargs)
            else:
                offspring_cs = self.variator(random=self._random, candidates=offspring_cs, args=self._kwargs)
            offspring_fit = evaluator(candidates=offspring_cs, args=self._kwargs)
            offspring = []
            for i in xrange(len(offspring_cs)):
                off = Individual(offspring_cs[i])
                off.fitness = offspring_fit[i]
                offspring.append(off)
            
            num_fun_evals += len(offspring)
            population = self.replacer(random=self._random, population=pop_copy, parents=parents, offspring=offspring, args=self._kwargs)
            population.sort(key=lambda x: x.fitness, reverse=True)
            num_generations += 1
            self.observer(population=population, num_generations=num_generations, num_fun_evals=num_fun_evals, args=self._kwargs)
        
        return population
        

class GA(EvolutionEngine):
    def __init__(self, prng):
        EvolutionEngine.__init__(self, prng)
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
    def __init__(self, prng):
        EvolutionEngine.__init__(self, prng)
        self.selector = selectors.default_selection
        self.variator = variators.gaussian_mutation
        self.replacer = replacers.plus_replacement
        self.operators = [self.selector,
                          self.variator,
                          self.replacer]
        self.observer = observers.default_observer
        

