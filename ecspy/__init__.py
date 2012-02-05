"""
    This package allows the creation of evolutionary computations.
    
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

import analysis
import archivers
import benchmarks
import contrib
import ec
import emo
import evaluators
import migrators
import observers
import replacers
import selectors
import swarm
import terminators
import topologies
import variators

__all__ = ['analysis', 'archivers', 'benchmarks', 'contrib', 'ec', 'emo', 'evaluators', 'migrators', 
           'observers', 'replacers', 'selectors', 'swarm', 'terminators', 'topologies', 'variators']
__version__ = '1.1'
__author__ = 'Aaron Garrett <aaron.lee.garrett@gmail.com>'
__url__ = 'http://ecspy.googlecode.com'
