

# Introduction #
The beginnings of evolutionary computation (EC) can be traced back as far as the late 1950's, but it was the last two decades that saw truly exponential increases in the amount of attention given to the field `[2]`. EC can be thought of more as a problem solving strategy than a one-size-fits-all tool `[2,13]`. At its core, an EC attempts to mimic the biological process of evolution in order to solve a given problem `[7]`. This, consequently, suggests that there should be a simulated analog to the biological process of reproduction and some measure of or mechanism for survivability. Indeed, these must be defined for any EC. However, before these processes can be defined, it is necessary first to define what makes up an _individual_.

An individual is simply a _candidate solution_. As such, it can be represented in any way that the designer chooses, and most representations are problem-specific. The manner in which a candidate solution is represented is known as the _genotype_ `[2]` (in keeping with the biological analogy). Since two or more solutions must be compared with one another in order to determine which is "better", it is necessary to also have some measure of "goodness", which in the EC literature is known as the _fitness_ of an individual `[2]`. The fitness is a measure of how well one candidate solution solves a problem, sometimes in comparison to the performance of other candidate solutions. Usually, candidate solutions cannot be compared (and thus their fitness values cannot be assessed) by simply looking at the genotype values. Instead, the candidate solution undergoes a transformation to convert its genotype into the corresponding _phenotype_ `[2]`, which can be thought of as its representation in the fitness space.

To make this discussion more clear, an example is in order. Suppose we wish to find the real value for _x_ (-10 <= _x_ <= 10) such that it minimizes the function

_y_ = f(_x_) = _x_<sup>2</sup>.


(Clearly, the minimum value will occur when _x_=0.) In the simplest case, we would say that the _x_ value represents the genotype of the candidate solution, and the set of all candidate solutions is simply the line from -10 to 10. The phenotype for a given _x_ value, in this case, is also that same _x_ value. (In other words, the mapping function between genotype space and phenotype space is simply the identity function.) The phenotype space is simply all of the possible values for _x_, which in this case is the curve representing f(_x_) = _x_<sup>2</sup>. The fitness for a candidate solution _x_ is simply the value of _y_ at that point, _y_ = _x_<sup>2</sup>.

Once the representation is chosen, the _evolutionary operators_ must be specified. These operators define the mechanisms of _selection_, _variation_, and _replacement_ `[2]`. Selection determines how solutions are chosen to participate in the creation of new solutions. Variation determines how new solutions are created from existing solutions (i.e., reproduction) and how existing solutions are modified to explore new areas of the search space (i.e., mutation). Replacement determines how solutions are chosen to remain viable candidates. In some cases, one or more of these operators are simply identity functions, which means that they have no actual function. However, when viewed in this way, all of the EC approaches are simply variations on this basic theme `[2]`.

The basic EC is presented in the algorithm listing below. There, `P[t]` is a set of candidate solutions (the _population_) at time `t`. Typically, the population is of a fixed size. The `Evaluate()` function performs the mapping from genotype to phenotype space and assigns appropriate fitness values to each individual in the population. The `Selection()` function takes the current population and returns a set of individuals to be used for variation. The `Variation()` function takes that set of individuals and produces a set of new individuals, `offspring`. Finally, the `Replacement()` function performs the selection of individuals (chosen from the union of the original and modified individuals) which will make up the population in the next generation.

```
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
```

An important point of which to take note here is that the number of _function evaluations_ is critical when comparing two evolutionary computation algorithms. A function evaluation is simply one mapping from genotype to fitness. (The mapping is often called the _evaluation function_ or _fitness function_, so the term "function evaluations" is appropriate.) That is the typical processing unit used in the EC literature when referring to the efficiency of a particular algorithm.

According to Back et al `[2]`, the majority of current evolutionary computation implementations come from three different, but related, areas: genetic algorithms (GAs) `[8, 9, 10, 14]`, evolutionary programming (EPs) `[2, 5, 6]`, and evolution strategies (ESs) `[1, 6]`. However, as stated earlier, each area is defined by its choice of representation and/or operators. These choices are discussed in the following sections.

