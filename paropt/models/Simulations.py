#### Neuzy

## Simulations concatenates input and runs the system

import sys, pathlib, time, os
import auxiliaries as ax

PP = pathlib.Path(__file__).parent
sys.path.insert(1, str(PP / '..' / 'auxiliaries'))


class GenSim():
    def __init__(   self, 
                    par:object, 
                    model:object, 
                    stim:object, 
                    opt:object, 
                    calc:object, 
                    testing:bool = None
                    ):
        """
        General Simulation Class GenSim() to run the simulations.
        Concatenates all objects from the different classes and uses them to sim.
        """
        if testing:
            self.testing = True
        else:
            self.testing = False
        
        pass
    
    @classmethod
    def run(self):
        """ 
        Run for output 
        """
        ## Creating output files as variables to append outputs/results
        # Standard output of regular optimized results
        for i in range(9999):
            if os.path.exists(ax.constants.SAVEPATH_PAR + "/output_data_sim_" + str(i) + ".csv") or \
                os.path.exists(ax.constants.SAVEPATH_PAR + "/output_fun_data_sim_" + str(i) + ".csv") or \
                os.path.exists(ax.constants.SAVEPATH_PAR + "/sample_output_par_data_sim_" + str(i) + ".csv") or \
                os.path.exists(ax.constants.SAVEPATH_PAR + "/sample_fun_data_sim_" + str(i) + ".csv") or \
                os.path.exists(ax.constants.SAVEPATH_PAR + "/sample_best_output_par_data_sim_" + str(i) + ".csv") or \
                os.path.exists(ax.constants.SAVEPATH_PAR + "/sample_best_fun_data_sim_" + str(i) + ".csv"):
                continue
            else:
                self.output_csv_data = (ax.constants.SAVEPATH_PAR + "/output_data_sim_" + str(i) + ".csv")
                self.output_csv_fun_data = (ax.constants.SAVEPATH_PAR + "/output_fun_data_sim_" + str(i) + ".csv")
                 # Results after sampling
                self.sample_output_csv_par_data = (ax.constants.SAVEPATH_PAR + "/sample_output_par_data_sim_" + str(i) + ".csv")
                self.sample_output_csv_fun_data = (ax.constants.SAVEPATH_PAR + "/sample_fun_data_sim_" + str(i) + ".csv")
                # Best sampling results
                self.sample_best_output_csv_par_data = (ax.constants.SAVEPATH_PAR + "/sample_best_output_par_data_sim_" + str(i) + ".csv")
                self.sample_best_output_csv_fun_data = (ax.constants.SAVEPATH_PAR + "/sample_best_fun_data_sim_" + str(i) + ".csv")
                break

        self.starttime = time.time()
        
        
    

    def finalParameters(self, x):
        """
        Get the final parameter output???
        """
        # finalParameters - Sectionlist Specific! Every section inside a section has the same values (maybe distributed function in hoc still works)
        # No nan value inserting here, they come out with nan values due to position-based updating of the values in a dataframe, see below or in updateHOCParameters()
        
        # Convert back to 2D array
        X = convert1DTo2DnpArr(x[5])        # just testing for the first combination of values
        df = pd.DataFrame(X, index = self.sectionlist_list, columns = self.ionchnames).transpose()      # updated df # Reassign model-specific ordered ion channel names
        #print(df)  # tested, prints with nans
        self.ionchnames = list(df.index)  # redundant, but anyway who tf cares
        if self.sectionlist_list:
            for sl in self.sectionlist_list:
                inputsl = getattr(self.mycell, sl)
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