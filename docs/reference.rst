***************
ECsPy Reference
***************

This chapter provides a complete reference to all of the functionality included in ECsPy.

========================
Evolutionary Computation
========================

.. automodule:: ecspy.ec
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
   

