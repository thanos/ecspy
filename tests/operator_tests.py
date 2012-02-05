
import unittest
import random
import logging
import itertools
import ecspy


def test_generator(random, args):
    return [random.random() for _ in range(6)]
    
def test_evaluator(candidates, args):
    fitness = []
    for c in candidates:
        fitness.append(sum(c))
    return fitness

def test_multiobjective_evaluator(candidates, args):
    fitness = []
    for c in candidates:
        fitness.append(ecspy.emo.Pareto([sum(c), sum(c)]))
    return fitness
    
prng = random.Random()
prng.seed(111111)
test_candidates = [test_generator(prng, {}) for _ in range(12)]
test_fitnesses = test_evaluator(test_candidates, {})
test_multiobjective_fitnesses = test_multiobjective_evaluator(test_candidates, {})
test_population = [ecspy.ec.Individual(candidate=c) for c in test_candidates]
test_multiobjective_population = [ecspy.ec.Individual(candidate=c) for c in test_candidates]
for i, f in zip(test_population, test_fitnesses):
    i.fitness = f
test_parents = test_population[:6]
test_offspring = test_population[6:]
for i, f in zip(test_multiobjective_population, test_multiobjective_fitnesses):
    i.fitness = f
test_multiobjective_parents = test_multiobjective_population[:6]
test_multiobjective_offspring = test_multiobjective_population[6:]
    

class ArchiverTests(unittest.TestCase):
    def test_default_archiver(self):
        new_archive = ecspy.archivers.default_archiver(prng, test_population, [], {})
        assert new_archive == test_population
        
    def test_best_archiver(self):
        new_archive = ecspy.archivers.best_archiver(prng, test_population, [], {})
        assert new_archive == [max(test_population)]
        
    def test_adaptive_grid_archiver(self):
        new_archive = ecspy.archivers.adaptive_grid_archiver(prng, test_multiobjective_population, [], {})
        assert len(new_archive) == 1
        
class EvaluatorTests(unittest.TestCase):
    def test_parallel_evaluation_pp(self):
        class fake_ec(object):
            def __init__(self):
                self.logger = logging.getLogger('ecspy.test')
        x = fake_ec()
        fitnesses = ecspy.evaluators.parallel_evaluation_pp(test_candidates, {'_ec':x, 'pp_evaluator':test_evaluator})
        assert fitnesses == test_fitnesses
        
    def test_parallel_evaluation_mp(self):
        class fake_ec(object):
            def __init__(self):
                self.logger = logging.getLogger('ecspy.test')
        x = fake_ec()
        fitnesses = ecspy.evaluators.parallel_evaluation_mp(test_candidates, {'_ec':x, 'mp_evaluator':test_evaluator})
        assert fitnesses == test_fitnesses
        
class MigratorTests(unittest.TestCase):
    def test_default_migration(self):
        migrants = ecspy.migrators.default_migration(prng, test_population, {})
        assert migrants == test_population
        
