'''
refactoring proposal for the variators
inspired by vtk. construct a pipeline of functions that operate on lists and values:
functions are implemented as callable objects can store their parameters.
all functions except leaf-functions (gaussian_mutation/n_point_crossover) are initialized with a input function

many types of variators can be constructed:
linear_n_point_crossover = recombine_candidates(2, iterate_rate(0.5, n_point_crossover(3)))
two_d_gaussian_mutation = mutate_candidates(iterate(iterate_rate(0.1, bound(0., 1., gaussian_mutation(0.5, 0.5)))))

function parameters can be modulated :
mut = iterate(iterate_rate(0, gaussian_mutation(-1)))
mut.input.rate = lambda v: 0.1 * (1+mut.index)
mut.input.input.stdev = lambda v: mut.index + 1

see unit tests in test-dir for examples

some issues:
-not possible to set crossover rate, both iterate_rate and recombine_candidates are iterators
-random is a module variable, lot of clutter to pass it down all the calls....
-naming should be a bit more consistent/meaningful
-...



'''


from random import Random
from itertools import izip, izip_longest
import unittest

__author__ = 'henrik'

random = Random()

def grouper(n, iterable, fillvalue=None, crop=False):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    if crop:
        return izip(*args)
    return izip_longest(fillvalue=fillvalue, *args)


#
# Leaf functions
#


class bit_flip_mutation(object):
    def __call__(self, v):
        return (v + 1) % 2

class gaussian_mutation(object):
    def __init__(self, mean=0.0, stdev=1.0):
        self.mean = mean
        self.stdev = stdev
    def __call__(self, v):
        return v + random.gauss(self.mean, self.stdev)

class n_point_crossover(object):
    def __init__(self, num_crossover_points):
        self.num_crossover_points = num_crossover_points

    def __call__(self, sources):
        offspring = [list(cand) for cand in sources]
        cand_len = len(offspring[0])
        num_cuts = min(cand_len-1, self.num_crossover_points)
        cut_points = random.sample(range(1, cand_len), num_cuts)
        cut_points.sort()
        for p in cut_points:
            for i in xrange(len(sources)):
                offspring[i][p:] = sources[(i+1)%len(sources)][p:]

        return offspring

#
# Iterators
#

class iterate(object):
    def __init__(self, input=lambda v: v):
        self.input = input
        self.wrapped_input = self._maintain_state(input)

    def __call__(self, candidates=None, random=random, args={}):
        '''signature hack to be compatible with ec.py'''
        self.index = 0
        #noinspection PyCallingNonCallable
        return [self.wrapped_input(i, li) for i, li in enumerate(candidates)]

    def _maintain_state(self, fn):
        '''override this method to store state parameters
           possibly alters the method signature
        '''
        def _ms(i, *args):
            self.index = i
            return fn(*args)
        return _ms


class mutate_candidates(iterate):
    pass

class recombine_candidates(iterate):
    def __init__(self, group_size, input=lambda v: v):
        super(recombine_candidates, self).__init__(input)
        self.group_size = group_size

    def __call__(self, candidates=None, random=random, args={}):
        cs_copy = [] * len(candidates)
        random.shuffle(candidates)
        for gi, group in enumerate(grouper(self.group_size, candidates, crop=True)):
            i = gi * self.group_size
            cs_copy[i:i+self.group_size] = self.wrapped_input(gi, group)
        return cs_copy

class iterate_rate(iterate):
    def __init__(self, rate, input=lambda v: v):
        super(iterate_rate, self).__init__(input)
        self.rate = rate

    def __call__(self, v):
        f = lambda i, v: self.wrapped_input(i, v) if random.random() < self.rate else v
        return [f(i, vi) for i, vi in enumerate(v)]



class bound(object):
    def __init__(self, lower, upper, input=lambda v: v):
        self.input = input
        self.lower = lower
        self.upper = upper

    def __call__(self, v):
        return max(min(self.input(v), self.upper), self.lower)

class wrap_around(bound):
    def __call__(self, v):
        return (self.input(v) - self.lower) % (self.upper - self.lower) + self.lower
