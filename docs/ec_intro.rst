*****************************************
Evolutionary Computation: An Introduction
*****************************************

The beginnings of evolutionary computation (EC) can be traced back as far as the late 1950's, but it was the last two decades that saw truly exponential increases in the amount of attention given to the field [Back1997]_. EC can be thought of more as a problem solving strategy than a one-size-fits-all tool [Back1997]_ [Michalewicz2004]_. At its core, an EC attempts to mimic the biological process of evolution in order to solve a given problem [Fogel2000]_. This, consequently, suggests that there should be a simulated analog to the biological process of reproduction and some measure of or mechanism for survivability. Indeed, these must be defined for any EC. However, before these processes can be defined, it is necessary first to define what makes up an *individual*.

An individual is simply a *candidate solution*. As such, it can be represented in any way that the designer chooses, and most representations are problem-specific. The manner in which a candidate solution is represented is known as the *genotype* [Back1997]_ (in keeping with the biological analogy). Since two or more solutions must be compared with one another in order to determine which is "better", it is necessary to also have some measure of "goodness", which in the EC literature is known as the *fitness* of an individual [Back1997]_. The fitness is a measure of how well one candidate solution solves a problem, sometimes in comparison to the performance of other candidate solutions. Usually, candidate solutions cannot be compared (and thus their fitness values cannot be assessed) by simply looking at the genotype values. Instead, the candidate solution undergoes a transformation to convert its genotype into the corresponding *phenotype* [Back1997]_, which can be thought of as its representation in the fitness space.

To make this discussion more clear, an example is in order. Suppose we wish to find the real value for :math:`-10 \leq x \leq 10` such that it minimizes the function

.. math::

    y = f(x) = x^2


(Clearly, the minimum value will occur when :math:`x=0`.) In the simplest case, we would say that the *x* value represents the genotype of the candidate solution, and the set of all candidate solutions is simply the line from -10 to 10. The phenotype for a given *x* value, in this case, is also that same *x* value. (In other words, the mapping function between genotype space and phenotype space is simply the identity function.) The phenotype space is simply all of the possible values for *x*, which in this case is the curve representing :math:`f(x) = x^2`. The fitness for a candidate solution *x* is simply the value of *y* at that point, :math:`y = x^2`. 

Once the representation is chosen, the *evolutionary operators* must be specified. These operators define the mechanisms of *selection*, *variation*, and *replacement* [Back1997]_. Selection determines how solutions are chosen to participate in the creation of new solutions. Variation determines how new solutions are created from existing solutions (i.e., reproduction) and how existing solutions are modified to explore new areas of the search space (i.e., mutation). Replacement determines how solutions are chosen to remain viable candidates. In some cases, one or more of these operators are simply identity functions, which means that they have no actual function. However, when viewed in this way, all of the EC approaches are simply variations on this basic theme [Back1997]_.

The basic EC is presented in the algorithm listing below. There, ``P[t]`` is a set of candidate solutions (the *population*) at time ``t``. Typically, the population is of a fixed size. The ``Evaluate()`` function performs the mapping from genotype to phenotype space and assigns appropriate fitness values to each individual in the population. The ``Selection()`` function takes the current population and returns a set of individuals to be used for variation. The ``Variation()`` function takes that set of individuals and produces a set of new individuals, ``offspring``. Finally, the ``Replacement()`` function performs the selection of individuals (chosen from the union of the original and modified individuals) which will make up the population in the next generation.

::

    ALGORITHM EvolutionaryComputation()
       t = 0
       Initialize(P[t]) # P[t] represents the population at time t
       Evaluate(P[t])
       WHILE NOT termination_criteria LOOP
          parents = Selection(P[t])
          offspring = Variation(P[t]) 
          Evaluate(offspring)
          P[t+1] = Replacement(P[t] union offspring)
          t = t + 1
       END LOOP


An important point of which to take note here is that the number of *function evaluations* is critical when comparing two evolutionary computation algorithms. A function evaluation is simply one mapping from genotype to fitness. (The mapping is often called the *evaluation function* or *fitness function*, so the term "function evaluations" is appropriate.) That is the typical processing unit used in the EC literature when referring to the efficiency of a particular algorithm.

According to Back et al [Back1997]_, the majority of current evolutionary computation implementations come from three different, but related, areas: genetic algorithms (GAs) [Forrest1993]_, [Goldberg1989]_, [Holland1975]_, [Vose1999]_, evolutionary programming (EPs) [Back1997]_, [Fogel1966]_, [Fogel1994]_, and evolution strategies (ESs) [Back1991]_, [Fogel1994]_. However, as stated earlier, each area is defined by its choice of representation and/or operators. These choices are discussed in the following sections.

