
def default_selection(random, population, args):
    return population

    
def uniform_selection(random, population, args):
    try:
        num_selected = args['num_selected']
    except KeyError:
        num_selected = 1
        args['num_selected'] = num_selected
    pop = list(population)
    selected = []
    for _ in xrange(num_selected):
        selected.append(pop[random.randint(0, len(pop)-1)])
    return selected


def roulette_wheel_selection(random, population, args):
    try:
        num_selected = args['num_selected']
    except KeyError:
        num_selected = 1
        args['num_selected'] = num_selected
        
    pop = list(population)
    len_pop = len(pop)
    psum = [i for i in xrange(len_pop)]
    pop_max_fit = (max(pop, key=lambda x: x.fitness)).fitness
    pop_min_fit = (min(pop, key=lambda x: x.fitness)).fitness
    
    # Set up the roulette wheel
    if pop_max_fit == pop_min_fit:
        for index in xrange(len_pop):
            psum[index] = index + 1 / float(len_pop)
    elif (pop_max_fit > 0 and pop_min_fit >= 0) or (pop_max_fit <= 0 and pop_min_fit < 0):
        pop.sort(key=lambda x: x.fitness, reverse=True)
        psum[0] = pop[0].fitness
        for i in xrange(1, len_pop):
            psum[i] = pop[i].fitness + psum[i-1]
        for i in xrange(len_pop):
            psum[i] /= float(psum[len_pop-1])
            
    # Select the individuals
    selected = []
    for _ in xrange(num_selected):
        cutoff = random.random()
        lower = 0
        upper = len_pop - 1
        while(upper >= lower):
            i = lower + (upper - lower) / 2
            if psum[i] > cutoff: 
                upper = i - 1
            else: 
                lower = i + 1
        lower = min(len_pop-1, lower)
        lower = max(0, lower)
        selected.append(pop[lower])

    return selected


def rank_selection(random, population, args):
    try:
        num_selected = args['num_selected']
    except KeyError:
        num_selected = 1
        args['num_selected'] = num_selected
    pop = list(population)
    len_pop = len(pop)
    pop.sort(key=lambda x: x.fitness)
    psum = [i for i in xrange(len_pop)]
    den = (len_pop * (len_pop + 1)) / 2.0
    for i in xrange(len_pop):
        psum[i] = (i + 1) / den
        
    # Select the individuals
    selected = []
    for _ in xrange(num_selected):
        cutoff = random.random()
        lower = 0
        upper = len_pop - 1
        while(upper >= lower):
            i = lower + (upper - lower) / 2
            if psum[i] > cutoff: 
                upper = i - 1
            else: 
                lower = i + 1
        lower = min(len_pop-1, lower)
        lower = max(0, lower)
        selected.append(pop[lower])

    return selected


def tournament_selection(random, population, args):
    try:
        num_selected = args['num_selected']
    except KeyError:
        num_selected = 1
        args['num_selected'] = num_selected
    try:
        tourn_size = args['tourn_size']
    except KeyError:
        tourn_size = 2
        args['tourn_size'] = tourn_size
    pop = list(population)
    selected = []
    for _ in xrange(num_selected):
        tourn = random.sample(pop, tourn_size)
        selected.append(max(tourn, key=lambda x: x.fitness))
    return selected


