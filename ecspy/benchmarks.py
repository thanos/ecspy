"""
    This module provides a set of benchmark problems for global optimization.

    .. Copyright (C) 2009  Inspired Intelligence Initiative

    .. This program is free software: you can redistribute it and/or modify
       it under the terms of the GNU General Public License as published by
       the Free Software Foundation, either version 3 of the License, or
       (at your option) any later version.

    .. This program is distributed in the hope that it will be useful,
       but WITHOUT ANY WARRANTY; without even the implied warranty of
       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
       GNU General Public License for more details.

    .. You should have received a copy of the GNU General Public License
       along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import math
import random
from ecspy import ec
from ecspy import emo


class Benchmark(object):
    """Defines a global optimization benchmark problem.
    
    This abstract class defines the basic structure of a global
    optimization problem. Subclasses should implement the generator 
    and evaluator methods for a particular optimization problem, 
    which can be used with ECsPy evolutionary computations. 
    
    In addition to being used with evolutionary computations, subclasses
    of this are also callable. the arguments passed to such a call are
    combined into a list and passed as the single candidate to the 
    evaluator method. The single calculated fitness is returned.
    
    Public Attributes:
    
    - *dimensions* -- the number of inputs to the problem
    - *objectives* -- the number of outputs of the problem (default 1)
    - *bounder* -- the bounding function for the problem (default None)
    - *maximize* -- whether the problem is one of maximization (default True)
    
    """
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
    """Defines a binary problem based on an existing benchmark problem.
    
    This class can be used to modify an existing benchmark problem to
    allow it to use a binary representation. The generator creates
    a list of binary values of size `dimensions` x `dimension_bits`.
    The evaluator accepts a candidate represented by such a binary list
    and transforms that candidate into a real-valued list as follows:
    
    1. Each set of `dimension_bits` bits is converted to its positive
       integer representation. 
    2. Next, that integer value is divided by the maximum integer that 
       can be represented by `dimension_bits` bits to produce a real 
       number in the range [0, 1]. 
    3. That real number is then scaled to the range [lower_bound, 
       upper_bound] for that dimension (which should be defined by 
       the bounder).
    
    Public Attributes:
    
    - *benchmark* -- the original benchmark problem
    - *dimension_bits* -- the number of bits to use to represent each dimension
    - *bounder* -- the bounding function for the underlying benchmark problem
    - *maximize* -- whether the underlying benchmark problem is one of maximization
    
    """
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
    """Defines the Ackley benchmark problem.
    
    This class defines the Ackley global optimization problem. This 
    is a multimodal minimization problem defined as follows:
    
    .. math::
    
        f(x) = -20e^{-0.2\sqrt{\\frac{1}{n} \sum_{i=1}^n x_i^2}} - e^{\\frac{1}{n} \sum_{i=1}^n \cos(2 \pi x_i)} + 20 + e
    
    Here, :math:`n` represents the number of dimensions and :math:`x_i \in [-32, 32]` for :math:`i=1,...,n`.
    
    .. figure:: http://www-optima.amp.i.kyoto-u.ac.jp/member/student/hedar/Hedar_files/TestGO_files/image6011.jpg
        :alt: Ackley function
        :align: center
        
        Two-dimensional Ackley function 
        (`image source <http://www-optima.amp.i.kyoto-u.ac.jp/member/student/hedar/Hedar_files/TestGO_files/Page295.htm>`__)
    
    Public Attributes:
    
    - *global_optimum* -- the problem input that produces the optimum output.
      Here, this corresponds to [0, 0, ..., 0].
    
    """
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
    """Defines the Griewank benchmark problem.
    
    This class defines the Griewank global optimization problem. This 
    is a highly multimodal minimization problem with numerous, wide-spread, 
    regularly distributed local minima. It is defined as follows:
    
    .. math::
    
        f(x) = \\frac{1}{4000} \sum_{i=1}^n x_i^2 - \prod_{i=1}^n \cos(\\frac{x_i}{\sqrt{i}}) + 1
    
    Here, :math:`n` represents the number of dimensions and :math:`x_i \in [-600, 600]` for :math:`i=1,...,n`.
    
    .. figure:: http://www-optima.amp.i.kyoto-u.ac.jp/member/student/hedar/Hedar_files/TestGO_files/image8891.jpg
        :alt: Griewank function
        :align: center
        
        Two-dimensional Griewank function 
        (`image source <http://www-optima.amp.i.kyoto-u.ac.jp/member/student/hedar/Hedar_files/TestGO_files/Page1905.htm>`__)
    
    Public Attributes:
    
    - *global_optimum* -- the problem input that produces the optimum output.
      Here, this corresponds to [0, 0, ..., 0].
    
    """
    def __init__(self, dimensions=2):
        Benchmark.__init__(self, dimensions)
        self.bounder = ec.Bounder([-600.0] * self.dimensions, [600.0] * self.dimensions)
        self.maximize = False
        self.global_optimum = [0 for _ in range(self.dimensions)]
        
    def generator(self, random, args):
        return [random.uniform(-600.0, 600.0) for _ in range(self.dimensions)]
        
    def evaluator(self, candidates, args):
        fitness = []
        for c in candidates:
            fitness.append(1.0 / 4000.0 * sum([x**2 for x in c]) - 
                           reduce(lambda x, y: x*y, [math.cos(x / math.sqrt(i+1)) for i, x in enumerate(c)]) + 1)
        return fitness

class Rastrigin(Benchmark):
    """Defines the Rastrigin benchmark problem.
    
    This class defines the Rastrigin global optimization problem. This 
    is a highly multimodal minimization problem where the local minima
    are regularly distributed. It is defined as follows:
    
    .. math::
    
        f(x) = \sum_{i=1}^n (x_i^2 - 10\cos(2\pi x_i) + 10)
    
    Here, :math:`n` represents the number of dimensions and :math:`x_i \in [-5.12, 5.12]` for :math:`i=1,...,n`.
    
    .. figure:: http://www-optima.amp.i.kyoto-u.ac.jp/member/student/hedar/Hedar_files/TestGO_files/image12271.jpg
        :alt: Rastrigin function
        :align: center
        
        Two-dimensional Rastrigin function 
        (`image source <http://www-optima.amp.i.kyoto-u.ac.jp/member/student/hedar/Hedar_files/TestGO_files/Page2607.htm>`__)
    
    Public Attributes:
    
    - *global_optimum* -- the problem input that produces the optimum output.
      Here, this corresponds to [0, 0, ..., 0].
    
    """
    def __init__(self, dimensions=2):
        Benchmark.__init__(self, dimensions)
        self.bounder = ec.Bounder([-5.12] * self.dimensions, [5.12] * self.dimensions)
        self.maximize = False
        self.global_optimum = [0 for _ in range(self.dimensions)]
        
    def generator(self, random, args):
        return [random.uniform(-5.12, 5.12) for _ in range(self.dimensions)]
        
    def evaluator(self, candidates, args):
        fitness = []
        for c in candidates:
            fitness.append(sum([x**2 - 10 * math.cos(2 * math.pi * x) + 10 for x in c]))
        return fitness

class Rosenbrock(Benchmark):
    """Defines the Rosenbrock benchmark problem.
    
    This class defines the Rosenbrock global optimization problem, 
    also known as the "banana function." The global optimum sits 
    within a narrow, parabolic-shaped flattened valley. It is 
    defined as follows:
    
    .. math::
    
        f(x) = \sum_{i=1}^{n-1} [100(x_i^2 - x_{i+1})^2 + (x_i - 1)^2]
    
    Here, :math:`n` represents the number of dimensions and :math:`x_i \in [-5, 10]` for :math:`i=1,...,n`.
    
    .. figure:: http://www-optima.amp.i.kyoto-u.ac.jp/member/student/hedar/Hedar_files/TestGO_files/image12371.jpg
        :alt: Rosenbrock function
        :align: center
        
        Two-dimensional Rosenbrock function 
        (`image source <http://www-optima.amp.i.kyoto-u.ac.jp/member/student/hedar/Hedar_files/TestGO_files/Page2537.htm>`__)
    
    Public Attributes:
    
    - *global_optimum* -- the problem input that produces the optimum output.
      Here, this corresponds to [1, 1, ..., 1].
    
    """
    def __init__(self, dimensions=2):
        Benchmark.__init__(self, dimensions)
        self.bounder = ec.Bounder([-5.0] * self.dimensions, [10.0] * self.dimensions)
        self.maximize = False
        self.global_optimum = [1 for _ in range(self.dimensions)]
    
    def generator(self, random, args):
        return [random.uniform(-5.0, 10.0) for _ in range(self.dimensions)]
        
    def evaluator(self, candidates, args):
        fitness = []
        for c in candidates:
            total = 0
            for i in range(len(c) - 1):
                total += 100 * (c[i]**2 - c[i+1])**2 + (c[i] - 1)**2
            fitness.append(total)
        return fitness
    
class Schwefel(Benchmark):
    """Defines the Schwefel benchmark problem.
    
    This class defines the Schwefel global optimization problem. 
    It is defined as follows:
    
    .. math::
    
        f(x) = 418.9829n - \sum_{i=1}^n \\left[-x_i \sin(\sqrt{|x_i|})\\right]
    
    Here, :math:`n` represents the number of dimensions and :math:`x_i \in [-500, 500]` for :math:`i=1,...,n`.
    
    .. figure:: http://www-optima.amp.i.kyoto-u.ac.jp/member/student/hedar/Hedar_files/TestGO_files/image12721.jpg
        :alt: Schwefel function
        :align: center
        
        Two-dimensional Schwefel function 
        (`image source <http://www-optima.amp.i.kyoto-u.ac.jp/member/student/hedar/Hedar_files/TestGO_files/Page2530.htm>`__)
    
    Public Attributes:
    
    - *global_optimum* -- the problem input that produces the optimum output.
      Here, this corresponds to [420.9687, 420.9687, ..., 420.9687].
    
    """
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
    """Defines the Sphere benchmark problem.
    
    This class defines the Sphere global optimization problem, also called
    the "first function of De Jong's" or "De Jong's F1." It is continuous,
    convex, and unimodal, and it is defined as follows:
    
    .. math::
    
        f(x) = \sum_{i=1}^n x_i^2
    
    Here, :math:`n` represents the number of dimensions and :math:`x_i \in [-5.12, 5.12]` for :math:`i=1,...,n`.
    
    .. figure:: http://www-optima.amp.i.kyoto-u.ac.jp/member/student/hedar/Hedar_files/TestGO_files/image11981.jpg
        :alt: Sphere function
        :align: center
        
        Two-dimensional Sphere function 
        (`image source <http://www-optima.amp.i.kyoto-u.ac.jp/member/student/hedar/Hedar_files/TestGO_files/Page1113.htm>`__)
    
    Public Attributes:
    
    - *global_optimum* -- the problem input that produces the optimum output.
      Here, this corresponds to [0, 0, ..., 0].
    
    """
    def __init__(self, dimensions=2):
        Benchmark.__init__(self, dimensions)
        self.bounder = ec.Bounder([-5.12] * self.dimensions, [5.12] * self.dimensions)
        self.maximize = False
        self.global_optimum = [0 for _ in range(self.dimensions)]
    
    def generator(self, random, args):
        return [random.uniform(-5.12, 5.12) for _ in range(self.dimensions)]
        
    def evaluator(self, candidates, args):
        fitness = []
        for c in candidates:
            fitness.append(sum([x**2 for x in c]))
        return fitness
    


        
#------------------------------------------------------
#              Multi-objective problems
#------------------------------------------------------

class Kursawe(Benchmark):
    """Defines the Kursawe multiobjective benchmark problem.
    
    This class defines the Kursawe multiobjective minimization problem. 
    This function accepts an n-dimensional input and produces a 
    two-dimensional output. It is defined as follows:
    
    .. math::
    
        f_1(x) &= \sum_{i=1}^{n-1} \\left[-10e^{-0.2\sqrt{x_i^2 + x_{i+1}^2}}\\right] \\\\
        f_2(x) &= \sum_{i=1}^n \\left[|x_i|^{0.8} + 5\sin(x_i)^3\\right] \\\\
    
    Here, :math:`n` represents the number of dimensions and :math:`x_i \in [-5, 5]` for :math:`i=1,...,n`.
    
    .. figure:: http://delta.cs.cinvestav.mx/~ccoello/EMOO/testfuncs/mopfigs/kursawefun.jpg
        :alt: Kursawe Pareto front
        :width: 700 px
        :align: center
        
        Three-dimensional Kursawe Pareto front 
        (`image source <http://delta.cs.cinvestav.mx/~ccoello/EMOO/testfuncs/>`__)
    
    """
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
            f2 = sum([math.pow(abs(x), 0.8) + 5 * math.sin(x)**3 for x in c])
            fitness.append(emo.Pareto([f1, f2]))
        return fitness

class DTLZ1(Benchmark):
    """Defines the DTLZ1 multiobjective benchmark problem.
    
    This class defines the DTLZ1 multiobjective minimization problem.
    taken from `(Deb et al., "Scalable Multi-Objective Optimization Test Problems."
    CEC 2002, pp. 825--830) <http://www.tik.ee.ethz.ch/sop/download/supplementary/testproblems/dtlz1/index.php>`__.
    This function accepts an n-dimensional input and produces an m-dimensional output.
    It is defined as follows:
    
    .. math::
    
        f_1(\\vec{x}) &= \\frac{1}{2} x_1 \\dots x_{m-1}(1 + g(\\vec{x_m})) \\\\
        f_i(\\vec{x}) &= \\frac{1}{2} x_1 \\dots x_{m-i}(1 + g(\\vec{x_m})) \\\\
        f_m(\\vec{x}) &= \\frac{1}{2} (1 - x_1)(1 + g(\\vec{x_m})) \\\\
        g(\\vec{x_m}) &= 100\\left[|\\vec{x_m}| + \sum_{x_i \in \\vec{x_m}}\\left((x_i - 0.5)^2 - \cos(20\pi(x_i - 0.5))\\right)\\right] \\\\
    
    Here, :math:`n` represents the number of dimensions, :math:`m` represents the
    number of objectives, :math:`x_i \in [0, 1]` for :math:`i=1,...,n`, and 
    :math:`\\vec{x_m} = x_m x_{m+1} \\dots x_{n}.`
    
    The recommendation given in the paper mentioned above is to provide 4 more
    dimensions than objectives. For instance, if we want to use 2 objectives, we
    should use 6 dimensions.
    
    .. figure:: http://delta.cs.cinvestav.mx/~ccoello/EMOO/testfuncs/mopfigs/dtlz1funb.jpg
        :alt: DTLZ1 Pareto front
        :width: 700 px
        :align: center
        
        Three-dimensional DTLZ1 Pareto front 
        (`image source <http://delta.cs.cinvestav.mx/~ccoello/EMOO/testfuncs/>`__)
        
    """
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
    """Defines the DTLZ2 multiobjective benchmark problem.
    
    This class defines the DTLZ2 multiobjective minimization problem.
    taken from `(Deb et al., "Scalable Multi-Objective Optimization Test Problems."
    CEC 2002, pp. 825--830) <http://www.tik.ee.ethz.ch/sop/download/supplementary/testproblems/dtlz1/index.php>`__.
    This function accepts an n-dimensional input and produces an m-dimensional output.
    It is defined as follows:
    
    .. math::
    
        f_1(\\vec{x}) &= (1 + g(\\vec{x_m}))\cos(x_1 \pi/2)\cos(x_2 \pi/2)\\dots\cos(x_{m-2} \pi/2)\cos(x_{m-1} \pi/2) \\\\
        f_i(\\vec{x}) &= (1 + g(\\vec{x_m}))\cos(x_1 \pi/2)\cos(x_2 \pi/2)\\dots\cos(x_{m-i} \pi/2)\sin(x_{m-i+1} \pi/2) \\\\
        f_m(\\vec{x}) &= (1 + g(\\vec{x_m}))\sin(x_1 \pi/2) \\\\
        g(\\vec{x_m}) &= \sum_{x_i \in \\vec{x_m}}(x_i - 0.5)^2 \\\\
    
    Here, :math:`n` represents the number of dimensions, :math:`m` represents the
    number of objectives, :math:`x_i \in [0, 1]` for :math:`i=1,...,n`, and 
    :math:`\\vec{x_m} = x_m x_{m+1} \\dots x_{n}.`
    
    The recommendation given in the paper mentioned above is to provide 9 more
    dimensions than objectives. For instance, if we want to use 2 objectives, we
    should use 11 dimensions.
    
    """
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
    """Defines the DTLZ3 multiobjective benchmark problem.
    
    This class defines the DTLZ3 multiobjective minimization problem.
    taken from `(Deb et al., "Scalable Multi-Objective Optimization Test Problems."
    CEC 2002, pp. 825--830) <http://www.tik.ee.ethz.ch/sop/download/supplementary/testproblems/dtlz1/index.php>`__.
    This function accepts an n-dimensional input and produces an m-dimensional output.
    It is defined as follows:
    
    .. math::
    
        f_1(\\vec{x}) &= (1 + g(\\vec{x_m}))\cos(x_1 \pi/2)\cos(x_2 \pi/2)\\dots\cos(x_{m-2} \pi/2)\cos(x_{m-1} \pi/2) \\\\
        f_i(\\vec{x}) &= (1 + g(\\vec{x_m}))\cos(x_1 \pi/2)\cos(x_2 \pi/2)\\dots\cos(x_{m-i} \pi/2)\sin(x_{m-i+1} \pi/2) \\\\
        f_m(\\vec{x}) &= (1 + g(\\vec{x_m}))\sin(x_1 \pi/2) \\\\
        g(\\vec{x_m}) &= 100\\left[|\\vec{x_m}| + \sum_{x_i \in \\vec{x_m}}\\left((x_i - 0.5)^2 - \cos(20\pi(x_i - 0.5))\\right)\\right] \\\\
    
    Here, :math:`n` represents the number of dimensions, :math:`m` represents the
    number of objectives, :math:`x_i \in [0, 1]` for :math:`i=1,...,n`, and 
    :math:`\\vec{x_m} = x_m x_{m+1} \\dots x_{n}.`
    
    The recommendation given in the paper mentioned above is to provide 9 more
    dimensions than objectives. For instance, if we want to use 2 objectives, we
    should use 11 dimensions.
    
    """
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
    """Defines the DTLZ4 multiobjective benchmark problem.
    
    This class defines the DTLZ4 multiobjective minimization problem.
    taken from `(Deb et al., "Scalable Multi-Objective Optimization Test Problems."
    CEC 2002, pp. 825--830) <http://www.tik.ee.ethz.ch/sop/download/supplementary/testproblems/dtlz1/index.php>`__.
    This function accepts an n-dimensional input and produces an m-dimensional output.
    It is defined as follows:
    
    .. math::
    
        f_1(\\vec{x}) &= (1 + g(\\vec{x_m}))\cos(x_1^\\alpha \pi/2)\cos(x_2^\\alpha \pi/2)\\dots\cos(x_{m-2}^\\alpha \pi/2)\cos(x_{m-1}^\\alpha \pi/2) \\\\
        f_i(\\vec{x}) &= (1 + g(\\vec{x_m}))\cos(x_1^\\alpha \pi/2)\cos(x_2^\\alpha \pi/2)\\dots\cos(x_{m-i}^\\alpha \pi/2)\sin(x_{m-i+1}^\\alpha \pi/2) \\\\
        f_m(\\vec{x}) &= (1 + g(\\vec{x_m}))\sin(x_1^\\alpha \pi/2) \\\\
        g(\\vec{x_m}) &= \sum_{x_i \in \\vec{x_m}}(x_i - 0.5)^2 \\\\
    
    Here, :math:`n` represents the number of dimensions, :math:`m` represents the
    number of objectives, :math:`x_i \in [0, 1]` for :math:`i=1,...,n`,  
    :math:`\\vec{x_m} = x_m x_{m+1} \\dots x_{n},` and :math:`\\alpha=100.`
    
    The recommendation given in the paper mentioned above is to provide 9 more
    dimensions than objectives. For instance, if we want to use 2 objectives, we
    should use 11 dimensions.
    
    """
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
    """Defines the DTLZ5 multiobjective benchmark problem.
    
    This class defines the DTLZ5 multiobjective minimization problem.
    taken from `(Deb et al., "Scalable Multi-Objective Optimization Test Problems."
    CEC 2002, pp. 825--830) <http://www.tik.ee.ethz.ch/sop/download/supplementary/testproblems/dtlz1/index.php>`__.
    This function accepts an n-dimensional input and produces an m-dimensional output.
    It is defined as follows:
    
    .. math::
    
        f_1(\\vec{x}) &= (1 + g(\\vec{x_m}))\cos(\\theta_1 \pi/2)\cos(\\theta_2 \pi/2)\\dots\cos(\\theta_{m-2} \pi/2)\cos(\\theta_{m-1} \pi/2) \\\\
        f_i(\\vec{x}) &= (1 + g(\\vec{x_m}))\cos(\\theta_1 \pi/2)\cos(\\theta_2 \pi/2)\\dots\cos(\\theta_{m-i} \pi/2)\sin(\\theta_{m-i+1} \pi/2) \\\\
        f_m(\\vec{x}) &= (1 + g(\\vec{x_m}))\sin(\\theta_1 \pi/2) \\\\
        \\theta_i     &= \\frac{\pi}{4(1+g(\\vec{x_m}))}(1 + 2g(\\vec{x_m}) x_i) \\\\
        g(\\vec{x_m}) &= \sum_{x_i \in \\vec{x_m}}(x_i - 0.5)^2 \\\\
    
    Here, :math:`n` represents the number of dimensions, :math:`m` represents the
    number of objectives, :math:`x_i \in [0, 1]` for :math:`i=1,...,n`, and 
    :math:`\\vec{x_m} = x_m x_{m+1} \\dots x_{n}.`
    
    The recommendation given in the paper mentioned above is to provide 9 more
    dimensions than objectives. For instance, if we want to use 2 objectives, we
    should use 11 dimensions.
    
    """
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
    """Defines the DTLZ6 multiobjective benchmark problem.
    
    This class defines the DTLZ6 multiobjective minimization problem.
    taken from `(Deb et al., "Scalable Multi-Objective Optimization Test Problems."
    CEC 2002, pp. 825--830) <http://www.tik.ee.ethz.ch/sop/download/supplementary/testproblems/dtlz1/index.php>`__.
    This function accepts an n-dimensional input and produces an m-dimensional output.
    It is defined as follows:
    
    .. math::
    
        f_1(\\vec{x}) &= (1 + g(\\vec{x_m}))\cos(\\theta_1 \pi/2)\cos(\\theta_2 \pi/2)\\dots\cos(\\theta_{m-2} \pi/2)\cos(\\theta_{m-1} \pi/2) \\\\
        f_i(\\vec{x}) &= (1 + g(\\vec{x_m}))\cos(\\theta_1 \pi/2)\cos(\\theta_2 \pi/2)\\dots\cos(\\theta_{m-i} \pi/2)\sin(\\theta_{m-i+1} \pi/2) \\\\
        f_m(\\vec{x}) &= (1 + g(\\vec{x_m}))\sin(\\theta_1 \pi/2) \\\\
        \\theta_i     &= \\frac{\pi}{4(1+g(\\vec{x_m}))}(1 + 2g(\\vec{x_m}) x_i) \\\\
        g(\\vec{x_m}) &= \sum_{x_i \in \\vec{x_m}}x_i^{0.1} \\\\
    
    Here, :math:`n` represents the number of dimensions, :math:`m` represents the
    number of objectives, :math:`x_i \in [0, 1]` for :math:`i=1,...,n`, and 
    :math:`\\vec{x_m} = x_m x_{m+1} \\dots x_{n}.`
    
    The recommendation given in the paper mentioned above is to provide 9 more
    dimensions than objectives. For instance, if we want to use 2 objectives, we
    should use 11 dimensions.
    
    """
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
    """Defines the DTLZ7 multiobjective benchmark problem.
    
    This class defines the DTLZ7 multiobjective minimization problem.
    taken from `(Deb et al., "Scalable Multi-Objective Optimization Test Problems."
    CEC 2002, pp. 825--830) <http://www.tik.ee.ethz.ch/sop/download/supplementary/testproblems/dtlz1/index.php>`__.
    This function accepts an n-dimensional input and produces an m-dimensional output.
    It is defined as follows:
    
    .. math::
    
        f_1(\\vec{x}) &= x_1 \\\\
        f_i(\\vec{x}) &= x_i \\\\
        f_m(\\vec{x}) &= (1 + g(\\vec{x_m}))h(f_1, f_2, \\dots, f_{m-1}, g) \\\\
        g(\\vec{x_m}) &= 1 + \\frac{9}{|\\vec{x_m}|}\sum_{x_i \in \\vec{x_m}}x_i \\\\
        h(f_1, f_2, \\dots, f_{m-1}, g) &= m - \sum_{i=1}^{m-1}\\left[\\frac{f_1}{1+g}(1 + \sin(3\pi f_i))\\right] \\\\
    
    Here, :math:`n` represents the number of dimensions, :math:`m` represents the
    number of objectives, :math:`x_i \in [0, 1]` for :math:`i=1,...,n`, and 
    :math:`\\vec{x_m} = x_m x_{m+1} \\dots x_{n}.`
    
    The recommendation given in the paper mentioned above is to provide 19 more
    dimensions than objectives. For instance, if we want to use 2 objectives, we
    should use 21 dimensions.
    
    .. figure:: http://delta.cs.cinvestav.mx/~ccoello/EMOO/testfuncs/mopfigs/dtlz7funb.jpg
        :alt: DTLZ7 Pareto front
        :width: 700 px
        :align: center
        
        Three-dimensional DTLZ7 Pareto front 
        (`image source <http://delta.cs.cinvestav.mx/~ccoello/EMOO/testfuncs/>`__)
        
    """
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



    


