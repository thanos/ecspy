#start_imports
from random import Random
from time import time
from time import sleep
from ecspy import ec
from ecspy import observers
from ecspy import replacers
from ecspy import selectors
from ecspy import terminators
from ecspy import variators
from Tkinter import *
#end_imports


def area(p):
    return 0.5 * abs(sum([x0*y1 - x1*y0 for ((x0, y0), (x1, y1)) in segments(p)]))

def segments(p):
    return zip(p, p[1:] + [p[0]])

def generate_polygon(random, args):
    try:
        size = args['num_vertices']
    except KeyError:
        size = 1
    try:
        lower = args['lower_bound']
    except KeyError:
        lower = -1
    try:
        upper = args['upper_bound']
    except KeyError:
        upper = 1
    return [(random.uniform(lower, upper), random.uniform(lower, upper)) for i in xrange(size)]

def evaluate_polygon(candidates, args):
    fitness = []
    for cs in candidates:
        fit = area(cs)
        fitness.append(fit)
    return fitness

def mutate_polygon(random, candidates, args):
    try:
        mut_rate = args['mutation_rate']
    except KeyError:
        mut_rate = 0.1
        args['mutation_rate'] = mut_rate
    try:
        mut_range = args['mutation_range']
    except KeyError:
        mut_range = 1.0
        args['mutation_range'] = mut_range
    try:
        lower_bound = args['lower_bound']
    except KeyError:
        lower_bound = 0
        args['lower_bound'] = lower_bound
    try:
        upper_bound = args['upper_bound']
    except KeyError:
        upper_bound = 1
        args['upper_bound'] = upper_bound
        
    try:
        iter(lower_bound)
    except TypeError:
        clen = max([len(x) for x in candidates])
        lower_bound = [lower_bound] * clen
        
    try:
        iter(upper_bound)
    except TypeError:
        clen = max([len(x) for x in candidates])
        upper_bound = [upper_bound] * clen
        
    cs_copy = list(candidates)
    for i, cs in enumerate(cs_copy):
        for j, c in enumerate(cs):
            if random.random() < mut_rate:
                x = c[0] + random.gauss(0, mut_range) * (upper_bound[j] - lower_bound[j])
                x = max(min(x, upper_bound[j]), lower_bound[j])
                y = c[1] + random.gauss(0, mut_range) * (upper_bound[j] - lower_bound[j])
                y = max(min(y, upper_bound[j]), lower_bound[j])
                cs_copy[i][j] = (x, y)
    return cs_copy
        
def polygon_observer(population, num_generations, num_evaluations, args):
    try:
        canvas = args['canvas']
    except KeyError:
        root = Tk()
        canvas = Canvas(root, bg='white', height=400, width=400)
        args['canvas'] = canvas
        
    # Get the best polygon in the population.
    poly = population[0].candidate
    coords = [(100*x + 200, -100*y + 200) for (x, y) in poly]
    old_polys = canvas.find_withtag('poly')
    for p in old_polys:
        canvas.delete(p)
    old_rects = canvas.find_withtag('rect')
    for r in old_rects:
        canvas.delete(r)
    old_verts = canvas.find_withtag('vert')
    for v in old_verts:
        canvas.delete(v)
        
    canvas.create_rectangle(100, 100, 300, 300, fill='', outline='yellow', width=6, tags='rect')
    canvas.create_polygon(coords, fill='', outline='black', width=2, tags='poly')
    vert_radius = 3
    for (x, y) in coords:
        canvas.create_oval(x-vert_radius, y-vert_radius, x+vert_radius, y+vert_radius, fill='blue', tags='vert')
    canvas.pack()
    canvas.update()
    print('%d evaluations' % num_evaluations)
    sleep(0.05)

#start_main
rand = Random()
rand.seed(int(time()))
my_ec = ec.EvolutionaryComputation(rand)
my_ec.selector = ec.selectors.tournament_selection
my_ec.variator = [ec.variators.uniform_crossover, mutate_polygon]
my_ec.replacer = ec.replacers.steady_state_replacement
my_ec.observer = polygon_observer
window = Tk()
window.title('Evolving Polygons')
can = Canvas(window, bg='white', height=400, width=400)
can.pack()

final_pop = my_ec.evolve(generator=generate_polygon,
                         evaluator=evaluate_polygon,
                         terminator=[terminators.evaluation_termination, terminators.avg_fitness_termination],
                         max_evaluations=5000,
                         num_selected=2,
                         mutation_rate=0.25,
                         pop_size=100,
                         num_vertices=3,
                         lower_bound=-1,
                         upper_bound=1,
                         canvas=can)
# Print the best individual, who will be at index 0.
print(final_pop[0])
sleep(5)
#end_main
