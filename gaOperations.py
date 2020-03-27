"""
    Juan Gonzalez Cavero
    Master Thesis, Digital Engineering, Bauhaus Universität Weimar
"""

import numpy as np
import random

"""
As stated in the testGA, the y=target is to minimize:
	y = f(x1,x2,x3,x4)
	To asses this one, we use a Fitness function that depends on the analytical results derived from the FEA
	Fitness(x) = f(w,s,d) 		# Weight, Stress, Displacement
	We obtain the Fitness value for each chromosomes (x) that form the population.

	Pop contains number of chromosomes
	Results contains the analytical results from Sofistik: weight(kg/m), stress (MPa), midspan displacement (mm)
	Penalties contains the penalizations that are applied to the results w.r.t their control values
"""

# Fitness of each chromosome is calculated
def cal_pop_fitness(pop, results,allowable_stress, penalties):
	weight_score=np.empty(pop)

	# Remember results contains Weight, Stress and Displacement in each column
	for i in range(pop):
		weight_score[i]=results[i][0]						# real weight
		stress_ratio = results[i][1] / allowable_stress
		
		if stress_ratio < penalties[0][1]:
			weight_score[i]=weight_score[i]+penalties[0][0]
		if stress_ratio > penalties[1][1]:
			weight_score[i]=weight_score[i]+penalties[1][0]
		if results[i][2] > penalties[2][1]:
			weight_score[i]=weight_score[i]+penalties[2][0]
	return weight_score


def select_mating_pool(population, fitness, num_parents):
    # Selecting the best individuals in the current generation as parents for producing the offspring of the next generation.
    parents = np.empty((num_parents, population.shape[1]))
    for parent_num in range(num_parents):
        min_fitness_idx = np.where(fitness == np.min(fitness))     # This is minimization problem
        min_fitness_idx = min_fitness_idx[0][0]
        parents[parent_num, :] = population[min_fitness_idx, :]
        fitness[min_fitness_idx] = 999999999                       
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