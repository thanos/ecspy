"""
    This module provides analysis methods for the results of evolutionary computations.

    .. Copyright (C) 2010  Inspired Intelligence Initiative

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

import math
import csv


def generation_plot(filename, errorbars=True):
    """Plot the results of the EC using generation statistics.
    
    This function creates a plot of the generation fitness statistics 
    (best, worst, median, and average). 

    .. figure:: http://mcis.jsu.edu/faculty/agarrett/generation_plot.png
        :alt: Example generation plot
        :align: center
        
        An example image saved from the generation_plot function (without error bars).
    
    Arguments:
    
    - *filename* -- the name of the statistics file produced by the file_observer 
    - *errorbars* -- Boolean value stating whether standard error bars should 
      be drawn (default True)

    """
    import pylab
    import matplotlib.font_manager 
    
    generation = []
    psize = []
    worst = []
    best = []
    median = []
    average = []
    stdev = []
    reader = csv.reader(open(filename))
    for row in reader:
        generation.append(int(row[0]))
        psize.append(int(row[1]))
        worst.append(float(row[2]))
        best.append(float(row[3]))
        median.append(float(row[4]))
        average.append(float(row[5]))
        stdev.append(float(row[6]))
    stderr = [s / math.sqrt(p) for s, p in zip(stdev, psize)]
    
    data = [average, median, best, worst]
    colors = ['black', 'blue', 'green', 'red']
    labels = ['average', 'median', 'best', 'worst']
    figure = pylab.figure()
    if errorbars:
        pylab.errorbar(generation, average, stderr, color=colors[0], label=labels[0])
    else:
        pylab.plot(generation, average, color=colors[0], label=labels[0])
    for d, col, lab in zip(data[1:], colors[1:], labels[1:]):
        pylab.plot(generation, d, color=col, label=lab)
    pylab.fill_between(generation, data[2], data[3], color='#e6f2e6')
    pylab.grid(True)
    ymin = min([min(d) for d in data])
    ymax = max([max(d) for d in data])
    yrange = ymax - ymin
    pylab.ylim((ymin - 0.1*yrange, ymax + 0.1*yrange))  
    prop = matplotlib.font_manager.FontProperties(size=8) 
    pylab.legend(loc='upper left', prop=prop)    
    pylab.xlabel('Generation')
    pylab.ylabel('Fitness')
    pylab.show()    
    
    
def hypervolume(pareto_set, reference_point=None):
    """Calculates the hypervolume by slicing objectives (HSO).
    
    This function calculates the hypervolume (or S-measure) of a nondominated
    set using the Hypervolume by Slicing Objectives (HSO) procedure of `While, et al. 
    (IEEE CEC 2005) <http://www.lania.mx/~ccoello/EMOO/while05a.pdf.gz>`_.
    The *pareto_set* should be a list of lists of objective values.
    The *reference_point* may be specified or it may be left as the default 
    value of None. In that case, the reference point is calculated to be the
    maximum value in the set for all objectives (the ideal point). This function 
    assumes that objectives are to be maximized.
    
    Arguments:
    
    - *pareto_set* -- the list or lists of objective values comprising the Pareto front
    - *reference_point* -- the reference point to be used (default None)
    
    """
    def dominates(p, q, k=None):
        if k is None:
            k = len(p)
        d = True
        while d and k < len(p):
            d = not (q[k] > p[k])
            k += 1
        return d
        
    def insert(p, k, pl):
        ql = []
        while pl and pl[0][k] > p[k]:
            ql.append(pl[0])
            pl = pl[1:]
        ql.append(p)
        while pl:
            if not dominates(p, pl[0], k):
                ql.append(pl[0])
            pl = pl[1:]
        return ql

    def slice(pl, k, ref):
        p = pl[0]
        pl = pl[1:]
        ql = []
        s = []
        while pl:
            ql = insert(p, k + 1, ql)
            p_prime = pl[0]
            s.append((math.fabs(p[k] - p_prime[k]), ql))
            p = p_prime
            pl = pl[1:]
        ql = insert(p, k + 1, ql)
        s.append((math.fabs(p[k] - ref[k]), ql))
        return s

    ps = pareto_set
    ref = reference_point
    n = min([len(p) for p in ps])
    if ref is None:
        ref = [max(ps, key=lambda x: x[o])[o] for o in range(n)]
    pl = ps[:]
    pl.sort(key=lambda x: x[0], reverse=True)
    s = [(1, pl)]
    for k in range(n - 1):
        s_prime = []
        for x, ql in s:
            for x_prime, ql_prime in slice(ql, k, ref):
                s_prime.append((x * x_prime, ql_prime))
        s = s_prime
    vol = 0
    for x, ql in s:
        vol = vol + x * math.fabs(ql[0][n - 1] - ref[n - 1])
    return vol



    
    