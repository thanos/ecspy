"""
    This module provides pre-defined observers for evolutionary computations.
    
    All observer functions have the following arguments:
    
    - *population* -- the population of Individuals
    - *num_generations* -- the number of elapsed generations
    - *num_evaluations* -- the number of candidate solution evaluations
    - *args* -- a dictionary of keyword arguments    
    
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

import time
import math


def default_observer(population, num_generations, num_evaluations, args):
    """Do nothing."""    
    pass
    
    
def screen_observer(population, num_generations, num_evaluations, args):
    """Print the output of the EC to the screen.
    
    This function displays the results of the evolutionary computation
    to the screen. The output includes the generation number, the current
    number of evaluations, the average fitness, the maximum fitness, and 
    the full population.
    
    .. Arguments:
       population -- the population of Individuals
       num_generations -- the number of elapsed generations
       num_evaluations -- the number of candidate solution evaluations
       args -- a dictionary of keyword arguments
    
    """

    population = list(population)
    population.sort(reverse=True)
    worst_fit = population[-1].fitness
    best_fit = population[0].fitness

    plen = len(population)
    if plen % 2 == 1:
        med_fit = population[(plen - 1) / 2].fitness
    else:
        med_fit = float(population[plen / 2 - 1].fitness + population[plen / 2].fitness) / 2
    avg_fit = sum([p.fitness for p in population]) / float(plen)
    std_fit = math.sqrt(sum([(p.fitness - avg_fit)**2 for p in population]) / float(plen - 1))
    
    print('Generation Evaluation Worst      Best       Median     Average    Std Dev   ')
    print('---------- ---------- ---------- ---------- ---------- ---------- ----------')
    print('{0:10} {1:10} {2:10} {3:10} {4:10} {5:10} {6:10}\n'.format(num_generations, num_evaluations, worst_fit, best_fit, med_fit, avg_fit, std_fit))
    print('Current Population:')
    for ind in population:
        print(str(ind))
    print('----------------------------------------------------------------------------')

    
def file_observer(population, num_generations, num_evaluations, args):
    """Print the output of the EC to a file.
    
    This function saves the results of the evolutionary computation
    to two files. The first file, which by default is named 
    'ecspy-statistics-file-<timestamp>.csv', contains the basic
    generational statistics of the population throughout the run
    (worst, best, median, and average fitness and standard deviation
    of the fitness values). The second file, which by default is named
    'ecspy-individuals-file-<timestamp>.csv', contains every individual
    during each generation of the run. Both files may be passed to the
    function as keyword arguments (see below).
    
    .. Arguments:
       population -- the population of Individuals
       num_generations -- the number of elapsed generations
       num_evaluations -- the number of candidate solution evaluations
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    - *statistics_file* -- a file object (default: see text)
    - *individuals_file* -- a file object (default: see text) 
    
    """
    
    try:
        statistics_file = args['statistics_file']
    except KeyError:
        statistics_file = open('ecspy-statistics-file-' + time.strftime('%m%d%Y-%H%M%S') + '.csv', 'w')
    try:
        individuals_file = args['individuals_file']
    except KeyError:
        individuals_file = open('ecspy-individuals-file-' + time.strftime('%m%d%Y-%H%M%S') + '.csv', 'w')

    population = list(population)
    population.sort(reverse=True)
    worst_fit = population[-1].fitness
    best_fit = population[0].fitness

    plen = len(population)
    if plen % 2 == 1:
        med_fit = population[(plen - 1) / 2].fitness
    else:
        med_fit = float(population[plen / 2 - 1].fitness + population[plen / 2].fitness) / 2
    avg_fit = sum([p.fitness for p in population]) / float(plen)
    std_fit = math.sqrt(sum([(p.fitness - avg_fit)**2 for p in population]) / float(plen - 1))
    
    statistics_file.write('{0}, {1}, {2}, {3}, {4}, {5}, {6}\n'.format(num_generations, len(population), worst_fit, best_fit, med_fit, avg_fit, std_fit))
    for i, p in enumerate(population):
        individuals_file.write('{0}, {1}, {2}, {3}\n'.format(num_generations, i, p.fitness, str(p.candidate)))
    statistics_file.flush()
    individuals_file.flush()
    

def archive_observer(population, num_generations, num_evaluations, args):
    """Print the current archive to the screen."""
    archive = args['_ec'].archive
    print('                         Archive Size: %5d' % len(archive))
    print('----------------------------------------------------------------------')
    for a in archive:
        print(a)
    print('----------------------------------------------------------------------')

        
def plot_observer(population, num_generations, num_evaluations, args):    
    """Plot the output of the EC as a graph.
    
    This function plots the performance of the EC as a line graph 
    using the pylab library (matplotlib). The graph consists of a 
    blue line representing the best fitness, a green line representing
    the average fitness, and a red line representing the median fitness.
    It modifies the keyword arguments variable 'args' by including an
    entry called 'plot_data'.
    
    If this observer is used, the calling script should also import
    the pylab library and should end the script with 
    
    pylab.show()
    
    Otherwise, the program may generate a runtime error.
    
    .. Arguments:
       population -- the population of Individuals
       num_generations -- the number of elapsed generations
       num_evaluations -- the number of candidate solution evaluations
       args -- a dictionary of keyword arguments
    
    """
    import pylab
    import numpy
    
    population = list(population)
    population.sort(reverse=True)
    best_fitness = population[0].fitness
    worst_fitness = population[-1].fitness
    median_fitness = numpy.median([p.fitness for p in population])
    average_fitness = numpy.mean([p.fitness for p in population])
    colors = ['black', 'blue', 'green', 'red']
    labels = ['average', 'median', 'best', 'worst']
    data = []
    if num_generations == 0:
        pylab.ion()
        data = [[num_evaluations], [average_fitness], [median_fitness], [best_fitness], [worst_fitness]]
        lines = []
        for i in range(4):
            line, = pylab.plot(data[0], data[i+1], color=colors[i], label=labels[i])
            lines.append(line)
        # Add the legend when the first data is added.
        pylab.legend(loc='lower right')
        args['plot_data'] = data
        args['plot_lines'] = lines
        pylab.xlabel('Evaluations')
        pylab.ylabel('Fitness')
    else:
        data = args['plot_data']
        data[0].append(num_evaluations)
        data[1].append(average_fitness)
        data[2].append(median_fitness)
        data[3].append(best_fitness)
        data[4].append(worst_fitness)
        lines = args['plot_lines']
        for i, line in enumerate(lines):
            line.set_xdata(numpy.array(data[0]))
            line.set_ydata(numpy.array(data[i+1]))
        args['plot_data'] = data
        args['plot_lines'] = lines
    ymin = min([min(d) for d in data[1:]])
    ymax = max([max(d) for d in data[1:]])
    yrange = ymax - ymin
    pylab.xlim((0, num_evaluations))
    pylab.ylim((ymin - 0.1*yrange, ymax + 0.1*yrange))
    pylab.draw()
