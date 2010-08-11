from docutils.parsers.rst.directives import encoding

__author__ = 'henrik'

import networkx, random, math, unittest, time
from itertools import izip_longest, dropwhile

class CartesianGraphEncoding:
    '''
       Stores the specification of the gp array to generate variation operators and
       decode the candidate matrix into a graph
    '''
    def __init__(self, n_inputs, matrix_size, node_size, n_outputs, levelsback):
        '''
        arguments:

        - *n_inputs* -- number of rows in the input column (including constants)
        - *matrix_size* -- tuple (columns, rows), excluding input and output columns
        - *node_size* -- tuple (number of edges pr node, number of data fields pr node)
        - *n_outputs* -- number of rows in the output column
        - *levelsback* -- parameter that limits how many columns back a node can connect to, minimum 1
        '''
        self.n_inputs = n_inputs
        self.matrix_size = matrix_size
        self.node_size = node_size
        self.n_outputs = n_outputs
        self.levelsback = levelsback

    def generator(self, random_edge, random_data):
        '''
        returns a generator function that generates a candidate matrix in the form:
        cols x rows x [edges, data]

        Arguments:

        - *random_edge* -- function to generate a random float edge index between 0. 1.
        - *random_data* -- function to generate a random data value (problem dependent)
        '''
        def gen(random, args):
            matrix = []
            for col in xrange(self.matrix_size[0]):
                col_rows = []
                for row in xrange(self.matrix_size[1]):
                    edges = [random_edge() for _ in xrange(self.node_size[0])]
                    #TODO: should perhaps return the whole data array, to allow multiple data types etc
                    data = [random_data() for _ in xrange(self.node_size[1])]
                    col_rows.append([edges, data])
                matrix.append(col_rows)
            outputs = [[[random_edge()],[]] for _ in xrange(self.n_outputs)]
            return matrix+[outputs]
        return gen

    def mutator(self, rate, mutate_edge, mutate_data):
        '''
        Arguments:

        - *mutate_edge* -- function to mutate a float edge index between 0. 1.
        - *mutate_data* -- function to mutate a random data value (problem dependent)
        '''
        def mut(random, cand, args):
            maybe_mutate = lambda v, func: func(v) if random.random() < rate else v
            matrix = []
            for col, cval in enumerate(cand[:-1]):
                col_rows = []
                for row, (edges, data) in enumerate(cval):
                    edges = [maybe_mutate(v, mutate_edge) for v in edges]
                    data = [maybe_mutate(v, mutate_data) for v in data]
                    col_rows.append([edges, data])
                matrix.append(col_rows)
            outputs = [[[maybe_mutate(v, mutate_edge)],[]] for _ in xrange(self.n_outputs)]
            return matrix+[outputs]
        return lambda random, candidates, args: [mut(random, candidate, args) for candidate in candidates]

    def decode(self, matrix, graph=None):
        '''
        creates a networkx.MultiDiGraph from the given candidate matrix
        '''

        #multiple cgps could potentially be stacked to implement rudimentary typing (not tested)
        graph = graph or networkx.MultiDiGraph()

        #the input column dont encode any data, so the input column
        #has to be appended with empty node values
        matrix  = [[[[], []]] * self.n_inputs] + matrix

        for col, rows in enumerate(matrix):
            for row, (inputs, data) in enumerate(rows):
                #node identifier in the graph
                node = (col, row)

                #create a dictionary of the data fields
                node_data = dict((i, v) for i, v in enumerate(data))

                #set input and output flags for first and last column
                if col == 0:
                    node_data['input'] = True
                if col == self.matrix_size[0] + 1:
                    node_data['output'] = True
                graph.add_node(node, node_data)

                #get edges as a tuple of node tuples (col, row)
                decode = lambda input: self._decode_input_node(col, input)
                edges = [(decode(input), node) for input in inputs]

                graph.add_edges_from(edges)
        return graph

    def _decode_input_node(self, col,  float_index):
        '''
            returns the source node for an input edge (col, row) tuple
            - *col* -- the column of the destination node
            - *float_index* -- encoded value of edge
        '''
        #determine column range
        mincol = max(0, (col - self.levelsback))
        range = col - mincol
        if range == 0:
            return None
        #scale float index to range
        float_index = mincol + (float_index % 1.) * range

        #column is floored value
        col = int(float_index)

        #determine number of rows
        row_len = self.matrix_size[1]
        if col == 0:
            row_len = self.n_inputs
        if col == self.matrix_size[0] + 1:
            row_len = self.n_outputs

        #scale remainder of float_index to row range
        row = int(row_len * (float_index - col))

        return col, row

def node_function_template(node, args, graph):
    return 0.0

