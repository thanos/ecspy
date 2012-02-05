``ecspy`` -- A framework for creating evolutionary computations in Python.
--------------------------------------------------------------------------

ECsPy (Evolutionary Computations in Python) is a free, open source framework for 
creating evolutionary computations in Python. Additionally, ECsPy 
provides an easy-to-use canonical genetic algorithm (GA), evolution 
strategy (ES), estimation of distribution algorithm (EDA), differential 
evolution algorithm (DEA), and particle swarm optimizer (PSO) for users 
who don't need much customization.

  
Requirements
============

  * Requires at least Python 2.6 (not compatible with Python 3+).
  * Numpy and Matplotlib are required if the line plot observer is used.
  * Parallel Python (pp) is required if parallel_evaluation_pp is used.



License
=======

This package is distributed under the GNU General Public License 
version 3.0 (GPLv3). This license can be found online at
http://www.opensource.org/licenses/gpl-3.0.html.

  
Package Structure
=================
  
ECsPy consists of the following modules:

  * analysis.py -- provides tools for analyzing the results of an EC
  
  * archivers.py -- defines useful archiving methods, particularly for EMO algorithms
  
  * benchmarks.py -- defines several single- and multi-objective benchmark optimization problems
  
  * ec.py -- provides the basic framework for an EvolutionaryComputation and specific ECs
  
  * emo.py -- provides the Pareto class for multiobjective optimization along with specific EMOs (e.g. NSGA-II)
  
  * evaluators.py -- defines useful evaluation schemes, such as parallel evaluation
  
  * migrators.py -- defines a few built-in migrators, including migration via network and migration among concurrent processes

  * observers.py -- defines a few built-in observers, including screen, file, and plotting observers
  
  * replacers.py -- defines standard replacement schemes such as generational and steady-state replacement

  * selectors.py -- defines standard selectors (e.g., tournament)
  
  * swarm.py -- provides a basic particle swarm optimizer
  
  * terminators.py -- defines standard terminators (e.g., exceeding a maximum number of generations)
  
  * topologies.py -- defines standard topologies for particle swarms

  * variators.py -- defines standard variators (crossover and mutation schemes such as n-point crossover)


Resources
=========

  * Homepage: http://ecspy.googlecode.com
  
  * Email: aaron.lee.garrett@gmail.com
  
