#import psyco; psyco.full()
import unittest, sys, os, random
pth = os.path.split( os.path.split( os.path.abspath(__file__) )[0] )[0] 
sys.path.append( pth )

from examples import custom_ec_example
from examples import dea_example
from examples import eda_example
from examples import es_example
from examples import ga_example
from examples import niche_example
from examples import nsga_example
from examples import paes_example
from examples import pso_example
from examples import sa_example

prng = random.Random()
prng.seed(12345) 

class Custom_EC_Test(unittest.TestCase):
    def test(self):
        ea = custom_ec_example.main(do_plot=False, prng=prng)
        best = max(ea.population)
        assert best.fitness < 0.19

class DEA_Test(unittest.TestCase):
    def test(self):
        dea = dea_example.main(do_plot=False, prng=prng)
        best = max(dea.population)
        assert best.fitness < 0.3

class EDA_Test(unittest.TestCase):
    def test(self):
        eda = eda_example.main(do_plot=False, prng=prng)
        best = max(eda.population)
        assert 79 < best.fitness < 82

class ES_Test(unittest.TestCase):
    def test(self):
        es = es_example.main(do_plot=False, prng=prng)
        best = max(es.population)
        assert best.fitness < 0.02

class GA_Test(unittest.TestCase):
    def test(self):
        ga = ga_example.main(do_plot=False, prng=prng)
        best = max(ga.population)
        assert best.fitness < 0.004
        
class NSGA_Test(unittest.TestCase):
    def test(self):
        nsga = nsga_example.main(do_plot=False, prng=prng)
        fitnesses = [a.fitness for a in nsga.archive]
        assert all([(-21 < f[0] < -12) and (-12 < f[1] < 1) for f in fitnesses])

class PAES_Test(unittest.TestCase):
    def test(self):
        paes = paes_example.main(do_plot=False, prng=prng)
        fitnesses = [a.fitness for a in paes.archive]
        assert all([(-21 < f[0] < -12) and (-12 < f[1] < 1) for f in fitnesses])

class PSO_Test(unittest.TestCase):
    def test(self):
        pso = pso_example.main(do_plot=False, prng=prng)
        best = max(pso.population)
        assert best.fitness < 2

class Niche_Test(unittest.TestCase):
    def test(self):
        ea = niche_example.main(do_plot=False, prng=prng)
        candidates = [p.candidate[0] for p in ea.population]
        self.assertTrue(any(map(lambda x: 1 < x < 2, candidates)), 'expected a solution in [1, 2]')
        self.assertTrue(any(map(lambda x: 7 < x < 8, candidates)), 'expected a solution in [7, 8]')
        self.assertTrue(any(map(lambda x: 14 < x < 15, candidates)), 'expected a solution in [14, 15]')
        self.assertTrue(any(map(lambda x: 20 < x < 21, candidates)), 'expected a solution in [20, 21]')
        

if __name__ == '__main__':
    unittest.main()
