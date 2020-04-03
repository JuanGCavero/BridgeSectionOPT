"""
    Juan Gonzalez Cavero
    Master Thesis, Digital Engineering, Bauhaus Universität Weimar
"""

"""
As stated in the testGA, the y=target is to minimize:
    y = f(x1,x2,x3,x4,x5,x6)
    To asses this one, we use a Fitness function that depends on the analytical results derived from the FEA
    Fitness(x) = f(w,s,d) 		# Weight, Stress, Displacement
    We obtain the Fitness value for each chromosomes (x) that form the population.  
    Pop contains number of chromosomes
    Results contains the analytical results from Sofistik: weight(kg/m), stress (MPa), midspan displacement (mm)
    Penalties contains the penalizations that are applied to the results w.r.t their control values
"""

import numpy as np


# Fitness of each chromosome is calculated
def calc_fitness(results, allowable_stress, penalties):
    weight_score = np.empty(results.shape[0])
    # Remember results contains Weight, Stress and Displacement in each column
    for i in range(results.shape[0]):
        weight_score[i] = results[i][0]						# real weight
        stress_ratio = results[i][1] / allowable_stress

        if stress_ratio < penalties[0][1]:
            weight_score[i] = weight_score[i]+penalties[0][0]
        if stress_ratio > penalties[1][1]:
            weight_score[i] = weight_score[i]+penalties[1][0]
        if results[i][2] > penalties[2][1]:
            weight_score[i] = weight_score[i]+penalties[2][0]
    return weight_score


def select_parents(population, fitness, num_parents):
    # Select best chromosomes in current generation as parents
    parents = np.empty((num_parents, population.shape[1]))
    for parent_num in range(num_parents):
        min_fitness_idx = np.where(fitness == np.min(fitness))    # Minimization problem
        min_fitness_idx = min_fitness_idx[0][0]
        parents[parent_num] = population[min_fitness_idx]         # Best chromosome is add to parent
        fitness[min_fitness_idx] = 9999                           # Its fitness replaced so is not called again
    return parents


def crossover(parents, offspring_size):
    offspring = np.empty(offspring_size)

    # Best parents have more chances to be crossovered
    probability = np.flip(np.arange(1, parents.shape[0]+1))
    probability = probability/(np.sum(probability))

    for k in range(offspring_size[0]):
        # Crossover takes place at a random point to create offsprings of different parents.
        crossover_point = np.random.randint(1, parents.shape[1])

        # Index of the first parent to mate.
        father = np.random.choice(np.arange(0, parents.shape[0]), p=probability)
        # Index of the second parent to mate.
        mother = np.random.choice(np.arange(0, parents.shape[0]), p=probability)

        # There is a chance parents are the same. This reduce diversity and must be avoided.
        safe_stop = 0          # In case father = mother because there are only two parents.
        while father == mother & safe_stop < 10:
            father = np.random.choice(np.arange(0, parents.shape[0]), p=probability)
            mother = np.random.choice(np.arange(0, parents.shape[0]), p=probability)
            safe_stop += 1

        # The new offspring will have its first half of its genes taken from the first parent.
        offspring[k, 0:crossover_point] = parents[father, 0:crossover_point]
        # The new offspring will have its second half of its genes taken from the second parent.
        offspring[k, crossover_point:] = parents[mother, crossover_point:]
    return offspring


# Mutation changes a single gene in each offspring_crossover within the limits.
def mutation(offspring_crossover, lower_limits, upper_limits):
    for i in range(offspring_crossover.shape[0]):
        # A gene is randomly chosen
        gene = np.random.randint(1, offspring_crossover.shape[1])
        # The gene mutates
        offspring_crossover[i, gene] = np.round(np.random.uniform(lower_limits[gene], upper_limits[gene]), decimals=4)
    return offspring_crossover
