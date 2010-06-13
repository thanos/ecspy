import random
from ecspy import ec
from ecspy import variators
from ecspy import replacers
from ecspy import terminators
from ecspy import observers

def my_constraint_function(candidate):
    """Return the number of constraints that candidate violates."""
    # In this case, we'll just say that the point has to lie 
    # within a circle of radius 1.
    if candidate[0]**2 + candidate[1]**2 > 1:
        return 1
    else:
        return 0

def my_generator(random, args):
    # Create pairs in the range [-2, 2].
    return [4.0 * random.random() - 2.0 for i in range(2)]

def my_evaluator(candidates, args):
    # The fitness will be how close the point is to
    # the edge of the circle. (We're maximizing, in
    # this case.)
    WORST_FIT = -1
    fitness = []
    for cand in candidates:
        if my_constraint_function(cand) > 0:
            fitness.append(WORST_FIT)
        else:
            fit = cand[0]**2 + cand[1]**2
            fitness.append(fit)
    return fitness

def constrained_tournament_selection(random, population, args):
    num_selected = args.setdefault('num_selected', 1)
    constraint_func = args.setdefault('constraint_func', None)
    tourn_size = 2
    pop = list(population)
    selected = []
    for _ in range(num_selected):
        tourn = random.sample(pop, tourn_size)
        # If there is not a constraint function,
        # just do regular tournament selection.
        if constraint_func is None:
            selected.append(max(tourn))
        else:
            x = constraint_func(tourn[0].candidate)
            y = constraint_func(tourn[1].candidate)
            # If no constraints are violated, just do 
            # regular tournament selection.
            if max(x, y) == 0:
                selected.append(max(tourn))
            # Otherwise, choose the least violator 
            # (which may be a non-violator).
            elif x < y:
                selected.append(tourn[0])
            else:
                selected.append(tourn[1])
    return selected

r = random.Random()
myec = ec.EvolutionaryComputation(r)
myec.selector = constrained_tournament_selection
myec.variator = variators.gaussian_mutation
myec.replacer = replacers.generational_replacement
myec.terminator = terminators.evaluation_termination
myec.observer = observers.screen_observer
pop = myec.evolve(my_generator, my_evaluator, 
                  pop_size=100, 
                  num_selected=100,
                  lower_bound=-2.0,
                  upper_bound=2.0, 
                  constraint_func=my_constraint_function, 
                  max_evaluations=1000)
