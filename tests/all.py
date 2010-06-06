#===============================================================================
#
#    A unittest is an example that asserts
#    that an example returns a given result
#    and converges in at a given generation
#    
#    TODO:
#    *   too much rounding going on in DEA_Test
#    *   too much rounding going on in EDA_Test
#    *   no guarantee that all test will converge in due time
#    so expect false alarms, best to run the test 2 or 3 times
#    before committing changes made to SVN. its a delicate balance between
#    testing speed and the change of all tests converging. 
#
#
# Mehhh relative imports do not work in python 2.5 if 
# when a script is run as "__main__"
# that's why I'm adding to sys.path
#===============================================================================
import unittest, sys, os, random
pth = os.path.split( os.path.split( os.path.abspath(__file__) )[0] )[0] 
sys.path.append( pth )

from examples import dea_example
from examples import custom_ec_example
from examples import eda_example
from examples import es_example
from examples import ga_example
from examples import nsga_example
from examples import nsga_example_sch
from examples import paes_example
from examples import pso_example

prng = random.Random()
prng.seed(1000) 


class DEA_Test(unittest.TestCase):
    def test(self):
        dea = dea_example.main(prng=prng)
        target = [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0]
        # should I make a property "dea.archive" that returns the archive?
        # perhaps looking it up in the ._kwargs is a little obscure?

        result = [round(i.fitness, 0) for i in dea._kwargs['_archive']]
        
        self.assertEqual(result, target,
                         'expected %s as a result, got %s' % ( target, result )
                         )
        result = dea._kwargs['_num_generations']
        target = 2495
        
        if result < target:
            print 'dea_example converged earlier than expected... something got better!'
        else:
            self.assertEqual( result, target,
                             'expected to converge in %s generations, but converged in %s ' % (target, result)
                             )


class Custom_EC_Test(unittest.TestCase):
    def test(self):
        custom = custom_ec_example.main(do_plot=False,prng=prng)
        archive = custom._kwargs['_archive']
        result = round(archive[0].fitness, 1)
        target = 4
        self.assertEqual(result, target,
                         'expected a fitness of %s, got %s' % ( result, target)
                        )


class EDA_Test(unittest.TestCase):
    def test(self):
        eda = eda_example.main(prng=prng)
        archive = eda._kwargs['_archive']
        # too much rounding!!!
        result = round(archive[0].fitness, 0)
        target = 4
        self.assertEqual(result, target,
                         'expected a fitness of %s, got %s' % ( result, target)
                        )

class ES_Test(unittest.TestCase):
    def test(self):
        
        try:
            import pp
        except ImportError:
            self.fail('evolutionary strategies example requires the parallel python module')
        
        if sys.version_info[1] < 6:
            self.fail('evolutionary strategies example requires python >= 2.6')
        
        es = es_example.main(prng=prng)
        archive = es._kwargs['_archive']
        self.assertTrue( all([i.fitness==4 for i in archive]), 'not all archive fitness equal to 4' )
        

class GA_Test(unittest.TestCase):
    def test(self):
        ga = ga_example.main(prng=prng)
        archive = ga._kwargs['_archive']
        result = archive[0].candidate
        target = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1] 
        self.assertEqual(result, target,
                         'expected a fitness of %s, got %s' % ( target, result )
                        )

class NSGA_Test(unittest.TestCase):
    def test(self):
        nsga = nsga_example.main(do_plot=False,prng=prng)
        archive = nsga._kwargs['_archive']
        fitnesses = [[round(j,3) for j in i.fitness] for i in archive]
        self.assertTrue([0.0, 1.0] in fitnesses, 'expected a fitness contained [0,1]')
        self.assertTrue([1.0, 0.0] in fitnesses, 'expected a fitness contained [1,0]')


class NSGA_SCH_Test(unittest.TestCase):
    def test(self):
        nsga = nsga_example_sch.main(do_plot=False,prng=prng)
        archive = nsga._kwargs['_archive']
        fitnesses = [[round(j,1) for j in i.fitness] for i in archive]
        self.assertTrue([0.0,4.0] in fitnesses or [4.0, 0.0] in fitnesses, 'expected a fitness of either 0.0 or 4.0')
        self.assertTrue(nsga._kwargs['_num_generations']<=20, 'expected to converge in 20 generations')

class PAES_Test(unittest.TestCase):
    def test(self):
        paes = paes_example.main(do_plot=False,prng=prng)
        archive = paes._kwargs['_archive']
        fitnesses = [[round(j,1) for j in i.fitness] for i in archive]
        self.assertTrue([0.0, 1.0] in fitnesses, 'expected a fitness contained [0,1]')
        self.assertTrue([1.0, 0.0] in fitnesses, 'expected a fitness contained [1,0]')

class PSO_Test(unittest.TestCase):
    def test(self):
        pso = pso_example.main(prng=prng)
        archive = pso._kwargs['_archive']
        fitnesses = [i.fitness for i in archive]
        self.assertTrue(6.0 in fitnesses, 'expected a fitness to be 6.0')

if __name__ == '__main__':
    unittest.main()
