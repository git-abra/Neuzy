#### Neuzy ####
# start Neuzy with Python
# leads to a legacystart.sh > ./paropt/models/run_mpi.py > ./paropt/models/CompleteOptModel.py call

import os, subprocess
import pathlib as pl

RP = pl.Path(__file__).parent       # RP rootpath

try:
    subprocess.call(['bash', str(RP / 'legacystart.sh')])
except Exception as e:
    print("Unexpected pathing error for relative path, trying with cwd, if called from root of the repository.")
    print(e)
    cwd = os.getcwd()       # get call cwd
    if cwd.split("/")[-1] != "neuzy":
        print("Error: A wild path error occurred. Path error uses 'wrong pathing' with path: " + cwd + ".") 
        print("It is very effective.")
        print("To counter, call Neuzy from the root of the package (e.g. 'home/user/downloads/Neuzy') and restart.")
    else:
        subprocess.call(['bash', './legacystart.sh'])