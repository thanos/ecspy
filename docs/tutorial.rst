********
Tutorial
********

This chapter presents several optimization examples to which ECsPy can be applied. Each example presents a particular problem for which the chosen evolutionary computation is well-suited.

======================
The Rastrigin Function
======================

The Rastrigin function is a well-known benchmark in the optimization literature. It is defined as follows:

Minimize

.. math::

    10n + \sum_{i=1}^n\left((x_i - 1)^2 - 10\cos(2\pi(x_i - 1))\right)

for :math:`x_i \in [-5.12, 5.12]`.

Since this problem is defined on a set of continuous-valued variables, using an evolution strategy as our optimizer seems appropriate. However, as always, we'll need to first create the *generator* and the *evaluator* for the candidate solutions. First, the generator...

"""""""""""""
The Generator
"""""""""""""

.. literalinclude:: rastrigin.py
    :start-after: #start_imports
    :end-before: #end_imports
    
.. literalinclude:: rastrigin.py
    :pyobject: generate_rastrigin

First, we import all the necessary libraries. ``random`` and ``time`` are needed for the random number generation; ``math`` is needed for the evaluation function; and ``ecspy`` is, of course, needed for the evolutionary computation.    

This function must take the random number generator object along with the keyword arguments. Notice that we can use the ``args`` variable to pass anything we like to our functions. There is nothing special about the ``num_inputs`` key. But, as we'll see, we can pass in that value as a keyword argument to the ``evolve`` method of our evolution strategy. In contrast, there is something a bit special about the ``lower_bound`` and ``upper_bound`` keys. Those keys are used by some of the evolutionary operators (e.g., Gaussian mutation) that are distributed with ECsPy. 

This code is pretty straightforward. We're simply generating a list of ``num_inputs`` uniform random values between ``lower_bound`` and ``upper_bound``. If ``num_inputs`` has not been specified, then we will default to generating 10 values. Likewise the bounds would default to 0 and 1, respectively. 

And now we can tackle the evaluator...

"""""""""""""
The Evaluator
"""""""""""""

.. literalinclude:: rastrigin.py
    :pyobject: evaluate_rastrigin
    :end-before: #start_main

This function takes an iterable object containing the candidates along with the keyword arguments. The function should perform the evaluation of each of the candidates and return an iterable object containing each fitness value in the same order as the candidates [#]_. The Rastrigin problem is one of minimization, so we'll need to tell the evolution strategy that we are minimizing (by using ``maximize=True`` in the call to ``evolve``).

""""""""""""""""""""""""""""
The Evolutionary Computation
""""""""""""""""""""""""""""

Now that we have decided upon our generator and evaluator, we can create the EC. In this case since our problem is real-coded, we'll choose a evolution strategy (ES) [#]_. The default for an ES is to select the entire population, use each to produce a child via Gaussian mutation, and then use "plus" replacement. 

.. literalinclude:: rastrigin.py
    :start-after: #start_main
    :end-before: #end_main

.. {{{cog
.. cog.out(run_script(cog.inFile, 'rastrigin.py'))
.. }}}

::

	$ python rastrigin.py
	TERMINATED DUE TO evaluation_termination
	[0.99067964706794498, 0.99932552559142507, 1.0006467772340022] : 0.0174024611432

.. {{{end}}}

As can be seen, we first create our random number generator object, seeding it with the current system time. Then we construct our ES, specifying a terminator (that stops after a given number of function evaluations). Finally, we call the ``evolve`` method of the ES. To this method, we pass the generator, evaluator, a flag to denote that we're minimizing in this problem (which defaults to ``maximize=True`` if unspecified), and a set of keyword arguments that will be needed by one or more of the functions involved. For instance, we pass ``num_inputs`` to be used by our generator. Likewise, ``max_evaluations`` will be used by our terminator.

The script outputs the best individual in the final generation, which will always be located at index 0 because the population is sorted by fitness before it is returned. Since the random number generator was seeded with the current time, your particular output will be different when running this script from that presented here. 

.. rubric:: Footnotes

.. [#] The evaluator was designed to evaluate all candidates, rather than a single candidate (with iteration happening inside the evolution engine), because this allows more complex evaluation functions that make use of the current set of individuals. Of course, such a function would also rely heavily on the choice of selector, as well.

.. [#] We can also certainly create real-coded genetic algorithms, among many other choices for our EC. However, for this discussion we are attempting to use the canonical versions to which most people would be accustomed.


=================
Evolving Polygons
=================

In this example, we will attempt to create a polygon of *n* vertices that has maximal area. We'll also create a custom observer that allows us to display the polygon as it evolves.

"""""""""""""
The Generator
"""""""""""""

.. literalinclude:: polyarea.py
    :start-after: #start_imports
    :end-before: #end_imports
    
.. literalinclude:: polyarea.py
    :pyobject: generate_polygon

Once again, we import the necessary libraries. In this case, we'll also need to tailor elements of the EC, as well as provide graphical output.

After the libraries have been imported, we define our generator function. It looks for keyword arguments ``num_vertices``, ``lower_bound``, and ``upper_bound``, and it creates a list of ``num_vertices`` ordered pairs (tuples) where each coordinate is in the range ``[lower_bound, upper_bound]``.

"""""""""""""
The Evaluator
"""""""""""""

.. literalinclude:: polyarea.py
    :pyobject: segments

.. literalinclude:: polyarea.py
    :pyobject: area

.. literalinclude:: polyarea.py
    :pyobject: evaluate_polygon

In order to evaluate the polygon, we need to calculate its area. The ``segments`` and ``area`` functions do this for us. Therefore, the ``evaluate_polygon`` function simply needs to assign the fitness to be the value returned as the area.

""""""""""""
The Observer
""""""""""""

.. literalinclude:: polyarea.py
    :pyobject: polygon_observer
    :end-before: #start_main

Since we are evolving a two-dimensional shape, it makes sense to use a graphical approach to observing the current best polygon during each iteration. The ``polygon_observer`` accomplishes this by drawing the best polygon in the population to a Tk canvas. Notice that the canvas is passed in via the keyword arguments parameter ``args``.

""""""""""""""""""""""""""""
The Evolutionary Computation
""""""""""""""""""""""""""""

For this task, we'll create a custom evolutionary computation by selecting the operators to be used. First, we will need to create a custom mutation operator since none of the pre-defined operators deal particularly well with a list of tuples.

.. literalinclude:: polyarea.py
    :pyobject: mutate_polygon

Notice that this is essentially a Gaussian mutation on each coordinate of each tuple. Now we can create our custom EC.
    
.. literalinclude:: polyarea.py
    :start-after: #start_main
    :end-before: #end_main

This EC uses tournament selection, uniform crossover, our custom mutation operator, and steady-state replacement. We also set up the custom observer and create the canvas, which is passed into the ``evolve`` method as a keyword argument.