class CallableGraph:
    '''
       A function defined by an acyclic graph with function mapped to the nodes
    '''


    def __init__(self, graph, function):
        '''
           Arguments:

           - *graph* -- networkx.DiGraph or MultiDiGraph
           - *function* -- function to be executed at each node.
           signature: (node, args_values, node_data)
        '''
        self.graph = graph
        self.function = function
        self.values = None

        self.inputs = filter(lambda n: 'input' in graph.node[n], graph.nodes())
        self.outputs = filter(lambda n: 'output' in graph.node[n], graph.nodes())


        #call order array is an list of all nodes with corresponding input nodes ordered
        #by their dependency.
        #TODO: better would probably be to generate the function code and compile/eval it
        call_order = []
        for out_node in self.outputs:
            path = networkx.dfs_postorder(graph.reverse(), out_node)
            call_order.extend(tuple(dropwhile(lambda p: p in call_order, path)))

        arg_func = lambda node: (e[0] for e in graph.in_edges_iter(node))
        self.call_order = tuple((node, list(arg_func(node))) for node in call_order)

    def __call__(self, input_values):
        '''
        call the function.
        Arguments:

        - *input_values* -- array of input values (including constants)

        '''
        values = {}
        output_values = []

        #iterate over node, preceding nodes
        for node, arg_nodes in self.call_order:
            #map the input values to the input nodes in the values dict
            if node[0] == 0:
                values[node] = input_values[node[1]]
                continue

            #fetch argument values (call order guarantees that input nodes are already in the dict
            args = list((values[arg] for arg in arg_nodes))

            #call node function


            self.values = values
            if not node in self.outputs:
                values[node] = self.function(node, args, self.graph.node[node])
            else:
                output_values.append(args[0])
        return output_values

def draw_graph(graph, scale = 20):

    def view_pos(pos, scale):
        col, row = pos
        x = col * scale + scale / 5.  + (row % 2) * scale / 8
        y = row * scale + scale / 5. + (col % 2) * scale / 6
        return x, y

    pos = dict(((n, view_pos(n, 20)) for n in graph.nodes()))
    networkx.draw(graph, pos)

class CGPTest(unittest.TestCase):
    def setUp(self):
        matrix_size = 4, 3
        n_inputs, n_outputs = 2, 1
        node_size = 2, 1
        levelsback = 3
        self.encoding = CartesianGraphEncoding(n_inputs, matrix_size, node_size, n_outputs, levelsback)


    def test_decode_edge(self):
        def assert_decode(node, col, val):
            dnode = enc._decode_input_node(col, val)
            assert node == dnode, ("decoding failed %s != %s" % (node, dnode)) 
        enc = self.encoding
        cols, rows = enc.matrix_size
        assert_decode((0,0), 1, 0.0)
        assert_decode((0,1),1, 0.5)
        assert_decode((1,0),2, 0.5)
        assert_decode((1,2),2, 0.9999)
        assert_decode((0,1),3, 0.17)
        assert_decode((1,2),3, 1.0 / 3 + 2. / 9)
        assert_decode((2,0),5, 0.0)
        assert_decode((3,0),5, 1.0 / 3)
        assert_decode((4,2),5, 0.9999)
        
    def test_generator(self):
        enc = self.encoding
        gen = enc.generator(random_data=lambda: 'a', random_edge=lambda: 1.0)
        matrix = gen(random, {})
        assert len(matrix) == enc.matrix_size[0] + 1 #output column encoded, input column not
        assert len(matrix[0]) == enc.matrix_size[1]
        assert len(matrix[0][0]) == 2 #edge list and data list
        assert len(matrix[0][0][0]) == enc.node_size[0] #edge list and data list
        assert len(matrix[0][0][1]) == enc.node_size[1] #edge list and data list
        assert len(matrix[-1]) == enc.n_outputs
        assert len(matrix[-1][0][0]) == 1 #one input
        assert len(matrix[-1][0][1]) == 0 #no data

    def test_graph_decoder(self):
        enc = self.encoding
        gen = enc.generator(random_data=lambda: 'a', random_edge=random.random)
        matrix = gen(random, {})
        graph = enc.decode(matrix)
        n_nodes = enc.matrix_size[0] * enc.matrix_size[1]
        print n_nodes, len(graph.nodes()), len(graph.edges())

        #assert created
        assert len(graph.nodes()) == n_nodes + enc.n_outputs + enc.n_inputs
        assert len(graph.edges()) == n_nodes * 2 + enc.n_outputs

        #assert that all edges are valid, ie not on same column and within levelsback
        for (c1, r1), (c2, r2) in graph.edges():
            assert c2 - c1 > 0
            assert c2 - c1 <= enc.levelsback