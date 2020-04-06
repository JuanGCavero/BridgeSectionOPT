"""
    Juan Gonzalez Cavero
    Master Thesis, Digital Engineering, Bauhaus Universität Weimar
"""

import numpy as np
import pandas as pd
import subprocess
import shutil
import datetime
import os
import multiprocessing as mp


def copy_geometry_files(directory):
    # Create folder if it does not exist
    if not os.path.exists(directory+r"\PopulationMasterFiles"):
        os.mkdir(directory+r"\PopulationMasterFiles")

    source = directory+r"\SimpleAnalysis"
    destination = directory+r"\PopulationMasterFiles"
    # Copy all files from SimpleAnalysis to PopulationMasterFiles for the shake of clearliness
    src_files = os.listdir(source)
    for file in src_files:
        shutil.copyfile(os.path.join(source, file), os.path.join(destination, file))


# Parameters must be transfer to Sofistik
def parameters_to_Sofistik(population, directory, parameters):
    # Create folder if it does not exist
    if not os.path.exists(directory+r"\PopulationMasterFiles\PopulationParameters"):
        os.mkdir(directory+r"\PopulationMasterFiles\PopulationParameters")
    for k, chromosome in enumerate(population):
        # The string starts with the Head title of the file
        row = '$PROG AQUA","HEAD Parameters\n'
        # We add to the string the name of each parameter and its value concatenated
        for i, parameter in enumerate(parameters):
            row = row+'STO#' + str(parameter) + ' ' + str(chromosome[i])+'\n'

        # The files are saved in .dat so Sofistik can read them
        filePath = directory+r"\PopulationMasterFiles\PopulationParameters\ParameterPopulation"+str(k+1)+".dat"
        print(row, file=open(filePath, 'w'))


# FEA is performed to each chromosome (section). For each chromosome we create a master file
def create_sofistik_master_file(directory, pop, generation):
    with open(directory+r"\masterDB.dat", 'r') as f:
        master = f.readlines()

    # Create directory to save results
    if not os.path.exists(directory+r"\PopulationMasterFiles\OptResults"):
        os.mkdir(directory+r"\PopulationMasterFiles\OptResults")

    shorten = 0
    if generation > 0:
        shorten = int(pop/2)

    for i in range(shorten, pop):
        # Sofistik calls parameterPopulaiton file from the master file
        # After the FEA, results are stored in diferent sheets of an excel
        # Read a list of lines into data, modify desired lines, write it back
        master[17] = "#include PopulationParameters\\ParameterPopulation"+str(i+1)+".dat\n"
        master[20] = "#include section.dat\n"
        master[33] = "#include axis.dat\n"
        master[36] = "#include structuralpoints.dat\n"
        master[37] = "#include structuralpointsgroup.dat\n"
        master[102] = "XLSX NAME 'OptResults\data"+str(generation+1)+".xlsx' WS 'W"+str(i+1)+"' ROW 1 COL 1 CLNM YES\n"
        master[107] = "XLSX NAME 'OptResults\data"+str(generation+1)+".xlsx' WS 'S"+str(i+1)+"' ROW 1 COL 1 CLNM YES\n"
        master[115] = "XLSX NAME 'OptResults\data"+str(generation+1)+".xlsx' WS 'D"+str(i+1)+"' ROW 1 COL 1 CLNM YES\n"
        with open(directory+r"\PopulationMasterFiles\masterPopulation"+str(i+1)+".dat", 'w') as master_file:
            master_file.writelines(master)

    files = []
    for i in range(shorten, pop):
        files.append([directory+r"\PopulationMasterFiles\masterPopulation"+str(i+1)+".dat", i+1])
    return files


def analyze_section(file):
    print("Analyzing section ", file[1])
    # sps.exe (Sofistik executable) is system enviroment variable to avoid problems
    subprocess.call(["sps.exe", file[0], "-B0"])


# The optimization takes a long time. Parallel processing is used to reduce the time
def parallel_processing(files, generation):
    start_time = datetime.datetime.now()

    # Parallel processing (uncomment next two lines to activate it, and comment serial loop)
    #with mp.Pool() as pool:
    #    pool.map(analyze_section, files)

    # Serial processing (ensures correct working)
    for i,file in enumerate(files):
        if generation > 0:
            analyze_section(file)
        else:
            analyze_section(file)

    end_time = datetime.datetime.now()
    print("Sofistik calculations = "+str(end_time-start_time))


# Sofistik write results into an excel. Important data (weight, stress, displacement) is retieved
# Besides, Sofistik suscribe the data in the same file. We want to store all the data.
def retrieve_results(directory, pop, generation):
    source = directory+r"\PopulationMasterFiles\OptResults\data"+str(generation+1)+".xlsx"

    cells = [["B", 1], ["I", 3], ["E", 2]]
    results = []

    shorten = 0
    if(generation>0):
        shorten = int(pop/2)

    for i in range (shorten, pop):
        
        data = []
        Wdata= pd.read_excel(source, sheet_name="W"+str(i+1), usecols=cells[0][0], header=cells[0][1])   # Weight
        Sdata = pd.read_excel(source, sheet_name="S"+str(i+1), usecols=cells[1][0], header=cells[1][1])  # Stress
        Ddata = pd.read_excel(source, sheet_name="D"+str(i+1), usecols=cells[2][0], header=cells[2][1])  # Displacement
        results.append([Wdata.columns.values[0], Sdata.columns.values[0], Ddata.columns.values[0]])

    results = np.reshape(results, ((len(results), 3)))
    return results

def store_fitness(directory, fitness, generation):
    print(fitness, file=open(directory+r"\PopulationMasterFiles\OptResults\fitness"+str(generation+1)+".txt", 'w'))

