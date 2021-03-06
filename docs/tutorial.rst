********
Tutorial
********

This chapter presents an overview of ECsPy along with three optimization examples to which ECsPy can be applied. Each example presents a particular problem for which the chosen evolutionary computation is well-suited.

==============
ECsPy Overview
==============

The ECsPy library grew out of insights from Ken de Jong's book "Evolutionary Computation: A Unified Approach". The goal of the library is to separate problem-specific computation from algorithm-specific computation. Any evolutionary computation has at least two aspects that are entirely problem-specific: what solutions to the problem look like and how such solutions are evaluated. These components will certainly change from problem to problem. For instance, a problem dealing with optimizing the volume of a box might represent solutions as a three-element list of real values for the length, width, and height, respectively. In contrast, a problem dealing with genetic programming might represent solutions as a tree structure. Similarly, the way such candidate solutions are evaluated is entirely problem dependent.

On the other hand, there are algorithm-specific components that may make no (or only modest) assumptions about the type of solutions upon which they operate. These components include the mechanism by which parents are selected, the way offspring are generated, and the way individuals are replaced in succeeding generations. For example, the ever-popular tournament selection scheme makes no assumptions whatsoever about the type of solutions it is selecting. The n-point crossover operator, on the other hand, does make an assumption that the solutions will be linear lists that can be "sliced up," but it makes no assumptions about the contents of such lists. They could be lists of numbers, strings, other lists, or something even more exotic.

With that background, we can now explain that ECsPy treats every evolutionary computation as being composed of the following parts:

* Problem-specific components

  * A generator that defines how solutions are created
  * An evaluator that defines how fitness values are calculated for solutions

* Algorithm-specific evolutionary operators

  * An observer that defines how the user can monitor the state of the evolution
  * A terminator that determines whether the evolution should end
  * A selector that determines which individuals should become parents
  * A variator that determines how offspring are created from existing individuals
  * A replacer that determines which individuals should survive into the next generation
  * A migrator that defines how solutions are transferred among differnt populations
  * An archiver that defines how existing solutions are stored outside of the current population

Each of these components is specified by a function (or function-like) callback that the user can supply. The general flow of the ``evolve`` method in ECsPy is as follows, where user-supplied callback functions are in ALLCAPS:

::

    Create the initial population using the specified candidate seeds and the GENERATOR
    Evaluate the initial population using the EVALUATOR
    Set the number of evaluations to the size of the initial population
    Set the number of generations to 0
    Call the OBSERVER on the initial population
    While the TERMINATOR is not true Loop
        Choose parents via the SELECTOR
        Initialize offspring to the parents
        For each VARIATOR Loop
            Set offspring to the output of the VARIATOR on the offspring
        Evaluate offspring using the EVALUATOR
        Update the number of evaluations
        Replace individuals in the current population using the REPLACER
        Migrate individuals in the current population using the MIGRATOR
        Archive individuals in the current population using the ARCHIVER
        Increment the number of generations
        Call the OBSERVER on the current population

The observer, terminator, and variator callbacks may be lists or tuples of functions, rather
than just a single function. In each case, the functions are called sequentially in the order
listed. Unlike the other two, however, the variator behaves like a pipeline, where the output 
from one call is used as the input for the subsequent call.


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

This function must take the random number generator object along with the keyword arguments. Notice that we can use the ``args`` variable to pass anything we like to our functions. There is nothing special about the ``num_inputs`` key. But, as we'll see, we can pass in that value as a keyword argument to the ``evolve`` method of our evolution strategy. 

This code is pretty straightforward. We're simply generating a list of ``num_inputs`` uniform random values between -5.12 and 5.12. If ``num_inputs`` has not been specified, then we will default to generating 10 values. 

And now we can tackle the evaluator...

"""""""""""""
The Evaluator
"""""""""""""

.. literalinclude:: rastrigin.py
    :pyobject: evaluate_rastrigin
    :end-before: #start_main

