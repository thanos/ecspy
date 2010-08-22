
import math
import random
from ecspy import ec
from ecspy import emo


class Benchmark(object):
    def __init__(self, dimensions, objectives=1):
        self.dimensions = dimensions
        self.objectives = objectives
        self.bounder = None
        self.maximize = True
        
    def __str__(self):
        if self.objectives > 1:
            return '%s (%d dimensions, %d objectives)' % (self.__class__.__name__, self.dimensions, self.objectives)
        else:
            return '%s (%d dimensions)' % (self.__class__.__name__, self.dimensions)
        
    def __repr__(self):
        return '%s' % self.__class__.__name__
    
    def generator(self, random, args):
        raise NotImplementedError
        
    def evaluator(self, candidates, args):
        raise NotImplementedError
        
    def __call__(self, *args):
        candidate = [a for a in args]
        fit = self.evaluator([candidate], {})
        return fit[0]

class Binary(Benchmark):
    def __init__(self, benchmark, dimension_bits):
        Benchmark.__init__(self, benchmark.dimensions, benchmark.objectives)
        self.benchmark = benchmark
        self.dimension_bits = dimension_bits
        self.bounder = self.benchmark.bounder
        self.maximize = self.benchmark.maximize
        self.__class__.__name__ = self.__class__.__name__ + ' ' + self.benchmark.__class__.__name__
        
    def binary_to_real(self, binary):
        real = []
        for d, lo, hi in zip(range(self.dimensions), self.bounder.lower_bound, self.bounder.upper_bound):
            b = binary[d*self.dimension_bits:(d+1)*self.dimension_bits]
            real_val = float(int(''.join([str(i) for i in b]), 2))
            value = real_val / (2**(self.dimension_bits)-1) * (hi - lo) + lo
            real.append(value)
        return real
    
    def generator(self, random, args):
        return [random.choice([0, 1]) for _ in range(self.dimensions * self.dimension_bits)]
        
    def evaluator(self, candidates, args):
        binary_candidates = []
        for c in candidates:
            binary_candidates.append(self.binary_to_real(c))
        return self.benchmark.evaluator(binary_candidates, args)

        
        
#------------------------------------------------------
#             Single-objective problems
#------------------------------------------------------

class Ackley(Benchmark):
    def __init__(self, dimensions=2):
        Benchmark.__init__(self, dimensions)
        self.bounder = ec.Bounder([-32.0] * self.dimensions, [32.0] * self.dimensions)
        self.maximize = False
        self.global_optimum = [0 for _ in range(self.dimensions)]
    
    def generator(self, random, args):
        return [random.uniform(-32.0, 32.0) for _ in range(self.dimensions)]
        
    def evaluator(self, candidates, args):
        fitness = []
        for c in candidates:
            fitness.append(-20 * math.exp(-0.2 * math.sqrt(1.0 / self.dimensions * sum([x**2 for x in c]))) - 
                           math.exp(1.0 / self.dimensions * sum([math.cos(2 * math.pi * x) for x in c])) + 20 + math.e)
        return fitness

class Griewank(Benchmark):
    def __init__(self, dimensions=2):
        Benchmark.__init__(self, dimensions)
        self.bounder = ec.Bounder([-100.0] * self.dimensions, [100.0] * self.dimensions)
        self.maximize = False
        self.global_optimum = [0 for _ in range(self.dimensions)]
        
    def generator(self, random, args):
        return [random.uniform(-100.0, 100.0) for _ in range(self.dimensions)]
        
    def evaluator(self, candidates, args):
        fitness = []
        for c in candidates:
            fitness.append(1.0 / 4000.0 * sum([x**2 for x in c]) - 
                           reduce(lambda x, y: x*y, [math.cos(x / math.sqrt(i+1)) for i, x in enumerate(c)]) + 1)
        return fitness

class Rastrigin(Benchmark):
    def __init__(self, dimensions=2):
        Benchmark.__init__(self, dimensions)
        self.bounder = ec.Bounder([-5.0] * self.dimensions, [5.0] * self.dimensions)
        self.maximize = False
        self.global_optimum = [0 for _ in range(self.dimensions)]
        
    def generator(self, random, args):
        return [random.uniform(-5.0, 5.0) for _ in range(self.dimensions)]
        
    def evaluator(self, candidates, args):
        fitness = []
        for c in candidates:
            fitness.append(sum([x**2 - 10 * math.cos(2 * math.pi * x) + 10 for x in c]))
        return fitness

