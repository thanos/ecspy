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

def parallel_evaluation_pp(candidates, args):
    """Evaluate the candidates in parallel.

    This function allows parallel evaluation of candidate solutions.
    It uses the Parallel Python (pp) library to accomplish the 
    parallelization. This library must already be installed in order
    to use this function. The function assigns the evaluation of each
    candidate to its own job, all of which are then distributed to the
    available processing units.
    
    parallel_evaluation_mp is the slightly better choice for SMP / multicore parallelism
    since it does not require you to specify arguments and modules required for evaluation
    in a non-standard manner, therefore is trivial to set up.
    
    parallel_evaluation_pp supports both SMP / multicore parallelism
    as well  as distributed computing, which does require you to set setting up a network
    of clients. 
    
    .. Arguments:
       candidates -- the candidate solutions
       args -- a dictionary of keyword arguments

    Required keyword arguments in args:
    
    *serial_evaluator* -- the actual evaluation function, which should take a 
    single argument representing a candidate solution (required)
    
    Optional keyword arguments in args:
    
    - *serial_dependencies* -- tuple of functional dependencies of the serial 
      evaluator (default ())
    - *serial_modules* -- tuple of modules that must be imported for the 
      functional dependencies (default ())
    - *parallel_servers* -- tuple of servers (on a cluster) that will be used 
      for parallel processing (default ("*",))
    
    """
    # Import the necessary library here. Otherwise, it would have to be
    # installed even if this function is not called.
    import pp
    
    try:
        serial_eval = args['serial_evaluator']
    except KeyError:
        return [-float('inf') for c in candidates]
    try:
        job_server = args['_job_server']
    except KeyError:
        parallel_servers = args.get('parallel_servers', ("*",))
        job_server = pp.Server(ppservers=parallel_servers)
        args['_job_server'] = job_server
    serial_depend = args.setdefault('serial_dependencies', ())
    serial_mod = args.setdefault('serial_modules', ())
        
    func_template = pp.Template(job_server, serial_eval, serial_depend, serial_mod)
    jobs = [func_template.submit(cand) for cand in candidates]
    
    results = []
    for job in jobs:
        results.append(job())
    
    fitness = []
    for result in results:
        fitness.append(result)
    return fitness

def parallel_evaluation_mp(candidates, args):
    """Evaluate the candidates in parallel.

    This function allows parallel evaluation of candidate solutions.
    It uses the standard multiprocessing library to accomplish the 
    parallelization. The function assigns the evaluation of each
    candidate to its own job, all of which are then distributed to the
    available processing units.
    
    parallel_evaluation_mp is the slightly better choice for SMP / multicore parallelism
    since it does not require you to specify arguments and modules required for evaluation
    in a non-standard manner, therefore is trivial to set up.
    
    parallel_evaluation_pp supports both SMP / multicore parallelism
    as well  as distributed computing, which does require you to set setting up a network
    of clients.   
    
    Note: arguments for the evaluation function should be able to serialize
    
    .. Arguments:
       candidates -- the candidate solutions
       args -- a dictionary of keyword arguments

    Required keyword arguments in args:
    
    *serial_evaluator* -- the actual evaluation function, which should take a 
    single argument representing a candidate solution (required)
    
    Optional keyword arguments in args:
    
    - *nprocs* -- number of processors that will be used
    - *timeout* -- when more time than *timeout* seconds have passed, stop 
      evaluation of the population. Note that this is the time for the complete population
      not just a single individual  
    
    """
    try:
        import multiprocessing, time
    except ImportError:
        print '''multiprocessing is not installed...\n
        necspy has been designed to work with python 2.6 which has multiprocessing in the stdlib\n'''
        raise
    
    nprocs = args.setdefault('nprocs', multiprocessing.cpu_count())
    evaluator = args['evaluator']
    
    start = time.time()
    try:
        pool = multiprocessing.Pool(processes=nprocs)
        # its async, but does return values in order...
        pool_map = pool.map_async(evaluator, candidates)
        pool_outputs = pool_map.get(timeout=1000)
        return [i for i in pool_outputs]
    
    except (OSError, RuntimeError) as e:
        # do logging...
        print 'failed parallel fitness evaluation using multiprocessing'
        # re-raising the original exception
        raise
    
    else:
        end = time.time()
        # do logging...
        # logging....('completed parallel evaluation of generation %s in %s seconds
        