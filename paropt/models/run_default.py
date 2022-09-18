#### Neuzy ####

## Quickstart/run_default
# Can be written as jupyter notebook and configured by the user
# Runs with default parameters (e.g. population size)

import sys, pathlib, argparse
from auxiliaries.constants import *

## Classes
from Parallizers import MPIpar          # Parallelization Class
from HocModel import HocModel          # Model Class to read in HOC and have methods on the model
from Stims import SortOutStim           # Stim protocol class
from Calculations import FitnessCalcSD  # Calculations for Fitness
from Optimizers import ScipyOpt         # Optimizer

from Simulations import GenSim          # Run all objects in concatenation

from CompleteOptModel import CompleteOptModel

# Pathing
PP = pathlib.Path(__file__).parent  # parent path on directory
sys.path.insert(1, str(PP / '..'))

## Command Line Arguments
parser = argparse.ArgumentParser()
parser.add_argument("-l", "--legacy", dest = "legacy", default = "")
args = parser.parse_args()



def main():

    if args.legacy is not None:
        # Legacy Version Run
        CompleteOptModel.run()    
    else:
        ## Building default objects with "1" as ID

        hoc_1 = HocModel(
                            model_name = "Roe22.hoc", 
                            modpath = None,
                            target_feature_file = "somatic_features_hippounit.json", #"somatic_target_features.json", 
                            template_name = None, 
                            hippo_bAP = True,
                            channelblocknames = False,               # Run it with CompleteOptModel
                            verbose = True
                            )
        # hoc_1.mycell is now the hocobject property of hoc1 object.
        # hoc_1 describes the object of the instantiated meta files and properties.
        # hoc_1.mycell describes the instantiated hocobject with its extracted properties from hoc file


        
        mpi_1 = MPIpar(populationsize = 100)      # MPIpar object, 100 cells to generate


        stim_1 = SortOutStim()

        fcalc_1 = FitnessCalcSD(hoc1)

        opti_1 = ScipyOpt("Nelder-Mead")  


        ## Running default config
        run_instance_1 = GenSim()    # TODO check if classmethods are better

        ## call the objects together in Runner.run() and print output files in it
        run_instance_1.run(par = mpi_1, model = hoc_1, stim = stim_1, opt = opti_1, calc = fcalc_1)

        """
        ## Extra - HippoUnit
        finalpar = run_instance_1.finalParameters() # finalpar will be input for HippoModel if needed
        test1 = HippoModel(model_input_par = finalpar)
        """

if __name__ == '__main__':
    main()
   