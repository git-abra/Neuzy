"""
Neuzy - Population-based Neuron Modelling, Copyright (C) 2022 Adrian Röth

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
For details see the GNU General Public License and LICENSE.md in the root of the repository.
This is free software, and you are welcome to redistribute it
under certain conditions.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

## legacy version with CompleteOptModel.py

## start/run
import os, sys, pathlib

PP = pathlib.Path(__file__).parent  # parent path on directory
sys.path.insert(1, str(PP / '..' / 'auxiliaries'))

import logging as lg
from constants import *
from CompleteOptModel import CompleteOptModel
from TestingCompleteModel import *
from mpi4py import MPI


def main():
    ## Basic Setup
    cell_destination_size = 100      # I want to receive in total 10 optimized cells as output

    ## MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()          # current used core/process
    cpucount = comm.Get_size()      # number of cores/processes
    last_process = cpucount - 1

    ## create Log files
    for i in range(9999):
        if os.path.exists(SAVEPATH_LOG + "/rank_" + str(rank) + "_consolelog_sim_" + str(i)+ ".log"):
            continue
        else:
            output_log_data = ((SAVEPATH_LOG + "/rank_" + str(rank) + "_consolelog_sim_" + str(i)+ ".log"))
            break

    lg.basicConfig(filename = output_log_data, level = lg.INFO) 


    # INIT
    paroptmodel = CompleteOptModel (    model_name = "Roe22.hoc",                                 #"To21/To21_nap_strong_trunk_together.hoc",
                                        target_feature_file = "somatic_features_hippounit.json", #"somatic_target_features.json", 
                                        template_name = None, 
                                        hippo_bAP = True,
                                        rank = rank,
                                        comm = comm,
                                        cpucount = cpucount )                                   #TODO Look Up
    
    # paroptmodel.line = 1
    # testingfinaldata = TestingFinalData("./paropt/data/parameter_values/best10_par.csv", line = paroptmodel.line)

    paroptmodel.run(cell_destination_size, testing = False)   # testing flag if testingfinaldata is wanted or if it should proceed to random initialization

if __name__ == '__main__':
    main()
