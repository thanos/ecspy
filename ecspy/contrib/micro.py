
from ecspy import ec
from ecspy import terminators

class MicroEC(ec.EvolutionaryComputation):
    def __init__(self, random):
        ec.EvolutionaryComputation.__init__(self, random)
        
    def evolve(self, generator, evaluator, pop_size=10, seeds=[], maximize=True, bounder=ec.bounder(), **args):
        self._kwargs = args
        self._kwargs['_ec'] = self
        self.termination_cause = None
        self.generator = generator
        self.evaluator = evaluator
        self.bounder = bounder
        self.maximize = maximize
        self.population = []
        self.archive = []
        self.num_generations = 0
        self.num_evaluations = 0
        microseeds = seeds
        args.setdefault('min_diversity', 0.05)
        while not self._should_terminate(self.population, self.num_generations, self.num_evaluations):
            microec = ec.EvolutionaryComputation(self._random)
            microec.selector = self.selector
            microec.variator = self.variator
            microec.replacer = self.replacer
            microec.terminator = terminators.diversity_termination
            result = microec.evolve(generator=generator, evaluator=evaluator, pop_size=pop_size, seeds=microseeds, maximize=maximize, **args)
            microseeds = [result[0].candidate]
            self.population = list(result)
            self.num_evaluations += microec.num_evaluations

            # Migrate individuals.
            self.population = self.migrator(random=self._random, population=self.population, args=self._kwargs)
            
            # Archive individuals.
            pop_copy = list(self.population)
            arc_copy = list(self.archive)
            self.archive = self.archiver(random=self._random, archive=arc_copy, population=pop_copy, args=self._kwargs)
            
            self.num_generations += microec.num_generations
            if isinstance(self.observer, (list, tuple)):
                for obs in self.observer:
                    obs(population=self.population, num_generations=self.num_generations, num_evaluations=self.num_evaluations, args=self._kwargs)
            else:
                self.observer(population=self.population, num_generations=self.num_generations, num_evaluations=self.num_evaluations, args=self._kwargs)
        return self.population
    
    

    
       
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
    micro.variator = [variators.uniform_crossover, variators.gaussian_mutation]
    micro.archiver = archivers.best_archiver
    micro.observer = observers.screen_observer
    micro.terminator = terminators.evaluation_termination
    final_pop = micro.evolve(rastrigin_generator, rastrigin_evaluator, pop_size=10, maximize=False, bounder=ec.bounder(-5.12, 5.12),
                             max_evaluations=3000, num_selected=2, stdev=0.1)
                             
    print('Actual evaluations: %d' % micro.num_evaluations)

    for p in micro.archive:
        print p
