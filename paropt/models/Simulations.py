#### Neuzy

## Simulations concatenates input and runs the system

import sys, pathlib, time, os
import pandas as pd
import logging as lg

from paropt.models.Optimizers import ScipyOpt

PP = pathlib.Path(__file__).parent   # PP Parentpath from current file
sys.path.insert(1, str(PP/'..'))

import auxiliaries.constants as cs
import auxiliaries.functions as fnc

class GenSim():
    """
    General Simulation Class GenSim() to run the simulations.
    Concatenates all objects from the different classes and uses them to sim.
    """
    def __init__(   self, 
                    par:object, 
                    model:object, 
                    stim:object, 
                    opt:object, 
                    calc:object, 
                    testing:bool = None
                    ):
        
        ## Every parameter object is going to be a property for the GenSim instances. 
        # So new GenSim() objects can be created with different setups, 
        # while including their own properties of all the instances

        self.par = par
        self.model = model
        self.stim = stim
        self.opt = opt
        self.fcalc = calc

        if testing:
            self.testing = True
        else:
            self.testing = False
        

    def run(self):
        """ 
        Run for output.
        Creates output files.
        Gathers output of the program.
        """
        ## Creating output files as variables to append outputs/results
        # Standard output of regular optimized results
        for i in range(9999):
            if os.path.exists(cs.SAVEPATH_PAR + "/output_data_sim_" + str(i) + ".csv") or \
                os.path.exists(cs.SAVEPATH_PAR + "/output_fun_data_sim_" + str(i) + ".csv") or \
                os.path.exists(cs.SAVEPATH_PAR + "/sample_output_par_data_sim_" + str(i) + ".csv") or \
                os.path.exists(cs.SAVEPATH_PAR + "/sample_fun_data_sim_" + str(i) + ".csv") or \
                os.path.exists(cs.SAVEPATH_PAR + "/sample_best_output_par_data_sim_" + str(i) + ".csv") or \
                os.path.exists(cs.SAVEPATH_PAR + "/sample_best_fun_data_sim_" + str(i) + ".csv"):
                continue
            else:
                self.output_csv_data = (cs.SAVEPATH_PAR + "/output_data_sim_" + str(i) + ".csv")
                self.output_csv_fun_data = (cs.SAVEPATH_PAR + "/output_fun_data_sim_" + str(i) + ".csv")
                 # Results after sampling
                self.sample_output_csv_par_data = (cs.SAVEPATH_PAR + "/sample_output_par_data_sim_" + str(i) + ".csv")
                self.sample_output_csv_fun_data = (cs.SAVEPATH_PAR + "/sample_fun_data_sim_" + str(i) + ".csv")
                # Best sampling results
                self.sample_best_output_csv_par_data = (cs.SAVEPATH_PAR + "/sample_best_output_par_data_sim_" + str(i) + ".csv")
                self.sample_best_output_csv_fun_data = (cs.SAVEPATH_PAR + "/sample_best_fun_data_sim_" + str(i) + ".csv")
                break

        self.starttime = time.time()

        # Gather Output
        self.gather_output()


    def updateModel(self, parameter_data, indices):
        """
        Parameters
        ----------
        parameter_data: vector of parameter data
        indices: indices of parameter data
        model: model to be updated
        """  
        # print("test: ", parameter_data)
        if self.model.updateParAndModel(self.parameter_data, self.indices) is None:
            print("No spiking, aborting on rank, " + str(self.rank))  
            lg.info("No spiking, aborting on rank, " + str(self.rank))
            return 10000
        else:
            pass

    def updateParAndModel(self, parameter_data, indices):
            if self.method == "CG":
                parameter_data = abs(parameter_data)    # especially for CG, don't make negative values possible for conductances. Negative "bar" values produce a NEURON error. 
                                                        # If you want to add e_pas to the parameters, you have to specify this line

            ## TODO , could intialize the first self.model_features after instantiating the cell, to check for spikes and then throw it overboard before even calculating the fitness

            self.updateHOCParameters(parameter_data, indices)     # update "self.current_cell" Cell with random values

            if self.stim.AP_firstspike and self.stim.bAP_firstspike:
                traces_per_stepamp, time_vec = self.stimulateIClamp()
                self.extractModelFeatures(traces_per_stepamp, time_vec)
                return True 
            else:
                if self.stim.stimulateIClamp_firstspike():                           # if firstspike features
                    self.stim.AP_firstspike = True
                    self.stim.bAP_firstspike = True
                    traces_per_stepamp, time_vec = self.stim.stimulateIClamp()       # starting full-fledged stimulation
                    self.extractModelFeatures(traces_per_stepamp, time_vec)     # extracting all features
                    return True
                else:
                    return


    def gather_output(self):
        """
        Gathers the output of the optimizations and 
        """
        start = time.time()
        counter = 0
        # successcounter = 0 
        out_fun_list = []  
        init_rnd_par_list = []
        out_par_list = []    
        i = 0

        while i <= self.par.populationsize:
            counter = counter + 1

            self.model.AP_firstspike = False      # reset AP_firstspike
            self.model.bAP_firstspike = False     # reset bAP_firstspike

            print("Cell number " + str(counter) + " on rank number " + str(self.par.rank))

            lg.info("\n")
            lg.info("Cell number " + str(counter) + " on rank number " + str(self.par.rank) + " is starting.")

            if counter == 1:           
                print("First created Cell is used.")
                lg.info("First created Cell is used.")

                init_data, indices = self.model.getMechanismItems()  # Initial Conductances # tested
                init_output_data = fnc.insertNans(init_data, indices).tolist()

                outfile = pathlib.Path(cs.SAVEPATH_PAR + '/INITIAL_CONDUCTANCES_LIST.json')
                if outfile.is_file():
                    print("Initial Conductances already in a JSON file.")        
                    pass
                else:
                    X = fnc.convert1DTo2DnpArr(init_output_data)
                    df = pd.DataFrame(X, index = self.model.sectionlist_list, columns = self.model.ionchnames).transpose()
                    print("Creating Initial Conductances - JSON file")
                    print(df)         
                    fnc.writeJSON(cs.SAVEPATH_PAR, 'INITIAL_CONDUCTANCES_LIST.json', init_output_data)   

            elif counter > 1 :
                self.model.deleteCell()      # garbage collector deletion for ram
                print("Recreating Cell " + str(counter) + ", reinitializing.")
                lg.info("Recreating Cell " + str(counter) + ", reinitializing.")

                self.model.initializeCell()
                init_data, indices = self.model.getMechanismItems()  # Initial Conductances for new cell
                # print(init_data)

            ## Get Ouput         
            output = self.opt.runOptimizer(init_data, indices, self.calc) #   # output of optimizers

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
                self.calc.sampleRecAround(output_array, out_fun, indices, self.model, self.calc)    # see recaround.py for another solution

            if os.path.exists(self.output_csv_data):
                i = sum(1 for line in open(self.output_csv_data))
                print(str(i) + " results read in output file.")
                lg.info(str(i) + " results read in output file.")
  
        final_funcost_list = self.par.comm.gather(out_fun_list, root = 0)
        final_output_list = self.par.comm.gather(out_par_list, root = 0)
        final_rnd_out_list = self.par.comm.gather(init_rnd_par_list, root = 0)
        counters = self.par.comm.gather(counter, root = 0)
        end = self.time.time()

        if self.par.rank == 0:
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

    def finalParameters(self, x):
        """
        Get the final parameter output???
        """
        # finalParameters - Sectionlist Specific! Every section inside a section has the same values (maybe distributed function in hoc still works)
        # No nan value inserting here, they come out with nan values due to position-based updating of the values in a dataframe, see below or in updateHOCParameters()
        
        # Convert back to 2D array
        X = fnc.convert1DTo2DnpArr(x[5])        # just testing for the first combination of values
        df = pd.DataFrame(X, index = self.model.sectionlist_list, columns = self.ionchnames).transpose()      # updated df # Reassign model-specific ordered ion channel names
        #print(df)  # tested, prints with nans
        self.ionchnames = list(df.index)  # redundant, but anyway who tf cares
        if self.model.sectionlist_list:
            for sl in self.model.sectionlist_list:
                inputsl = getattr(self.model.current_cell, sl)
                for sec in inputsl:        
                    for ionchname in self.ionchnames:
                        ionchnamekey = ionchname.split('_', 1)[1]
                        ionchnamekeykey = ionchname.split('_', 1)[0]
                        if ionchnamekey in sec.psection()['density_mechs'].keys():
                            if ionchnamekeykey in sec.psection()['density_mechs'][ionchnamekey].keys():
                                setattr(sec, ionchname, df.loc[ionchname, sl]) 
                            else:
                                continue
        else:
            pass
            # TODO build for 1-column "all" sectionlist with fixed indices
            """
            for sec in self.mycell.all:
                for ionchname in self.ionchnames:
                        ionchnamekey = ionchname.split('_', 1)[1]
                        ionchnamekeykey = ionchname.split('_', 1)[0]
                        if ionchnamekey in sec.psection()['density_mechs'].keys():
                            if ionchnamekeykey in sec.psection()['density_mechs'][ionchnamekey].keys():
                            else:
                                continue
                        else:
                            continue
            """
        # return self.mycell