# Genetic Algorithms #
Genetic algorithms were first proposed by John Holland in the 1960's `[10]` in an attempt to leverage the power of natural selection to solve difficult optimization problems. In the canonical genetic algorithm, sometimes referred to as the _simple genetic algorithm_ (SGA) `[9, 14]`, the genotype for a candidate solution is represented as a binary string. The evaluation function is then a mapping from a binary string to some real-valued measure of fitness (as determined from the phenotype). As in all EC approaches, the fitness function is entirely problem-dependent.

The selection operator used in an SGA is _fitness proportionate selection_ `[9]`, sometimes called "roulette wheel" selection. In this type of selection, the probability of selecting a particular individual increases proportional to that individual's fitness. In some sense, the size of the individual's "roulette wheel section" increases with its fitness. In this way, the more fit an individual, the more likely it is to survive. However, this operator is stochastic, so it is possible that even the strongest individual will not survive (and, likewise, the weakest individual may survive).

A similar yet slightly more complex selection procedure is _remainder stochastic selection_. In this type of selection, any individual with an above average fitness is guaranteed to participate in creating the next generation of individuals, and the remaining slots are randomly assigned to individuals in a manner proportional to how well their fitness values compare to the average fitness. In this setup, the objective fitness for an individual (as determined by the fitness function) is modified to produce a relative fitness value as follows:

f<sup>_r_</sup><sub>_i_</sub> = f<sub>_i_</sub>/mean(f)

where f<sup>_r_</sup><sub>_i_</sub> is the relative fitness of individual _i_, f<sub>_i_</sub> is the objective fitness of individual _i_, and mean(f) is the average fitness of the current population.

Another popular selection method is _tournament selection_ `[9]`. In this type of selection, a subset of candidate solutions is chosen from the existing population against each of which the individual in question is compared (as if that individual is competing in a single-elimination tournament against all individuals in the subset). If the individual's fitness is better than all candidate solutions in the subset, then that individual is selected. The size of the subset (often called the _tournament size_ `[9]`) can be used to control the _selection pressure_ `[9]`.

After selection is performed, the participating individuals undergo variation through crossover and mutation. Each of these operators is performed according to some probability of occurrence (typically denoted _p<sub>c</sub>_ and _p<sub>m</sub>_, respectively) that must be specified as parameters to the system. The variation operators used in an SGA are single-point crossover `[9]` and bit-flip mutation `[9]`. In single-point crossover, two individuals (i.e., binary strings) are chosen, along with a single recombination point that determines the position in each string that will be "cut". The individuals are then recombined at that point to form two new individuals. This can be understood more clearly in the following example (where the vertical bar represents the recombination point):

```
Parent A: XXXXXXX | XX
Parent B: YYYYYYY | YY
Child 1 : XXXXXXXYY
Child 2 : YYYYYYYXX
```

This operation is applied to randomly selected parents with probability _p<sub>c</sub>_, which is typically set to be a fairly high (e.g., 0.75) value. Bit-flip mutation simply means that each bit in a newly created binary string is changed to the opposite value with probability _p<sub>m</sub>_, which is typically set to be a very low (e.g., 0.01) value.

The resultant population is made up entirely of the newly-created offspring. This is known as _generational replacement_ `[2]`, which means that no individuals from the previous generation are allowed to survive to the succeeding generations. This type of replacement strategy can be augmented with _elitism_ `[2]`, which would allow some proportion (as determined by system parameters) of the most fit individuals to survive into the next generation. Additionally, some genetic algorithms make use of _steady-state replacement_ `[2]`, in which only one offspring is created in a given generation, and this offspring always replaces the least-fit individual in the current population.

# Evolutionary Programming #
In the early 1960's, Lawrence Fogel attempted to use simulated evolution, which he called Evolutionary Programming (EP), to create artificial intelligence `[5, 6]`. In this seminal work, finite state machines (FSMs) were evolved to predict future symbols from a given input stream `[6]`. Using a FSM representation of the individuals in the population required novel variation operators. The following operators were used in the work: changing an output symbol, changing a state transition, adding a state, deleting a state, and changing a state. The fitness of a given FSM was determined by how accurate its predictions were, given the sequence of input symbols. More recently, EP approaches have been applied to real-valued, continuous optimization problems, but these approaches are similar to the approaches used in evolution strategies `[6]`, which are discussed below.

