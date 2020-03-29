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
    source = directory+r"\SimpleAnalysis"
    if not os.path.exists(directory+r"\PopulationMasterFiles"):
        os.mkdir(directory+r"\PopulationMasterFiles")
    destination = directory+r"\PopulationMasterFiles"
    # Copy all files from SimpleAnalysis to PopulationMasterFiles for the shake of clearliness
    src_files = os.listdir(source)
    for file in src_files:
        shutil.copyfile(os.path.join(source, file), os.path.join(destination, file))


# Parameters must be transfer to Sofistik
def parameters_to_Sofistik(population, directory, parameters):
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
def create_sofistik_master_file(directory, pop):
    filename = directory+r"\masterDB.dat"
    f = open(filename, "r")
    master = f.readlines()
    f.close
    for i in range(pop):
        # Sofistik calls parameterPopulaiton file from the master file
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

    files = []
    for i in range(pop):
        files.append([directory+r"\PopulationMasterFiles\masterPopulation"+str(i+1)+".dat", i+1])
    return files


def analyze_section(file):
    print("Analyzing section ", file[1])
    # sps.exe (Sofistik executable) is system enviroment variable to avoid problems
    subprocess.call(["sps.exe", file[0], "-B0"])


# The optimization takes a long time. Parallel processing is used to reduce the time
def parallel_processing(files):
    start_time = datetime.datetime.now()

    # with mp.Pool() as pool:
    #    pool.map(analyze_section, files)

    for file in files:
        analyze_section(file)

    end_time = datetime.datetime.now()
    print("Sofistik calculations = "+str(end_time-start_time))


# Sofistik write results into an excel. Important data (weight, stress, displacement) is retieved
# Besides, Sofistik suscribe the data in the same file. We want to store all the data.
def retrieve_results(directory, pop, generation):
    cells = [["B", 1], ["I", 3], ["E", 2]] * pop        # Specific values to consider for each chromosome
    source = directory+r"\PopulationMasterFiles\data.xlsx"
    # Create directory to save opt results
    if not os.path.exists(directory+r"\PopulationMasterFiles\OptResults"):
        os.mkdir(directory+r"\PopulationMasterFiles\OptResults")
    destination = directory+r"\PopulationMasterFiles\OptResults\dataGeneration"+str(generation)+".xlsx"
    # Copy the content of source to destination
    shutil.copyfile(source, destination)

    results = []
    cells = [["B", 1], ["I", 3], ["E", 2]]
    w_data = [pd.read_excel(source, sheet_name="W"+str(i), usecols=cells[0][0], header=cells[0][1]) for i in range(1, pop+1)]
    s_data = [pd.read_excel(source, sheet_name="S"+str(i), usecols=cells[1][0], header=cells[1][1]) for i in range(1, pop+1)]
    d_data = [pd.read_excel(source, sheet_name="D"+str(i), usecols=cells[2][0], header=cells[2][1]) for i in range(1, pop+1)]

    results.append([w_data[i].columns.values[0] for i in range(0, pop)])
    results.append([s_data[i].columns.values[0] for i in range(0, pop)])
    results.append([d_data[i].columns.values[0] for i in range(0, pop)])

    results = np.reshape(np.transpose(results), (4,3))
    return results
