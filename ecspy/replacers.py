
def default_replacement(random, population, parents, offspring, args):
    return offspring

    
def truncation_replacement(random, population, parents, offspring, args):
    pool = list(population)
    pool.extend(list(offspring))
    pool.sort(key=lambda x: x.fitness, reverse=True)
    return pool[:len(population)]

    
def steady_state_replacement(random, population, parents, offspring, args):    
    off = list(offspring)
    pop = list(population)
    pop.sort(key=lambda x: x.fitness)
    num_to_replace = min(len(off), len(pop))
    pop[:num_to_replace] = off[:num_to_replace]
    return pop


def generational_replacement(random, population, parents, offspring, args):
    try:
        num_elites = args['num_elites']
    except KeyError:
        num_elites = 0
        args['num_elites'] = num_elites
    off = list(offspring)
    pop = list(population)
    pop.sort(key=lambda x: x.fitness, reverse=True)
    off.extend(pop[:num_elites])
    off.sort(key=lambda x: x.fitness, reverse=True)
    survivors = off[:len(population)]
    return survivors


def random_replacement(random, population, parents, offspring, args):
    try:
        num_elites = args['num_elites']
    except KeyError:
        num_elites = 0
        args['num_elites'] = num_elites
    off = list(offspring)
    pop = list(population)
    pop.sort(key=lambda x: x.fitness, reverse=True)
    num_to_replace = min(len(off), len(pop) - num_elites) 
    valid_indices = range(num_elites, len(pop))
    rep_index = random.sample(valid_indices, num_to_replace)
    for i in xrange(len(off)):
        pop[rep_index[i]] = off[i]
    return pop


def plus_replacement(random, population, parents, offspring, args):
    try:
        use_one_fifth_rule = args['use_one_fifth_rule']
    except KeyError:
        use_one_fifth = False
        args['use_one_fifth_rule'] = use_one_fifth_rule
    pool = list(parents)
    pool.extend(list(offspring))
    pool.sort(key=lambda x: x.fitness, reverse=True)
    survivors = pool[:len(population)]
    if use_one_fifth_rule:
        count = len([x for x in offspring if x in survivors])
        rate = count / float(len(offspring))
        if rate < 0.2:
            try:
                args['mutation_rate'] = args['mutation_rate'] * 0.8
            except KeyError:
                args['use_one_fifth_rule'] = False
        elif rate > 0.2:
            try:
                args['mutation_rate'] = args['mutation_rate'] * 1.2
            except KeyError:
                args['use_one_fifth_rule'] = False            
    return survivors


def comma_replacement(random, population, parents, offspring, args):
    pool = list(offspring)
    pool.sort(key=lambda x: x.fitness, reverse=True)
    survivors = pool[:len(population)]
    return survivors
