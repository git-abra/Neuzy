## Class for MPI Object Instantiation

from CompleteOptModel import CompleteOptModel
import Models
from mpi4py import MPI
from Testingfinaldata import *



class MPIrun():
    def __init__(self, populationsize = 100):
        ## MPI properties
        self.comm = MPI.COMM_WORLD
        self.rank = comm.Get_rank()          # current used core/process
        self.cpucount = comm.Get_size()      # number of cores/processes
        self.last_process = cpucount - 1

        # Create Log files for up to 9999 different ones
        for i in range(9999):
            if os.path.exists(SAVEPATH_LOG + "/rank_" + str(self.rank) + "_consolelog_sim_" + str(i)+ ".log"):
                continue
            else:
                self.output_log_data = ((SAVEPATH_LOG + "/rank_" + str(self.rank) + "_consolelog_sim_" + str(i) + ".log"))
                break

        lg.basicConfig(filename = output_log_data, level = lg.INFO) 
    
    def run(self, model_name, target_feature_file, template_name, hippo_bAP):
        """ Missing Doc """
        newmodel = HocModel(model_name = )
        runmodel = HOC
        paroptmodel = CompleteOptModel (    model_name = "Roe22.hoc",                                #"To21_nap_strong_trunk_together.hoc", 
                                            target_feature_file = "somatic_features_hippounit.json", #"somatic_target_features.json", 
                                            template_name = None, 
                                            hippo_bAP = True    )
    
    def testData():
        # TODO
        paroptmodel.line = 1
        testingfinaldata = TestingFinalData("./paropt/datadump/parameter_values/best10_par.csv", line = paroptmodel.line)

        paroptmodel.run(cell_destination_size, testing = False)   # testing flag if testingfinaldata is wanted or if it should proceed to random initialization
