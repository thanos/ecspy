import csv
import time
import random
from ecspy import ec
from ecspy import selectors
from ecspy import replacers
from ecspy import variators
from ecspy import terminators
from ecspy import observers



class MetaEC(ec.EvolutionaryComputation):
    def __init__(self, random):
        ec.EvolutionaryComputation.__init__(self, random)
        self.selector = selectors.tournament_selection
        self.replacer = replacers.generational_replacement
        self.variator = [variators.uniform_crossover, self._internal_variator]
        self.terminator = self._internal_meta_terminator
        
    def _create_selector_replacer(self, random):
        pop_size = random.randint(1, 100)
        selector = random.choice(range(0, 5))
        replacer = random.choice(range(0, 8))
        sel = [selector]
        if selector > 0:
            if replacer == 0 or replacer == 2 or replacer == 3:
                sel.append(pop_size)
            else:
                sel.append(random.randint(1, pop_size))
        if selector == 2:
            sel.append(random.randint(min(2, pop_size), pop_size))
        rep = [replacer]
        if replacer == 0 or replacer == 4:
            rep.append(random.choice([False, True]))
        elif replacer == 1:
            rep.append(random.randint(min(2, pop_size), pop_size))
        elif replacer == 3 or replacer == 5:
            rep.append(random.randint(0, pop_size))
        return [pop_size, sel, rep]
    
    def _create_variators(self, random):
        crossover = random.choice([0, 1, 2, 3, 4, 6])
        mutator = random.choice([5, 6])
        variators = ([crossover], [mutator])
        if crossover == 0 or crossover == 1 or crossover == 4:
            variators[0].append(random.random())
            variators[0].append(random.random())
        elif crossover == 2:
            variators[0].append(random.random())
            variators[0].append(random.randint(1, 10))
        elif crossover == 3:
            variators[0].append(random.randint(0, 30))
        if mutator == 5:
            variators[1].append(random.random())
            variators[1].append(random.random())
        return variators
    
    def _internal_generator(self, random, args):
        cross, mut = self._create_variators(random)
        return [self._create_selector_replacer(random), cross, mut]
        
    def _internal_variator(self, random, candidates, args):
        cs_copy = list(candidates)
        for i, cs in enumerate(cs_copy):
            if random.random() < 0.1:
                cs_copy[i][0] = self._create_selector_replacer(random)
            if random.random() < 0.1:
                cross, mut = self._create_variators(random)
                cs_copy[i][1] = cross
                cs_copy[i][2] = mut
        return cs_copy

    def _internal_observer(self, population, num_generations, num_evaluations, args):
        for i, p in enumerate(population):
            self._observer_file.write('{0}, {1}, {2}\n'.format(i, p.fitness, str(p.candidate)))
            self._observer_file.flush()
    
    def _internal_terminator(self, population, num_generations, num_evaluations, args):
        maxevals = args.get('max_evaluations', 0)
        self._meta_evaluations += num_evaluations
        return num_evaluations >= maxevals or self._meta_evaluations >= self._max_meta_evaluations
        
    def _internal_meta_terminator(self, population, num_generations, num_evaluations, args):
        return self._meta_evaluations >= self._max_meta_evaluations
        
    def _internal_evaluator(self, candidates, args):
        the_generator = args.get('the_generator')
        the_evaluator = args.get('the_evaluator')
        do_maximize = args.get('do_maximize', True)
    
        fitness = []
        for candidate in candidates:
            popsize, selector, replacer, crossover, mutator, myargs = self.interpret_candidate(candidate)
            myargs['max_evaluations'] = args.get('num_trial_evaluations', popsize * 10)
            myargs['lower_bound'] = args['lower_bound']
            myargs['upper_bound'] = args['upper_bound']
            num_trials = args.get('num_trials', 1)
            evo = ec.EvolutionaryComputation(self._random)
            evo.terminator = self._internal_terminator
            evo.observer = self._internal_observer
            evo.selector = selector
            evo.variator = [crossover, mutator]
            evo.replacer = replacer
            best_fit = []
            for i in range(num_trials):
                final_pop = evo.evolve(generator=the_generator,
                                       evaluator=the_evaluator,
                                       pop_size=popsize,
                                       maximize=do_maximize,
                                       args=myargs)
                best_fit.append(final_pop[0].fitness)
            fitness.append(sum(best_fit) / float(len(best_fit)))
        return fitness
    
    def interpret_candidate(self, candidate):
        selector_mapping = (selectors.default_selection,
                            selectors.rank_selection,
                            selectors.tournament_selection,
                            selectors.truncation_selection,
                            selectors.uniform_selection)
        variator_mapping = (variators.blend_crossover, 
                            variators.differential_crossover,
                            variators.n_point_crossover,
                            variators.simulated_binary_crossover,
                            variators.uniform_crossover,
                            variators.gaussian_mutation,
                            variators.default_variation)
        replacer_mapping = (replacers.comma_replacement,
                            replacers.crowding_replacement, 
                            replacers.default_replacement,
                            replacers.generational_replacement,
                            replacers.plus_replacement,
                            replacers.random_replacement,
                            replacers.steady_state_replacement,
                            replacers.truncation_replacement)
        
        myargs = dict()
        # Selectors
        if candidate[0][1][0] == 1:
            myargs['num_selected'] = candidate[0][1][1]
        elif candidate[0][1][0] == 2:
            myargs['num_selected'] = candidate[0][1][1]
            myargs['tourn_size'] = candidate[0][1][2]
        elif candidate[0][1][0] == 3:
            myargs['num_selected'] = candidate[0][1][1]
        elif candidate[0][1][0] == 4:
            myargs['num_selected'] = candidate[0][1][1]
            
        # Replacers
        if candidate[0][2][0] == 0:
            myargs['use_one_fifth_rule'] = candidate[0][2][1]
        elif candidate[0][2][0] == 1:
            myargs['crowding_distance'] = candidate[0][2][1]
        elif candidate[0][2][0] == 3:
            myargs['num_elites'] = candidate[0][2][1]
        elif candidate[0][2][0] == 4:
            myargs['use_one_fifth_rule'] = candidate[0][2][1]
        elif candidate[0][2][0] == 5:
            myargs['num_elites'] = candidate[0][2][1]
            
        # Crossovers
        if candidate[1][0] == 0:
            myargs['crossover_rate'] = candidate[1][1]
            myargs['blx_alpha'] = candidate[1][2]
        elif candidate[1][0] == 1:
            myargs['crossover_rate'] = candidate[1][1]
            myargs['differential_phi'] = candidate[1][2]
        elif candidate[1][0] == 2:
            myargs['crossover_rate'] = candidate[1][1]
            myargs['num_crossover_points'] = candidate[1][2]
        elif candidate[1][0] == 3:
            myargs['sbx_etac'] = candidate[1][1]
        elif candidate[1][0] == 4:
            myargs['crossover_rate'] = candidate[1][1]
            myargs['pux_bias'] = candidate[1][2]
            
        # Mutators
        if candidate[2][0] == 5:
            myargs['mutation_rate'] = candidate[2][1]
            myargs['mutation_range'] = candidate[2][2]
            
        return (candidate[0][0], 
                selector_mapping[candidate[0][1][0]], 
                replacer_mapping[candidate[0][2][0]], 
                variator_mapping[candidate[1][0]],
                variator_mapping[candidate[2][0]],
                myargs)
                
    def evolve(self, generator, evaluator, pop_size=100, seeds=[], maximize=True, **args):
        args.setdefault('the_generator', generator)
        args.setdefault('the_evaluator', evaluator)
        args.setdefault('do_maximize', maximize)
        args.setdefault('num_elites', 1)
        args.setdefault('num_selected', pop_size)
        self._observer_file = open('metaec-individuals-file-' + time.strftime('%m%d%Y-%H%M%S') + '.csv', 'w')
        self._meta_evaluations = 0
        self._max_meta_evaluations = args.get('max_evaluations', 0)
        final_pop = ec.EvolutionaryComputation.evolve(self, self._internal_generator, self._internal_evaluator, pop_size, seeds, maximize, **args)
        self._observer_file.close()
        return final_pop
        
        
  



