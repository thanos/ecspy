import time

def default_observer(population, num_generations, num_fun_evals, args):
    """Do nothing."""    
    pass
    
    
def screen_observer(population, num_generations, num_fun_evals, args):
    """Print the output of the EC to the screen.
    
    This function displays the results of the evolutionary computation
    to the screen. The output includes the generation number, the current
    number of function evaluations, the average fitness, the maximum
    fitness, and the full population.
    Arguments:
    population -- the population of Individuals
    num_generations -- the number of elapsed generations
    num_fun_evals -- the number of of used function evaluations
    args -- a dictionary of keyword arguments
    
    """
    print('Generation Number: %d' % num_generations)
    print('Function Evaluations: %d' % num_fun_evals)
    avg_fit = sum([x.fitness for x in population]) / float(len(population))
    print('Average Fitness: %0.5f     Maximum Fitness: %0.5f' % (avg_fit, population[0].fitness))
    for ind in population:
        print(str(ind))
    print('')

    
def file_observer(population, num_generations, num_fun_evals, args):
    """Print the output of the EC to a file.
    
    This function saves the results of the evolutionary computation
    to a file. The output includes the generation number, the current
    number of function evaluations, the average fitness, the maximum
    fitness, and the full population. The default action for the file
    is to create a new file called 'ecspy_observer_file-<timestamp>'
    in which to write the information.
    Arguments:
    population -- the population of Individuals
    num_generations -- the number of elapsed generations
    num_fun_evals -- the number of of used function evaluations
    args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    observer_file -- a file object (default see text)
    
    """
    try:
        observer_file = args['observer_file']
    except KeyError:
        filename = 'ecspy_observer_file-' + str(time.time())
        observer_file = open(filename, 'w')
        args['observer_file'] = observer_file

    observer_file.write('Generation Number: %d \n' % num_generations)
    observer_file.write('Function Evaluations: %d \n' % num_fun_evals)
    avg_fit = sum([x.fitness for x in population]) / float(len(population))
    observer_file.write('Average Fitness: %0.5f     Maximum Fitness: %0.5f' % (avg_fit, population[0].fitness))
    for ind in population:
        observer_file.write(str(ind) + '\n')
    observer_file.write('\n')