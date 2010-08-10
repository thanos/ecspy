__author__ = 'henrik'

#from ecspy.contrib.variator_pipe import iterate, iterate, composite_variator, composite_variator, gaussian_mutation, bound


import networkx, random, math, unittest, time
from itertools import izip_longest, dropwhile

class CartesianGraphEncoding:
    def __init__(self, n_inputs, matrix_size, node_size, n_outputs, levelsback):
        '''matrix in the format [cols] x [rows] x [[node_size[0]][node_size[1]]]'''
        self.n_inputs = n_inputs
        self.matrix_size = matrix_size
        self.node_size = node_size
        self.n_outputs = n_outputs
        self.levelsback = levelsback

    def generator(self, random_edge, random_data):
        def gen(random, args):
            matrix = []
            for col in xrange(self.matrix_size[0]):
                col_rows = []
                for row in xrange(self.matrix_size[1]):
                    edges = [random_edge() for _ in xrange(self.node_size[0])]
                    data = [random_data() for _ in xrange(self.node_size[1])]
                    col_rows.append([edges, data])
                matrix.append(col_rows)
            outputs = [[[random_edge()],[]] for _ in xrange(self.n_outputs)]
            return matrix+[outputs]
        return gen

    def mutator(self, rate, mutate_edge, mutate_data):
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
        graph = graph or networkx.MultiDiGraph()
        matrix  = [[([1], [1])]] * self.n_inputs + matrix
        for col, rows in enumerate(matrix):
            for row, (inputs, data) in enumerate(rows):
                node = (col, row)
                node_data = dict(('s'+str(i), v) for i, v in enumerate(data))
                if col == 0:
                    node_data['input'] = True
                if col == self.matrix_size[0] + 1:
                    node_data['output'] = True
                graph.add_node(node, **node_data)
                if inputs is None:
                    import ipdb; ipdb.set_trace()
                decode = lambda input: self._decode_edge(col, input)

                edges = [(decode(input), node) for input in inputs]
                graph.add_edges_from(edges)
        return graph

    def _decode_edge(self, col,  float_index):
        mincol = max(0, (col - self.levelsback))
        range = col - mincol
        if range == 0:
            return None
        float_index = mincol + (float_index % 1.) * range
        col = int(float_index)
        row_len = self.matrix_size[1]
        if col == 0:
            row_len = self.n_inputs
        row = int(row_len * (float_index - col))
        return col, row

def node_function_template(node, args, graph):
    return 0.0

class CallableGraph:
    def __init__(self, graph, function, output_function=None, constants=None):
        self.graph = graph
        self.function = function
        self.output_function = output_function or self.output_function
        self.values = None

        self.inputs = filter(lambda n: 'input' in graph.node[n], graph.nodes())
        self.outputs = filter(lambda n: 'output' in graph.node[n], graph.nodes())

        call_order = []
        for out_node in self.outputs:
            path = networkx.dfs_postorder(graph.reverse(), out_node)
            call_order.extend(tuple(dropwhile(lambda p: p in call_order, path)))

        arg_func = lambda node: (e[0] for e in graph.in_edges_iter(node))
        self.call_order = tuple((node, list(arg_func(node))) for node in call_order)
        #self.constants = constants or []

    def __call__(self, input_values):
        values = {}
        output_values = []
        #input_values = input_values + self.constants
        for node, arg_nodes in self.call_order:
            if node[0] == 0:
                values[node] = input_values[node[1]]
                continue
            args = list((values[arg] for arg in arg_nodes))
            if node in self.outputs:
                values[node] = self.output_function(node, args, self.graph.node[node])
                output_values.append(values[node])
            else:
                values[node] = self.function(node, args, self.graph.node[node])
        self.values = values
        return output_values

    def output_function(self, node, args, data):
        return args

def draw_graph(graph, scale = 20):

    def view_pos(pos, scale):
        col, row = pos
        x = col * scale + scale / 5.  + (row % 2) * scale / 8
        y = row * scale + scale / 5. + (col % 2) * scale / 6
        return x, y

    pos = dict(((n, view_pos(n, 20)) for n in graph.nodes()))
    networkx.draw(graph, pos)

class CGPTest(unittest.TestCase):
    pass
