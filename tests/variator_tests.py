from ecspy.contrib.variator_pipe import iterate, iterate_rate, bit_flip_mutation, mutate_candidates,  recombine_candidates, n_point_crossover, wrap_around, bound, bound, gaussian_mutation, gaussian_mutation
import unittest
from random import Random
from ecspy.ec import bounder

__author__ = 'henrik'
random = Random()

#test helpers
def generator(length, func):
    return tuple(func() for _ in xrange(length))

class setval_mutator(object):
    def __init__(self, val):
        self.val = val
    def __call__(self, v):
        return self.val

def assert_almost_equal(v1, v2, tol):
    assert abs(v1 - v2) < tol
class TestVariators(unittest.TestCase):
    def test_dynamic_params(self):
        candidate = [[0] * 200] * 8
        mut = iterate(iterate_rate(0, setval_mutator(-1)))
        mut.input.rate = lambda v: 0.1 * (1+mut.index)
        mut.input.input.val = lambda v: mut.index + 1
        next_gen = mut(candidate)
        for i, col in enumerate(next_gen):
            mutated = len(filter(lambda v: v > 0, next_gen))
            not_mutated = len(filter(lambda v: v == 0, next_gen))
            assert_almost_equal(mutated, 0.1 * (1+i), 25)

    def test_generate(self):
        candidate = generator(10, random.random)
        assert len(candidate) == 10

    def test_nested_generate(self):
        candidate = generator(10, lambda: generator(3, random.random))
        assert len(candidate) == 10
        assert len(candidate[2]) == 3

    def test_iterate_cartesian_candidate(self):
        pop = 3
        d1, d2, d3 = 2, 3, 2
        candidates = [generator(d1, lambda: generator(d2, lambda: generator(d3, lambda: 0))) for _ in xrange(pop)]
        mutator = mutate_candidates(iterate(iterate(iterate(bit_flip_mutation()))))
        next_gen = mutator(candidates)
        for i in xrange(pop):
            for j in xrange(d1):
                for k in xrange(d2):
                    for l in xrange(d3):
                        assert next_gen[i][j][k][l] == 1


    def test_n_point_crossover(self):
        candidate1 = [0 for i in xrange(30)]
        candidate2 = [1 for i in xrange(30)]
        candidates = [candidate1, candidate2]
        crossover = recombine_candidates(2, n_point_crossover(1))
        next_gen = crossover(candidates)
        crossed1 = len(filter(lambda v: v == 1, next_gen[0]))
        crossed2 = len(filter(lambda v: v == 0, next_gen[1]))
        assert crossed1 == crossed2

    def test_variation_rate(self):
        candidate = [0 for i in xrange(100)]
        mutator = iterate_rate(0.3, bit_flip_mutation())
        next_gen = mutator(candidate)
        mutated = len(filter(lambda v: v == 1, next_gen))
        not_mutated = len(filter(lambda v: v == 0, next_gen))
        assert mutated + not_mutated == len(candidate)
        assert mutated < 38 and mutated > 22, "%s mutated nodes, values are random, so might be a freak occurence" % mutated

    def test_wrap_around(self):
        wrapper = wrap_around(2, 6)
        assert wrapper(3) == 3
        assert wrapper(6) == 2
        assert wrapper(0) == 4
        assert wrapper(8) == 4

    def test_bound(self):
        bounder = bound(2, 6)
        assert bounder(4) == 4
        assert bounder(1) == 2
        assert bounder(7) == 6

    def test_speed(self):
        candidates1 = [[0.5]*200]*200
        candidates2 = [[0.5]*200]*200
        mut = mutate_candidates(iterate_rate(0.1, bound(0., 1., gaussian_mutation)))
        import time
        from ecspy.variators import mutators
        t0 = time.time()
        mutated = mut(candidates1)
        t1 = time.time()
        class ec:
            bounder = bounder
        mutated = mutators.gaussian_mutation(random, candidates1, {'_evolutionary_computation':ec})
        t2 = time.time()
        lap1 = t1-t0
        lap2 = t2-t1
        print "new time: %s, old time: %s, %s times slower" % (lap1, lap2, lap1 / lap2)
