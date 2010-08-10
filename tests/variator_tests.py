from ecspy.contrib.variator_pipe import iterate, bit_flip_mutation, n_point_crossover, wrap_around, bound, group_candidates, pick_rate, pick_fixed, gaussian_mutation, base_function, Accessor
import unittest
from random import Random
from ecspy.ec import bounder

__author__ = 'henrik'
random = Random()

#test helpers
def generator(length, func):
    return tuple(func() for _ in xrange(length))

class setval_mutator(base_function):
    def __call__(self, accessor):
        return self.params['val'](accessor)

def assert_almost_equal(v1, v2, tol):
    assert abs(v1 - v2) < tol
class TestVariators(unittest.TestCase):
    def test_dynamic_params(self):
        #TODO: not sure about this test
        candidate = [[0] * 200] * 8
        val_func = lambda acc: acc.pos[-1]
        rate_func = lambda acc: 0.1 * float(acc.pos[-1]) / (len(acc.parent)+1)
        mut = iterate(input=pick_rate(rate=rate_func,
                                      input=iterate(input=setval_mutator(val=val_func))))


        #mut.input.rate = lambda v: 0.1 * (1+mut.index)
        #mut.input.input.input.val = lambda v: mut.index + 1
        next_gen = mut(Accessor(candidate))
        for i, col in enumerate(next_gen):
            mutated = len(filter(lambda v: v > 0, next_gen))
            not_mutated = len(filter(lambda v: v == 0, next_gen))
            assert_almost_equal(mutated, 0.1 * (1+i), 10)

    def test_generate(self):
        candidate = generator(10, random.random)
        assert len(candidate) == 10

    def test_nested_generate(self):
        candidate = generator(10, lambda: generator(3, random.random))
        assert len(candidate) == 10
        assert len(candidate[2]) == 3

    def test_iterate_nested(self):
        pop = 3
        d1, d2, d3 = 2, 3, 2
        candidates = [generator(d1, lambda: generator(d2, lambda: generator(d3, lambda: 0))) for _ in xrange(pop)]
        mutator = iterate(input=iterate(input=iterate(input=iterate(input=bit_flip_mutation()))))
        next_gen = mutator(Accessor(candidates))
        for i in xrange(pop):
            for j in xrange(d1):
                for k in xrange(d2):
                    for l in xrange(d3):
                        assert next_gen[i][j][k][l] == 1


    def test_n_point_crossover(self):
        candidate1 = [0 for i in xrange(30)]
        candidate2 = [1 for i in xrange(30)]
        candidates = [candidate1, candidate2]
        crossover = group_candidates(size=2, input=iterate(n_point_crossover(1)))
        next_gen = crossover(Accessor(candidates))
        crossed1 = len(filter(lambda v: v == 1, next_gen[0]))
        crossed2 = len(filter(lambda v: v == 0, next_gen[1]))
        assert crossed1 == crossed2

    def test_variation_rate(self):
        candidate = [0 for i in xrange(100)]
        mutator = pick_rate(rate=0.3, input=iterate(input=bit_flip_mutation()))
        next_gen = mutator(Accessor(candidate))
        mutated = len(filter(lambda v: v == 1, next_gen))
        not_mutated = len(filter(lambda v: v == 0, next_gen))
        assert mutated + not_mutated == len(candidate)
        assert mutated < 38 and mutated > 22, "%s mutated nodes, values are random, so might be a freak occurence" % mutated




    def test_composite_mutator(self):

        candidate = [(0, 'a') for _ in xrange(100)]

        mut_v = lambda acc: 'b' if acc.value == 'a' else 'a'
        mut_bit = bit_flip_mutation()
        def mut(accessor):
            #v = accessor.value
            if random.random() < 0.5:
                return (mut_bit(accessor[0]), accessor[1].value)
            else:
                return (accessor[0].value, mut_v(accessor[1]))

        mutator = pick_rate(rate=1.0, input=iterate(input=mut))

        mutated = mutator(Accessor(candidate))
        v_mutated = 0
        bit_mutated = 0
        for bit, v in mutated:
            if bit == 1:
                bit_mutated += 1
            if v == 'b':
                v_mutated += 1
        assert v_mutated+bit_mutated == len(candidate)
        assert v_mutated > 35
        assert bit_mutated > 35



    #def test_wrap_around(self):
    #    wrapper = wrap_around(lower=2, upper=6)
    #    assert wrapper(None, None, 3) == 3
    #    assert wrapper(None, None, 6) == 2
    #    assert wrapper(None, None, 0) == 4
    #    assert wrapper(None, None, 8) == 4

    #def test_bound(self):
    #    bounder = bound(lower=2, upper=6)
    #    assert bounder(None, None, 4) == 4
    #    assert bounder(None, None, 1) == 2
    #    assert bounder(None, None, 7) == 6

    def test_speed(self):
        candidates1 = [[0.5]*200]*800
        candidates2 = [[0.5]*200]*800
        mut = iterate(input=pick_fixed(num=20, input=iterate(input=bound(lower=0., upper=1., input=gaussian_mutation(mean=0.0, stdev=1.0)))))
        import time
        from ecspy.variators import mutators
        t0 = time.time()
        mutated = mut(Accessor(candidates1))
        t1 = time.time()
        #bounder = bound(lower=0.0, upper=1.0)
        class ec:
            def bounder(self, v, args):
                return bounder(v)
        mutated = mutators.gaussian_mutation(random, candidates2, {'_evolutionary_computation':ec(), 'mutation_rate':0.1})
        t2 = time.time()
        lap1 = t1-t0
        lap2 = t2-t1
        print "new time: %s, old time: %s, %s times slower" % (lap1, lap2, lap1 / lap2)