class ReplacerTests(unittest.TestCase):
    def test_default_replacement(self):
        survivors = ecspy.replacers.default_replacement(prng, test_population, test_parents, test_offspring, {})
        assert survivors == test_offspring
        
    def test_truncation_replacement(self):
        survivors = ecspy.replacers.truncation_replacement(prng, test_population, test_parents, test_offspring, {})
        assert len(survivors) == len(test_population) and max(max(test_population), max(test_offspring)) == max(survivors)
        
    def test_steady_state_replacement(self):
        survivors = ecspy.replacers.steady_state_replacement(prng, test_population, test_parents, test_offspring, {})
        assert len(survivors) == len(test_population) and all([o in survivors for o in test_offspring])
        
    def test_generational_replacement(self):
        survivors = ecspy.replacers.generational_replacement(prng, test_population, test_parents, test_offspring, {})
        assert all([s in test_offspring for s in survivors])
        
    def test_random_replacement(self):
        survivors = ecspy.replacers.random_replacement(prng, test_population, test_parents, test_offspring, {})
        assert len(survivors) == len(test_population) and all([o in survivors for o in test_offspring])
    
    def test_plus_replacement(self):
        survivors = ecspy.replacers.plus_replacement(prng, test_population, test_parents, test_offspring, {})
        assert len(survivors) == len(test_population) and max(max(test_parents), max(test_offspring)) == max(survivors)
    
    def test_comma_replacement(self):
        survivors = ecspy.replacers.comma_replacement(prng, test_population, test_parents, test_offspring, {})
        assert len(survivors) == min(len(test_population), len(test_offspring)) and all([s in test_offspring for s in survivors])
    
    def test_crowding_replacement(self):
        survivors = ecspy.replacers.crowding_replacement(prng, test_population, test_parents, test_offspring, {})
        assert len(survivors) == len(test_population) and max(max(test_population), max(test_offspring)) == max(survivors)
    
    def test_simulated_annealing_replacement(self):
        class fake_ec(object):
            def __init__(self):
                self.num_evaluations = 10
        x = fake_ec()
        survivors = ecspy.replacers.simulated_annealing_replacement(prng, test_population, test_parents, test_offspring, 
                                                                    {'_ec':x, 'max_evaluations':100})
        assert len(survivors) == len(test_parents) and max(max(test_parents), max(test_offspring)) == max(survivors)
    
    def test_nsga_replacement(self):
        survivors = ecspy.replacers.nsga_replacement(prng, test_multiobjective_population, test_multiobjective_parents, test_multiobjective_offspring, {})
        assert (len(survivors) == len(test_multiobjective_population) and 
                max(max(test_multiobjective_population), max(test_multiobjective_offspring)) == max(survivors))
    
    def test_paes_replacement(self):
        class fake_ec(object):
            def __init__(self):
                self.archive = []
                self.archiver = ecspy.archivers.adaptive_grid_archiver
        x = fake_ec()
        survivors = ecspy.replacers.paes_replacement(prng, test_multiobjective_population, test_multiobjective_parents, 
                                                     test_multiobjective_offspring, {'_ec':x})
        assert (len(survivors) == min(len(test_multiobjective_parents), len(test_multiobjective_offspring)) and 
                max(survivors) == max(max(test_multiobjective_parents), max(test_multiobjective_offspring)))
    
class SelectorTests(unittest.TestCase):
    def test_default_selection(self):
        parents = ecspy.selectors.default_selection(prng, test_population, {})
        assert parents == test_population

    def test_truncation_selection(self):
        parents = ecspy.selectors.truncation_selection(prng, test_population, {})
        assert all([p in parents for p in test_population])

    def test_uniform_selection(self):
        parents = ecspy.selectors.uniform_selection(prng, test_population, {})
        assert len(parents) == 1 and all([p in test_population for p in parents])

    def test_fitness_proportionate_selection(self):
        parents = ecspy.selectors.fitness_proportionate_selection(prng, test_population, {})
        assert len(parents) == 1 and all([p in test_population for p in parents])

    def test_rank_selection(self):
        parents = ecspy.selectors.rank_selection(prng, test_population, {})
        assert len(parents) == 1 and all([p in test_population for p in parents])

    def test_tournament_selection(self):
        parents = ecspy.selectors.tournament_selection(prng, test_population, {'tourn_size':len(test_population)})
        assert len(parents) == 1 and max(parents) == max(test_population)

class TerminatorTests(unittest.TestCase):
    def test_default_termination(self):
        t = ecspy.terminators.default_termination(test_population, 1, 1, {})
        assert t == True

    def test_diversity_termination(self):
        p = [ecspy.ec.Individual(candidate=[1, 1, 1]) for _ in range(10)]
        t = ecspy.terminators.diversity_termination(p, 1, 1, {})
        assert t == True

    def test_average_fitness_termination(self):
        p = [ecspy.ec.Individual(candidate=i.candidate) for i in test_population]
        for x in p:
            x.fitness = 1
        t = ecspy.terminators.average_fitness_termination(p, 1, 1, {})
        assert t == True

    def test_evaluation_termination(self):
        t = ecspy.terminators.evaluation_termination(test_population, 1, len(test_population), {})
        assert t == True

    def test_generation_termination(self):
        t = ecspy.terminators.generation_termination(test_population, 1, 1, {})
        assert t == True

    def test_time_termination(self):
        class fake_ec(object):
            def __init__(self):
                self.logger = logging.getLogger('ecspy.test')
        x = fake_ec()
        t = ecspy.terminators.time_termination(test_population, 1, 1, {'_ec':x, 'max_time':0})
        assert t == True

