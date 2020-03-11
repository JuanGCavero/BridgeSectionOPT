"""
    Juan Gonzalez Cavero
    Master Thesis, Digital Engineering, Bauhaus Universität Weimar
"""

import numpy as np
import pandas as pd
import subprocess
import shutil
import datetime
import fileinput

# Parameters must be transfer to Sofistik
def parameters_to_Sofistik(population, directory, parameters):
    for k, chromosome in enumerate(population):
        # The string starts with the Head title of the file
        row='$PROG AQUA","HEAD Parameters\n'
        # We add to the string the name of each parameter and its value concatenated
        for i, parameter in enumerate(parameters):
            row=row+'STO#' + str(parameter) + ' ' + str(chromosome[i])+'\n'

        # The files are saved in .dat so Sofistik can read them
        filePath = directory+r"\ParameterPopulation"+str(k+1)+".dat"
        print(row, file=open(filePath, 'w'))

# FEA is performed to each chromosome (section)
def analyse_section(directory, pop):
	start_time = datetime.datetime.now()
	for i in range(pop):

		filename = directory+r"\sp-short.dat"

		# Sofistik call sections (stored in files) from the main file sp-short.dat. Set chromosomes
		# After the FEA, results are stored in diferent sheets of an excel

		# Read a list of lines into data, modify desired lines, write it back
		with open(filename, 'r') as file:
			data = file.readlines()
		data[17] = "#include parameterPopulation"+str(i+1)+".dat\n"
		data[103] = "XLSX NAME 'data.xlsx' WS 'W"+str(i+1)+"' ROW 1 COL 1 CLNM YES\n"
		data[108] = "XLSX NAME 'data.xlsx' WS 'S"+str(i+1)+"' ROW 1 COL 1 CLNM YES\n"
		data[116] = "XLSX NAME 'data.xlsx' WS 'D"+str(i+1)+"' ROW 1 COL 1 CLNM YES\n"
		with open(filename, 'w') as file:
			file.writelines(data)

		print("Analysing cross section "+str(i+1)+" of "+str(pop))
		# sps.exe (Sofistik executable) is system enviroment variable to avoid problems
		subprocess.call(["sps.exe",filename, "-B0"])

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

