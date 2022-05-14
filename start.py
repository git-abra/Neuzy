#### Neuzy ####
# start Neuzy with Python
# leads to a start.sh > ./paropt/models/run_mpi.py > ./paropt/models/CompleteOptModel.py call

import os, subprocess

cwd = os.getcwd()       # get call cwd
if cwd.split("/")[-1] != "neuzy":
    print("Error: A wild path error occurred. Path error uses 'wrong pathing' with path: " + cwd + ".") 
    print("It is very effective.")
    print("To counter, call Neuzy from the root of the package (e.g. 'home/user/downloads/Neuzy') and restart.")
else:
    subprocess.call(['bash', './start.sh'])