class VariatorTests(unittest.TestCase):
    def test_default_variation(self):
        offspring = ecspy.variators.default_variation(prng, list(test_candidates), {})
        assert offspring == test_candidates

    def test_estimation_of_distribution_variation(self):
        class fake_ec(object):
            def __init__(self):
                self.bounder = ecspy.ec.Bounder()
        x = fake_ec()
        test_candidates = [[1] * 6 for _ in range(10)]
        offspring = ecspy.variators.estimation_of_distribution_variation(prng, list(test_candidates), {'_ec':x})
        assert len(offspring) == 1 and offspring[0] == test_candidates[0]

    def test_n_point_crossover(self):
        offspring = ecspy.variators.n_point_crossover(prng, list(test_candidates), {'num_crossover_points':3})
        moms = test_candidates[::2]
        dads = test_candidates[1::2]
        dmoms = itertools.chain.from_iterable([[t, t] for t in moms])
        ddads = itertools.chain.from_iterable([[t, t] for t in dads])
        offs = [(offspring[i], offspring[i+1]) for i in range(0, len(offspring), 2)]
        assert (all([x in m or x in d for m, d, o in zip(dmoms, ddads, offspring) for x in o]) and 
                all([(x in o[0] or x in o[1]) and (y in o[0] or y in o[1]) for m, d, o in zip(moms, dads, offs) for x in m for y in m]))

    def test_uniform_crossover(self):
        offspring = ecspy.variators.uniform_crossover(prng, list(test_candidates), {})
        moms = test_candidates[::2]
        dads = test_candidates[1::2]
        dmoms = itertools.chain.from_iterable([[t, t] for t in moms])
        ddads = itertools.chain.from_iterable([[t, t] for t in dads])
        offs = [(offspring[i], offspring[i+1]) for i in range(0, len(offspring), 2)]
        assert (all([x in m or x in d for m, d, o in zip(dmoms, ddads, offspring) for x in o]) and 
                all([(x in o[0] or x in o[1]) and (y in o[0] or y in o[1]) for m, d, o in zip(moms, dads, offs) for x in m for y in m]))
    
    def test_blend_crossover(self):
        class fake_ec(object):
            def __init__(self):
                self.bounder = ecspy.ec.Bounder()
        x = fake_ec()
        alpha = 0.1
        offspring = ecspy.variators.blend_crossover(prng, list(test_candidates), {'_ec':x, 'blx_alpha':alpha})
        moms = itertools.chain.from_iterable([[t, t] for t in test_candidates[::2]])
        dads = itertools.chain.from_iterable([[t, t] for t in test_candidates[1::2]])
        tests = []
        for mom, dad, off in zip(moms, dads, offspring):
            for m, d, x in zip(mom, dad, off):
                tol = alpha * (max(m, d) - min(m, d))
                tests.append(x >= (min(m, d) - tol) and x <= (max(m, d) + tol))
        assert all(tests)
    
    def test_differential_crossover(self):
        class fake_ec(object):
            def __init__(self):
                self.bounder = ecspy.ec.Bounder()
                self.population = list(test_population)
        x = fake_ec()
        offspring = ecspy.variators.differential_crossover(prng, list(test_candidates), {'_ec':x})
        moms = itertools.chain.from_iterable([[t, t] for t in test_candidates[::2]])
        dads = itertools.chain.from_iterable([[t, t] for t in test_candidates[1::2]])
        tests = []
        for mom, dad, off in zip(moms, dads, offspring):
            for m, d, x in zip(mom, dad, off):
                tests.append(x >= min(m, d) and x <= max(m, d))
        assert all(tests)
    
    def test_simulated_binary_crossover(self):
        assert True
    
    def test_laplace_crossover(self):
        assert True
    
    def test_gaussian_mutation(self):
        class fake_ec(object):
            def __init__(self):
                self.bounder = ecspy.ec.Bounder(0, 1)
        x = fake_ec()
        offspring = ecspy.variators.gaussian_mutation(prng, list(test_candidates), {'_ec':x})
        assert([x >= 0 and x <= 1 for o in offspring for x in o])
        
    def test_bit_flip_mutation(self):
        assert True
    
    def test_nonuniform_mutation(self):
        assert True
    
    def test_mptm_mutation(self):
        assert True
    



    
if __name__ == '__main__':
    unittest.main()
        
        
        
        
        
