############################################################################
#  Codice per automatizzare la ricostruzione dei dati delle camere di LNL  #
#  autore  : Davide Pagano (davide.pagano@unibs.it)                        #
#  versione: 1.1 (7 Marzo 2025)                                            #
############################################################################

import os
import re
import subprocess

cartella_sw = "/home/almalinux/PC/Software"
cartella_dati = "/mnt/muotom-data/data/castor/datatest"
data_tag = "cosmiciorand"
mixer_max_event = 1000000

##########################
# creo files di supporto #
##########################
print(">>> Creo files di supporto")
with open(cartella_sw + "/PreProcess/run/runPreProcesst0.sh", "w") as f:
    f.write("#!/bin/bash \n")
    f.write("cd " + cartella_sw + "/PreProcess/run \n")
    f.write("make \n")
    f.write("./runPreProcess t0 \n")
os.system("chmod +x " + cartella_sw + "/PreProcess/run/runPreProcesst0.sh")

with open(cartella_sw + "/PreProcess/run/runPreProcessNoise.sh", "w") as f:
    f.write("#!/bin/bash \n")
    f.write("cd " + cartella_sw + "/PreProcess/run \n")
    f.write("make \n")
    f.write("./runPreProcess noise \n")
os.system("chmod +x " + cartella_sw + "/PreProcess/run/runPreProcessNoise.sh")

with open(cartella_sw + "/DTFitter/run/runDT.sh", "w") as f:
    f.write("#!/bin/bash \n")
    f.write("cd " + cartella_sw + "/DTFitter/run \n")
    f.write("make \n")
    f.write("./runDT \n")
os.system("chmod +x " + cartella_sw + "/DTFitter/run/runDT.sh")

with open(cartella_sw + "/PattRec/runPR.sh", "w") as f:
    f.write("#!/bin/bash \n")
    f.write("cd " + cartella_sw + "/PattRec \n")
    f.write("make \n")
    f.write("./runPR --dataset=${1} --maxevn=${2} \n")
os.system("chmod +x " + cartella_sw + "/PattRec/runPR.sh")
##########################
##########################
##########################



regex = re.compile(r".*_" + data_tag + "_.*\.i0")
runs = []
for root, dirs, files in os.walk(cartella_dati):
    for file in files:
        if regex.match(file):
            run = re.findall(r'\d+\_\w+\_(\d+)\.\w+', file)
            if (run[0] not in runs):
                runs.append(run[0])
print("- Elenco run:")



for i in runs:
    print(i)
run_to_process = input("\n- Run da processare: ")
print("\n>>> Processo run ", run_to_process, sep="")



noise_map_clone = 356
print("\n>>> Noise map")
print("...clono da run " + str(noise_map_clone))
os.system("cp " + cartella_sw + "/PreProcess/output/NoiseMap_" + str(noise_map_clone) + ".txt " + cartella_sw + "/PreProcess/output/NoiseMap_" + str(run_to_process) + ".txt")
print("......fatto")



print("\n>>> Modifico PreProcess/run/config.ini")
with open (cartella_sw + "/PreProcess/run/config.ini", "r") as f:
    content = f.read()
    content_new = re.sub("(\_\d\d+)", "_" + str(run_to_process), content, flags = re.M)
with open(cartella_sw + "/PreProcess/run/config.ini", "w") as f:
    f.write(content_new)
print("......fatto")



