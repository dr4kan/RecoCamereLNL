############################################################################
#  Codice per automatizzare la ricostruzione dei dati delle camere di LNL  #
#  autore  : Davide Pagano (davide.pagano@unibs.it)                        #
#  versione: 1.3 (17 Luglio 2025)                                           #
############################################################################

# Attenzione: ho commentato la visualizzazione dei plot in PreProcess/run/main.cpp

import os
import re
import subprocess
import sys
import time

# Configurazione globale
cartella_sw = "/home/davide/Camere_LNL/software"
cartella_dati = "/home/davide/Camere_LNL/dati_raw_LNL"
data_tag = "phi1ANDch1_OR_phi2ANDch2"
cartella_output = "/home/davide/Camere_LNL/dati_reco_LNL"
debug = False
mostra_solo_non_processati = True
mixer_max_event = 1000000
last_processed_run = 4
#_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/



def crea_file_supporto():
    '''
    Crea i files di supporto che servono per la ricostruzione
    '''
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
        f.write("cp src/runPR . \n")
        f.write("./runPR --dataset=${1} --maxevn=${2} \n")
    os.system("chmod +x " + cartella_sw + "/PattRec/runPR.sh")

    with open(cartella_sw + "/python-muotom-utils/src/mixer.sh", "w") as f:
        f.write("#!/bin/bash \n")
        f.write("cd " + cartella_sw + "/python-muotom-utils/src \n")
        f.write("./mutomca_mixer_ali --config=${1} \n")
    os.system("chmod +x " + cartella_sw + "/python-muotom-utils/src/mixer.sh")
#_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/



