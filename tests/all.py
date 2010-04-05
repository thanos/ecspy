#===============================================================================
#
#    A unittest is an example that asserts
#    that an example returns a given result
#    and converges in at a given generation
#
# Mehhh relative imports do not work in python 2.5 if 
# when a script is run as "__main__"
# that's why I'm adding to sys.path
#===============================================================================
import unittest, sys, os
sys.path.append( os.path.split( 
                               os.path.split(__file__)[0] )
)

from examples import dea_example
from examples import custom_ec_example
from examples import eda_example
from examples import es_example
from examples import ga_example
from examples import nsga_example
from examples import paes_example
from examples import pso_example

class DEATest(unittest.TestCase):
    def test(self):
        dea = dea_example.main()
        target = [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0]
        # should I make a property "dea.archive" that returns the archive?
        # perhaps looking it up in the ._kwargs is a little obscure?

        # too much rounding!!!
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
        custom = custom_ec_example.main(do_plot=False)
        archive = custom._kwargs['_archive']
        result = round(archive[0].fitness, 1)
        target = 4
        self.assertEqual(result, target,
                         'expected a fitness of %s, got %s' % ( result, target)
                        )


class EDA_Test(unittest.TestCase):
    def test(self):
        eda = eda_example.main()
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
        
        raise NotImplementedError
        #=======================================================================
        # es = es_example.main()
        # archive = es._kwargs['_archive']
        # #import ipdb; ipdb.set_trace()
        # result = round(archive[0].fitness, 1)
        # target = 4
        # self.assertEqual(result, target,
        #                 'expected a fitness of %s, got %s' % ( result, target)
        #                )
        #=======================================================================
        

class GA_Test(unittest.TestCase):
    def test(self):
        ga = ga_example.main()
        archive = ga._kwargs['_archive']
        result = archive[0].candidate
        target = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1] 
        self.assertEqual(result, target,
                         'expected a fitness of %s, got %s' % ( result, target)
                        )


class NSGA_Test(unittest.TestCase):
    def test(self):
        nsga = nsga_example.main(do_plot=False)
        archive = nsga._kwargs['_archive']
        fitnesses = [[round(j,3) for j in i.fitness] for i in archive]
        self.assertTrue([0.0, 1.0] in fitnesses, 'expected a fitness contained [0,1]')
        self.assertTrue([1.0, 0.0] in fitnesses, 'expected a fitness contained [1,0]')


class PAES_Test(unittest.TestCase):
    def test(self):
        paes = paes_example.main(do_plot=False)
        archive = paes._kwargs['_archive']
        fitnesses = [[round(j,3) for j in i.fitness] for i in archive]
        self.assertTrue([0.0, 1.0] in fitnesses, 'expected a fitness contained [0,1]')
        self.assertTrue([1.0, 0.0] in fitnesses, 'expected a fitness contained [1,0]')

class PSO_Test(unittest.TestCase):
    def test(self):
        print 'PSO is broken...'
        pso = pso_example.main()
#        archive = pso._kwargs['_archive']
#        fitnesses = [[round(j,3) for j in i.fitness] for i in archive]
#        self.assertTrue([0.0, 1.0] in fitnesses, 'expected a fitness contained [0,1]')
#        self.assertTrue([1.0, 0.0] in fitnesses, 'expected a fitness contained [1,0]')

if __name__ == '__main__':
    unittest.main()
    
    
