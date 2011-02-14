'''
Created on Dec 14, 2010

`Self-modifying Cartesian Genetic Programming (SMCGP) is a general purpose,
graph-based, developmental form of Genetic Programming founded on Cartesian Genetic Programming.
In addition to the usual computational functions, it includes functions that can modify
the program encoded in the genotype. This means that programs can be iterated to produce an
infinite sequence of programs (phenotypes) from a single evolved genotype. It also allows programs
to acquire more inputs and produce more outputs during this iteration.`
--Harding,Miller,Banzhaf

Implementation based on the paper
Developments in Cartesian Genetic Programming: self-modifying CGP
by
Simon Harding,Julian F. Miller,Wolfgang Banzhaf



@author: Henrik Rudstrom



'''
import random
import inspect
from ecspy.variators.mutators import mutator


def call_mod(gene, a, b):
    if gene.activated:
        return b
    return a
def get_call_mod(func, call):
    '''called when a modification node is activated'''
    def f(gene, a, b):
        return call(gene,a,b)
    f.__name__ = func.__name__
    f.call_mod = True
    return f

def get_arity(function):
    if hasattr(function, 'input') and function.input:
        return 0
    if hasattr(function, 'call_mod') and function.call_mod:
        return 2
    
    args = len(inspect.getargspec(function).args)
    if hasattr(function, '__self__'):
        return args-1
    return args

class SMCGPGene(object):
    __slots__ = ['function', 'inputs', 'vars', 'activated', '__repr__', '__eq__', '__deepcopy__']
    def __init__(self, function=None, inputs=None, variables=None):
        self.function = function
        self.inputs = inputs
        self.vars = variables
        
    @property
    def activated(self):
        return self.inputs[0] > self.inputs[1]
    
    def __repr__(self):
        varstr = ",".join([str(a)[:5] for a in self.vars])
        return "<%s,%s,%s>" % (self.function, self.inputs, varstr)
    def __eq__(self, other):
        if self.function != other.function:
            return False
        eq = [a == b for a,b in zip(self.inputs, other.inputs)]
        if len(eq) != sum(eq):
            return False
        eq = [a == b for a,b in zip(self.vars, other.vars)]
        if len(eq) != sum(eq):
            return False
        return True
    
    def __deepcopy__(self, memo):
        cpy = self.__class__()
        memo[id(self)] = cpy
        cpy.function = self.function
        cpy.inputs = list(self.inputs)
        cpy.vars = list(self.vars)
        return cpy

class SMCGPEncoding:
    def __init__(self, length, max_arity, levelsback, min_outputs=1, max_modifications=2, variables=3):
        '''
        arguments:
        - *length* -- number of columns in the cgp matrix
        - *max_arity* -- tuple (number of edges pr node, number of data fields pr node) 
        - *levelsback* -- parameter that limits how many columns back a node can connect to, minimum 1
        - *min_outputs* -- minimum outputs needed
        '''
        self.length = length
        self.arity = max_arity
        self.levelsback = levelsback
        self.max_modifications = max_modifications
        self.variables = variables
        self.min_outputs = min_outputs
        self.gene_class = SMCGPGene
        
        
    def set_functions(self, functions, mod_callable=call_mod):
        function_names = []
        user_functions = []
        mod_functions = []
        io_functions = []
        for i, f in enumerate(functions):
            if hasattr(f, 'mod') and f.mod:
                mod_functions.append(f)
            elif hasattr(f, 'input') and f.input:
                io_functions.append(f)
            else:
                user_functions.append(f)
                
        self.functions = io_functions + user_functions + [get_call_mod(f, call_mod) for f in mod_functions]
        self.mod_functions = mod_functions
        #print "IOF", io_functions
        self.io_func_range = (0,len(io_functions))
        self.user_func_range = (self.io_func_range[1],self.io_func_range[1]+len(user_functions))
        self.mod_func_range = (self.user_func_range[1],self.user_func_range[1]+len(mod_functions))
        self.io_func_bias = 0.33
        self.user_func_bias = 0.33
        self.mod_func_bias = 0.33
        self.func_bias_sum = 0.99
        
        self.function_arity = {}
        for i, f in enumerate(self.functions):
            function_names.append(f.__name__)
            self.function_arity[i] = get_arity(f)
            #f.arity = get_arity(f)
        self.function_names = function_names
        
    def get_mod_function(self, index):
        return self.mod_functions[index - self.mod_func_range[0]]     
    
    
    def random_gene(self, col):
        mincol = 1
        if col < 1:
            mincol = 0
        return self.gene_class(
            #random.randint(0, len(self.functions)-1),
            self.random_func(col),
            [random.randint(mincol, min(col, self.levelsback)) for _ in xrange(self.arity)],               
            [random.random() * 10 for _ in xrange(self.variables)]
        )
    
    def generator(self):
        '''
        returns a generator function that generates a candidate
        '''
        
        def gen(random, args):
            matrix = []
            for col in xrange(self.length):
                matrix.append(self.random_gene(col))
            return matrix
        return gen
    
    def random_func(self, v):
        rnd = random.random() * self.func_bias_sum
        def in_range(range):
            return rnd >= range[0] and rnd < range[1]
        bias = self.io_func_bias
        range = self.io_func_range
        if rnd < bias:
            #print range
            return random.randint(range[0], range[1]-1)
        bias += self.user_func_bias
        range = self.user_func_range
        if rnd < bias:
            return random.randint(range[0], range[1]-1)
        bias += self.mod_func_bias
        range = self.mod_func_range
        if rnd < bias:
            return random.randint(range[0], range[1]-1)
        
    def random_edge(self, v):
        return (v + random.randint(1, self.levelsback)) % self.levelsback
    
    def random_var(self, v):
        return random.gauss(v, 1)   

    def mutator(self):        
        def mut(random, cand, args):
            maybe_mutate = lambda v, func: func(v) if random.random() < args['mutation_rate'] else v
            for gene in cand:
                gene.function = maybe_mutate(gene.function, self.random_func)
                gene.inputs = [maybe_mutate(c, self.random_edge) for c in gene.inputs]
                gene.vars = [maybe_mutate(c, self.random_var) for c in gene.vars]
                #gene.vars = [maybe_noise(c, randomize_var) for c in gene.vars] #TODO:get right noise
            return cand
        
        return mutator(mut)       

