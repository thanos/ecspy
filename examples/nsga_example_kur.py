import random, time, math

from ecspy import emo, ec
from ecspy import selectors
from ecspy import variators
from ecspy import observers
from ecspy import terminators
from ecspy.contrib.utils import round_fitness

def generate_candidate(random, args):
    try:
        lower_bound = args['lower_bound']
    except KeyError:
        lower_bound = 0
    try:
        upper_bound = args['upper_bound']
    except KeyError:
        upper_bound = 1
    return [random.random() * (upper_bound - lower_bound) + lower_bound for i in range(2)]

def evaluate_sch(candidates, args):
    
    def kur1(cs):
        result = 0.
        for i in range(len(cs)-1):
            xi = math.pow(cs[i], 2.0) 
            xj = math.pow(cs[i]+1., 2.0)
            aux = -0.2 * math.sqrt((xi+xj))
            result += -10. * math.exp(aux)
        return result  

    def kur2(cs):
        result = 0.
        for i in range(len(cs)):
            xi = cs[i] 
            result += math.pow(abs(xi), 0.8) + (5.0 * math.sin(math.pow(xi, 3.0)))
        return result  
    
    maximize = args['maximize']
    fitness = []
    for cs in candidates:
        x = kur1(cs)
        y = kur2(cs) 
#        x = cs[0]**2
#        y = (cs[0]-2)**2 
        fitness.append(emo.Pareto(maximize, [x, y]))
    return fitness

def converged_kur(population, num_generations, num_evaluations, args):
    if num_generations == 20:
        return True
    #pop = round_fitness(population, 1)
    #return [0.0, 4.0] in pop

def my_observer(population, num_generations, num_evaluations, args):
    try:
        archive = args['_archive']
    except KeyError:
        archive = []
    
    x = []
    y = []
    print('----------------------------')
    print('Gens: %d   Evals: %d' % (num_generations, num_evaluations))
    print('-----------')
    print('Population:')
    for p in population:
        print(p)
    print('-----------')
    print('Archive:')
    for a in archive:
        print(a)
    print('-----------')
    
   
def main(do_plot=True, prng=None):
    if prng is None:
        prng = random.Random()
        prng.seed(time.time()) 

    nsga = emo.NSGA2(prng)
    nsga.variator = [variators.gaussian_mutation, variators.blend_crossover]
    nsga.observer = my_observer
    final_arc = nsga.evolve(maximize=False,
                            generator=generate_candidate, 
                            evaluator=evaluate_sch, 
                            pop_size=100,
                            terminator=[terminators.evaluation_termination,converged_kur], 
                            max_evaluations=1e6,
                            lower_bound=-5.,
                            upper_bound= 5.,
                            )
    
    print('*******************************')
    if do_plot:
        import pylab
        x = []
        y = []
        for f in final_arc[1:]:
            print(f)
#             filter out left over values in the archive...
#            a,b = abs(f.fitness[0]), abs(f.fitness[1])
#            if a>4 or b>4:
#                continue 
            
            x.append(f.fitness[0])
            y.append(f.fitness[1])
            
        pylab.scatter(x, y, color='b')
        pylab.show()
        #pylab.savefig('nsga2-front.pdf', format='pdf')
    return nsga
        
if __name__ == '__main__':
    main()    
