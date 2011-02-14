'''
(Self Modifying) Cartesian Genetic Programming. 
implemented as specified in the paper:
"Developments in Cartesian Genetic Programming: self-modifying CGP"
by Harding, Miller & Banzhaf (2010)

(no self modification yet)  


'''
__author__ = 'Henrik Rudstrom'
from docutils.parsers.rst.directives import encoding
import inspect
from ecspy.variators.mutators import mutator

import networkx, random, math, unittest, time
from itertools import izip_longest, dropwhile

class CGPEncoding:
    '''
       Defines a one single row cgp genome encoding.
    '''
    
    
    def __init__(self, length, max_arity, levelsback, user_functions, min_outputs=1):
        '''
        arguments:

        - *length* -- number of columns in the cgp matrix
        - *max_arity* -- tuple (number of edges pr node, number of data fields pr node)
        - *user_functions* -- list of node functions 
        - *levelsback* -- parameter that limits how many columns back a node can connect to, minimum 1
        - *min_outputs* -- minimum outputs needed
        '''
        self.length = length
        self.arity = max_arity
        self.levelsback = levelsback
        self.user_functions = user_functions
        
        self.min_outputs = min_outputs
        
        self.function_names = ['inp', 'inpp', 'out']
        self.function_arity = [0,0,1]
        for f in user_functions:
            self.function_names.append(f.__name__)
            self.function_arity.append(self.get_arity(f))
        self._function_count = len(self.function_names)
        
    def get_arity(self, function):
        args = len(inspect.getargspec(function))
        if hasattr(function, '__self__'):
            return args
        return args-1
        
            
        
    def generator(self):
        '''
        returns a generator function that generates a candidate
        '''
        def random_edges(col):
            return [random.randint(1, self.levelsback) for _ in xrange(self.arity)]
        
        def random_func(col):
            return random.randint(0, self._function_count-1)
        
        def gen(random, args):
            matrix = []
            for col in xrange(self.length):
                node = [random_func(col)]
                node += random_edges(col)
                matrix.append(node)
            return matrix
        return gen

    def mutator(self):        
        def mutate_edge(v):
            return (v + random.randint(1, self.levelsback)) % self.levelsback
        
        def mutate_func(v):
            l = self._function_count
            return (v + random.randint(1, l)) % l 
        
        def mut(random, cand, args):
            maybe_mutate = lambda v, func: func(v) if random.random() < args['mutation_rate'] else v
            matrix = []
            for col in cand:
                node = [maybe_mutate(col[0], mutate_func)] 
                node += [maybe_mutate(c, mutate_edge) for c in col[1:1+self.arity]]
                matrix.append(node)
                
            return matrix
        
        return mutator(mut)

class CGPPhenotype:
    def __init__(self, encoding, candidate):
        self.encoding = encoding
        self.candidate = candidate

    
#    def get_outputs(self):
#        outputs = []
#        for i, c in enumerate(self.candidate):
#            if c[0] == 2:
#                outputs.append(i)
#        return outputs

    def get_inputs(self, node):
        if node == 0:
            return []
        
        return [(node - i) % node for i in self.candidate[node][1:1+self.encoding.arity]]  
        
    def traverse(self, outputs=None):
        '''yields the nodes and their inputs in depth-first ordering'''
        
        nlist = outputs or self.get_outputs()
        seen={} # nodes seen      
        for source in nlist:
            if source in seen: continue
            queue=[source]     # use as LIFO queue
            while queue:
                v=queue[-1]
                if v not in seen:
                    seen[v]=True
                done=1
                inputs = self.get_inputs(v)
                for w in inputs:
                    if w not in seen:
                        queue.append(w)
                        done=0
                        break
                if done == 1:
                    yield v, inputs
                    queue.pop()



    def get_outputs(self):
        outputs = []
        for i, c in enumerate(self.candidate):
            if c[0] == 2 and i != 0: #first column cant be output
                outputs.append(self.get_inputs(i)[0])
        
        '''
        A number of measures need to be taken when the number of OUTPUT nodes 
        does not match the number of program outputs.
        - If there are no OUTPUT nodes in the graph, then the last n nodes in the graph are used
        - If there are more OUTPUT nodes than are required, then the right-most OUTPUT 
            nodes are used until the required number of outputs is reached.
        - If the graph has fewer OUTPUT nodes than are required graph, then nodes are 
        chosen as outputs by moving forwards from the right-most node flagged as an output.
        - If there is a condition where not enough nodes can be used as outputs (as there are 
        not enough nodes in the graph), the individual is labeled as corrupt and is given a 
        bad fitness score to prevent selection.
        '''
        #print "outputs", outputs
        mino = self.encoding.min_outputs
        if len(outputs) == 0:
            outputs = [len(self.candidate)-mino+i for i in xrange(mino)]
        while len(outputs) < self.encoding.min_outputs:
            outputs.append(outputs[-1]+1)
        return outputs
    
    def __call__(self, inputs, alternate_functions=None):
        io = FunctionIO(inputs)
        functions = [io.inp, io.inpp, io.out] + (alternate_functions or self.encoding.user_functions)
        
        values = {}
        
        for index, inp in self.traverse():
            
            node = self.candidate[index]
            #print index, inp, node
            f = node[0]
            if index == 0: #first node can only be input node
                f = f % 2
            
            args = [values[i] for i in inp[0:self.encoding.function_arity[f]]]
            val = functions[f](*args)
            values[index] = val
        
        return [values[inp] for inp in self.get_outputs()]
    
    def __repr__(self):
        values = {}
        for index, inp in self.traverse():
            node = self.candidate[index]
            name = self.encoding.function_names[node[0]]
            args = [values[i] for i in inp[0:self.encoding.function_arity[node[0]]]]
            values[index] = "%s(%s)" % (name, ", ".join(args))
        return "\n".join(["f(%s): %s" % (i, values[i]) for i in self.get_outputs()])
            

                


