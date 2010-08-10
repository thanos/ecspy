'''
refactoring proposal for the variators
inspired by vtk. construct a pipeline of functions that operate on lists and values:
functions are implemented as callable objects (could also be decorators/functions returning functions with closure).
they key is that they can store parameters specified during initialization.

the functions returns an object of the same type and size as it is input.
they can be divided into three categories:
* leaf-functions: the last function in the pipeline, these operate on the
  'raw' values of the genome and dont need any onput function to be specified
* iterators: calls the specified input function on all items in the passed list
* list-modifiers: modifies a list before it passes it to its input function, and
  reconstructs the original structure of the list before returning.

>>> mutator = select_by_rate(0.1, iterate(input=gaussian_mutation(mean=0.0, stdev=1.0)
returns a mutator that takes an candidater as input:
  1. select_by_rate makes a sublist based on the mutation rate
  2. iterate over the sublist
  3. apply gaussian mutation to the item
  4. select_by_rate places the mutate values back at its original place in the candidate list

>>> mutator.rate = lambda self, caller:


>>> mutator.rate = lambda self.pos, root: pos[-1] / len(get_recursive(pos[:-1], root)) * 0.8 + 0.2)
>>> def falloff(level, func):
        def f(pos, root):
            p = -(1+level)
            return pos[p] / len(get_recursive(pos[:p], root))
        return lambda, lambda self.pos: pos[-(1+level)] / len(get_recursive(pos[:-1], root)) * 0.8 + 0.2)


mut = iterate(iterate_rate(0, gaussian_mutation(-1)))
mut.input.rate = lambda v: 0.1 * (1+mut.index)
mut.input.input.stdev = lambda v: mut.index + 1


>>> pop = ...
>>> for root, pos, val in pop:
        pop.set(pos, select_by_rate(0.1 * pos[-1] + 0.2, iterate(input=mutator)
pop = list of candidates of n x n matrixes
#falloff pr column
mutator = iterate(variation_rate=lambda i, v: i * 0.1 / len(pop),
                  input=iterate(stdev=lambda i, v: i / len(pop[0]),
                                input=gaussian_mutation(mean=0.0)


##accessor style

mut = select(rate=0.1, input=iterate(input=gaussian_mutation(0.0, lambda acc: 1 - float(acc.pos[-1]) / len(acc.parent)) 

see unit tests in test-dir for examples

issues:
* integrate random argument, or find other means of storing the random generator
* give EC class the responsibility of iterating over the candidates
* functions has to be stateless (think they are mostly now, except .index parameter

'''


from random import Random
from itertools import izip, izip_longest, chain
import unittest
from copy import copy

__author__ = 'henrik'

random = Random()

def grouper(n, iterable, fillvalue=None, crop=False):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    if crop:
        return izip(*args)
    return izip_longest(fillvalue=fillvalue, *args)

class Accessor:
    def __init__(self, source, pos=None, value=None, mapping=None, group_size=1):
        self.source = source

        self.value = value if pos is not None else source
        self.pos = pos if pos is not None else []


        self.group_size = group_size

        self.mapping = mapping
        if mapping is None:
            if hasattr(self.value, '__len__'):
                self.mapping = xrange(len(self.value))

    @property
    def parent(self):
        return self.source[self.pos[-2]] if len(self.pos) > 1 else []

    def copy(self, root=None, pos=None, value=None, mapping=None, group_size=None):
        return Accessor(root or self.source, pos or self.pos,
                        value or self.value, mapping or self.mapping,
                        group_size or self.group_size)

    def get_param_values(self, function):
        return dict((name, function.params[name](self)) for name in function.params)



    def __getitem__(self, i):
        #ni = i
        #if self.mapping:
        #    ni = self.mapping[i]
        #if self.group_size > 1:
        #    ni = i * self.group_size
        ni = (self.mapping[i] if self.mapping is not None else i) * self.group_size
        return Accessor(self.source, pos=self.pos+[ni], value=self.value[i])

    def __len__(self):
        if self.mapping is None:
            return len(self.value)
        return len(self.mapping)

    def map_indices(self, mapping):
        return self.copy(mapping=mapping)

    def group(self, size, value):
        return self.copy(group_size=size, value=value)

    def __iter__(self):
        map_index = lambda i: (self.mapping[i] if self.mapping is not None else i) * self.group_size
        #mapping = self.mapping
        #if mapping is None:
        #    mapping = xrange(len(self.value))
        for m in self.mapping:
            yield Accessor(self.source, pos=self.pos+[m], value=self.value[self.mapping[m]])
        #return [self.input(accessor[i]) for i, vi in enumerate(accessor)]

