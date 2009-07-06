from setuptools import setup

setup(name='ecspy',
      version='0.1',
      packages=['ecspy'],

      description="A framework for creating evolutionary computations "\
        "in Python.",

      long_description="""
ECsPy (pronounced "easy as pie") provides a framework for creating 
evolutionary computations in Python. Additionally, ECsPy provides an
easy-to-use canonical genetic algorithm (GA), evolution strategy (ES), 
and particle swarm optimizer (PSO) for users who don't need much 
customization.

  
Requirements
============

Requires at least Python 2.6.


License
=======

This package is distributed under the GNU General Public License 
version 3.0 (GPLv3). This license can be found online at
http://www.opensource.org/licenses/gpl-3.0.html.

  
Package Structure
=================
  
ECsPy consists of the following 6 modules:

  * ec.py -- provides the basic framework for the EvolutionEngine and specific ECs
             
  * observers.py -- defines a few built-in (screen and file) observers  
  
  * replacers.py -- defines standard replacement schemes such as generational and steady-state replacement
                    
  * selectors.py -- defines standard selectors (e.g., tournament)
  
  * terminators.py -- defines standard terminators (e.g., exceeding a maximum number of generations)
                      
  * variators.py -- defines standard variators (crossover and mutation schemes such as n-point crossover)


Resources
=========

  * Homepage: http://ecspy.googlecode.com
  
  * Email: aaron.lee.garrett@gmail.com
  
""",

      author='Aaron Garrett',
      author_email='aaron.lee.garrett@gmail.com',
      url='http://ecspy.googlecode.com',
      license='GPLv3+',
      keywords='evolutionary computation genetic algorithm optimization',

      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.6',
          'Topic :: Scientific/Engineering :: Artificial Intelligence'
          ]

     )

