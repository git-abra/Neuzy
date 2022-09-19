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
import numpy as np
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

    def gather_output(  self, 
                        model,
                        testing = None):
        """
        Gathers the output of the optimizations and 
        """

        counter = 0
        successcounter = 0 
        out_fun_list = []  
        init_rnd_par_list = []
        out_par_list = []    
        i = 0

        while i <= self.populationsize:
            counter = counter + 1

            self.AP_firstspike = False      # reset AP_firstspike
            self.bAP_firstspike = False     # reset bAP_firstspike

            print("Cell number " + str(counter) + " on rank number " + str(self.rank))

            lg.info("\n")
            lg.info("Cell number " + str(counter) + " on rank number " + str(self.rank) + " is starting.")

            if counter == 1:           
                print("First created Cell is used.")
                lg.info("First created Cell is used.")

                init_data, indices = model.getMechanismItems()  # Initial Conductances # tested
                init_output_data = fnc.insertNans(init_data, indices).tolist()

                outfile = pathlib.Path(cs.SAVEPATH_PAR + '/INITIAL_CONDUCTANCES_LIST.json')
                if outfile.is_file():
                    print("Initial Conductances already in a JSON file.")        
                    pass
                else:
                    X = fnc.convert1DTo2DnpArr(init_output_data)
                    df = pd.DataFrame(X, index = self.sectionlist_list, columns = self.ionchnames).transpose()
                    print("Creating Initial Conductances - JSON file")
                    print(df)         
                    fnc.writeJSON(cs.SAVEPATH_PAR, 'INITIAL_CONDUCTANCES_LIST.json', init_output_data)   

            elif counter > 1 :
                self.deleteCell()      # garbage collector deletion for ram
                print("Recreating Cell " + str(counter) + ", reinitializing.")
                lg.info("Recreating Cell " + str(counter) + ", reinitializing.")

                self.initializeCell()
                init_data, indices = self.getMechanismItems()  # Initial Conductances for new cell
                # print(init_data)

                        
            ############Run#################################
            output = self.runOptimizer(init_data, indices) #   # output of optimizers
            ############Run#################################

            if isinstance(output, int) and output == 1:
                print("Abort Error 1: Model didn't spike at enough frequency at start i.e. no Action Potentials at the start. No save.")
                lg.error("Abort Error 1: Model didn't spike at enough frequency at start i.e. no Action Potentials at the start. No save.")             
                #continue

            elif isinstance(output, int) and output == 2:
                print("Abort Error 2: Model wasn't able to be optimized below the treshold. No save.")
                lg.error("Abort Error 2: Model wasn't able to be optimized below the treshold. No save.")              
                #continue             
                
            elif isinstance(output, int) and output == 3:
                print("Abort Error 3: Models spike frequency was sufficient but Initial costs were too high to send into the Optimizer")
                lg.error("Abort Error 3: Models spike frequency was sufficient but Initial costs were too high to send into the Optimizer")
                #continue

            else:           # with results

                if isinstance(output, list):  
                    print("Successful parameter combination got optimized!")
                    lg.info("Successful parameter combination got optimized!")
                    output_array = output[0]                     # array of valid output combination
                    input_random_array = output[1]               # array of its initial random combination
                    out_fun = output[2]

                    out_fun_list.append(output[2])
                    out_par_list.append(output_array.tolist())
                    init_rnd_par_list.append(input_random_array.tolist())            

                    # input_random_array = insertNans(input_random_array)
                    # output_array = insertNans(output_array) 
                    # out_par_df = pd.DataFrame(convert1DTo2DnpArr(output_array), index = self.sectionlist_list, columns = self.ionchnames).transpose()
                    # init_rnd_par_df = pd.DataFrame(convert1DTo2DnpArr(input_random_array), index = self.sectionlist_list, columns = self.ionchnames).transpose()                       

                elif isinstance(output, tuple):                 # np.ndarray
                    print("Random parameters already sufficient. Next cell.")
                    lg.info("Random parameters already sufficient. Next cell.")
                    output_array = output[0]  
                    out_fun = output[1]

                    out_fun_list.append(output[1])
                    out_par_list.append(output_array.tolist())
                    init_rnd_par_list.append(output_array.tolist())  # init = out , so saving double   


                with open(self.output_csv_fun_data, "a") as f:
                    print(out_fun, end='\n', file=f)                # *out_fun

                output_list = output_array.tolist()
                with open(self.output_csv_data, "a") as f:
                    print(*output_list, sep=',', end='\n', file=f)

                # Sample recursively around, terminate recursion if maxiter or maxresults is exceeded
                # check sampleRecAround documentation
                self.sampleRecAround(output_array, out_fun, indices)    # see recaround.py for another solution

            if os.path.exists(self.output_csv_data):
                i = sum(1 for line in open(self.output_csv_data))
                print(str(i) + " results read in output file.")
                lg.info(str(i) + " results read in output file.")
  
        final_funcost_list = self.comm.gather(out_fun_list, root = 0)
        final_output_list = self.comm.gather(out_par_list, root = 0)
        final_rnd_out_list = self.comm.gather(init_rnd_par_list, root = 0)
        counters = self.comm.gather(counter, root = 0)
        end = self.time.time()

        if self.rank == 0:
            self.final_fun_list = []
            final_out_list = []
            final_rnd_list = []
            for i in range(self.cpucount):
                self.final_fun_list = final_out_list + final_funcost_list[i]
                self.final_out_list = final_out_list + final_output_list[i]
                self.final_rnd_list = final_rnd_list + final_rnd_out_list[i]

            print("ELAPSED TIME: ", end - start, " seconds")
            print("COUNTER WHETHER ALL CELLS WERE TRIED IN EACH RANK: ", counters)

            lg.info("\n")
            lg.info("ELAPSED TIME: ")      # Logging Time
            lg.info(end - start)
            lg.info("seconds")
            lg.info("\n")
            lg.info("COUNTER - How many cells did one rank do?: ")
            lg.info(counters)
            lg.info("COUNTER - How many cells in total?: ")
            lg.info(sum(counters))
            lg.info("\n")

            # writeJSON(SAVEPATH_OUT_PAR, 'OUTPUT_OUT_PAR_LIST_NESTED.json', final_output_list)
            # writeJSON(SAVEPATH_OUT_PAR, 'OUTPUT_RND_PAR_LIST_NESTED.json', final_rnd_out_list)
            fnc.writeJSON(cs.SAVEPATH_PAR, 'OUTPUT_OUT_PAR_LIST.json', self.final_out_list)
            fnc.writeJSON(cs.SAVEPATH_PAR, 'OUTPUT_RND_PAR_LIST.json', self.final_rnd_list)
            fnc.writeJSON(cs.SAVEPATH_PAR, 'OUTPUT_COSTS_LIST.json', self.final_fun_list)
