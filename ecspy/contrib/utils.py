
class memoized(object):
    """Cache a function's return value each time it is called.
    
    This function serves as a function decorator to provide a caching of
    evaluated fitness values. If called later with the same arguments, 
    the cached value is returned instead of being re-evaluated.
    
    This decorator assumes that candidates can be converted into 
    ``tuple`` objects to be used for hashing into a dictionary. It 
    should be used when evaluating an *expensive* fitness 
    function to avoid costly re-evaluation of those fitnesses. The 
    typical usage is as follows::
    
        @memoized
        def expensive_fitness_function(candidates, args):
            # Implementation of expensive fitness calculation
    
    """
    def __init__(self, target):
        self.target = target
        self.cache = {}
        
    def __getattr__(self, name):
        if name == '__name__':
            return self.target.__name__
        else:
            return getattr(self, name)

    def __repr__(self):
        return self.target.__doc__
        
    def __call__(self, candidates, args):
        fitness = []
        for candidate in candidates:
            try:
                fitness.append(self.cache[tuple(candidate)])
            except KeyError:
                fitness.append(self.target([candidate], args)[0])
                self.cache[tuple(candidate)] = fitness[-1]
            except TypeError:
                fitness.append(self.target([candidate], args)[0])
        return fitness
        


import inspect
class instantiated(object):
    """Create a instantiated version of a function.
    
    This function allows an ordinary function passed to it to act 
    very much like a callable instance of a class. For ``ecspy``, 
    this means that evolutionary operators (selectors, variators,
    replacers, etc.) can be created as normal functions and then
    be given the ability to have attributes *that are specific to
    the instance*. Python functions can always have attributes without
    employing any special mechanism, but those attributes exist for the 
    function, and there is no way to create a new "instance" except
    by implementing a new function with the same functionality.
    This class provides a way to "instantiate" the same function
    multiple times in order to provide each "instance" with its own
    set of independent attributes.
    
    The attributes that are created on a instantiated function are
    passed into that function via the ubiquitous ``args`` variable
    in ``ecspy``. Any user-specified attributes are added to the 
    ``args`` dictionary and replace any existing entry if necessary.
    If the function modifies those entries in the dictionary (e.g.,
    when dynamically modifying parameters), the corresponding 
    attributes are modified as well.
    
    Note that this class makes heavy use of run-time inspection
    provided by the ``inspect`` core library. 
    
    The typical usage is as follows::
    
        def typical_function(*args, **kwargs):
            # Implementation of typical function
        
        fun_one = instantiated(typical_function)
        fun_two = instantiated(typical_function)
        fun_one.attribute = value_one
        fun_two.attribute = value_two
    
    """
    def __init__(self, target):
        self.target = target
        
    def __getattr__(self, name):
        if name == '__name__':
            return self.target.__name__
        else:
            return getattr(self, name)
        
    def __repr__(self):
        return self.target.__doc__
        
    def __call__(self, *args, **kwargs):
        params = self.__parameters()
        try:
            orig_args = dict(kwargs['args'])
            orig_args.update(params)
            newkwargs = dict(kwargs)
            newkwargs['args'] = orig_args
            newargs = args
        except KeyError:
            orig_args = dict(args[-1])
            orig_args.update(params)
            newargs = list(args[:-1])
            newargs.append(orig_args)
            newargs = tuple(newargs)
            newkwargs = kwargs
        return_value = self.target(*newargs, **newkwargs)
        local_dict = self.__find_self().__dict__
        try:
            for key in newkwargs['args']:
                if key in local_dict:
                    local_dict[key] = newkwargs['args'][key]
        except KeyError:
            for key in newargs[-1]:
                if key in local_dict:
                    local_dict[key] = newargs[-1][key]
        return return_value
        
    def __find_self(self):
        for i, entry in enumerate(inspect.stack()):
            locals = entry[0].f_locals
            for var in locals:
                if isinstance(locals[var], self.__class__):
                    return locals[var]
        raise TypeError('%s class is not being used' % self.__class__.__name__)
        
    def __parameters(self):
        found_self = self.__find_self()
        params = dict(found_self.__dict__)
        try:
            del params['target']
        except KeyError:
            pass
        return params
        