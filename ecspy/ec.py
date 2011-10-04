"""
    This module provides the framework for making evolutionary computations.
    
    .. Copyright (C) 2009  Inspired Intelligence Initiative

    .. This program is free software: you can redistribute it and/or modify
       it under the terms of the GNU General Public License as published by
       the Free Software Foundation, either version 3 of the License, or
       (at your option) any later version.

    .. This program is distributed in the hope that it will be useful,
       but WITHOUT ANY WARRANTY; without even the implied warranty of
       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
       GNU General Public License for more details.

    .. You should have received a copy of the GNU General Public License
       along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import time
import copy
import logging
import itertools
from ecspy import selectors
from ecspy import variators
from ecspy import replacers
from ecspy import migrators
from ecspy import archivers
from ecspy import terminators
from ecspy import observers


class Bounder(object):
    """Defines a basic bounding function for numeric lists.
    
    This callable class acts as a function that bounds a 
    numeric list between the lower and upper bounds specified.
    These bounds can be single values or lists of values. For
    instance, if the candidate is composed of five values, each
    of which should be bounded between 0 and 1, you can say
    ``Bounder([0, 0, 0, 0, 0], [1, 1, 1, 1, 1])`` or just
    ``Bounder(0, 1)``. If either the ``lower_bound`` or 
    ``upper_bound`` argument is ``None``, the Bounder leaves 
    the candidate unchanged (which is the default behavior).
    
    A bounding function is necessary to ensure that all 
    evolutionary operators respect the legal bounds for 
    candidates. If the user is using only custom operators
    (which would be aware of the problem constraints), then 
    those can obviously be tailored to enforce the bounds
    on the candidates themselves. But the built-in operators
    make only minimal assumptions about the candidate solutions.
    Therefore, they must rely on an external bounding function
    that can be user-specified (so as to contain problem-specific
    information). As a historical note, ECsPy was originally 
    designed to require the maximum and minimum values for all
    components of the candidate solution to be passed to the
    ``evolve`` method. However, this was replaced by the bounding
    function approach because it made fewer assumptions about
    the structure of a candidate (e.g., that candidates were 
    going to be lists) and because it allowed the user the
    flexibility to provide more elaborate boundings if needed.
    
    In general, a user-specified bounding function must accept
    two arguments: the candidate to be bounded and the keyword
    argument dictionary. Typically, the signature of such a 
    function would be ``bounding_function(candidate, args)``.
    This function should return the resulting candidate after 
    bounding has been performed.
    
    Public Attributes:
    
    - *lower_bound* -- the lower bound for a candidate
    - *upper_bound* -- the upper bound for a candidate
    
    """
    def __init__(self, lower_bound=None, upper_bound=None):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        if self.lower_bound is not None and self.upper_bound is not None:
            try:
                iter(self.lower_bound)
            except TypeError:
                self.lower_bound = itertools.repeat(self.lower_bound)
            try:
                iter(self.upper_bound)
            except TypeError:
                self.upper_bound = itertools.repeat(self.upper_bound)
            

    def __call__(self, candidate, args):
        # The default would be to leave the candidate alone
        # unless both bounds are specified.
        if self.lower_bound is None or self.upper_bound is None:
            return candidate
        else:
            try:
                iter(self.lower_bound)
            except TypeError:
                self.lower_bound = [self.lower_bound] * len(candidate)
            try:
                iter(self.upper_bound)
            except TypeError:
                self.upper_bound = [self.upper_bound] * len(candidate)
            bounded_candidate = copy.copy(candidate)
            for i, (c, lo, hi) in enumerate(zip(candidate, self.lower_bound, self.upper_bound)):
                bounded_candidate[i] = max(min(c, hi), lo)
            return bounded_candidate


class Individual(object):
    """Represents an individual in an evolutionary computation.
    
    An individual is defined by its candidate solution and the
    fitness (or value) of that candidate solution.
    
    Public Attributes:
    
    - *candidate* -- the candidate solution
    - *fitness* -- the value of the candidate solution
    - *birthdate* -- the system time at which the individual was created
    - *maximize* -- Boolean value stating use of maximization
    
    """
    def __init__(self, candidate=None, maximize=True):
        self.candidate = candidate
        self.fitness = None
        self.birthdate = time.time()
        self.maximize = maximize
    
    def __setattr__(self, name, val):
        if name == 'candidate':
            self.__dict__[name] = val
            self.fitness = None
        else:
            self.__dict__[name] = val
    
    def __str__(self):
        return '%s : %s' % (str(self.candidate), str(self.fitness))
        
    def __repr__(self):
        return '<Individual: candidate = %s, fitness = %s, birthdate = %s>' % ( str(self.candidate), str(self.fitness), self.birthdate )
        
    def __lt__(self, other):
        if self.fitness is not None and other.fitness is not None:
            if self.maximize: 
                return self.fitness < other.fitness
            else:
                return self.fitness > other.fitness
        else:
            raise Exception('fitness is not defined')

    def __le__(self, other):
        return self < other or not other < self
            
    def __gt__(self, other):
        if self.fitness is not None and other.fitness is not None:
            return other < self
        else:
            raise Exception('fitness is not defined')

    def __ge__(self, other):
        return other < self or not self < other
        
    def __lshift__(self, other):
        return self < other
    
    def __rshift__(self, other):
        return other < self
        
    def __ilshift__(self, other):
        raise TypeError("unsupported operand type(s) for <<=: 'Individual' and 'Individual'")
    
    def __irshift__(self, other):
        raise TypeError("unsupported operand type(s) for >>=: 'Individual' and 'Individual'")
        
    def __eq__(self, other):
        return self.candidate == other.candidate
        
    def __ne__(self, other):
        return self.candidate != other.candidate


class EvolutionExit(Exception):
    """An exception that may be raised and caught to end the evolution.
    
    This is an empty exception class that can be raised by the user
    at any point in the code and caught outside of the ``evolve``
    method. 
    
    """
    pass


class EvolutionaryComputation(object):
    """Represents a basic evolutionary computation.
    
    This class encapsulates the components of a generic evolutionary
    computation. These components are the selection mechanism, the
    variation operators, the replacement mechanism, the migration
    scheme, and the observers.
    
    Public Attributes:
    
    - *selector* -- the selection operator
    - *variator* -- the (possibly list of) variation operator(s)
    - *replacer* -- the replacement operator
    - *migrator* -- the migration operator
    - *archiver* -- the archival operator
    - *observer* -- the (possibly list of) observer(s)
    - *terminator* -- the (possibly list of) terminator(s)
    
    The following public attributes do not have legitimate values
    until after the ``evolve`` method executes:
    
    - *termination_cause* -- the name of the function causing 
      ``evolve`` to terminate
    - *generator* -- the generator function passed to ``evolve``
    - *evaluator* -- the evaluator function passed to ``evolve``
    - *bounder* -- the bounding function passed to ``evolve``
    - *maximize* -- Boolean stating use of maximization passed to ``evolve``
    - *archive* -- the archive of individuals
    - *population* -- the population of individuals
    - *num_evaluations* -- the number of fitness evaluations used
    - *num_generations* -- the number of generations processed
    - *logger* -- the logger to use (defaults to the logger 'ecspy.ec')
    
    Note that the attributes above are, in general, not intended to 
    be modified by the user. (They are intended for the user to query
    during or after the ``evolve`` method's execution.) However, 
    there may be instances where it is necessary to modify them 
    within other functions. This is possible but should be the 
    exception, rather than the rule.
    
    If logging is desired, the following basic code segment can be 
    used in the ``main`` or calling scope to accomplish that::
    
        logger = logging.getLogger('ecspy.ec')
        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler('ec.log', mode='w')
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    Protected Attributes:
    
    - *_random* -- the random number generator object
    - *_kwargs* -- the dictionary of keyword arguments initialized
      from the *args* parameter in the *evolve* method
    
    Public Methods:
    
    - ``evolve`` -- performs the evolution and returns the final
      archive of individuals
    
    """
    def __init__(self, random):
        self.selector = selectors.default_selection
        self.variator = variators.default_variation
        self.replacer = replacers.default_replacement
        self.migrator = migrators.default_migration
        self.observer = observers.default_observer
        self.archiver = archivers.default_archiver
        self.terminator = terminators.default_termination
        self.termination_cause = None
        self.generator = None
        self.evaluator = None
        self.bounder = None
        self.maximize = True
        self.archive = None
        self.population = None
        self.num_evaluations = 0
        self.num_generations = 0
        self.logger = logging.getLogger('ecspy.ec')
        self._random = random
        self._kwargs = dict()
        
    def _should_terminate(self, pop, ng, ne):
        terminate = False
        fname = ''
        try:
            for clause in self.terminator:
                self.logger.debug('termination test using %s at generation %d and evaluation %d' % (clause.__name__, ng, ne))
                terminate = terminate or clause(population=pop, num_generations=ng, num_evaluations=ne, args=self._kwargs)
                if terminate:
                    fname = clause.__name__
                    break
        except TypeError:
            self.logger.debug('termination test using %s at generation %d and evaluation %d' % (self.terminator.__name__, ng, ne))
            terminate = self.terminator(population=pop, num_generations=ng, num_evaluations=ne, args=self._kwargs)
            fname = self.terminator.__name__
        if terminate:
            self.termination_cause = fname
            self.logger.debug('termination from %s at generation %d and evaluation %d' % (self.termination_cause, ng, ne))
        return terminate
        
    
    def evolve(self, generator, evaluator, pop_size=100, seeds=[], maximize=True, bounder=Bounder(), **args):
        """Perform the evolution.
        
        This function creates a population and then runs it through a series
        of evolutionary epochs until the terminator is satisfied. The general
        outline of an epoch is selection, variation, evaluation, replacement,
        migration, archival, and observation. The function returns a list of
        elements of type ``Individual`` representing the individuals contained
        in the final population.
        
        Arguments:
        
        - *generator* -- the function to be used to generate candidate solutions 
        - *evaluator* -- the function to be used to evaluate candidate solutions
        - *pop_size* -- the number of Individuals in the population (default 100)
        - *seeds* -- an iterable collection of candidate solutions to include
          in the initial population (default [])
        - *maximize* -- Boolean value stating use of maximization (default True)
        - *bounder* -- a function used to bound candidate solutions (default Bounder())
        - *args* -- a dictionary of keyword arguments

        Note that the *_kwargs* class variable will be initialized to the args 
        parameter here. It will also be modified to include the following 'built-in' 
        keyword arguments:
        
        - *_ec* -- the evolutionary computation (this object)
        
        """
        self._kwargs = args
        self._kwargs['_ec'] = self
        
        self.termination_cause = None
        self.generator = generator
        self.evaluator = evaluator
        self.bounder = bounder
        self.maximize = maximize
        self.population = []
        self.archive = []
        
        # Create the initial population.
        try:
            iter(seeds)
        except TypeError:
            seeds = [seeds]
        initial_cs = list(seeds)
        num_generated = max(pop_size - len(seeds), 0)
        i = 0
        self.logger.debug('generating initial population')
        while i < num_generated:
            cs = generator(random=self._random, args=self._kwargs)
            if cs not in initial_cs:
                initial_cs.append(cs)
                i += 1
        self.logger.debug('evaluating initial population')
        initial_fit = evaluator(candidates=initial_cs, args=self._kwargs)
        
        for cs, fit in zip(initial_cs, initial_fit):
            ind = Individual(cs, maximize=maximize)
            ind.fitness = fit
            self.population.append(ind)
        self.logger.debug('population size is now %d' % len(self.population))
        
        self.num_evaluations = len(initial_fit)
        self.num_generations = 0
        
        self.logger.debug('archiving initial population')
        self.archive = self.archiver(random=self._random, population=list(self.population), archive=list(self.archive), args=self._kwargs)
        self.logger.debug('archive size is now %d' % len(self.archive))
        self.logger.debug('population size is now %d' % len(self.population))
                
        if isinstance(self.observer, (list, tuple)):
            for obs in self.observer:
                self.logger.debug('observation using %s at generation %d and evaluation %d' % (obs.__name__, self.num_generations, self.num_evaluations))
                obs(population=list(self.population), num_generations=self.num_generations, num_evaluations=self.num_evaluations, args=self._kwargs)
        else:
            self.logger.debug('observation using %s at generation %d and evaluation %d' % (self.observer.__name__, self.num_generations, self.num_evaluations))
            self.observer(population=list(self.population), num_generations=self.num_generations, num_evaluations=self.num_evaluations, args=self._kwargs)
        
        while not self._should_terminate(list(self.population), self.num_generations, self.num_evaluations):
            # Select individuals.
            self.logger.debug('selection using %s at generation %d and evaluation %d' % (self.selector.__name__, self.num_generations, self.num_evaluations))
            parents = self.selector(random=self._random, population=list(self.population), args=self._kwargs)
            self.logger.debug('selected %d candidates' % len(parents))
            parent_cs = [copy.deepcopy(i.candidate) for i in parents]
            offspring_cs = parent_cs
            
            if isinstance(self.variator, (list, tuple)):
                for op in self.variator:
                    self.logger.debug('variation using %s at generation %d and evaluation %d' % (op.__name__, self.num_generations, self.num_evaluations))
                    offspring_cs = op(random=self._random, candidates=offspring_cs, args=self._kwargs)
            else:
                self.logger.debug('variation using %s at generation %d and evaluation %d' % (self.variator.__name__, self.num_generations, self.num_evaluations))
                offspring_cs = self.variator(random=self._random, candidates=offspring_cs, args=self._kwargs)
            self.logger.debug('created %d offspring' % len(offspring_cs))
            
            # Evaluate offspring.
            self.logger.debug('evaluation using %s at generation %d and evaluation %d' % (evaluator.__name__, self.num_generations, self.num_evaluations))
            offspring_fit = evaluator(candidates=offspring_cs, args=self._kwargs)
            offspring = []
            for cs, fit in zip(offspring_cs, offspring_fit):
                off = Individual(cs, maximize=maximize)
                off.fitness = fit
                offspring.append(off)
            self.num_evaluations += len(offspring_fit)        

            # Replace individuals.
            self.logger.debug('replacement using %s at generation %d and evaluation %d' % (self.replacer.__name__, self.num_generations, self.num_evaluations))
            self.population = self.replacer(random=self._random, population=list(self.population), parents=parents, offspring=offspring, args=self._kwargs)
            self.logger.debug('population size is now %d' % len(self.population))
            
            # Migrate individuals.
            self.logger.debug('migration using %s at generation %d and evaluation %d' % (self.migrator.__name__, self.num_generations, self.num_evaluations))
            self.population = self.migrator(random=self._random, population=list(self.population), args=self._kwargs)
            self.logger.debug('population size is now %d' % len(self.population))
            
            # Archive individuals.
            self.logger.debug('archival using %s at generation %d and evaluation %d' % (self.archiver.__name__, self.num_generations, self.num_evaluations))
            self.archive = self.archiver(random=self._random, archive=list(self.archive), population=list(self.population), args=self._kwargs)
            self.logger.debug('archive size is now %d' % len(self.archive))
            self.logger.debug('population size is now %d' % len(self.population))
            
            self.num_generations += 1
            if isinstance(self.observer, (list, tuple)):
                for obs in self.observer:
                    self.logger.debug('observation using %s at generation %d and evaluation %d' % (obs.__name__, self.num_generations, self.num_evaluations))
                    obs(population=list(self.population), num_generations=self.num_generations, num_evaluations=self.num_evaluations, args=self._kwargs)
            else:
                self.logger.debug('observation using %s at generation %d and evaluation %d' % (self.observer.__name__, self.num_generations, self.num_evaluations))
                self.observer(population=list(self.population), num_generations=self.num_generations, num_evaluations=self.num_evaluations, args=self._kwargs)
        return self.population
        

class GA(EvolutionaryComputation):
    """Evolutionary computation representing a canonical genetic algorithm.
    
    This class represents a genetic algorithm which uses, by 
    default, rank selection, n-point crossover, bit-flip mutation, 
    and generational replacement. In the case of bit-flip mutation, 
    it is expected that the candidate solution is an iterable object 
    of binary values. 
    
    Optional keyword arguments in ``evolve`` args parameter:
    
    - *num_selected* -- the number of individuals to be selected (default 1)
    - *crossover_rate* -- the rate at which crossover is performed 
      (default 1.0)
    - *num_crossover_points* -- the n crossover points used (default 1)
    - *mutation_rate* -- the rate at which mutation is performed (default 0.1)
    - *num_elites* -- number of elites to consider (default 0)
    
    """
    def __init__(self, random):
        EvolutionaryComputation.__init__(self, random)
        self.selector = selectors.rank_selection 
        self.variator = [variators.n_point_crossover, variators.bit_flip_mutation]
        self.replacer = replacers.generational_replacement
        
    def evolve(self, generator, evaluator, pop_size=100, seeds=[], maximize=True, bounder=Bounder(), **args):
        args.setdefault('num_selected', pop_size)
        return EvolutionaryComputation.evolve(self, generator, evaluator, pop_size, seeds, maximize, bounder, **args)


class ES(EvolutionaryComputation):
    """Evolutionary computation representing a canonical evolution strategy.
    
    This class represents an evolution strategy which uses, by 
    default, the default selection (i.e., all individuals are selected), 
    Gaussian mutation, and 'plus' replacement. It is assumed that the
    candidate solution is an iterable object of real values. 

    Optional keyword arguments in ``evolve`` args parameter:
    
    - *mutation_rate* -- the rate at which mutation is performed (default 0.1)
    - *mean* -- the mean used in the Gaussian function (default 0)
    - *stdev* -- the standard deviation used in the Gaussian function
      (default 1.0)
    - *use_one_fifth_rule* -- whether the 1/5 rule should be used (default False)
    
    """
    def __init__(self, random):
        EvolutionaryComputation.__init__(self, random)
        self.selector = selectors.default_selection
        self.variator = variators.gaussian_mutation
        self.replacer = replacers.plus_replacement
        

class EDA(EvolutionaryComputation):
    """Evolutionary computation representing a canonical estimation of distribution algorithm.
    
    This class represents an estimation of distribution algorithm which
    uses, by default, truncation selection, estimation of distribution 
    variation, and generational replacement. It is assumed that the
    candidate solution is an iterable object of real values. 

    Optional keyword arguments in ``evolve`` args parameter:
    
    - *num_selected* -- the number of individuals to be selected 
      (default len(population))
    - *num_offspring* -- the number of offspring to create (default 1)
    - *num_elites* -- number of elites to consider (default 0)
    
    """
    def __init__(self, random):
        EvolutionaryComputation.__init__(self, random)
        self.selector = selectors.truncation_selection
        self.variator = variators.estimation_of_distribution_variation
        self.replacer = replacers.generational_replacement
        
    def evolve(self, generator, evaluator, pop_size=100, seeds=[], maximize=True, bounder=Bounder(), **args):
        args.setdefault('num_selected', pop_size // 2)
        args.setdefault('num_offspring', pop_size)
        return EvolutionaryComputation.evolve(self, generator, evaluator, pop_size, seeds, maximize, bounder, **args)


class DEA(EvolutionaryComputation):
    """Evolutionary computation representing a differential evolutionary algorithm.
    
    This class represents a differential evolutionary algorithm which uses, by 
    default, tournament selection, differential crossover, Gaussian mutation,
    and steady-state replacement. It is expected that the candidate solution 
    is an iterable object of real values. 
    
    Optional keyword arguments in ``evolve`` args parameter:
    
    - *num_selected* -- the number of individuals to be selected (default 1)
    - *tourn_size* -- the tournament size (default 2)
    - *crossover_rate* -- the rate at which crossover is performed 
      (default 1.0)
    - *differential_phi* -- the amount of random change in the crossover 
      (default 0.1)
    - *mutation_rate* -- the rate at which mutation is performed (default 0.1)
    - *mean* -- the mean used in the Gaussian function (default 0)
    - *stdev* -- the standard deviation used in the Gaussian function
      (default 1.0)

    """
    def __init__(self, random):
        EvolutionaryComputation.__init__(self, random)
        self.selector = selectors.tournament_selection
        self.variator = [variators.differential_crossover, variators.gaussian_mutation]
        self.replacer = replacers.steady_state_replacement
        
    def evolve(self, generator, evaluator, pop_size=100, seeds=[], maximize=True, bounder=Bounder(), **args):
        args.setdefault('num_selected', 2)
        return EvolutionaryComputation.evolve(self, generator, evaluator, pop_size, seeds, maximize, bounder, **args)


class SA(EvolutionaryComputation):
    """Evolutionary computation representing simulated annealing."""
    def __init__(self, random):
        EvolutionaryComputation.__init__(self, random)
        self.selector = selectors.default_selection
        self.variator = variators.gaussian_mutation
        self.replacer = replacers.simulated_annealing_replacement
    
    def evolve(self, generator, evaluator, pop_size=1, seeds=[], maximize=True, bounder=Bounder(), **args):
        pop_size=1
        return EvolutionaryComputation.evolve(self, generator, evaluator, pop_size, seeds, maximize, bounder, **args)