==================
Genetic Algorithms
==================

Genetic algorithms were first proposed by John Holland in the 1960's [Holland1975]_ in an attempt to leverage the power of natural selection to solve difficult optimization problems. In the canonical genetic algorithm, sometimes referred to as the *simple genetic algorithm* (SGA) [Goldberg1989]_, [Vose1999]_, the genotype for a candidate solution is represented as a binary string. The evaluation function is then a mapping from a binary string to some real-valued measure of fitness (as determined from the phenotype). As in all EC approaches, the fitness function is entirely problem-dependent.

The selection operator used in an SGA is *fitness proportionate selection* [Goldberg1989]_, sometimes called "roulette wheel" selection. In this type of selection, the probability of selecting a particular individual increases proportional to that individual's fitness. In some sense, the size of the individual's "roulette wheel section" increases with its fitness. In this way, the more fit an individual, the more likely it is to survive. However, this operator is stochastic, so it is possible that even the strongest individual will not survive (and, likewise, the weakest individual may survive).

A similar yet slightly more complex selection procedure is *remainder stochastic selection*. In this type of selection, any individual with an above average fitness is guaranteed to participate in creating the next generation of individuals, and the remaining slots are randomly assigned to individuals in a manner proportional to how well their fitness values compare to the average fitness. In this setup, the objective fitness for an individual (as determined by the fitness function) is modified to produce a relative fitness value as follows:

.. math::

    f_i^r = \frac{f_i}{\bar f}

where :math:`f_i^r` is the relative fitness of individual *i*, :math:`f_i` is the objective fitness of individual *i*, and :math:`\bar f` is the average fitness of the current population.

Another popular selection method is *tournament selection* [Goldberg1989]_. In this type of selection, a subset of candidate solutions is chosen from the existing population against each of which the individual in question is compared (as if that individual is competing in a single-elimination tournament against all individuals in the subset). If the individual's fitness is better than all candidate solutions in the subset, then that individual is selected. The size of the subset (often called the *tournament size* [Goldberg1989]_) can be used to control the *selection pressure* [Goldberg1989]_.

After selection is performed, the participating individuals undergo variation through crossover and mutation. Each of these operators is performed according to some probability of occurrence (typically denoted :math:`p_c` and :math:`p_m`, respectively) that must be specified as parameters to the system. The variation operators used in an SGA are single-point crossover [Goldberg1989]_ and bit-flip mutation [Goldberg1989]_. In single-point crossover, two individuals (i.e., binary strings) are chosen, along with a single recombination point that determines the position in each string that will be "cut". The individuals are then recombined at that point to form two new individuals. This can be understood more clearly in the following example (where the vertical bar represents the recombination point):

::

    Parent A: XXXXXXX | XX
    Parent B: YYYYYYY | YY
    Child 1 : XXXXXXXYY
    Child 2 : YYYYYYYXX

This operation is applied to randomly selected parents with probability :math:`p_c`, which is typically set to be a fairly high (e.g., 0.75) value. Bit-flip mutation simply means that each bit in a newly created binary string is changed to the opposite value with probability :math:`p_m`, which is typically set to be a very low (e.g., 0.01) value.

The resultant population is made up entirely of the newly-created offspring. This is known as *generational replacement* [Back1997]_, which means that no individuals from the previous generation are allowed to survive to the succeeding generations. This type of replacement strategy can be augmented with *elitism* [Back1997]_, which would allow some proportion (as determined by system parameters) of the most fit individuals to survive into the next generation. Additionally, some genetic algorithms make use of *steady-state replacement* [Back1997]_, in which only one offspring is created in a given generation, and this offspring always replaces the least-fit individual in the current population.

========================
Evolutionary Programming
========================

In the early 1960's, Lawrence Fogel attempted to use simulated evolution, which he called Evolutionary Programming (EP), to create artificial intelligence [Fogel1966]_, [Fogel1994]_. In this seminal work, finite state machines (FSMs) were evolved to predict future symbols from a given input stream [Fogel1994]_. Using a FSM representation of the individuals in the population required novel variation operators. The following operators were used in the work: changing an output symbol, changing a state transition, adding a state, deleting a state, and changing a state. The fitness of a given FSM was determined by how accurate its predictions were, given the sequence of input symbols. More recently, EP approaches have been applied to real-valued, continuous optimization problems, but these approaches are similar to the approaches used in evolution strategies [Fogel1994]_, which are discussed below.

====================
Evolution Strategies
====================

