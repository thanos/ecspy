from itertools import izip


def default_variation(random, candidates, args):
    return candidates


def n_point_crossover(random, candidates, args):
    try:
        crossover_rate = args['crossover_rate']
    except KeyError:
        crossover_rate = 1.0
        args['crossover_rate'] = crossover_rate
    try:
        num_crossover_points = args['num_crossover_points']
    except KeyError:
        num_crossover_points = 1
        args['num_crossover_points'] = num_crossover_points
    cand = list(candidates)
    if len(cand) % 2 == 1:
        cand = cand[:-1]
    random.shuffle(cand)
    moms = cand[::2]
    dads = cand[1::2]
    children = []
    for mom, dad in izip(moms, dads):
        if random.random() < crossover_rate:
            bro = list(mom)
            sis = list(dad)
            num_cuts = min(len(mom)-1, num_crossover_points)
            cut_points = random.sample(range(1, len(mom)), num_cuts)
            cut_points.sort()
            for p in cut_points:
                bro[p:] = dad[p:]
                sis[:p] = mom[:p]
            children.append(bro)
            children.append(sis)
        else:
            children.append(mom)
            children.append(dad)            
    return children


def uniform_crossover(random, candidates, args):
    try:
        pux_bias = args['pux_bias']
    except KeyError:
        pux_bias = 0.5
        args['pux_bias'] = pux_bias
    try:
        crossover_rate = args['crossover_rate']
    except KeyError:
        crossover_rate = 1.0
        args['crossover_rate'] = crossover_rate
    cand = list(candidates)
    if len(cand) % 2 == 1:
        cand = cand[:-1]
    random.shuffle(cand)
    moms = cand[::2]
    dads = cand[1::2]
    children = []
    for mom, dad in izip(moms, dads):
        if random.random() < crossover_rate:
            bro = []
            sis = []
            for m, d in izip(mom, dad):
                if random.random() < pux_bias:
                    bro.append(m)
                    sis.append(d)
                else:
                    bro.append(d)
                    sis.append(m)
            children.append(bro)
            children.append(sis)
        else:
            children.append(mom)
            children.append(dad)
    return children

    
def blend_crossover(random, candidates, args):
    try:
        blx_alpha = args['blx_alpha']
    except KeyError:
        blx_alpha = 0.1
    try:
        crossover_rate = args['crossover_rate']
    except KeyError:
        crossover_rate = 1.0
    try:
        lower_bound = args['lower_bound']
    except KeyError:
        lower_bound = 0
    try:
        upper_bound = args['upper_bound']
    except KeyError:
        upper_bound = 1
    cand = list(candidates)
    if len(cand) % 2 == 1:
        cand = cand[:-1]
    random.shuffle(cand)
    moms = cand[::2]
    dads = cand[1::2]
    children = []
    for mom, dad in izip(moms, dads):
        if random.random() < crossover_rate:
            child = []
            for m, d in izip(mom, dad):
                smallest = min(m, d)
                largest = max(m, d)
                delta = blx_alpha * (largest - smallest)
                value = smallest - delta + random.random() * (largest - smallest + 2 * delta)
                value = max(min(value, upper_bound), lower_bound)
                child.append(value)
            children.append(child)
        else:
            children.append(random.sample([mom, dad], 1))
    return children

    

def gaussian_mutation(random, candidates, args):
    try:
        mut_rate = args['mutation_rate']
    except KeyError:
        mut_rate = 0.1
        args['mutation_rate'] = mut_rate
    try:
        lower_bound = args['lower_bound']
    except KeyError:
        lower_bound = 0
        args['lower_bound'] = lower_bound
    try:
        upper_bound = args['upper_bound']
    except KeyError:
        upper_bound = 1
        args['upper_bound'] = upper_bound
        
    cs_copy = list(candidates)
    for i, cs in enumerate(cs_copy):
        for j, c in enumerate(cs):
            c += random.gauss(0, mut_rate) * (upper_bound - lower_bound)
            c = max(min(c, upper_bound), lower_bound)
            cs_copy[i][j] = c
    return cs_copy


def bit_flip_mutation(random, candidates, args):
    try:
        rate = args['mutation_rate']
    except KeyError:
        rate = 0.1
        args['mutation_rate'] = rate
    cs_copy = list(candidates)
    for i, cs in enumerate(cs_copy):
        if len(cs) == len([x for x in cs if x in [0, 1]]):
            for j, c in enumerate(cs):
                if random.random() < rate:
                    cs_copy[i][j] = (c + 1) % 2
    return cs_copy
