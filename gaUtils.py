"""
    Juan Gonzalez Cavero
    Master Thesis, Digital Engineering, Bauhaus Universität Weimar
"""

import numpy as np
import random

def select_mating_pool(population, fitness, num_parents):
    # Selecting the best individuals in the current generation as parents for producing the offspring of the next generation.
    parents = np.empty((num_parents, population.shape[1]))
    for parent_num in range(num_parents):
        max_fitness_idx = np.where(fitness == np.min(fitness))     # This is minimization problem
        max_fitness_idx = max_fitness_idx[0][0]
        parents[parent_num, :] = population[max_fitness_idx, :]
        fitness[max_fitness_idx] = 99999999999
    return parents


def crossover(parents, offspring_size):
    offspring = np.empty(offspring_size)

    # Best parents have more chances to be crossovered
    probability = np.flip(np.arange(1,parents.shape[0]+1))
    probability = probability/(np.sum(probability))
        
    for k in range(offspring_size[0]):
        # Crossover takes place at a random point to create offsprings of different parents.
        crossover_point = np.random.randint(1,offspring_size[1]/2)      # Remember: Last two parameters = const

        # Index of the first parent to mate.
        father = np.random.choice(np.arange(0, parents.shape[0]), p=probability)
        # Index of the second parent to mate.
        mother = np.random.choice(np.arange(0, parents.shape[0]), p=probability)

        # There is a chance parents are the same. This reduce diversity and must be avoided.
        while father == mother:
            father = np.random.choice(np.arange(0, parents.shape[0]), p=probability)
            mother = np.random.choice(np.arange(0, parents.shape[0]), p=probability)

        # The new offspring will have its first half of its genes taken from the first parent.
        offspring[k, 0:crossover_point] = parents[father, 0:crossover_point]
        # The new offspring will have its second half of its genes taken from the second parent.
        offspring[k, crossover_point:] = parents[mother, crossover_point:]
    return offspring

def mutation(offspring_crossover):
    # Mutation changes a single gene in each offspring randomly.
    for idx in range(offspring_crossover.shape[0]):
        # The random value to be added to the gene.
        random_value = np.random.uniform(-1.0, 1.0, 1)
        offspring_crossover[idx, 4] = offspring_crossover[idx, 4] + random_value
    return offspring_crossover