class Rosenbrock(Benchmark):
    def __init__(self, dimensions=2):
        Benchmark.__init__(self, dimensions)
        self.bounder = ec.Bounder([-100.0] * self.dimensions, [100.0] * self.dimensions)
        self.maximize = False
        self.global_optimum = [1 for _ in range(self.dimensions)]
    
    def generator(self, random, args):
        return [random.uniform(-100.0, 100.0) for _ in range(self.dimensions)]
        
    def evaluator(self, candidates, args):
        fitness = []
        for c in candidates:
            total = 0
            for i in range(len(c) - 1):
                total += 100 * (c[i]**2 - c[i+1])**2 + (c[i] - 1)**2
            fitness.append(total)
        return fitness
    
class Schwefel(Benchmark):
    def __init__(self, dimensions=2):
        Benchmark.__init__(self, dimensions)
        self.bounder = ec.Bounder([-500.0] * self.dimensions, [500.0] * self.dimensions)
        self.maximize = False
        self.global_optimum = [420.9687 for _ in range(self.dimensions)]
    
    def generator(self, random, args):
        return [random.uniform(-500.0, 500.0) for _ in range(self.dimensions)]
        
    def evaluator(self, candidates, args):
        fitness = []
        for c in candidates:
            fitness.append(418.9829 * self.dimensions - sum([x * math.sin(math.sqrt(abs(x))) for x in c]))
        return fitness
    
class Sphere(Benchmark):
    def __init__(self, dimensions=2):
        Benchmark.__init__(self, dimensions)
        self.bounder = ec.Bounder([-100.0] * self.dimensions, [100.0] * self.dimensions)
        self.maximize = False
        self.global_optimum = [0 for _ in range(self.dimensions)]
    
    def generator(self, random, args):
        return [random.uniform(-100.0, 100.0) for _ in range(self.dimensions)]
        
    def evaluator(self, candidates, args):
        fitness = []
        for c in candidates:
            fitness.append(sum([x**2 for x in c]))
        return fitness
    
class Weierstrass(Benchmark):
    def __init__(self, dimensions=2, a=0.5, b=3, kmax=20):
        Benchmark.__init__(self, dimensions)
        self.bounder = ec.Bounder([-0.5] * self.dimensions, [0.5] * self.dimensions)
        self.maximize = False
        self.a = a
        self.b = b
        self.kmax = kmax
        self.global_optimum = None
    
    def generator(self, random, args):
        return [random.uniform(-0.5, 0.5) for _ in range(self.dimensions)]
        
    def evaluator(self, candidates, args):
        fitness = []
        for c in candidates:
            fitness.append(sum([sum([self.a**k * math.cos(2 * math.pi * self.b**k * (x + 0.5)) for k in range(self.kmax)]) for x in c]) -
                           self.dimensions * sum([self.a**k + math.cos(math.pi * self.b**k) for k in range(self.kmax)]))
        return fitness


        
#------------------------------------------------------
#              Multi-objective problems
#------------------------------------------------------

class Kursawe(Benchmark):
    def __init__(self, dimensions=2):
        Benchmark.__init__(self, dimensions, 2)
        self.bounder = ec.Bounder([-5.0] * self.dimensions, [5.0] * self.dimensions)
        self.maximize = False

    def generator(self, random, args):
        return [random.uniform(-5.0, 5.0) for _ in range(self.dimensions)]
        
    def evaluator(self, candidates, args):
        fitness = []
        for c in candidates:
            f1 = sum([-10 * math.exp(-0.2 * math.sqrt(c[i]**2 + c[i+1]**2)) for i in range(len(c) - 1)])
            f2 = sum([math.pow(abs(x), 0.8) + 5 * math.sin(x**3) for x in c])
            fitness.append(emo.Pareto([f1, f2]))
        return fitness

class DTLZ1(Benchmark):
    def __init__(self, dimensions=2, objectives=2):
        Benchmark.__init__(self, dimensions, objectives)
        if dimensions < objectives:
            raise ValueError('dimensions (%d) must be greater than or equal to objectives (%d)' % (dimensions, objectives))
        self.bounder = ec.Bounder([0.0] * self.dimensions, [1.0] * self.dimensions)
        self.maximize = False
        
    def global_optimum(self):
        x = [random.uniform(0, 1) for _ in range(self.objectives - 1)]
        x.extend([0 for _ in range(self.dimensions - self.objectives + 1)])
        return x
    
    def generator(self, random, args):
        return [random.uniform(0.0, 1.0) for _ in range(self.dimensions)]
        
    def evaluator(self, candidates, args):
        fitness = []
        g = lambda x: 100 * (len(x) + sum([(a - 0.5)**2 - math.cos(20 * math.pi * (a - 0.5)) for a in x]))
        for c in candidates:
            gval = g(c[self.objectives-1:])
            fit = [0.5 * reduce(lambda x,y: x*y, c[:self.objectives-1]) * (1 + gval)]
            for m in reversed(range(1, self.objectives)):
                fit.append(0.5 * reduce(lambda x,y: x*y, c[:m-1], 1) * (1 - c[m-1]) * (1 + gval))
            fitness.append(emo.Pareto(fit))
        return fitness

