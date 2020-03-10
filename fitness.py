# Fitness function

import numpy as np
import pandas as pd
import subprocess
import shutil
import datetime

"""
As stated in the testGA, the y=target is to minimize:
	y = f(x1,x2,x3,x4)
	To asses this one, we use a Fitness function that depends on the analytical results derived from the FEM application.
	Fitness(x) = f(w,s,d) 		# Weight, Stress, Displacement
	We obtain the Fitness value for each of the chromosomes (x) that form the population.
"""

# parameters = ["Parapet_Height", "Beam_Width", "Slab_Height", "Parapet", "Lane", "Beam_Height"]

# Parameters must be transfer to Sofistik
def parameters_to_Sofistik(population, directory, parameters):
    for k, element in enumerate(population):
        # The string starts with the Head title of the file
        row='$PROG AQUA","HEAD Parameters\n'
        # We add to the string the name of each parameter and its value concatenated
        for i, parameter in enumerate(parameters):
            row=row+'STO#' + str(parameter) + ' ' + str(element[i])+'\n'

        # The files are saved in .dat so Sofistik can read them
        filePath = directory+r"\ParameterPopulation"+str(k+1)+".dat"
        print(row, file=open(filePath, 'w'))


def analyse_section(directory, pop):
	# to avoid problems sps.exe (Sofistik's FEM calculation executable) was set as a system enviroment variable
	# otherwise, the complete directory for sps.exe must be input
	print("SOFiSTiK SPS - Copyright (C) 1997 - 2019, SOFiSTiK AG, Version 2.0.527")
	start_time = datetime.datetime.now()
	for i in range(pop):
		file = directory+r"\sp-short"+str(i+1)+".dat"
		print("Analysing cross section "+str(i+1)+" of "+str(pop))
		subprocess.call(["sps.exe",file, "-B0"])
	end_time = datetime.datetime.now()
	print("Sofistik calculations = "+str(end_time-start_time))


# Sofistik write results into an excel. Important data (weight, stress, displacement) is retieved
# Besides, Sofistik suscribe the data in the same file. We want to store all the data.
def retrieve_results(directory, pop, generation):
    cells=[["B",1],["I",3],["E",2]]*pop	# Specific values to consider for each chromosome
    source = directory+r"\data.xlsx"
    destination = directory+r"\dataGeneration"+str(generation)+".xlsx"
	# Copy the content of source to destination
    shutil.copyfile(source, destination) 

    results=[]
    for i in range(pop*3):
        data = pd.read_excel(source, i+1, index_col=None, usecols = cells[i][0], header=cells[i][1], nrows=0)
        results.append(data.columns.values[0])
	# Results are reshaped [Population_size, results(Weight, Stress and Displazement)]
    results=np.reshape(results,(pop,3))
    return results


""" 
# Set the maximal allowable stress
allowable_stress = 275/1.1 # Steel S-275
# Set the penalty weight, which is the fictive weight that will be applied when the stress ratio is not within the min/max range.
min_penalty_stress = 20
max_penalty_stress = 50
max_penalty_displacement = 40
# Ratio range for optimal design
min_stress_ratio = 0.8
max_stress_ratio = 1
max_displacement = 10 # mm
penalties = [[min_penalty_stress, max_penalty_stress, max_penalty_displacement],
			[min_stress_ratio, max_stress_ratio, max_displacement = 10]] 
"""

"""
	Population contains all parameters...
	Results contains the analytical results from Sofistik: weight(kg/m), stress (MPa), midspan displacement (mm)
	Penalties contains the penalizations that are applied to the results and the repective thresholds
"""


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


#Assign your output to the OUT variable.