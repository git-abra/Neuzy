## Class for MPI Object Instantiation

## Create objects to distribute them over your cores. 
# E.g. 2 MPIrun objects can lead to 2x5 cores usage. 
# Therefore the user can choose which model object has to be prioritized in core usage.
# On the other hand, the choice to use another parallelization is made by creating objects of another class, currently placeholder.

import os, sys, pathlib

PP = pathlib.Path(__file__).parent  # parent path on directory
sys.path.insert(1, str(PP / '..' / 'auxiliaries'))

import logging as lg
import pandas as pd
from mpi4py import MPI

import auxiliaries.constants as cs
import auxiliaries.functions as fnc

# TODO should replace this kind of path management soon
PP = pathlib.Path(__file__).parent  # parent path on directory
sys.path.insert(1, str(PP / '..' / 'auxiliaries'))


class Parallizer():
    """
    Wrapper class for parallelization options.
    """
    def __init__(self):
        pass


class PlaceholderCls(Parallizer):
    """
    Placeholder until further parallelization gets integrated.
    """
    def __init__(self):
        pass


class MPIpar(Parallizer):
    """
    Class for usage of MPI as parallization option.
    """
    def __init__(self, populationsize:int = 100):
        """
        Initialization of MPI properties and Logfiles. # TODO make logfile creation extra
        """

        self.populationsize = populationsize

        ## MPI properties
        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()          # current used core/process
        self.cpucount = self.comm.Get_size()      # number of cores/processes
        self.last_process = self.cpucount - 1

        # Create Log files for up to 9999 different ones
        for i in range(9999):
            if os.path.exists(cs.SAVEPATH_LOG + "/rank_" + str(self.rank) + "_consolelog_sim_" + str(i)+ ".log"):
                continue
            else:
                self.output_log_data = ((cs.SAVEPATH_LOG + "/rank_" + str(self.rank) + "_consolelog_sim_" + str(i) + ".log"))
                break

        lg.basicConfig(filename = self.output_log_data, level = lg.INFO) 
