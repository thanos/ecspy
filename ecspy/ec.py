
import time
import copy
import math
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
        self.operators = [self.selector,
                          self.variator, 
                          self.replacer]
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
            population = self.replacer(random=self._random, population=pop_copy, parents=parents, offspring=offspring, args=self._kwargs)
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
        

class Particle(Individual):
    def __init__(self, candidate = None):
        Individual.__init__(self, candidate)
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
        

class PSO(EvolutionEngine):
    def __init__(self, random):
        self._random = random
        self.selector = []
        self.variator = []
        self.replacer = []
        self.operators = [self.selector,
                          self.variator, 
                          self.replacer]
        self.observer = observers.default_observer
        self._kwargs = dict()

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

