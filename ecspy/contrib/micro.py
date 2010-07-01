
from ecspy import ec
from ecspy import terminators

class MicroEC(ec.EvolutionaryComputation):
    def __init__(self, random):
        ec.EvolutionaryComputation.__init__(self, random)
        
    def evolve(self, generator, evaluator, pop_size=10, seeds=[], maximize=True, **args):
        self._kwargs = dict(args)
        # Add entries to the keyword arguments dictionary
        # if they're not already present.
        self._kwargs.setdefault('_generator', generator)
        self._kwargs.setdefault('_evaluator', evaluator)
        self._kwargs.setdefault('_population_size', pop_size)
        self._kwargs.setdefault('_evolutionary_computation', self)
        self.termination_cause = None
        microseeds = seeds
        args.setdefault('min_diversity', 0.05)
        
        population = []
        archive = []
        num_evaluations = 0
        num_generations = 0
        self._kwargs['_num_generations'] = num_generations
        self._kwargs['_num_evaluations'] = num_evaluations
        self._kwargs['_population'] = population
        self._kwargs['_archive'] = archive
        
        while not self._should_terminate(population, num_generations, num_evaluations):
            microec = ec.EvolutionaryComputation(self._random)
            microec.selector = self.selector
            microec.variator = self.variator
            microec.replacer = self.replacer
            microec.terminator = terminators.diversity_termination
            result = microec.evolve(generator=generator, evaluator=evaluator, pop_size=pop_size, seeds=microseeds, maximize=maximize, **args)
            microseeds = [result[0].candidate]
            population = list(result)
            num_evaluations += microec._kwargs['_num_evaluations']
            self._kwargs['_num_evaluations'] = num_evaluations

            # Migrate individuals.
            population = self.migrator(random=self._random, population=population, args=self._kwargs)
            population.sort(reverse=True)
            self._kwargs['_population'] = population
            
            # Archive individuals.
            pop_copy = list(population)
            arc_copy = list(archive)
            archive = self.archiver(random=self._random, archive=arc_copy, population=pop_copy, args=self._kwargs)
            self._kwargs['_archive'] = archive
            
            num_generations += microec._kwargs['_num_generations']
            self._kwargs['_num_generations'] = num_generations
            if isinstance(self.observer, (list, tuple)):
                for obs in self.observer:
                    obs(population=population, num_generations=num_generations, num_evaluations=num_evaluations, args=self._kwargs)
            else:
                self.observer(population=population, num_generations=num_generations, num_evaluations=num_evaluations, args=self._kwargs)
            
        return archive
    
    

    
       
if __name__ == '__main__':
    import random
    import math
    import time
    from ecspy import ec
    from ecspy import observers
    from ecspy import terminators
    from ecspy import selectors
    from ecspy import replacers
    from ecspy import variators
    from ecspy import archivers


    def rastrigin_generator(random, args):
        return [random.uniform(-5.12, 5.12) for _ in range(2)]

    def rastrigin_evaluator(candidates, args):
        fitness = []
        for cand in candidates:
            fitness.append(10 * len(cand) + sum([x**2 - 10 * (math.cos(2*math.pi*x)) for x in cand]))
        return fitness
        
    prng = random.Random()
    prng.seed(time.time())
    micro = MicroEC(prng)
    micro.selector = selectors.tournament_selection
    micro.replacer = replacers.steady_state_replacement
    micro.variator = variators.uniform_crossover
    micro.archiver = archivers.best_archiver
    micro.observer = observers.screen_observer
    micro.terminator = terminators.evaluation_termination
    final_pop = micro.evolve(rastrigin_generator, rastrigin_evaluator, pop_size=10, maximize=False, 
                             max_evaluations=3000, lower_bound=-5.12, upper_bound=5.12, num_selected=2)
                             
    print('Actual evaluations: %d' % micro._kwargs['_num_evaluations'])

    for p in final_pop:
        print p
