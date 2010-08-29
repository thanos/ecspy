***************
ECsPy Reference
***************

This chapter provides a complete reference to all of the functionality included in ECsPy.

========================
Evolutionary Computation
========================

.. autoclass:: ecspy.ec.EvolutionExit
   :members:
   
.. autoclass:: ecspy.ec.Bounder
   :members:
   
.. autoclass:: ecspy.ec.Individual
   :members:
   
.. autoclass:: ecspy.ec.EvolutionaryComputation
   :members:
   
.. autoclass:: ecspy.ec.DEA
   :members:
   
.. autoclass:: ecspy.ec.EDA
   :members:
   
.. autoclass:: ecspy.ec.ES
   :members:
   
.. autoclass:: ecspy.ec.GA
   :members:
   
.. autoclass:: ecspy.ec.SA
   :members:
   
---------
Functions
---------

An evolutionary computation is composed of many parts:

- an archiver -- stores solutions separate from the population (e.g., in a multiobjective EC)
- an evaluator -- measures the fitness of candidate solutions; problem-dependent
- a generator -- creates new candidate solutions; problem-dependent
- a migrator -- moves individuals to other populations (in the case of distributed ECs) 
- observers -- view the progress of an EC in operation; may be a list of observers
- a replacer -- determines the survivors of a generation
- a selector -- determines the parents of a generation
- terminators -- determine whether the evolution should stop; may be a list of terminators
- variators -- modify candidate solutions; may be a list of variators

Each of these parts may be specified to create custom ECs to suit particular problems.

^^^^^^^^^
Archivers
^^^^^^^^^

.. automodule:: ecspy.archivers
   :members:
   
^^^^^^^^^^
Evaluators
^^^^^^^^^^

.. automodule:: ecspy.evaluators
   :members:
   
^^^^^^^^^^
Generators
^^^^^^^^^^

Generator functions are problem-specific. They are used to create the initial set of candidate
solutions needed by the evolutionary computation. All generator functions have the following arguments:
    
- *random* -- the random number generator object
- *args* -- a dictionary of keyword arguments
   
^^^^^^^^^
Migrators
^^^^^^^^^

.. automodule:: ecspy.migrators
   :members:
   
^^^^^^^^^
Observers
^^^^^^^^^

.. automodule:: ecspy.observers
   :members:
   
^^^^^^^^^
Replacers
^^^^^^^^^

.. automodule:: ecspy.replacers
   :members:
   
^^^^^^^^^
Selectors
^^^^^^^^^

.. automodule:: ecspy.selectors
   :members:
   
^^^^^^^^^^
Teminators
^^^^^^^^^^

.. automodule:: ecspy.terminators
   :members:
   
^^^^^^^^^
Variators
^^^^^^^^^

.. automodule:: ecspy.variators
   :members:
   
===========================
Particle Swarm Optimization
===========================

.. automodule:: ecspy.swarm
   :members:
   
----------
Topologies
----------

Additionally, particle swarms make use of topologies, which determine the logical
relationships among particles in the swarm (i.e., which ones belong to the same
"neighborhood").

.. automodule:: ecspy.topologies
   :members:

========================================
Evolutionary Multiobjective Optimization
========================================

.. automodule:: ecspy.emo
   :members:
   
========
Analysis
========

.. automodule:: ecspy.analysis
   :members:
   
==================
Benchmark Problems
==================

.. autoclass:: ecspy.benchmarks.Benchmark
   :members:
   
.. autoclass:: ecspy.benchmarks.Binary
   :members:
   
---------------------------
Single-Objective Benchmarks
---------------------------

.. autoclass:: ecspy.benchmarks.Ackley
   :members:
   
.. autoclass:: ecspy.benchmarks.Griewank
   :members:
   
.. autoclass:: ecspy.benchmarks.Rastrigin
   :members:
   
.. autoclass:: ecspy.benchmarks.Rosenbrock
   :members:
   
.. autoclass:: ecspy.benchmarks.Schwefel
   :members:
   
.. autoclass:: ecspy.benchmarks.Sphere
   :members:
   
--------------------------
Multi-Objective Benchmarks
--------------------------

.. autoclass:: ecspy.benchmarks.Kursawe
   :members:
   
.. autoclass:: ecspy.benchmarks.DTLZ1
   :members:
   
.. autoclass:: ecspy.benchmarks.DTLZ2
   :members:
   
.. autoclass:: ecspy.benchmarks.DTLZ3
   :members:
   
.. autoclass:: ecspy.benchmarks.DTLZ4
   :members:
   
.. autoclass:: ecspy.benchmarks.DTLZ5
   :members:
   
.. autoclass:: ecspy.benchmarks.DTLZ6
   :members:
   
.. autoclass:: ecspy.benchmarks.DTLZ7
   :members:
   
=====================
Contributed Utilities
=====================

.. automodule:: ecspy.contrib.utils
   :members:




