"""
    Evaluator functions are problem-specific. This module provides pre-defined 
    evaluators for evolutionary computations.

    All evaluator functions have the following arguments:
    
    - *candidates* -- the candidate solutions
    - *args* -- a dictionary of keyword arguments

    
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

import pickle

def evaluator(evaluate):
    """Return an ecspy evaluator function based on the given function.
    
    This function generator takes a function that evaluates only one
    candidate. The generator handles the iteration over each candidate 
    to be evaluated.

    The given function ``evaluate`` must have the following signature::
    
        fitness = evaluate(candidate, args)
        
    This function is most commonly used as a function decorator with
    the following usage::
    
        @evaluator
        def evaluate(candidate, args):
            # Implementation of evaluation
            
    The generated function also contains an attribute named
    ``single_evaluation`` which holds the original evaluation function.
    In this way, the original single-candidate function can be
    retrieved if necessary.
    
    """
    def ecspy_evaluator(candidates, args):
        fitness = []
        for candidate in candidates:
            fitness.append(evaluate(candidate, args))
        return fitness
    ecspy_evaluator.__dict__ = evaluate.__dict__
    ecspy_evaluator.single_evaluation = evaluate
    ecspy_evaluator.__name__ = evaluate.__name__
    ecspy_evaluator.__doc__ = evaluate.__doc__
    return ecspy_evaluator
    

def parallel_evaluation_pp(candidates, args):
    """Evaluate the candidates in parallel using Parallel Python.

    This function allows parallel evaluation of candidate solutions.
    It uses the Parallel Python (pp) library to accomplish the 
    parallelization. This library must already be installed in order
    to use this function. The function assigns the evaluation of each
    candidate to its own job, all of which are then distributed to the
    available processing units.
    
    parallel_evaluation_mp is the slightly better choice for SMP/multicore 
    parallelism since it does not require you to specify arguments and 
    modules required for evaluation in a non-standard manner. It is, 
    therefore, trivial to set up.
    
    parallel_evaluation_pp supports both SMP / multicore parallelism,
    as well as distributed computing, which does require you to set up 
    a network of clients. 
    
    .. Arguments:
       candidates -- the candidate solutions
       args -- a dictionary of keyword arguments

    Required keyword arguments in args:
    
    *pp_evaluator* -- actual evaluation function to be used (This function
    should have the same signature as any other ecspy evaluation function.)

    Optional keyword arguments in args:
    
    - *pp_dependencies* -- tuple of functional dependencies of the serial 
      evaluator (default ())
    - *pp_modules* -- tuple of modules that must be imported for the 
      functional dependencies (default ())
    - *pp_servers* -- tuple of servers (on a cluster) that will be used 
      for parallel processing (default ("*",))
      
    For more information about these arguments, please consult the
    documentation for Parallel Python.
    
    """
    try:
        import pp
    except ImportError:
        print '''Parallel Python is not installed...\n
        The parallel_evaluation_pp function requires Parallel Python.\n'''
        raise
    logger = args['_ec'].logger
    
    try:
        evaluator = args['pp_evaluator']
    except KeyError:
        logger.error('\'mp_evaluator\' is not in the keyword arguments list')
        raise 
    try:
        job_server = args['_pp_job_server']
    except KeyError:
        pp_servers = args.get('pp_servers', ("*",))
        job_server = pp.Server(ppservers=pp_servers, secret="ecspy")
        args['_pp_job_server'] = job_server
    pp_depends = args.setdefault('pp_dependencies', ())
    pp_modules = args.setdefault('pp_modules', ())
        
    func_template = pp.Template(job_server, evaluator, pp_depends, pp_modules)
    jobs = [func_template.submit([c], {}) for c in candidates]
    
    results = []
    for job in jobs:
        r = job()
        results.append(r[0])
    
    fitness = []
    for result in results:
        fitness.append(result)
    return fitness

def parallel_evaluation_mp(candidates, args):
    """Evaluate the candidates in parallel using ``multiprocessing``.

    This function allows parallel evaluation of candidate solutions.
    It uses the standard multiprocessing library to accomplish the 
    parallelization. The function assigns the evaluation of each
    candidate to its own job, all of which are then distributed to the
    available processing units.
    
    parallel_evaluation_mp is the slightly better choice for SMP/multicore 
    parallelism since it does not require you to specify arguments and 
    modules required for evaluation in a non-standard manner. It is, 
    therefore, trivial to set up.
    
    parallel_evaluation_pp supports both SMP / multicore parallelism,
    as well as distributed computing, which does require you to set up 
    a network of clients. 
    
    Note: arguments for the evaluation function should be able to serialize
    
    .. Arguments:
       candidates -- the candidate solutions
       args -- a dictionary of keyword arguments

    Required keyword arguments in args:
    
    *mp_evaluator* -- actual evaluation function to be used (This function
    should have the same signature as any other ecspy evaluation function.)

    Optional keyword arguments in args:
    
    - *mp_num_cpus* -- number of processors that will be used (default is machine cpu count)
    
    """
    import time
    try:
        import multiprocessing
    except ImportError:
        print '''multiprocessing is not installed...\n
        ecspy has been designed to work with Python 2.6, which has multiprocessing as a standard library\n'''
        raise
    logger = args['_ec'].logger
    
    try:
        evaluator = args['mp_evaluator']
    except KeyError:
        logger.error('\'mp_evaluator\' is not in the keyword arguments list')
        raise 
    try:
        nprocs = args['mp_num_cpus']
    except KeyError:
        nprocs = multiprocessing.cpu_count()
    mp_args = {}
    for key in args:
        try:
            pickle.dumps(args[key])
            mp_args[key] = args[key]
        except (TypeError, pickle.PickleError, pickle.PicklingError):
            logger.debug('in mp_evaluator: unable to pickle args parameter %s' % key)
            pass
            
    start = time.time()
    try:
        pool = multiprocessing.Pool(processes=nprocs)
        results = [pool.apply_async(evaluator, ([c], mp_args)) for c in candidates]
        pool.close()
        return [r.get()[0] for r in results]
    except (OSError, RuntimeError) as e:
        logger.error('failed parallel fitness evaluation using multiprocessing')
        raise
    else:
        end = time.time()
        logger.debug('completed parallel evaluation in %f seconds' % (end - start))
        