def processa_run(run_to_process):
    '''
    Processa il run specificato
    - run_to_process: run da processare (come stringa)
    '''
    crea_file_supporto()
    
    noise_map_clone = 356
    start = time.time()
    print("\n>>> Noise map")
    print("...clono da run " + str(noise_map_clone))
    os.system("cp " + cartella_sw + "/PreProcess/output/NoiseMap_" + str(noise_map_clone) + ".txt " + cartella_sw + "/PreProcess/output/NoiseMap_" + str(run_to_process) + ".txt")
    end = time.time()
    print(f"......fatto (tempo impiegato: {end - start:.2f} s)")


    start = time.time()
    print("\n>>> Modifico PreProcess/run/config.ini")
    with open(cartella_sw + "/PreProcess/run/config.ini", "r") as f:
        content = f.read()
        content_new = re.sub(r"(_\w+_\d+)", "_" + data_tag + "_" + str(run_to_process), content, flags=re.M)
        content_new = re.sub(r"rawDirName\s([\/\-\w]+)", "rawDirName " + cartella_dati, content_new, flags=re.M)
        content_new = re.sub(r"t0FileName\s(\w+)", "t0FileName T0Map_" + str(run_to_process), content_new, flags=re.M)
        content_new = re.sub(r"noiseFileName\s(\w+)", "noiseFileName NoiseMap_" + str(run_to_process), content_new, flags=re.M)
    with open(cartella_sw + "/PreProcess/run/config.ini", "w") as f:
        f.write(content_new)
    end = time.time()
    print(f"......fatto (tempo impiegato: {end - start:.2f} s)")


    start = time.time()
    print("\n>>> Mappa t0")
    print("...eseguo runPreProcess t0 (richiede tempo)")
    process = subprocess.Popen([cartella_sw + "/PreProcess/run/runPreProcesst0.sh", ""], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True: 
        line = process.stdout.readline()
        if not line and process.poll() is not None:
            break
        if debug:
            print(line.decode())
        if ("Quit ROOT" in line.decode()):
            print("ATTENZIONE! chiudere ROOT cliccando su File->Quit (non chiudere con Ctrl+c)")
    end = time.time()
    print(f"......fatto (tempo impiegato: {end - start:.2f} s)")


    start = time.time()
    print("...sposto mappa t0")
    os.system("cp " + cartella_sw + "/PreProcess/output/T0Map_" + str(run_to_process) + ".txt " + cartella_sw + "/DTFitter/utils/T0Map/")
    end = time.time()
    print(f"......fatto (tempo impiegato: {end - start:.2f} s)")

    
    start = time.time()
    print("...sposto mappa noise")
    os.system("cp " + cartella_sw + "/PreProcess/output/NoiseMap_" + str(run_to_process) + ".txt " + cartella_sw + "/DTFitter/utils/NoiseMap/")
    end = time.time()
    print(f"......fatto (tempo impiegato: {end - start:.2f} s)")


    start = time.time()
    print("\n...eseguo runPreProcess noise (richiede tempo)")
    process = subprocess.Popen([cartella_sw + "/PreProcess/run/runPreProcessNoise.sh", ""], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True: 
        line = process.stdout.readline()
        if not line and process.poll() is not None:
            break
        if debug:
            print(line.decode())
        if ("Quit ROOT" in line.decode()):
            print("ATTENZIONE! chiudere ROOT cliccando su File->Quit (non chiudere con Ctrl+c)")
    end = time.time()
    print(f"......fatto (tempo impiegato: {end - start:.2f} s)")


    start = time.time()
    print("\nDTFitter")
    print("...config")
    os.system("cp " + cartella_sw + "/DTFitter/utils/config-example.ini " + cartella_sw + "/DTFitter/run/config.ini")
    with open(cartella_sw + "/DTFitter/run/config.ini", "r") as f:
        content = f.read()
        content_new = re.sub(r"rawDirName\s([\/\-\w]+)", "rawDirName " + cartella_dati, content, flags=re.M)
        content_new = re.sub("(rawFileName_1 1_)", "rawFileName_1 1_" + data_tag + "_" + str(run_to_process), content_new, flags=re.M)
        content_new = re.sub("(rawFileName_2 2_)", "rawFileName_2 2_" + data_tag + "_" + str(run_to_process), content_new, flags=re.M)
        content_new = re.sub("(runNumber 0100)", "runNumber " + str(run_to_process), content_new, flags=re.M)
        content_new = re.sub("(noiseFileName ../utils/NoiseMap/NoiseMap_100)", "noiseFileName ../utils/NoiseMap/NoiseMap_" + str(run_to_process), content_new, flags=re.M)
        content_new = re.sub("(t0FileName ../utils/T0Map/T0Map_100)", "t0FileName ../utils/T0Map/T0Map_" + str(run_to_process), content_new, flags=re.M)
        content_new = re.sub("(outputFileName DTTtree_100)", "outputFileName DTTtree_" + str(run_to_process), content_new, flags=re.M)
        content_new = re.sub("(logFileName DTLog_100)", "logFileName DTLog_" + str(run_to_process), content_new, flags=re.M)
    with open(cartella_sw + "/DTFitter/run/config.ini", "w") as f:
        f.write(content_new)
    end = time.time()
    print(f"......fatto (tempo impiegato: {end - start:.2f} s)")


    start = time.time()
    print("...modifico Space-Time_Parameters.txt")
    space_time_pars = str(run_to_process) + "_data exp 27.8 8.43 143.35 0.00186 -3.46e-07  27.8 8.43 143.35 0.00186 -3.46e-07"
    space_time_data = open(cartella_sw + "/DTFitter/utils/Space-Time_Parameters.txt", "r").read()
    if (str(run_to_process) + "_data" not in space_time_data):
        with open(cartella_sw + "/DTFitter/utils/Space-Time_Parameters.txt", "a") as stfile:
            stfile.write(space_time_pars + "\n")
    end = time.time()
    print(f"......fatto (tempo impiegato: {end - start:.2f} s)")


    start = time.time()
    print("\n...eseguo runDT (richiede tempo)")
    process = subprocess.Popen([cartella_sw + "/DTFitter/run/runDT.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()
    if debug:
        while True: 
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            print(line.decode())
    end = time.time()
    print(f"......fatto (tempo impiegato: {end - start:.2f} s)")


    start = time.time()
    print("\nMixer")
    print("...config")
    os.system("cp " + cartella_sw + "/MutomcaReader/utils/config-example.ini " + cartella_sw + "/MutomcaReader/run/config.ini")
    with open(cartella_sw + "/MutomcaReader/run/config.ini", "r") as f:
        content = f.read()
        content_new = re.sub(r"rawDirName\s([\/\-\w]+)", "rawDirName " + cartella_dati, content, flags=re.M)
        content_new = re.sub("(rawFileNameTubes_1 1_)", "rawFileNameTubes_1 1_" + data_tag + "_" + str(run_to_process), content_new, flags=re.M)
        content_new = re.sub("(rawFileNameTubes_2 2_)", "rawFileNameTubes_2 2_" + data_tag + "_" + str(run_to_process), content_new, flags=re.M)
        content_new = re.sub("(rawFileNamePhi_3 3_)", "rawFileNamePhi_3 3_" + data_tag + "_" + str(run_to_process), content_new, flags=re.M)
        content_new = re.sub("(rawFileNamePhi_4 4_)", "rawFileNamePhi_4 4_" + data_tag + "_" + str(run_to_process), content_new, flags=re.M)
        content_new = re.sub("(noiseFileName NoiseMap_)", "noiseFileName NoiseMap_" + str(run_to_process), content_new, flags=re.M)
        content_new = re.sub("(maxEventNumber 10)", "maxEventNumber " + str(mixer_max_event), content_new, flags=re.M)
    with open(cartella_sw + "/MutomcaReader/run/config.ini", "w") as f:
        f.write(content_new)
    end = time.time()
    print(f"......fatto (tempo impiegato: {end - start:.2f} s)")


    # PattRec vuole l'estensione .i0
    # se non esiste il link simbolico lo creo
    start = time.time()
    link_path = cartella_dati + "/3_" + data_tag + "_" + str(run_to_process) + ".i0"
    target_path = cartella_dati + "/3_" + data_tag + "_" + str(run_to_process)
    if not os.path.exists(link_path):
        os.symlink(target_path, link_path)
    print("\n...eseguo runPR su file " + "3_" + data_tag + "_" + str(run_to_process) + " (richiede tempo)")
    process = subprocess.Popen([cartella_sw + "/PattRec/runPR.sh", cartella_dati + "/3_" + data_tag + "_" + str(run_to_process), str(mixer_max_event)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()
    if debug:
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            print(line.decode())
    end = time.time()
    print(f"......fatto (tempo impiegato: {end - start:.2f} s)")


    start = time.time()
    link_path = cartella_dati + "/4_" + data_tag + "_" + str(run_to_process) + ".i0"
    target_path = cartella_dati + "/4_" + data_tag + "_" + str(run_to_process)
    if not os.path.exists(link_path):
        os.symlink(target_path, link_path)
    print("\n...eseguo runPR su file " + "4_" + data_tag + "_" + str(run_to_process) + " (richiede tempo)")
    process = subprocess.Popen([cartella_sw + "/PattRec/runPR.sh", cartella_dati + "/4_" + data_tag + "_" + str(run_to_process), str(mixer_max_event)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()
    if debug:
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            print(line.decode())
    end = time.time()
    print(f"......fatto (tempo impiegato: {end - start:.2f} s)")


    start = time.time()
    print(">>> Creo file di supporto")
    with open(cartella_sw + "/python-muotom-utils/src/configMixer.ini", "w") as f:
        f.write("[geom] \n")
        f.write("sl_dt_hdist = 229.0 \n")
        f.write("sl_dt_vdist = 520.0 \n\n")
        f.write("[IO] \n")
        f.write("sl0_file = " + cartella_sw + "/PattRec/OUTPUT/3_" + data_tag + "_" + str(run_to_process) + "_tuples.root \n")
        f.write("sl1_file = " + cartella_sw + "/PattRec/OUTPUT/4_" + data_tag + "_" + str(run_to_process) + "_tuples.root \n")
        f.write("dt0_file = " + cartella_sw + "/DTFitter/output/DTTtree_" + str(run_to_process) + ".root \n")
        f.write("dt1_file = " + cartella_sw + "/DTFitter/output/DTTtree_" + str(run_to_process) + ".root \n")
        f.write("main_file = " + cartella_output + "/mixed_data_ali_" + str(run_to_process) + ".root \n")
        f.write("tstamp_file = " + cartella_dati + "/time_" + data_tag + "_" + str(run_to_process) + "\n\n")
        f.write("[main] \n")
        f.write("write_all_events = true \n")
    end = time.time()
    print(f"......fatto (tempo impiegato: {end - start:.2f} s)")


    start = time.time()
    print("\n...eseguo Mixer (richiede tempo)")
    process = subprocess.Popen([cartella_sw + "/python-muotom-utils/src/mixer.sh", "configMixer.ini"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        line = process.stdout.readline()
        if not line and process.poll() is not None:
            break
        if debug:
            print(line.decode())
    end = time.time()
    print(f"......fatto (tempo impiegato: {end - start:.2f} s)")
#_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/



def main():
    # Trova i run non ancora processati con la tag specificata
    regex = re.compile(r"\d+_" + data_tag + r"_\d+")
    runs = []
    for root, dirs, files in os.walk(cartella_dati):
        for file in files:
            if regex.match(file):
                run = re.findall(r'\d+\_\w+\_(\d+)', file)
                if (run[0] not in runs):
                    if (mostra_solo_non_processati == True):
                        if not os.path.exists(cartella_output + "/mixed_data_ali_" + run[0] + ".root"):
                            if (int(run[0]) > last_processed_run):
                                runs.append(run[0])
                    else:
                        if (int(run[0]) > last_processed_run):
                            runs.append(run[0])

    runs = sorted(runs)

    if (mostra_solo_non_processati == True):
        print("- Elenco run NON PROCESSATI successivi a " + str(last_processed_run) + " (con data tag '" + data_tag + "'):")
    else:
        print("- Elenco run successivi a " + str(last_processed_run) + " (con data tag '" + data_tag + "'):")
 
    runs_str = ""
    for i in runs:
        runs_str += str(i) + ", "
    runs_str = runs_str[:-2]
    print(runs_str)

    if (mostra_solo_non_processati == True):
        run_to_process = input("\n- Run da processare (-1 per processarli tutti): ")
        if (run_to_process != "-1" and run_to_process not in runs):
            print("Run non valido!")
            sys.exit(1)
    else:
        run_to_process = input("\n- Run da processare: ")
        if (run_to_process not in runs):
            print("Run non valido!")
            sys.exit(1)

    if (run_to_process == "-1"):
        print("\n###################################")
        print("\n>>> Processamento di tutti i run")
        print("\n###################################")
        for run in runs:
            print("\n###################################")
            print("\n>>> Processamento del run " + str(run))
            print("\n###################################")
            processa_run(run)
    else:
        print("\n>>> Processamento del run " + str(run_to_process))
        processa_run(run_to_process)
#_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/



if __name__ == "__main__":
    main()
