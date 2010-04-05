
def round_fitness(population, _round=3):
    '''
    returns the rounded fitness values of a population
    @param population: the population which has the fitness to be rounded    
    @param _round:     decimal digits to round off
    '''
    _pop = []
    for p in population:
        if hasattr(p.fitness, '__iter__'):
            _pop.append([round(i,_round) for i in p.fitness])
        else:
            _pop.append(round(p.fitness,_round))
    return _pop