This function takes an iterable object containing the candidates along with the keyword arguments. The function should perform the evaluation of each of the candidates and return an iterable object containing each fitness value in the same order as the candidates [#]_. The Rastrigin problem is one of minimization, so we'll need to tell the evolution strategy that we are minimizing (by using ``maximize=False`` in the call to ``evolve``).

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
	[1.000015980034728, 1.000420691084238, 0.9986289052268122] : 0.000408117434489

.. {{{end}}}

As can be seen, we first create our random number generator object, seeding it with the current system time. Then we construct our ES, specifying a terminator (that stops after a given number of function evaluations). Finally, we call the ``evolve`` method of the ES. To this method, we pass the generator, evaluator, the population size, a flag to denote that we're minimizing in this problem (which defaults to ``maximize=True`` if unspecified), a bounding function to use for candidate solutions, and a set of keyword arguments that will be needed by one or more of the functions involved. For instance, we pass ``num_inputs`` to be used by our generator. Likewise, ``max_evaluations`` will be used by our terminator.

The script outputs the best individual in the final generation, which will be located at index 0 after the final population is sorted. Since the random number generator was seeded with the current time, your particular output will be different when running this script from that presented here. 

.. rubric:: Footnotes

.. [#] The evaluator was designed to evaluate all candidates, rather than a single candidate (with iteration happening inside the evolutionary computation), because this allows more complex evaluation functions that make use of the current set of individuals. Of course, such a function would also rely heavily on the choice of selector, as well.

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

After the libraries have been imported, we define our generator function. It looks for the keyword argument ``num_vertices``, and it creates a list of ``num_vertices`` ordered pairs (tuples) where each coordinate is in the range [-1, 1].

"""""""""""""
The Evaluator
"""""""""""""

.. literalinclude:: polyarea.py
    :pyobject: segments

.. literalinclude:: polyarea.py
    :pyobject: area

.. literalinclude:: polyarea.py
    :pyobject: evaluate_polygon
    :end-before: #start_bounder

In order to evaluate the polygon, we need to calculate its area. The ``segments`` and ``area`` functions do this for us. Therefore, the ``evaluate_polygon`` function simply needs to assign the fitness to be the value returned as the area.

"""""""""""
The Bounder
"""""""""""

.. literalinclude:: polyarea.py
    :start-after: #start_bounder
    :end-before: #end_bounder
    
Because our representation is a bit non-standard (a list of tuples), we need to create a bounding function that the EC can use to bound potential candidate solutions. Here, the bounding function is simple enough. It just make sure that each element of each tuple lies in the range [-1, 1]. The ``lower_bound`` and ``upper_bound`` attributes are added to the function so that the ``mutate_polygon`` function can make use of them without being hard-coded. While this is not strictly necessary, it does mimic the behavior of the ``Bounder`` callable class provided by ECsPy.

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



==============
Lunar Explorer
==============

In this example [#]_, we will evolve the configuration for a space probe designed to travel around the Moon and return to Earth. The space probe is defined by five parameters: its orbital height, mass, boost velocity (both x and y components), and initial y (vertical from Earth) velocity. The physical problem which we are here using optimization to solve is known as "Gravity Assist" or "Gravity Slingshot" and is used by spacecraft to alter the direction and speed of spacecraft, reducing the need for propellant. It was first propsed by Yuri Kondratyuk and first used by the Soviet space probe Luna 3 in 1959 to take the first pictures of the never-before seen far side of the moon. The computational power available to the designers of the Luna 3 was much smaller than what is available today. The optimization of the space craft's trajectory was therefore a very difficult task. The evaluator presented here makes some simplifying assumptions, but demonstrates the general principle of using evolutionary computation to solve an engineering or scientific task.

"""""""""""""
The Generator
"""""""""""""

.. literalinclude:: moonshot.py
    :start-after: #start_imports
    :end-before: #end_imports
    
.. literalinclude:: moonshot.py
    :pyobject: satellite_generator

After the libraries have been imported, we define our generator function. It simply pulls the bounder values for each of the five parameters of the satellite and randomly chooses a value between.

"""""""""""""
The Evaluator
"""""""""""""

.. literalinclude:: moonshot.py
    :pyobject: pairwise

This function breaks a one-dimensional list into a set of overlapping pairs. This is necessary because the trajectory of the satellite is a set of points, and the total distance traveled is calculated by summing the pairwise distances.
    
.. literalinclude:: moonshot.py
    :pyobject: distance_between

This function calculates the Euclidean distance between points.
    
.. literalinclude:: moonshot.py
    :pyobject: gravitational_force

This function calculates the gravitational force between the two given bodies.  
    
.. literalinclude:: moonshot.py
    :pyobject: force_on_satellite
    
This function calculates the force on the satellite from both the Earth and the Moon.

.. literalinclude:: moonshot.py
    :pyobject: acceleration_of_satellite

This function calculates the acceleration of the satellite due to the forces acting upon it.
    
.. literalinclude:: moonshot.py
    :pyobject: moonshot

This function does the majority of the work for the evaluation. It accepts the parameters that are being evolved, and it simulates the trajectory of a satellite as it moves around the Moon and back to the Earth. The fitness of the trajectory is as follows:

fitness = minimum distance from moon + 1% of total distance traveled + Moon crash penalty - Earth landing reward

The penalty/reward is 100000, and the fitness is designed to be minimized.

.. literalinclude:: moonshot.py
    :pyobject: moonshot_evaluator

The evaluator simply calls the `moonshot` function.
    
""""""""""""""""""""""""""""
The Evolutionary Computation
""""""""""""""""""""""""""""

.. literalinclude:: moonshot.py
    :start-after: #start_main
    :end-before: #end_main

The results, if plotted, will look similar to the figure below. Here, the color denotes the passage of time, from red to blue.

.. image:: moonshot.jpg
   :width: 600
   :alt: Sample Results
   :align: center
    
.. [#] This example was suggested and implemented by Mike Vella (vellamike@gmail.com), a contributor to ECsPy.

