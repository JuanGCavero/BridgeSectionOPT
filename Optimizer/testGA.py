"""
    Juan Gonzalez Cavero
    Master Thesis, Digital Engineering, Bauhaus Universität Weimar

    Bridge cross section optimization by means of Genetic Algorithm and Sofistik's analysis
    Needed: Dynamo (Reivt), Python 3 and Sofistik 2020 (or 2018: modify URL)

    This script produces diferent combinations of parameters, according to some designing constraint
    and send them to Sofistik, which in turn, analyse a specific bridge with the transferred section
    parameters (FEA). Analysis results are returned to perform some GA operations and keep the loop.

    Designing parameter constrains, penalties and control values are defined in Dynamo and written to a txt.
    That data sets the properties of the GA and is read from the txt file by this script.
"""

"""
The y=target is to minimize a function (too complex to be defined in a mathematical expresion):
    y = f(x1,x2,x3,x4,x5,x6):
        where xi are the design parameter constrains of a bridge cross section [meters]:
        - Beam_Height           [0.30 - 0.60]
        - Beam_Thickness        [0.01 - 0.04]
        - Lane_Width            [1.50]
        - Parapet_Thickness     [0.10 - 0.16]
        - Parapet_Width         [0.30 - 0.60]
        - Slab_Thickness        [0.10]
    What are the best values for the 4 weights x1 to x4?
    A genetic algorithm is utilized in order to find the best (or close) possible values.

    # Allowable_stress = 275/1.1      # Steel S-275
    # Penalties (fictive weights that are applied when the stress or displacement are not within the min/max range)
    # Ratio range and thresholds (control values) set the GA for optimal design
"""
"""
Genetic algorithm parameters:
    Chromosomes: the higher number, higher diversity. So need less generations. Takes longer.
    Number of generations: or number of loops the GA runs. The higher, higher precision.
"""

# Import packages
import numpy as np
import datetime
import os
import copy

# Import definitions
import gaSofiLink
import gaOperations


# Chronometer
start_time = datetime.datetime.now()

#directory = os.path.dirname(os.path.abspath(__file__))
directory = r"C:\Users\juan_\Documents\Digital_Engineering\Semester_5\Masther_Thesis\Dynamo_v\simpleOPT_v6 - Report"

# File from Dynamo: Parameters
parameters = []
with open(directory+r"\parametersName.txt", "r") as f:
    parameters = [item for item in f.readlines()]
parameters = [item.replace("\n", "") for item in parameters]

# File from Dynamo: Contrains and penalties
lower_limits = []
upper_limits = []
with open(directory+r"\toPython.txt", 'r') as f:
    inputs = f.readlines()
inputs = [item.replace("\n", "") for item in inputs]
number_generations = int(inputs[0])
chromosomes = int(inputs[1])
lower_limits = [float(inputs[i]) for i in range(2, 8)]
upper_limits = [float(inputs[i]) for i in range(8, 14)]
allowable_stress = float(inputs[14])
min_penalty_stress = int(inputs[15])
max_penalty_stress = int(inputs[16])
min_stress_ratio = float(inputs[17])
max_stress_ratio = float(inputs[18])
max_penalty_displacement = int(inputs[19])
max_displacement = float(inputs[20])

# Penalties and respective ratios thresholds are grouped
penalties = [[min_penalty_stress, min_stress_ratio],
             [max_penalty_stress, max_stress_ratio],
             [max_penalty_displacement, max_displacement]]

# Files to run FEA in Sofistik are copied (they will be modified), so originals are conserved.
gaSofiLink.copy_geometry_files(directory)

# GA settings
genes = len(parameters)
num_parents_mating = int(chromosomes/2)   # For many chromosomes, chromosomes/2 might not be the best n#.
pop_size = (chromosomes, genes)           # Population are made of chromosomes, which consist in genes.

# Creating the initial population
print("Initialize Population")
new_population = np.round(np.random.uniform(lower_limits, upper_limits, size=pop_size), decimals=4)

if __name__ == '__main__':
    
    # Link parameters to Sofistik
    gaSofiLink.parameters_to_Sofistik(new_population, directory, parameters)

    # Sofistik master files are created
    file_names = gaSofiLink.create_sofistik_master_file(directory, new_population.shape[0], 0)

    # Sections are anaized by Sofistik
    print("Evaluate Population...")
    gaSofiLink.parallel_processing(file_names, 0)

    # Results from Sofistik are restrieved (Sofistik stores them in an excel)
    results = gaSofiLink.retrieve_results(directory, new_population.shape[0], 0)

    # Calculate the fitness of each chromosome in the population.
    fitness_value = gaOperations.calc_fitness(results, allowable_stress, penalties)
    fitness_value_copy = copy.deepcopy(fitness_value)
    print("Fitness: ",fitness_value)
    print("\nBest fitness: ", np.min(fitness_value))

    # Stores fitness values in folder
    gaSofiLink.store_fitness(directory, fitness_value, 0)

    # After evaluation, the loop starts
    for generation in range(1,number_generations):
        print("\nGeneration:", generation)

        # Selecting the best parents in the population for mating
        parents = gaOperations.select_parents(new_population, fitness_value, num_parents_mating)

        # Generateoffspring using crossover
        offspring_crossover = gaOperations.crossover(parents[0], offspring_size=(pop_size[0]-parents[0].shape[0], genes))

        # Modify offsrping using mutation
        offspring_mutation = gaOperations.mutation(offspring_crossover, lower_limits, upper_limits)

        # Creating the new population based on the parents and offspring
        new_population[0:parents[0].shape[0], :] = parents[0]
        new_population[parents[0].shape[0]:, :] = offspring_mutation

        # Link parameters to Sofistik
        gaSofiLink.parameters_to_Sofistik(new_population, directory, parameters)

        # Sofistik master files are created
        file_names = gaSofiLink.create_sofistik_master_file(directory, new_population.shape[0], generation)

        # Sections are analized by Sofistik
        print("Evaluate Population...")
        gaSofiLink.parallel_processing(file_names, generation)

        # Results from Sofistik are retrieved (Sofistik stores them in an excel)
        results = gaSofiLink.retrieve_results(directory, new_population.shape[0], generation)

        # Calculate the fitness of each chromosome in the population.
        fitness_value = gaOperations.calc_fitness(results, allowable_stress, penalties)

        fitness_value = np.concatenate((fitness_value_copy[parents[1]], fitness_value), axis=0)
        fitness_value_copy = copy.deepcopy(fitness_value)

        # Stores fitness values in folder
        gaSofiLink.store_fitness(directory, fitness_value, generation)

        # Find index for minimal fitness values
        min_fit_idx = np.where(fitness_value == np.min(fitness_value))
        min_fit_idx = min_fit_idx[0][0]

        # The best result in the current iteration.
        print("Fitness values of generation: ", fitness_value)
        print("\nBest fitness: ", np.min(fitness_value)," for = ", new_population[min_fit_idx])

    # Save optimized parameters
    opt_parameters = ''.join(str(e)+"\n" for e in new_population[min_fit_idx])
    print(opt_parameters, file=open(directory+r"\toDynamo.txt", 'w'))

    end_time = datetime.datetime.now()
    print("\nProcess duration = ", str(end_time-start_time))