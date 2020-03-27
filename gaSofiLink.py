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
import os

def copy_geometry_files(directory):
    source = directory+r"\SimpleAnalysis"
    if not os.path.exists(directory+r"\PopulationMasterFiles"):
    	os.mkdir(directory+r"\PopulationMasterFiles")
    destination = directory+r"\PopulationMasterFiles"
	# Copy all files from SimpleAnalysis to PopulationMasterFiles for the shake of clearliness
    src_files = os.listdir(source)
    for file in src_files:
        shutil.copyfile(os.path.join(source,file), os.path.join(destination,file))
	
	

# Parameters must be transfer to Sofistik
def parameters_to_Sofistik(population, directory, parameters):
    for k, chromosome in enumerate(population):
        # The string starts with the Head title of the file
        row='$PROG AQUA","HEAD Parameters\n'
        # We add to the string the name of each parameter and its value concatenated
        for i, parameter in enumerate(parameters):
            row=row+'STO#' + str(parameter) + ' ' + str(chromosome[i])+'\n'

        # The files are saved in .dat so Sofistik can read them
        filePath = directory+r"\PopulationMasterFiles\PopulationParameters\ParameterPopulation"+str(k+1)+".dat"
        print(row, file=open(filePath, 'w'))

# FEA is performed to each chromosome (section)
def analyse_section(directory, pop):
	start_time = datetime.datetime.now()
	filename = directory+r"\masterDB.dat"
	f = open(filename,"r")
	master = f.readlines()
	f.close
	for i in range(pop):
		# Sofistik calls parameterPopulaiton (stored in files) from the master file. Set chromosomes
		# After the FEA, results are stored in diferent sheets of an excel

		# Read a list of lines into data, modify desired lines, write it back
		master[17] = "#include PopulationParameters\\ParameterPopulation"+str(i+1)+".dat\n"
		master[20] = "#include section.dat\n"
		master[33] = "#include axis.dat\n"
		master[36] = "#include structuralpoints.dat\n"
		master[37] = "#include structuralpointsgroup.dat\n"
		master[102] = "XLSX NAME 'data.xlsx' WS 'W"+str(i+1)+"' ROW 1 COL 1 CLNM YES\n"
		master[107] = "XLSX NAME 'data.xlsx' WS 'S"+str(i+1)+"' ROW 1 COL 1 CLNM YES\n"
		master[115] = "XLSX NAME 'data.xlsx' WS 'D"+str(i+1)+"' ROW 1 COL 1 CLNM YES\n"
		with open(directory+r"\PopulationMasterFiles\masterPopulation"+str(i+1)+".dat", 'w') as file:
			file.writelines(master)

	for i in range(pop):	
		print("Analysing cross section "+str(i+1)+" of "+str(pop))
		# sps.exe (Sofistik executable) is system enviroment variable to avoid problems
		subprocess.call(["sps.exe",directory+r"\PopulationMasterFiles\masterPopulation"+str(i+1)+".dat", "-B0"])

	end_time = datetime.datetime.now()
	print("Sofistik calculations = "+str(end_time-start_time))


# Sofistik write results into an excel. Important data (weight, stress, displacement) is retieved
# Besides, Sofistik suscribe the data in the same file. We want to store all the data.
def retrieve_results(directory, pop, generation):
    cells=[["B",1],["I",3],["E",2]]*pop	# Specific values to consider for each chromosome
    source = directory+r"\PopulationMasterFiles\data.xlsx"
    if not os.path.exists(directory+r"\PopulationMasterFiles\OptResults"):
    	os.mkdir(directory+r"\PopulationMasterFiles\OptResults")
    destination = directory+r"\PopulationMasterFiles\OptResults\dataGeneration"+str(generation)+".xlsx"
	# Copy the content of source to destination
    shutil.copyfile(source, destination)

    results=[]
    for i in range(pop*3):
        data = pd.read_excel(source, i+1, index_col=None, usecols = cells[i][0], header=cells[i][1], nrows=0)
        results.append(data.columns.values[0])
	# Results are reshaped [Population_size, results(Weight, Stress and Displazement)]
    results=np.reshape(results,(pop,3))
    return results
