import time

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

def file_observer(population, num_generations, num_fun_evals, args):
    try:
        observer_file = args['observer_file']
    except KeyError:
        filename = 'ecspy_observer_file-' + str(time.time())
        observer_file = open(filename, 'w')
        args['observer_file'] = observer_file

    observer_file.write('Generation Number: %d \n' % num_generations)
    observer_file.write('Function Evaluations: %d \n' % num_fun_evals)
    avg_fit = sum([x.fitness for x in population]) / float(len(population))
    observer_file.write('Average Fitness: %0.2f \n' % avg_fit)
    for ind in population:
        observer_file.write(str(ind) + '\n')
    observer_file.write('\n')