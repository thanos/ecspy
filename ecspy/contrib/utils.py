
def round_fitness(population, _round=3):
    '''
    returns the rounded fitness values of a population
    @param population: the population which has the fitness to be rounded    
    @param _round:     decimal digits to round off
    '''
    _pop = []
    for p in population:
        if hasattr(p.fitness, '__iter__'):
            _pop.append([round(i,_round) for i in p.fitness])
        else:
            _pop.append(round(p.fitness,_round))
    return _pop

class memoized(object):
    """Decorator that caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.
    
    Use this function when you are evaluating an *expensive* fitness function 
    such that already evaluated individuals are cached, avoiding a costly 
    re-evaluation of its fitness.
    
    usage:
    
    @memoized
    my_fitness_function
    
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}
        
    def __call__(self, candidates, args):
        fitness = []
        for candidate in candidates:
            try:
                fitness.append(self.cache[tuple(candidate)])
            except KeyError:
                fitness.append(self.func([candidate], args)[0])
                self.cache[tuple(candidate)] = fitness[-1]
            except TypeError:
                fitness.append(self.func([candidate], args)[0])
        return fitness
        
    def __repr__(self):
        return self.func.__doc__

        