import math

class approximate(object):
    def __init__(self, alpha=0.75, beta=1, gamma=1, max_granules=200):
        self.granules = []
        self.threshold = float('infinity')
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.max_granules = max_granules
        
    def _add_granule(self, candidate, fitness):
        if len(self.granules) >= self.max_granules:
            self.granules.remove(min(self.granules, key=lambda x: x[3]))
        self.granules.append([candidate, fitness, self.gamma * 1.0 / (math.exp(fitness)**self.beta), 1])
    
    def _membership(self, x, center, spread):
        return math.exp(-(x - center)**2 / spread**2)
    
    def __call__(self, f):
        def approximate_f(candidates, args):
            fitness = []
            for candidate in candidates:
                if len(self.granules) == 0:
                    val = f([candidate], args)[0]
                    self._add_granule(candidate, val)
                    fitness.append(val)
                else:
                    similarity = []
                    for granule in self.granules:
                        similarity.append(sum([self._membership(x, c, granule[2]) / float(len(granule[0])) for x, c in zip(candidate, granule[0])]))
                    m = max(similarity)
                    if m > self.threshold:
                        sim_index = similarity.index(m)
                        self.granules[sim_index][3] += 1
                        fitness.append(self.granules[sim_index][1])
                    else:
                        val = f([candidate], args)[0]
                        self._add_granule(candidate, val)
                        fitness.append(val)
            avg_fit = sum(fitness) / float(len(fitness))
            self.threshold = self.alpha * max(fitness) / avg_fit
            return fitness
        return approximate_f

    def __repr__(self):
        return self.func.__doc__


        

if __name__ == '__main__':
    import random
    import math
    import time
    from ecspy import ec
    from ecspy import observers
    from ecspy import terminators


    def rastrigin_generator(random, args):
        return [random.uniform(-5.12, 5.12) for _ in range(20)]

    @approximate(alpha=0.75, beta=0.004, gamma=0.15)
    def rastrigin_evaluator(candidates, args):
        fitness = []
        for cand in candidates:
            fitness.append(10 * len(cand) + sum([x**2 - 10 * (math.cos(2*math.pi*x)) for x in cand]))
        return fitness
        
    prng = random.Random()
    prng.seed(time.time())
    es = ec.ES(prng)
    #es.observer = observers.screen_observer
    es.terminator = terminators.evaluation_termination
    final_pop = es.evolve(rastrigin_generator, rastrigin_evaluator, pop_size=20, maximize=False, 
                          max_evaluations=5000, lower_bound=-5.12, upper_bound=5.12)

    for p in final_pop:
        print p
