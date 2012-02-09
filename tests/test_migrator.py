import ecspy
import random
import multiprocessing

def test_process(random, population, migrator, output_queue):
    for i in range(9999):
        population = migrator(random, population, {})
    output_queue.put(population)
    
    
if __name__ == '__main__':
    rand = random.Random()
    rand.seed(1234)
    queue = multiprocessing.Queue()
    migrator = ecspy.migrators.MultiprocessingMigrator()
    populations = [["red", "orange", "yellow", "green", "blue", "indigo", "violet"],
                   [1, 2, 3, 4, 5, 6, 7],
                   ["bashful", "doc", "dopey", "grumpy", "happy", "sleepy", "sneezy"]]
    
    jobs = []
    for pop in populations:
        p = multiprocessing.Process(target=test_process, args=(rand, pop, migrator, queue))
        p.start()
        jobs.append(p)
    for j in jobs:
        j.join()    
        
    final_pops = []
    while queue.qsize() > 0:
        final_pops.append(set(queue.get()))
    for p in final_pops:
        a = p & set(populations[0])
        b = p & set(populations[1])
        c = p & set(populations[2])
        print(a)
        print(b)
        print(c)
        if len(a) > 0 and len(b) > 0 and len(c) > 0:
            print("overlap among all pops")
    