if __name__ == '__main__':  
    import math
            
    def rastrigin_generator(random, args):
        return [random.uniform(-5, 5), random.uniform(-5, 5)]
        
    def rastrigin_evaluator(candidates, args):
        fitness = []
        for cand in candidates:
            fitness.append(20 + cand[0]**2 + cand[1]**2 - 10 * (math.cos(2*math.pi*cand[0]) + math.cos(2*math.pi*cand[1])))
        return fitness
        
    prng = random.Random()
    prng.seed(time.time())
    mec = MetaEC(prng)
    mec.observer = observers.screen_observer
    final_pop = mec.evolve(rastrigin_generator, rastrigin_evaluator, pop_size=10, maximize=False,
                           num_trials=1, num_trial_evaluations=1000, max_evaluations=50000, 
                           lower_bound=[-5, -5], upper_bound=[5, 5])
        
    pop_size, selector, replacer, crossover, mutator, args = mec.interpret_candidate(final_pop[0].candidate)
    print('Best Fitness: %f' % final_pop[0].fitness)
    print('Population Size: %d' % pop_size)
    print('Selector: %s' % selector.__name__)
    print('Replacer: %s' % replacer.__name__)
    print('Crossover: %s' % crossover.__name__)
    print('Mutator: %s' % mutator.__name__)
    print('Parameters:')
    for key, val in args.iteritems():
        print('    %s: %s' % (key, str(val)))
    print('Actual Evaluations Used: %d' % mec._meta_evaluations)