class DTLZ2(Benchmark):
    def __init__(self, dimensions=2, objectives=2):
        Benchmark.__init__(self, dimensions, objectives)
        if dimensions < objectives:
            raise ValueError('dimensions (%d) must be greater than or equal to objectives (%d)' % (dimensions, objectives))
        self.bounder = ec.Bounder([0.0] * self.dimensions, [1.0] * self.dimensions)
        self.maximize = False
    
    def global_optimum(self):
        x = [random.uniform(0, 1) for _ in range(self.objectives - 1)]
        x.extend([0.5 for _ in range(self.dimensions - self.objectives + 1)])
        return x
    
    def generator(self, random, args):
        return [random.uniform(0.0, 1.0) for _ in range(self.dimensions)]
        
    def evaluator(self, candidates, args):
        fitness = []
        g = lambda x: sum([(a - 0.5)**2 for a in x])
        for c in candidates:
            gval = g(c[self.objectives-1:])
            fit = [(1 + gval) * 
                   reduce(lambda x,y: x*y, [math.cos(a * math.pi / 2.0) for a in c[:self.objectives-1]])]
            for m in reversed(range(1, self.objectives)):
                fit.append((1 + gval) * 
                           reduce(lambda x,y: x*y, [math.cos(a * math.pi / 2.0) for a in c[:m-1]], 1) *
                           math.sin(c[m-1] * math.pi / 2.0))
            fitness.append(emo.Pareto(fit))
        return fitness

class DTLZ3(Benchmark):
    def __init__(self, dimensions=2, objectives=2):
        Benchmark.__init__(self, dimensions, objectives)
        if dimensions < objectives:
            raise ValueError('dimensions (%d) must be greater than or equal to objectives (%d)' % (dimensions, objectives))
        self.bounder = ec.Bounder([0.0] * self.dimensions, [1.0] * self.dimensions)
        self.maximize = False
    
    def global_optimum(self):
        x = [random.uniform(0, 1) for _ in range(self.objectives - 1)]
        x.extend([0.5 for _ in range(self.dimensions - self.objectives + 1)])
        return x
        
    def generator(self, random, args):
        return [random.uniform(0.0, 1.0) for _ in range(self.dimensions)]
        
    def evaluator(self, candidates, args):
        fitness = []
        g = lambda x: 100 * (len(x) + sum([(a - 0.5)**2 - math.cos(20 * math.pi * (a - 0.5)) for a in x]))
        for c in candidates:
            gval = g(c[self.objectives-1:])
            fit = [(1 + gval) * reduce(lambda x,y: x*y, [math.cos(a * math.pi / 2.0) for a in c[:self.objectives-1]])]
            for m in reversed(range(1, self.objectives)):
                fit.append((1 + gval) * 
                           reduce(lambda x,y: x*y, [math.cos(a * math.pi / 2.0) for a in c[:m-1]], 1) *
                           math.sin(c[m-1] * math.pi / 2.0))
            fitness.append(emo.Pareto(fit))
        return fitness

class DTLZ4(Benchmark):
    def __init__(self, dimensions=2, objectives=2, alpha=100):
        Benchmark.__init__(self, dimensions, objectives)
        if dimensions < objectives:
            raise ValueError('dimensions (%d) must be greater than or equal to objectives (%d)' % (dimensions, objectives))
        self.bounder = ec.Bounder([0.0] * self.dimensions, [1.0] * self.dimensions)
        self.maximize = False
        self.alpha = alpha
    
    def global_optimum(self):
        x = [random.uniform(0, 1) for _ in range(self.objectives - 1)]
        x.extend([0.5 for _ in range(self.dimensions - self.objectives + 1)])
        return x
        
    def generator(self, random, args):
        return [random.uniform(0.0, 1.0) for _ in range(self.dimensions)]
        
    def evaluator(self, candidates, args):
        fitness = []
        g = lambda x: sum([(a - 0.5)**2 for a in x])
        for c in candidates:
            gval = g(c[self.objectives-1:])
            fit = [(1 + gval) * 
                   reduce(lambda x,y: x*y, [math.cos(a**self.alpha * math.pi / 2.0) for a in c[:self.objectives-1]])]
            for m in reversed(range(1, self.objectives)):
                fit.append((1 + gval) * 
                           reduce(lambda x,y: x*y, [math.cos(a**self.alpha * math.pi / 2.0) for a in c[:m-1]], 1) *
                           math.sin(c[m-1]**self.alpha * math.pi / 2.0))
            fitness.append(emo.Pareto(fit))
        return fitness

