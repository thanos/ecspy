
def default_observer(population, num_generations, num_fun_evals, args):
    pass
    
    
def screen_observer(population, num_generations, num_fun_evals, args):
    print('Generation Number: %d' % num_generations)
    print('Function Evaluations: %d' % num_fun_evals)
    avg_fit = sum([x.fitness for x in population]) / float(len(population))
    print('Average Fitness: %0.2f' % avg_fit)
    for ind in population:
        print(str(ind))
    print('')