class FunctionIO:
    '''
    INP, INPP and SKIPINP. When decoding the phenotype graph, a pointer is maintained that refers to an input. 
    If the first occurrence of an active input function is INP it returns the first program input. If the first 
    occurrence is INPP, the last program input is returned. After INP is called it increments the input pointer. 
    INPP decrements the input pointer.
    '''
    def __init__(self, inputs):
        self.inputs = inputs
        self.pointer = None
        self.n_inputs = len(self.inputs)
       
    def inp(self):
        if self.pointer is None:
            self.pointer = 0
        else:
            self.pointer = (self.pointer + 1) % self.n_inputs
        return self.inputs[self.pointer] 
    
    def inpp(self):
        if self.pointer is None:
            self.pointer = len(self.inputs) - 1
        else:
            self.pointer = (self.pointer - 1) % self.n_inputs
        return self.inputs[self.pointer] 
    
    def out(self, val):
        '''output function, passes first argument on, in case it is referenced'''
        return val
                

def create_graph(encoding, candidate):
    graph = networkx.DiGraph()
    for node, inputs in encoding.traverse(candidate):
        if node is None:
            node="out"
            graph.add_node(node)
        else:
            graph.add_node(node, {"f":candidate[node][0]})
        graph.add_edges_from([(i, node) for i in inputs])
    return graph       

def draw_graph(graph, scale = 20):

    def view_pos(col, scale):
        x = col * scale + scale / 5.
        return x, 0

    pos = dict(((n, view_pos(n, 20)) for n in graph.nodes()))
    networkx.draw(graph, pos)

class CGPTest(unittest.TestCase):
    def test_input_output(self):
        enc = CGPEncoding(2, 1, 1, [], 2)
        gen = [[0,0],[0,0], [2, 2], [2,2], [2,3]]
        input = [5,2]
        func = CGPPhenotype(enc, gen)
        res = func(input)
        assert res[0] == input[0]
        assert res[1] == input[1]
        assert res[2] == input[1]
        
    def test_no_outputs(self):
        enc = CGPEncoding(2, 1, 1, [], 2)
        gen = [[0,0],[0,0]]
        input = [5,2]
        func = CGPPhenotype(enc, gen)  

        res = func(input)
        
        assert res[0] == input[0], "res"+res[0]
        assert res[1] == input[1], "res"+res[1]

    def test_too_few_outputs(self):
        enc = CGPEncoding(2, 1, 1, [], 2)
        gen = [[0,0],[0,0], [2,2]]
        input = [5,2]
        func = CGPPhenotype(enc, gen)    
        res = func(input)
        
        assert res[0] == input[0]
        assert res[1] == input[1]  
        
        
    def test_arithmetics(self):
        def add(a, b):
            
            return a + b
        def sub(a,b):
            return a - b
        
        enc = CGPEncoding(2, 2, 1, [add, sub], 1)
        gen1 = [[0,0,0],[0,0,0], [3,2,1], [3,2,2], [4, 2, 1], [2,1,0]]
        func = CGPPhenotype(enc, gen1)    
        input = [1,10]
        #(1 + 10) - (10 + 10) 
        res = func(input)
        assert res[0] == -9

