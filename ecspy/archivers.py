"""
    This module provides pre-defined archivers for evolutionary computations.
    
    All archiver functions have the following arguments:
    
    - *random* -- the random number generator object
    - *population* -- the population of individuals
    - *archive* -- the current archive of individuals
    - *args* -- a dictionary of keyword arguments
    
    Each archiver function returns the updated archive.
    
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

import math


def default_archiver(random, population, archive, args):
    """Archive the current population.
    
    .. Arguments:
       random -- the random number generator object
       population -- the population of individuals
       archive -- the current archive of individuals
       args -- a dictionary of keyword arguments
    
    """
    new_archive = []
    for ind in population:
        new_archive.append(ind)
    return new_archive
    

def best_archiver(random, population, archive, args):
    """Archive only the best individual(s).
    
    This function archives the best solutions and removes inferior ones.
    If the comparison operators have been overloaded to define Pareto
    preference (as in the ``Pareto`` class), then this archiver will form 
    a Pareto archive.
    
    .. Arguments:
       random -- the random number generator object
       population -- the population of individuals
       archive -- the current archive of individuals
       args -- a dictionary of keyword arguments
    
    """
    new_archive = archive
    for ind in population:
        if len(new_archive) == 0:
            new_archive.append(ind)
        else:
            should_remove = []
            should_add = True
            for a in new_archive:
                if ind == a:
                    should_add = False
                    break
                elif ind < a:
                    should_add = False
                elif ind > a:
                    should_remove.append(a)
            for r in should_remove:
                new_archive.remove(r)
            if should_add:
                new_archive.append(ind)
    return new_archive

    
def adaptive_grid_archiver(random, population, archive, args):
    """Archive only the best individual(s) using a fixed size grid.
    
    This function archives the best solutions by using a fixed-size grid
    to determine which existing solutions should be removed in order to
    make room for new ones. This archiver is designed specifically for
    use with the Pareto Archived Evolution Strategy (PAES).

    .. Arguments:
       random -- the random number generator object
       population -- the population of individuals
       archive -- the current archive of individuals
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    - *max_archive_size* -- the maximum number of individuals in the archive
      (default len(population))
    - *num_grid_divisions* -- the number of grid divisions (default 1)
    
    """
    def get_grid_location(fitness, num_grid_divisions, global_smallest, global_largest):
        loc = 0
        n = 1
        num_objectives = len(fitness)
        inc = [0 for _ in range(num_objectives)]
        width = [0 for _ in range(num_objectives)]
        local_smallest = global_smallest[:]
        for i, f in enumerate(fitness):
            if f < local_smallest[i] or f > local_smallest[i] + global_largest[i] - global_smallest[i]:
                return -1
        for i in range(num_objectives):
            inc[i] = n
            n *= 2
            width[i] = global_largest[i] - global_smallest[i]
        for d in range(num_grid_divisions):
            for i, f in enumerate(fitness):
                if f < width[i] / 2.0 + local_smallest[i]:
                    loc += inc[i]
                else:
                    local_smallest[i] += width[i] / 2.0
            for i in range(num_objectives):
                inc[i] *= num_objectives * 2
                width[i] /= 2.0
        return loc
 
    def update_grid(individual, archive, num_grid_divisions, global_smallest, global_largest, grid_population):
        if len(archive) == 0:
            num_objectives = len(individual.fitness)
            smallest = [individual.fitness[o] for o in range(num_objectives)]
            largest = [individual.fitness[o] for o in range(num_objectives)]
        else:
            num_objectives = min(min([len(a.fitness) for a in archive]), len(individual.fitness))
            smallest = [min(min([a.fitness[o] for a in archive]), individual.fitness[o]) for o in range(num_objectives)] 
            largest = [max(max([a.fitness[o] for a in archive]), individual.fitness[o]) for o in range(num_objectives)]
        for i in range(num_objectives):
            global_smallest[i] = smallest[i] - abs(0.2 * smallest[i])
            global_largest[i] = largest[i] + abs(0.2 * largest[i])
        for i in range(len(grid_population)):
            grid_population[i] = 0
        for a in archive:
            loc = get_grid_location(a.fitness, num_grid_divisions, global_smallest, global_largest)
            a.grid_location = loc
            grid_population[loc] += 1
        loc = get_grid_location(individual.fitness, num_grid_divisions, global_smallest, global_largest)
        individual.grid_location = loc
        grid_population[loc] += 1

    max_archive_size = args.setdefault('max_archive_size', len(population))
    num_grid_divisions = args.setdefault('num_grid_divisions', 1)
        
    if not 'grid_population' in dir(adaptive_grid_archiver):
        adaptive_grid_archiver.grid_population = [0 for _ in range(2**(min([len(p.fitness) for p in population]) * num_grid_divisions))]
    if not 'global_smallest' in dir(adaptive_grid_archiver):
        adaptive_grid_archiver.global_smallest = [0 for _ in range(min([len(p.fitness) for p in population]))]
    if not 'global_largest' in dir(adaptive_grid_archiver):
        adaptive_grid_archiver.global_largest = [0 for _ in range(min([len(p.fitness) for p in population]))]
     
    new_archive = archive
    for ind in population:
        update_grid(ind, new_archive, num_grid_divisions, adaptive_grid_archiver.global_smallest, 
                    adaptive_grid_archiver.global_largest, adaptive_grid_archiver.grid_population)
        should_be_added = True
        for a in new_archive:
            if ind == a or a > ind:
                should_be_added = False
                
        if should_be_added:
            if len(new_archive) == 0:
                new_archive.append(ind)
            else:
                join = False
                nondominated = True
                removal_set = []
                for i, a in enumerate(new_archive):
                    if ind > a and not join:
                        new_archive[i] = ind
                        join = True
                    elif ind > a:
                        if not a in removal_set: 
                            removal_set.append(a)
                    # Otherwise, the individual is nondominated against this archive member.
                    
                new_archive = list(set(new_archive) - set(removal_set))
                
                if not join and nondominated:
                    if len(new_archive) == max_archive_size:
                        replaced_index = 0
                        found_replacement = False
                        loc = get_grid_location(ind.fitness, num_grid_divisions, 
                                                adaptive_grid_archiver.global_smallest, 
                                                adaptive_grid_archiver.global_largest)
                        ind.grid_location = loc
                        if ind.grid_location >= 0:
                            most = adaptive_grid_archiver.grid_population[ind.grid_location]
                        else:
                            most = -1
                        for i, a in enumerate(new_archive):
                            pop_at_a = adaptive_grid_archiver.grid_population[a.grid_location]
                            if pop_at_a > most:
                                most = pop_at_a
                                replaced_index = i
                                found_replacement = True
                        if found_replacement:
                            new_archive[replaced_index] = ind
                    else:
                        new_archive.append(ind)
    return new_archive