At the same time that Holland was developing the genetic algorithm, Rechenberg was independently discovering a technique for using natural selection for optimization problems, which he termed *evolution strategies* [Back1991]_. The simplest version of an evolution strategy (ES) is what is known as a *two-membered ES* [Back1991]_ or, more commonly, a (1+1)-ES. In this scenario, a single individual, represented as a vector of real values, comprises the population. At each generation, that individual is mutated (the variation operator) along each dimension using a Gaussian distribution with zero mean and a given variance (provided as a parameter to the system) to produce an offspring. The fitness values for both the parent and the offspring are compared, and the better of the two individuals is allowed to become the parent in the next generation.

It was discovered [Back1991]_ that online adjustment of the mutation rate (i.e., the variance of the normal distribution) could provide better performance. This online adjustment is known as the *one-fifth success rule* [Back1991]_, which states that around :math:`\frac{1}{5}` of the mutations should be successful. If the actual number of successful mutations is greater than :math:`\frac{1}{5}`, increase the variance. If the number is less than :math:`\frac{1}{5}`, decrease the variance.

In addition to online adjustment of the variance, more sophisticated versions of evolution strategies can also include the particular variance as a part of the genotype to be evolved [Back1991]_. It is also possible to evolve and use a different variance along each dimension of the problem [Back1991]_, thus allowing the search for a solution to conform more appropriately to the topology of the search space. When variances are included in the genotype, an additional parameter is needed to serve as the variance used to mutate the evolved variances.

The (1+1)-ES did not truly make use of the idea of a population of individuals, so this concept was generalized and extended to yield the (:math:`\mu+1`)-ES [Back1991]_. In this system, a population of :math:`\mu` individuals is maintained in each generation. Additionally, a reproduction operator is included that selects two (or more) individuals from this population and recombines them to form a new individual. This recombination is simply a random selection of each component from the parents. Once the new individual is created, it undergoes mutation as mentioned above. Finally, each offspring is added to the population if it is better than the least fit individual, producing the new population for the next generation. This approach can be and has been [Back1991]_, of course, extended to a (:math:`\mu+\lambda`)-ES, in which :math:`\mu` individuals produce :math:`\lambda` offspring. The best :math:`\mu` individuals of the :math:`\mu+\lambda` individuals are then chosen to survive.

It is also possible to provide somewhat of an analog to the generational replacement of a GA within an ES. This approach is known as a (:math:`\mu,\lambda`)-ES (where :math:`\lambda` must be greater than or equal to :math:`\mu`) [Back1991]_. In such a scenario, the :math:`\mu` individuals are used to create :math:`\lambda` offspring, and from those offspring only, :math:`\mu` individuals are chosen to comprise the population in the next generation.

===========================
Particle Swarm Optimization
===========================

In addition to the evolutionary computation techniques described above, another nature-inspired optimization algorithm, called *particle swarm optimization* (PSO), was developed by Kennedy and Eberhart in 1995 [Kennedy1995]_. Inspired by the movement of bird flocks and insect swarms, they attempted to develop a model of swarm behavior that could be used to solve optimization problems. To create the analogy, they imagined a flock of birds flying around in search of a corn field. Each bird was capable of remembering the best location it had found, and each was capable of knowing the best location that any of the birds had found. The birds were allowed to fly around while being pulled toward both their individual best locations and the flock's best location. Kennedy and Eberhart found that their simulation of this analogy produced very realistic-looking behavior in their virtual flocks [Kennedy1995]_.

In the PSO model presented in [Kennedy1995]_ and expanded in [Kennedy1997]_, each particle is composed of three vectors: :math:`x`, :math:`p`, and :math:`v`. These represent the particle's current location, best location found, and velocity, respectively. These vectors are each of the same dimensionality as the search space. Additionally, each particle maintains a two values: one corresponding to the fitness of the :math:`x` vector and the other to the fitness of the :math:`p` vector.

As the particles in the swarm move around the search space, their velocities are first updated according to the following equation:

.. math::

    v_{id} = v_{id} + \phi_1R_1(p_{id} - x_{id}) + \phi_2R_2(g_{id} - x_{id})

In this equation, :math:`v_{id}` is the velocity of the :math:`i^{th}` particle along the :math:`d^{th}` dimension. The :math:`g` vector represents the best location found by the flock, and :math:`R_1` and :math:`R_2` are uniform random values such that :math:`0 \leq R_1,R_2 \leq 1`. Finally, :math:`\phi_1` and :math:`\phi_2` are two constants that control the influence of the personal best and the global best locations, respectively, on the particle's velocity. These values are often referred to as *cognitive* and *social* learning rates, respectively [Kennedy1997]_.

