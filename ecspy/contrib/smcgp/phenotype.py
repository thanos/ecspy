'''
Created on Dec 14, 2010
@author: Henrik Rudstrom

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


'''
import copy



def input(func):
    '''decorator to mark functions as input functions'''
    func.input = True
    return func

@input
def inp(io, gene):
    #print io.inputs, io.pointer, gene
    if io.pointer is None:
        io.pointer = 0
    else:
        io.pointer = (io.pointer + 1) % len(io.inputs)
    return io.inputs[io.pointer] 

@input
def inpp(io, gene):
    if io.pointer is None:
        io.pointer = len(io.inputs) - 1
    else:
        io.pointer = (io.pointer - 1) % io.n_inputs
    return io.inputs[io.pointer] 

def out(self, gene, val):
    '''output function, passes first argument on, in case it is referenced'''
    return val

io_functions = [inp, inpp, out]
class InputPointer:
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



def bind_modification(enc, gene, index):
    '''bind modification functions with their arguments'''
    mod = enc.get_mod_function(gene.function)
    def f(cand):
        return mod(enc, gene, cand, index)
    f.__name__ = mod.__name__
    return f

class SMCGPPhenotype:
    def __init__(self, encoding, candidate):
        self.encoding = encoding
        self.candidate = candidate
        self._traversal = [(n, inp) for n, inp in self.traverse()]
        self.init_todo_list()
        
    def init_todo_list(self):
        mod_func_index = self.encoding.mod_func_range[0]
        mod_indices = filter(lambda n: n.function >= mod_func_index and n.activated, self.candidate)
        todo = []
        for i, n in enumerate(self.candidate):
            if n.function < mod_func_index or not n.activated:
                continue
            if len(todo) > self.encoding.max_modifications:
                break
            todo.append(bind_modification(self.encoding, n, i))
        self.todo_list = todo 
        return mod_indices    

    def get_inputs(self, node):
        if node == 0:
            return []
        if node >= len(self.candidate):
            print "warning", node
        inps= [(node - i) % node for i in self.candidate[node].inputs]
        for i in inps:
            if i >= len(self.candidate):
                raise Exception() 
        return inps 
        
    def traverse(self, outputs=None):
        '''yields the nodes and their inputs in depth-first ordering'''
        if len(self.candidate) < 1:
            return
        nlist = outputs or self.get_outputs()
        #print "trav", nlist
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
        outputs = []
        if len(self.candidate) == 0:
            return []
        for i, c in enumerate(self.candidate):
            if c.function == 2 and i != 0: #first column cant be output
                outputs.append(self.get_inputs(i)[0])
                
        mino = self.encoding.min_outputs
        if len(outputs) == 0:
            outputs = [len(self.candidate)-mino+i for i in xrange(mino)]
        while len(outputs) < self.encoding.min_outputs:
            outputs.append(outputs[-1]+1)
        if len(outputs) > 0:    
            assert max(outputs) < len(self.candidate), "Outputs: %s\nLength of candidate %s" % (outputs, len(self.candidate)) 
        return outputs

        
    def is_valid(self):
        if len(self.candidate) == 0:
            return False
        return True

    def is_active_mod(self, index):
        ''' 
        The input values to nodes are found and the behavior of the node is based on these input values. 
        If the first input is greater or equal to the second, then the graph manipulation function is 
        added to a 'To Do' list of pending modifications and the node returns the first input
        '''
        inputs = self.candidate[1:self.encoding.arity+1]
        return inputs[0] > inputs[1]


    
    def get_modified(self):
        cand = copy.deepcopy(self.candidate)
        #cand = [copy_gene(c) for c in self.candidate]
        for mod in self.todo_list:
            cand = mod(cand)
            if len(cand) == 0:
                break
        return SMCGPPhenotype(self.encoding, cand)
    
    def __call__(self, inputs, values=None):
        functions = list(self.encoding.functions)
        pointer = InputPointer(inputs)
        def input_wrap(func):
            def f(gene):
                return func(pointer, gene)
            f.arity = 0
            f.__name__ = func.__name__
            return f
        #input nodes are always the first in the set
        for i,f in enumerate(functions):
            if not hasattr(f, 'input') or not f.input:
                break
            #print "Func",f
            functions[i] = input_wrap(f)

        if values is None:
            values = {}
        #print self.candidate
        for index, inp in self._traversal:
            gene = self.candidate[index]
            f = gene.function
            if index == 0: #first node can only be input node
                f = f % 2
            func = functions[f]
            arity = self.encoding.function_arity[f]
            args = [gene]+[values[i] for i in inp[0:arity]]
            #print func, arity, args
            val = func(*args)
            values[index] = val
        #print values
        out = [values[inp] for inp in self.get_outputs()] 
        #print out
        return out
    
    def __repr__(self):
        values = {}
        for index, inp in self.traverse():
            node = self.candidate[index]
            name = self.encoding.function_names[node.function]
            arity = self.encoding.function_arity[node.function]
            args = [values[i] for i in inp[0:arity]]
            values[index] = "%s(%s)" % (name, ", ".join(args))
        return "\n".join(["f(%s): %s" % (i, values[i]) for i in self.get_outputs()])