# Evolution Strategies #
At the same time that Holland was developing the genetic algorithm, Rechenberg was independently discovering a technique for using natural selection for optimization problems, which he termed _evolution strategies_ `[1]`. The simplest version of an evolution strategy (ES) is what is known as a _two-membered ES_ `[1]` or, more commonly, a (1+1)-ES. In this scenario, a single individual, represented as a vector of real values, comprises the population. At each generation, that individual is mutated (the variation operator) along each dimension using a Gaussian distribution with zero mean and a given variance (provided as a parameter to the system) to produce an offspring. The fitness values for both the parent and the offspring are compared, and the better of the two individuals is allowed to become the parent in the next generation.

It was discovered `[1]` that online adjustment of the mutation rate (i.e., the variance of the normal distribution) could provide better performance. This online adjustment is known as the _one-fifth success rule_ `[1]`, which states that around 1/5 of the mutations should be successful. If the actual number of successful mutations is greater than 1/5, increase the variance. If the number is less than 1/5, decrease the variance.

In addition to online adjustment of the variance, more sophisticated versions of evolution strategies can also include the particular variance as a part of the genotype to be evolved `[1]`. It is also possible to evolve and use a different variance along each dimension of the problem `[1]`, thus allowing the search for a solution to conform more appropriately to the topology of the search space. When variances are included in the genotype, an additional parameter is needed to serve as the variance used to mutate the evolved variances.

The (1+1)-ES did not truly make use of the idea of a population of individuals, so this concept was generalized and extended to yield the (_mu_+1)-ES `[1]`. In this system, a population of _mu_ individuals is maintained in each generation. Additionally, a reproduction operator is included that selects two (or more) individuals from this population and recombines them to form a new individual. This recombination is simply a random selection of each component from the parents. Once the new individual is created, it undergoes mutation as mentioned above. Finally, each offspring is added to the population if it is better than the least fit individual, producing the new population for the next generation. This approach can be and has been `[1]`, of course, extended to a (_mu_ + _lambda_)-ES, in which _mu_ individuals produce _lambda_ offspring. The best _mu_ individuals of the _mu_ + _lambda_ individuals are then chosen to survive.

It is also possible to provide somewhat of an analog to the generational replacement of a GA within an ES. This approach is known as a (_mu_, _lambda_)-ES (where _lambda_ must be greater than or equal to _mu_) `[1]`. In such a scenario, the _mu_ individuals are used to create _lambda_ offspring, and from those offspring only, _mu_ individuals are chosen to comprise the population in the next generation.

# Particle Swarm Optimization #
In addition to the evolutionary computation techniques described above, another nature-inspired optimization algorithm, called _particle swarm optimization_ (PSO), was developed by Kennedy and Eberhart in 1995 `[11]`. Inspired by the movement of bird flocks and insect swarms, they attempted to develop a model of swarm behavior that could be used to solve optimization problems. To create the analogy, they imagined a flock of birds flying around in search of a corn field. Each bird was capable of remembering the best location it had found, and each was capable of knowing the best location that any of the birds had found. The birds were allowed to fly around while being pulled toward both their individual best locations and the flock's best location. Kennedy and Eberhart found that their simulation of this analogy produced very realistic-looking behavior in their virtual flocks `[11]`.

In the PSO model presented in `[11]` and expanded in `[12]`, each particle is composed of three vectors: _x_, _p_, and _v_. These represent the particle's current location, best location found, and velocity, respectively. These vectors are each of the same dimensionality as the search space. Additionally, each particle maintains a two values: one corresponding to the fitness of the _x_ vector and the other to the fitness of the _p_ vector.

As the particles in the swarm move around the search space, their velocities are first updated according to the following equation:

v<sub>id</sub> = v<sub>id</sub> + _phi<sub>1</sub>_ R<sub>1</sub>(p<sub>id</sub> - x<sub>id</sub>) + _phi<sub>2</sub>_ R<sub>2</sub>(g<sub>id</sub> - x<sub>id</sub>)

In this equation, _v<sub>id</sub>_ is the velocity of the _i_<sup>th</sup> particle along the _d_<sup>th</sup> dimension. The _g_ vector represents the best location found by the flock, and R<sub>1</sub> and R<sub>2</sub> are uniform random values such that 0 <= R<sub>1</sub>,R<sub>2</sub> <= 1. Finally, _phi<sub>1</sub>_ and _phi<sub>2</sub>_ are two constants that control the influence of the personal best and the global best locations, respectively, on the particle's velocity. These values are often referred to as _cognitive_ and _social_ learning rates, respectively `[12]`.