After the velocity vector is updated, the particle's location is updated by applying the following equation:

.. math::

    x_{id} = x_{id} + v_{id}

At this point, the new location's fitness is evaluated and compared to the fitness of the particle's personal best location. If the new location is better, then it also becomes the new personal best location for the particle.

The *topology* for a swarm refers to the structure of the neighborhood for each particle. In a *star topology*, all the particles exist in the same neighborhood, so the global best vector represents the best location found by any particle in the swarm. In contrast, a *ring topology* arranges the particles into overlapping neighborhoods of size *h*. The global best vector in this type of topology represents the best location found by any particle in that particle's neighborhood.

In 1999, Maurice Clerc introduced an improvement to the equation for updating the velocity of a particle [Clerc1999]_. He introduced a constant to be multiplied to the new velocity before updating the location of the particle. He called this constant the *constriction coefficient* [Clerc1999]_. The calculation of this coefficient is as follows:

.. math::

    K = \frac{2}{\left|2 - \phi - \sqrt{\phi^2 - 4\phi}\right|}

In this equation, :math:`\phi_ = \phi_1 + \phi_2` and :math:`\phi > 4`. The constriction coefficient is used to restrain the velocity vector of each particle so that it does not grow unbounded.

Finally, various other models have been proposed as alternatives to the so-called full model presented above [Eberhart2000]_. The *cognitive-only* model sets :math:`\phi_1` to 0, while the *social-only* model sets :math:`\phi_2` to 0. A *selfless* model was also developed which was identical to the social-only model except that a particle's personal best was not included in the search for that particle's neighborhood's global best [Eberhart2000]_.

==========
References
==========

.. [Back1991] \T. Back, F. Hoffmeister, and H.-P. Schwefel, "A survey of evolution strategies," in *Proceedings of the 4th International Conference on Genetic Algorithms*, R. K. Belew and L. B. Booker, Eds. Morgan Kaufman, 1991, pp. 2-9.

.. [Back1997] \T. Back, U. Hammel, and H.-P. Schwefel, "Evolutionary computation: Comments on the history and current state," *IEEE Transactions on Evolutionary Computation*, vol. 1, no. 1, pp. 3-17, apr 1997.

.. [Clerc1999] \M. Clerc, "The swarm and the queen: towards a deterministic and adaptive particle swarm optimization," in *Proceedings of the International Conference on Evolutionary Computation*, Washington, DC, 1999, pp. 1951-1957.

.. [Eberhart2000] \R. C. Eberhart and Y. Shi, "Comparing inertia weights and constriction factors in particle swarm optimization," in *Proceedings of the Congress on Evolutionary Computation*, Washington, DC, 2000, pp. 84-88. 

.. [Fogel1966] \L. J. Fogel, A. J. Owens, and M. J. Walsh, *Artificial intelligence through simulated evolution*. New York: Wiley, 1966.

.. [Fogel1994] \D. B. Fogel, "An introduction to simulated evolutionary optimization," *IEEE Transactions on Neural Networks*, vol. 5, no. 1, pp. 3-14, Jan. 1994.

.. [Fogel2000] \D. B. Fogel, "What is evolutionary computation?" *IEEE Spectrum*, vol. 37, no. 2, pp. 26-32, Feb. 2000.

.. [Forrest1993] \S. Forrest, "Genetic algorithms: principles of natural selection applied to computation," *Science*, vol. 60, pp. 872-878, Aug. 1993.

.. [Goldberg1989] \D. E. Goldberg, *Genetic Algorithms in Search, Optimization and Machine Learning*. Reading, MA: Addison-Wesley Publishing Company, Inc., 1989.

.. [Holland1975] \J. H. Holland, *Adaptation in Natural and Artificial Systems*. Ann Arbor, MI: University of Michigan Press, 1975.

.. [Kennedy1995] \J. Kennedy and R. Eberhart, "Particle swarm optimization," in *Proceedings of the IEEE Conference on Neural Networks*, Perth, Australia, 1995, pp. 1942-1948.

.. [Kennedy1997] \J. Kennedy, "The particle swarm: Social adaptation of knowledge," in *Proceedings of the International Conference on Evolutionary Computation*, Indianapolis, IN, 1997, pp. 303-308.

.. [Michalewicz2004] \Z. Michalewicz and D. B. Fogel, *How to Solve It: Modern Heuristics*. Springer, 2004.

.. [Vose1999] \M. D. Vose, *The Simple Genetic Algorithm: Foundations and Theory*. MIT Press, 1999.