# ECsPy Has Been Deprecated; Use inspyred Instead #
As of April 3, 2012, ECsPy has been deprecated. New users should instead use the inspyred library, available on PyPI or at http://inspyred.github.com. ECsPy will no longer be maintained.


---


---


ECsPy (Evolutionary Computations in Python) is a free, open source framework for
creating evolutionary computations in Python. Additionally, ECsPy
provides an easy-to-use canonical genetic algorithm (GA), evolution
strategy (ES), estimation of distribution algorithm (EDA), differential
evolution algorithm (DEA), and particle swarm optimizer (PSO) for users
who don't need much customization. The full documentation can be found at http://packages.python.org/ecspy/.



# Requirements #
  * Requires at least Python 2.6 (not compatible with Python 3+).
  * Numpy and Matplotlib are required if the line plot observer is used.
  * Parallel Python (pp) is required if parallel\_evaluation\_pp is used.


# License #
This package is distributed under the GNU General Public License version 3.0 (GPLv3). This license can be found online at [The Open Source Initiative](http://www.opensource.org/licenses/gpl-3.0.html).


# Background #
An extensive background on evolutionary computation, including references to the relevant academic literature, can be found in the [Project Wiki](IntroductionToECs.md). You can also find a great deal of information from the Wikipedia links in the sidebar.


# Package Structure #
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

# Example #
The following example illustrates the basics of the ECsPy package. In this example, candidate solutions are 10-bit binary strings whose decimal values should be maximized.
```
import random 
import time 
import ecspy

def generate_binary(random, args):
    bits = args.get('num_bits', 8)
    return [random.choice([0, 1]) for i in range(bits)]

@ecspy.evaluators.evaluator
def evaluate_binary(candidate, args):
    return int("".join([str(c) for c in candidate]), 2)

rand = random.Random()
rand.seed(int(time.time()))
ga = ecspy.ec.GA(rand)
ga.observer = ecspy.observers.screen_observer
ga.terminator = ecspy.terminators.evaluation_termination
final_pop = ga.evolve(evaluator=evaluate_binary,
                      generator=generate_binary,
                      max_evaluations=1000,
                      num_elites=1,
                      pop_size=100,
                      num_bits=10)
final_pop.sort(reverse=True)
for ind in final_pop:
    print(str(ind))
```