print("\n>>> Mappa t0")
print("...eseguo runPreProcess t0 (richiede tempo)")
process = subprocess.Popen([cartella_sw + "/PreProcess/run/runPreProcesst0.sh", ""], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
while True: 
    line = process.stdout.readline()
    if not line and process.poll() is not None:
        break
    if ("Quit ROOT" in line.decode()):
        print("ATTENZIONE! chiudere ROOT cliccando su File->Quit (non chiudere con Ctrl+c)")
print("......fatto")



print("...sposto mappa t0")
os.system("cp " + cartella_sw + "/PreProcess/output/T0Map_" + str(run_to_process) + ".txt " + cartella_sw + "/DTFitter/utils/T0Map/")
print("......fatto")

print("...sposto mappa noise")
os.system("cp " + cartella_sw + "/PreProcess/output/NoiseMap_" + str(run_to_process) + ".txt " + cartella_sw + "/DTFitter/utils/NoiseMap/")
print("......fatto")



print("\n...eseguo runPreProcess noise (richiede tempo)")
process = subprocess.Popen([cartella_sw + "/PreProcess/run/runPreProcessNoise.sh", ""], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
while True: 
    line = process.stdout.readline()
    if not line and process.poll() is not None:
        break
    if ("Quit ROOT" in line.decode()):
        print("ATTENZIONE! chiudere ROOT cliccando su File->Quit (non chiudere con Ctrl+c)")
print("......fatto")



print("\nDTFitter")
print("...config")
os.system("cp " + cartella_sw + "/DTFitter/utils/config-example.ini " + cartella_sw + "/DTFitter/run/config.ini")
with open (cartella_sw + "/DTFitter/run/config.ini", "r") as f:
    content = f.read()
    content_new = re.sub("(rawFileName_1 1_)", "rawFileName_1 1_" + data_tag + "_" + str(run_to_process), content, flags = re.M)
    content_new = re.sub("(rawFileName_2 2_)", "rawFileName_2 2_" + data_tag + "_" + str(run_to_process), content_new, flags = re.M)
    content_new = re.sub("(runNumber 0100)", "runNumber " + str(run_to_process), content_new, flags = re.M)
    content_new = re.sub("(noiseFileName NoiseMap_100)", "noiseFileName NoiseMap_" + str(run_to_process), content_new, flags = re.M)
    content_new = re.sub("(t0FileName T0Map_100)", "t0FileName T0Map_" + str(run_to_process), content_new, flags = re.M)
    content_new = re.sub("(outputFileName DTTtree_100)", "outputFileName DTTtree_" + str(run_to_process), content_new, flags = re.M)
    content_new = re.sub("(logFileName DTLog_100)", "logFileName DTLog_" + str(run_to_process), content_new, flags = re.M)
with open(cartella_sw + "/DTFitter/run/config.ini", "w") as f:
    f.write(content_new)
print("......fatto")



print("...modifico Space-Time_Parameters.txt")
space_time_pars = str(run_to_process) + "_data exp 27.8 8.43 143.35 0.00186 -3.46e-07  27.8 8.43 143.35 0.00186 -3.46e-07"
space_time_data = open(cartella_sw + "/DTFitter/utils/Space-Time_Parameters.txt", "r").read()
if (str(run_to_process) + "_data" not in space_time_data):
    with open(cartella_sw + "/DTFitter/utils/Space-Time_Parameters.txt", "a") as stfile:
        stfile.write(space_time_pars + "\n")
print("......fatto")



print("\n...eseguo runDT (richiede tempo)")
process = subprocess.Popen([cartella_sw + "/DTFitter/run/runDT.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
process.wait()
print("......fatto")



print("\nMixer")
print("...config")
os.system("cp " + cartella_sw + "/MutomcaReader/utils/config-example.ini " + cartella_sw + "/MutomcaReader/run/config.ini")
with open (cartella_sw + "/MutomcaReader/run/config.ini", "r") as f:
    content = f.read()
    content_new = re.sub("(rawFileNameTubes_1 1_)", "rawFileNameTubes_1 1_" + data_tag + "_" + str(run_to_process), content, flags = re.M)
    content_new = re.sub("(rawFileNameTubes_2 2_)", "rawFileNameTubes_2 2_" + data_tag + "_" + str(run_to_process), content_new, flags = re.M)
    content_new = re.sub("(rawFileNamePhi_3 3_)", "rawFileNamePhi_3 3_" + data_tag + "_" + str(run_to_process), content_new, flags = re.M)
    content_new = re.sub("(rawFileNamePhi_4 4_)", "rawFileNamePhi_4 4_" + data_tag + "_" + str(run_to_process), content_new, flags = re.M)
    content_new = re.sub("(noiseFileName NoiseMap_)", "noiseFileName NoiseMap_" + str(run_to_process), content_new, flags = re.M)
    content_new = re.sub("(maxEventNumber 10)", "maxEventNumber " + str(mixer_max_event), content_new, flags = re.M)
with open(cartella_sw + "/MutomcaReader/run/config.ini", "w") as f:
    f.write(content_new)
print("......fatto")



print("\n...eseguo runPR su file " + "3_" + data_tag + "_" + str(run_to_process) + " (richiede tempo)")
process = subprocess.Popen([cartella_sw + "/PattRec/runPR.sh", cartella_dati + "/3_" + data_tag + "_" + str(run_to_process), str(mixer_max_event)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
process.wait()
print("......fatto")

print("\n...eseguo runPR su file " + "4_" + data_tag + "_" + str(run_to_process) + " (richiede tempo)")
process = subprocess.Popen([cartella_sw + "/PattRec/runPR.sh", cartella_dati + "/4_" + data_tag + "_" + str(run_to_process), str(mixer_max_event)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
process.wait()
print("......fatto")