After the velocity vector is updated, the particle's location is updated by applying the following equation:

x<sub>id</sub> = x<sub>id</sub> + v<sub>id</sub>

At this point, the new location's fitness is evaluated and compared to the fitness of the particle's personal best location. If the new location is better, then it also becomes the new personal best location for the particle.

The _topology_ for a swarm refers to the structure of the neighborhood for each particle. In a _star topology_, all the particles exist in the same neighborhood, so the global best vector represents the best location found by any particle in the swarm. In contrast, a _ring topology_ arranges the particles into overlapping neighborhoods of size _h_. The global best vector in this type of topology represents the best location found by any particle in that particle's neighborhood.

In 1999, Maurice Clerc introduced an improvement to the equation for updating the velocity of a particle `[3]`. He introduced a constant to be multiplied to the new velocity before updating the location of the particle. He called this constant the _constriction coefficient_ `[3]`. The calculation of this coefficient is as follows:

_K_ = 2 / |2 - _phi_ - sqrt(_phi_<sup>2</sup> - 4 _phi_)|

In this equation, _phi_ = _phi<sub>1</sub>_ + _phi<sub>2</sub>_ and _phi_ > 4. The constriction coefficient is used to restrain the velocity vector of each particle so that it does not grow unbounded.

Finally, various other models have been proposed as alternatives to the so-called full model presented above `[4]`. The _cognitive-only_ model sets _phi<sub>1</sub>_ to 0, while the _social-only_ model sets _phi<sub>2</sub>_ to 0. A _selfless_ model was also developed which was identical to the social-only model except that a particle's personal best was not included in the search for that particle's neighborhood's global best `[4]`.


# References #

`[1]` T. Back, F. Hoffmeister, and H.-P. Schwefel, "A survey of evolution strategies," in Proceedings of the 4th International Conference on Genetic Algorithms, R. K. Belew and L. B. Booker, Eds. Morgan Kaufman, 1991, pp. 2-9.

`[2]` T. Back, U. Hammel, and H.-P. Schwefel, "Evolutionary computation: Comments
on the history and current state," IEEE Transactions on Evolutionary Computation,
vol. 1, no. 1, pp. 3-17, apr 1997.

`[3]` M. Clerc, "The swarm and the queen: towards a deterministic and adaptive particle swarm optimization," in Proceedings of the International Conference on Evolutionary Computation, Washington, DC, 1999, pp. 1951-1957.

`[4]` R. C. Eberhart and Y. Shi, "Comparing inertia weights and constriction factors in particle swarm optimization," in Proceedings of the Congress on Evolutionary Computation, Washington, DC, 2000, pp. 84-88.

`[5]` L. J. Fogel, A. J. Owens, and M. J. Walsh, _Artificial intelligence through simulated evolution_. New York: Wiley, 1966.

`[6]` D. B. Fogel, "An introduction to simulated evolutionary optimization," IEEE Transactions on Neural Networks, vol. 5, no. 1, pp. 3-14, Jan. 1994.

`[7]` D. B. Fogel, "What is evolutionary computation?" IEEE Spectrum, vol. 37, no. 2, pp. 26-32, Feb. 2000.

`[8]` S. Forrest, "Genetic algorithms: principles of natural selection applied to computation," Science, vol. 60, pp. 872-878, Aug. 1993.

`[9]` D. E. Goldberg, _Genetic Algorithms in Search, Optimization and Machine Learning_. Reading, MA: Addison-Wesley Publishing Company, Inc., 1989.

`[10]` J. H. Holland, _Adaptation in Natural and Artificial Systems_. Ann Arbor, MI: University of Michigan Press, 1975.

`[11]` J. Kennedy and R. Eberhart, "Particle swarm optimization," in Proceedings of the IEEE Conference on Neural Networks, Perth, Australia, 1995, pp. 1942-1948.

`[12]` J. Kennedy, "The particle swarm: Social adaptation of knowledge," in Proceedings of the International Conference on Evolutionary Computation, Indianapolis, IN, 1997, pp. 303-308.

`[13]` Z. Michalewicz and D. B. Fogel, _How to Solve It: Modern Heuristics_. Springer, 2004.

`[14]` M. D. Vose, _The Simple Genetic Algorithm: Foundations and Theory_. MIT Press, 1999.