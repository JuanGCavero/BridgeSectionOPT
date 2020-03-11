"""
    Juan Gonzalez Cavero
    Master Thesis, Digital Engineering, Bauhaus Universität Weimar

    Bridge cross section optimization by means of Genetic Algorithm and Sofistik's analysis
    Needed: Python 3 and Sofistik 2020 (or 2018: modify URL)

    This script produces diferent combinations of parameters, according to some designing constraint
    and send them to Sofistik, which in turn, analyse a specific bridge with the transferred section
    parameters (FEA). Analysis results are returned to perform some GA operations and keep the loop.

"""

"""
The y=target is to minimize a function (too complex to be defined in a mathematical expresion):
    y = f(x1,x2,x3,x4):
        where xi are the constrained parameters of a bridge cross section [meters]:
        - Parapet_Thickness     [0.10 - 0.16]
        - Parapet_Length        [0.02 - 0.05]
        - Beam_Thickness        [0.10 - 0.30]
        - Beam_Height           [0.30 - 0.60]
        - Lane                  [1.5]
        - Beam_Height           [0.8]
    What are the best values for the 4 weights x1 to x4?
    A genetic algorithm is utilized in order to find the best (or close) possible values.
"""

# Import packages
import numpy as np
import datetime

# Import definitions
import gaFitness
import gaUtils


# Chrono optimization
start_time = datetime.datetime.now()

directory=r"C:\Users\juan_\Documents\Digital_Engineering\Semester_5\Masther_Thesis\Dynamo_v\simpleOPT_v4"

"""
Designing parameters:
    Parameters and their constrains are given by the problem.
    The allowable stress is also given by the material tensile strength.
    Penalties and control values might be modified (and more can be added)
"""

parameters= ["Parapet_Height", "Beam_Width", "Slab_Height", "Parapet", "Lane", "Beam_Height"]

# Parameter Constrains
lower_limits=[0.10,0.02,0.1,0.3,1.5,0.8]
upper_limits=[0.16,0.05,0.3,0.6,1.5,0.8]

# Designing specifications to penalize bad results
allowable_stress = 275/1.1      # Steel S-275
# Penalization (fictive weights that will be applied when the stress or displacement are not within the min/max range)
min_penalty_stress = 20
max_penalty_stress = 50
max_penalty_displacement = 40
# Ratio range and thresholds (control values) for optimal design
min_stress_ratio = 0.6
max_stress_ratio = 1
max_displacement = 10 # mm

penalties = [[min_penalty_stress, min_stress_ratio],
            [max_penalty_stress, max_stress_ratio],
            [max_penalty_displacement, max_displacement]]

"""
Genetic algorithm parameters:
    Chromosomes: the higher, higher diversity. Need less generations. Takes longer.
    num_parents_mating: best chromosomes of generation, they act as parents, they survive current generation
"""

chromosomes = 20 # Must be even, minimum 4
genes = len(parameters)
num_parents_mating = int(chromosomes/2)   # Best parents survive. For ++ > chromosomes, chromosomes/2 might not be the best n#.

# Defining the population size.
pop_size = (chromosomes, genes) # Population is formed of chromosomes, which consist in genes.
#Creating the initial population.
new_population = np.random.uniform(lower_limits, upper_limits, size=pop_size)


num_generations = 5
for generation in range(num_generations):
    print("Generation : ", generation)

    # Link parameters to Sofistik
    gaFitness.parameters_to_Sofistik(new_population, directory, parameters)

    # The section is analysed in Sofistik
    gaFitness.analyse_section(directory, new_population.shape[0])

    # Results from Sofistik are restrieved (Sofistik stores them in an excel)
    results = gaFitness.retrieve_results(directory, new_population.shape[0], generation)

    # Calculate the fitness of each chromosome in the population.
    fitness = gaFitness.cal_pop_fitness(new_population.shape[0], results, allowable_stress, penalties)
    best_fitness = np.min(fitness)

    # Selecting the best parents in the population for mating.
    parents = gaUtils.select_mating_pool(new_population, fitness, num_parents_mating)
    

    # Generating next generation using crossover.
    offspring_crossover = gaUtils.crossover(parents, offspring_size=(pop_size[0]-parents.shape[0], genes))

    # Adding some variations to the offsrping using mutation. Not implemented yet
    #offspring_mutation = ga.mutation(offspring_crossover)

    # Creating the new population based on the parents and offspring.
    new_population[0:parents.shape[0], :] = parents
    new_population[parents.shape[0]:, :] = offspring_crossover

    # The best result in the current iteration.
    print("\nBest result : ", new_population[0])
    print("Fitness = ", best_fitness)

# Getting the best solution after iterating finishing all generations.
# At first, the fitness is calculated for each solution in the final generation.
gaFitness.parameters_to_Sofistik(new_population, directory, parameters)
print("Generation : ", num_generations)
gaFitness.analyse_section(directory, new_population.shape[0])
results = gaFitness.retrieve_results(directory, new_population.shape[0], (num_generations+1))
fitness = gaFitness.cal_pop_fitness(new_population.shape[0], results, allowable_stress, penalties)
best_fitness = np.max(fitness)
# Then return the index of that solution corresponding to the best fitness.
parents = gaUtils.select_mating_pool(new_population, fitness, num_parents_mating)

best_fitness = np.min(fitness)
print("\nBest solution : ", parents[0])
print("Fitness = ", best_fitness)

end_time = datetime.datetime.now()
print("\nProcess duration = ", str(end_time-start_time))