# Leaf functions
# generates value based on genome value (can still be chained though)

class base_function(object):
    def __init__(self, input=lambda root, pos, v: v, **kwargs):
        self.input = input
        make_funcs = lambda key: kwargs[key] if hasattr(kwargs[key], '__call__') else lambda acc: kwargs[key]
        self.params = dict((key, make_funcs(key)) for key in kwargs)
        
    def __call__(self, accessor):
        raise NotImplementedError


class bit_flip_mutation(base_function):
    def __call__(self, accessor):
        return (accessor.value + 1) % 2

class gaussian_mutation(base_function):
    def __call__(self, accessor):
        params = dict((name, self.params[name](accessor)) for name in self.params)
        #params = accessor.get_param_values(self)
        return accessor.value + random.gauss(params['mean'], params['stdev'])

class n_point_crossover(base_function):
    def __init__(self, input, num_crossover_points=1):
        super(n_point_crossover, self).__init__(input, num_crossover_points=num_crossover_points)

    def __call__(self, accessor):
        params = accessor.get_param_values(self)
        val = accessor.value
        offspring = [list(cand) for cand in accessor.value]
        cand_len = len(offspring[0])
        num_cuts = min(cand_len-1, params['num_crossover_points'])
        cut_points = random.sample(range(1, cand_len), num_cuts)
        cut_points.sort()
        for p in cut_points:
            for i in xrange(len(val)):
                offspring[i][p:] = val[(i+1)%len(val)][p:]

        return offspring
#
#value modifiers
#accepts and returns a single value

class bound(base_function):
    def __call__(self, accessor):
        params = accessor.get_param_values(self)
        return max(min(self.input(accessor), params['upper']), params['lower'])

class wrap_around(bound):
    def __call__(self, accessor):
        params = accessor.get_param_values(self)
        return (self.input(accessor) - params['lower']) % (self.params['upper'] - params['lower']) + params['lower']


#
# Iterators
#  accepts a list and executes input function for every item

class iterate(base_function):
    def __call__(self, accessor):
        return [self.input(acc) for i, acc in enumerate(accessor)]

# List modifiers

class pick_fixed(base_function):
    def __call__(self, accessor):
        params = accessor.get_param_values(self)
        val = accessor.value
        #make subset
        picked_indices = self._pick_index(params, val)

        #execute
        #try:
        processed = self.input(accessor.map_indices(picked_indices))
        #except Exception as e:
        #    print "hmm"
        #reconstruct
        ret = list(val)
        for pi, ps in izip(picked_indices, processed):
            ret[pi] = ps

        return ret

    def _pick_index(self, params, val):
        #TODO: pick unique values
        return [random.randint(0, len(val)-1) for _ in xrange(params['num'])]


class pick_rate(pick_fixed):
    def _pick_index(self, params, val):
        #TODO: allow falloff function pr random call
        return filter(lambda i: random.random() < params['rate'], xrange(len(val)))


class group_candidates(base_function):
    def __call__(self, accessor):
        params = accessor.get_param_values(self)
        val = accessor.value
        groups = list(izip(*[iter(val)] * params['size']))
        values = self.input(accessor.group(params['size'], groups))
        return list(chain(*values))

