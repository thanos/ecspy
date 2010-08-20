"""
    This module provides pre-defined variators for evolutionary computations.
    
    All variator functions have the following arguments:
    
    - *random* -- the random number generator object
    - *candidates* -- the candidate solutions
    - *args* -- a dictionary of keyword arguments
    
    Each variator function returns the list of modified individuals.
    
    These variators may make some limited assumptions about the type of
    candidate solutions on which they operate. These assumptions are noted
    in the table below.
    
    +--------------------------------------+----------+-----------+-----------+----------+---------+------+--------+
    | Variator                             | Iterable | Indexable | Sliceable | Listable | Lenable | Real | Binary |
    +======================================+==========+===========+===========+==========+=========+======+========+
    | blend_crossover                      |    X     |           |           |          |    X    |   X  |        |
    +--------------------------------------+----------+-----------+-----------+----------+---------+------+--------+
    | differential_crossover               |    X     |           |           |          |         |   X  |        |
    +--------------------------------------+----------+-----------+-----------+----------+---------+------+--------+
    | n_point_crossover                    |          |           |     X     |     X    |    X    |      |        |
    +--------------------------------------+----------+-----------+-----------+----------+---------+------+--------+
    | simulated_binary_crossover           |    X     |           |           |          |         |   X  |        |
    +--------------------------------------+----------+-----------+-----------+----------+---------+------+--------+
    | uniform_crossover                    |    X     |           |           |          |         |      |        |
    +--------------------------------------+----------+-----------+-----------+----------+---------+------+--------+
    | bit_flip_mutation                    |    X     |     X     |           |          |    X    |      |    X   |
    +--------------------------------------+----------+-----------+-----------+----------+---------+------+--------+
    | gaussian_mutation                    |    X     |     X     |           |          |    X    |   X  |        |
    +--------------------------------------+----------+-----------+-----------+----------+---------+------+--------+
    | default_variation                    |          |           |           |          |         |      |        |
    +--------------------------------------+----------+-----------+-----------+----------+---------+------+--------+
    | estimation_of_distribution_variation |          |     X     |           |          |    X    |   X  |        |
    +--------------------------------------+----------+-----------+-----------+----------+---------+------+--------+
        
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

from crossovers import crossover
from crossovers import blend_crossover
from crossovers import differential_crossover
from crossovers import n_point_crossover
from crossovers import simulated_binary_crossover
from crossovers import uniform_crossover
from mutators import mutator
from mutators import bit_flip_mutation
from mutators import gaussian_mutation
from variators import default_variation
from variators import estimation_of_distribution_variation

__all__ = ['crossover', 'blend_crossover', 'differential_crossover', 'n_point_crossover', 'simulated_binary_crossover', 'uniform_crossover', 
           'mutator', 'bit_flip_mutation', 'gaussian_mutation',
           'default_variation', 'estimation_of_distribution_variation']