class DTLZ5(Benchmark):
    def __init__(self, dimensions=2, objectives=2):
        Benchmark.__init__(self, dimensions, objectives)
        if dimensions < objectives:
            raise ValueError('dimensions (%d) must be greater than or equal to objectives (%d)' % (dimensions, objectives))
        self.bounder = ec.Bounder([0.0] * self.dimensions, [1.0] * self.dimensions)
        self.maximize = False
    
    def global_optimum(self):
        x = [random.uniform(0, 1) for _ in range(self.objectives - 1)]
        x.extend([0.5 for _ in range(self.dimensions - self.objectives + 1)])
        return x
        
    def generator(self, random, args):
        return [random.uniform(0.0, 1.0) for _ in range(self.dimensions)]
        
    def evaluator(self, candidates, args):
        fitness = []
        g = lambda x: sum([(a - 0.5)**2 for a in x])
        for c in candidates:
            gval = g(c[self.objectives-1:])
            theta = lambda x: math.pi / (4.0 * (1 + gval)) * (1 + 2 * gval * x)
            fit = [(1 + gval) * math.cos(math.pi / 2.0 * c[0]) *
                   reduce(lambda x,y: x*y, [math.cos(theta(a)) for a in c[1:self.objectives-1]])]
            for m in reversed(range(1, self.objectives)):
                if m == 1:
                    fit.append((1 + gval) * math.sin(math.pi / 2.0 * c[0]))
                else:
                    fit.append((1 + gval) * math.cos(math.pi / 2.0 * c[0]) *
                               reduce(lambda x,y: x*y, [math.cos(theta(a)) for a in c[1:m-1]], 1) *
                               math.sin(theta(c[m-1])))
            fitness.append(emo.Pareto(fit))
        return fitness

class DTLZ6(Benchmark):
    def __init__(self, dimensions=2, objectives=2):
        Benchmark.__init__(self, dimensions, objectives)
        if dimensions < objectives:
            raise ValueError('dimensions (%d) must be greater than or equal to objectives (%d)' % (dimensions, objectives))
        self.bounder = ec.Bounder([0.0] * self.dimensions, [1.0] * self.dimensions)
        self.maximize = False
    
    def global_optimum(self):
        x = [random.uniform(0, 1) for _ in range(self.objectives - 1)]
        x.extend([0 for _ in range(self.dimensions - self.objectives + 1)])
        return x
        
    def generator(self, random, args):
        return [random.uniform(0.0, 1.0) for _ in range(self.dimensions)]
        
    def evaluator(self, candidates, args):
        fitness = []
        g = lambda x: sum([a**0.1 for a in x])
        for c in candidates:
            gval = g(c[self.objectives-1:])
            theta = lambda x: math.pi / (4.0 * (1 + gval)) * (1 + 2 * gval * x)
            fit = [(1 + gval) * math.cos(math.pi / 2.0 * c[0]) *
                   reduce(lambda x,y: x*y, [math.cos(theta(a)) for a in c[1:self.objectives-1]])]
            for m in reversed(range(1, self.objectives)):
                if m == 1:
                    fit.append((1 + gval) * math.sin(math.pi / 2.0 * c[0]))
                else:
                    fit.append((1 + gval) * math.cos(math.pi / 2.0 * c[0]) *
                               reduce(lambda x,y: x*y, [math.cos(theta(a)) for a in c[1:m-1]], 1) *
                               math.sin(theta(c[m-1])))
            fitness.append(emo.Pareto(fit))
        return fitness

class DTLZ7(Benchmark):
    def __init__(self, dimensions=2, objectives=2):
        Benchmark.__init__(self, dimensions, objectives)
        if dimensions < objectives:
            raise ValueError('dimensions (%d) must be greater than or equal to objectives (%d)' % (dimensions, objectives))
        self.bounder = ec.Bounder([0.0] * self.dimensions, [1.0] * self.dimensions)
        self.maximize = False
    
    def global_optimum(self):
        x = [random.uniform(0, 1) for _ in range(self.objectives - 1)]
        x.extend([0 for _ in range(self.dimensions - self.objectives + 1)])
        return x
        
    def generator(self, random, args):
        return [random.uniform(0.0, 1.0) for _ in range(self.dimensions)]
        
    def evaluator(self, candidates, args):
        fitness = []
        g = lambda x: 1 + 9.0 / len(x) * sum([a for a in x])
        for c in candidates:
            gval = g(c[self.objectives-1:])
            fit = []
            for m in range(self.objectives-1):
                fit.append(c[m])
            fit.append((1 + gval) * (self.objectives - sum([a / (1.0 + gval) * (1 + math.sin(3 * math.pi * a)) for a in c[:self.objectives-1]])))
            fitness.append(emo.Pareto(fit))
        return fitness



    


