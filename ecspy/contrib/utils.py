
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
    
    Use this function when you are evaluating a -expensive- fitness function 
    such that already evaluated individuals are cached, avoiding a costly 
    re-evaluation of its fitness...
    
    usage:
    
    @memoized
    my_fitness_function
    
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}
    def __call__(self, *args, **kwargs):
        try:
            return self.cache.setdefault(args,self.func(*args, **kwargs))
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args, **kwargs)
    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__
