from setuptools import setup

setup(name='ecspy',
      version='0.1',
      py_modules=['ec', 'observers', 'replacers', 'selectors', 'terminators', 'variators'],

      description="A framework for creating evolutionary computations "\
        "in Python.",

      long_description="""
------------
ECsPy
------------

  ECsPy (pronounced "easy as pie") provides a framework for creating evolutionary computations 
  in Python. Additionally, ECsPy provides an   easy-to-use canonical genetic algorithm (GA), 
  evolution strategy (ES), and particle swarm optimizer (PSO) for users who don't need much 
  customization.
  
  
Package Structure
=================
  
  ECsPy consists of the following 6 modules:
    * ec.py -- provides the basic 
    * observers.py -- 
    * replacers.py -- 
    * selectors.py -- 
    * terminators.py -- 
    * variators.py -- 

Example
=======

from random import Random
from time import time
from ecspy import ec
from ecspy import terminators
from ecspy import selectors
from ecspy import replacers
from ecspy import variators
from ecspy import observers


def generate_real(random, args):
    try:
        size = args['chrom_size']
    except KeyError:
        size = 4
    return [random.random() for i in xrange(size)]

def evaluate_real(candidates, args):
    fitness = []
    for cand in candidates:
        num = sum(cand)
        fitness.append(num)
    return fitness

    
rand = Random()
rand.seed(int(time()))
engine = ec.EvolutionEngine(rand)
engine.selector = selectors.tournament_selection
engine.variator = [variators.uniform_crossover, variators.gaussian_mutation]
engine.replacer = replacers.steady_state_replacement
engine.observer = observers.screen_observer

start = time()
final_pop = engine.evolve(evaluator=evaluate_real, 
                          generator=generate_real, 
                          terminator=terminators.num_gen_termination,
                          pop_size=100, 
                          tourn_size=7,
                          num_selected=2, 
                          max_generations=100,
                          mutation_rate=0.2)
stop = time()

print('***********************************')
print('Total Execution Time: %0.5f seconds' % (stop - start))
for ind in final_pop:
    print(str(ind))


Requirements
============

  Requires at least Windows XP and Python 2.6.

Resources
=========

  * Homepage: http://ecspy.googlecode.com
  * Email: aaron.lee.garrett@gmail.com
  
""",

      author='Aaron Garrett',
      author_email='aaron.lee.garrett@gmail.com',
      url='http://ecspy.googlecode.com',
      keywords = "evolutionary computation genetic algorithm optimization",

      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Win32 (MS Windows)',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: Microsoft :: Windows',
          'Programming Language :: Python :: 2.6',
          'Topic :: Scientific/Engineering :: Artificial Intelligence'
          ]

     )

