********
Examples
********

We always find it easiest to learn a new library by adapting existing examples to our
purposes. For that reason, we provide many examples in this section in the hope that
they will prove useful to others using ECsPy.


=======================================
Off-the-shelf Evolutionary Computations
=======================================

The following examples illustrate how to use the different, built-in, evolutionary computations.
They are simple enough to be self-explanatory and are provided without additional documentation.


"""""""""""""""""
Genetic Algorithm
"""""""""""""""""

.. literalinclude:: ../examples/ga_example.py


""""""""""""""""""
Evolution Strategy
""""""""""""""""""

.. literalinclude:: ../examples/es_example.py


"""""""""""""""""""
Simulated Annealing
"""""""""""""""""""

.. literalinclude:: ../examples/sa_example.py


""""""""""""""""""""""""""""""""
Differential Evolution Algorithm
""""""""""""""""""""""""""""""""

.. literalinclude:: ../examples/dea_example.py


""""""""""""""""""""""""""""""""""""
Estimation of Distribution Algorithm
""""""""""""""""""""""""""""""""""""

.. literalinclude:: ../examples/eda_example.py


"""""""""""""""""""""""""""""""
Custom Evolutionary Computation
"""""""""""""""""""""""""""""""

.. literalinclude:: ../examples/custom_ec_example.py


"""""""""""""""""""""""""""
Particle Swarm Optimization
"""""""""""""""""""""""""""

.. literalinclude:: ../examples/pso_example.py


""""""""""""""""""""""""""""""""""""""""""""""""
Nondominated Sorting Genetic Algorithm (NSGA-II)
""""""""""""""""""""""""""""""""""""""""""""""""

.. literalinclude:: ../examples/nsga_example.py


"""""""""""""""""""""""""""""""""""""""""
Pareto Archived Evolution Strategy (PAES)
"""""""""""""""""""""""""""""""""""""""""

.. literalinclude:: ../examples/paes_example.py


===================
ECsPy Customization
===================

The true benefit of the ECsPy library is that it allows the programmer to customize
almost every aspect of the evolutionary computation. This is accomplished primarily
through the use of function (or function-like) callbacks that can be specified by
the programmer. 

The observer, terminator, and variator callbacks may be lists or tuples of functions, rather
than just a single function. In each case, the functions are called sequentially in the order
listed. For the variator, the output from one call is used as the input for the subsequent call.

The following examples provide some ideas for customization that we have found useful in practice.

"""""""""""""""
Custom Archiver
"""""""""""""""

The purpose of the archiver is to provide a mechanism for candidate solutions to be 
maintained without necessarily remaining in the population. This is important for 
most multiobjective evolutionary approaches, but it can also be useful for single-objective
problems, as well. In this example, we create an archiver that maintains the *worst*
individual found. (There is no reason we can imagine to actually do this. It is just 
for illustration purposes.)

.. literalinclude:: ../examples/custom_archiver_example.py


"""""""""""""""
Custom Migrator
"""""""""""""""

The purpose of the migrator is to provide a mechanism for candidate solutions to be 
shared across populations (e.g., in an island-model evolutionary computation). The following
custom migrator is a callable class (because the migrator must behave like a callback function)
that allows solutions to migrate from one network machine to another. It is assumed that
the EC islands are running on the given IP:port combinations.

.. literalinclude:: ../examples/custom_migrator_example.py


"""""""""""""""
Custom Observer
"""""""""""""""

Sometimes it is helpful to see certain aspects of the current population as it evolves.
The purpose of the "observer" functions is to provide a callback that executes at the
end of each generation so that the process can be monitored accordingly. In this example,
the only information desired at each generation is the current best individual.

.. literalinclude:: ../examples/custom_observer_example.py


"""""""""""""""
Custom Replacer
"""""""""""""""

The replacer callbacks are used to determine which of the parents, offspring, and current population
should survive into the next generation. And example of a not-quite-standard replacer might be
the ``crowding_replacement`` which provides a niching capability. An example using this replacer is
given below.

.. literalinclude:: ../examples/niche_example.py


"""""""""""""""
Custom Selector
"""""""""""""""



"""""""""""""""""
Custom Terminator
"""""""""""""""""



"""""""""""""""
Custom Variator
"""""""""""""""




==============
Advanced ECsPy
==============

The examples in this section deal with much less commonly used aspects of
the library. Beware that these parts may not have received as much testing
as the more core components exemplified above.

"""""""""""""""""""""""""""""""""""
Evaluating Individuals Concurrently
"""""""""""""""""""""""""""""""""""




















