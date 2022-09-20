#### Neuzy ####

## Quickstart/run_default
# Can be written as jupyter notebook and configured by the user
# Runs with default parameters (e.g. population size)

import sys, pathlib, argparse

# Pathing
PP = pathlib.Path(__file__).parent  # parent path on directory
sys.path.insert(1, str(PP / '..'))

## Classes
from Parallizers import MPIpar          # Parallelization Class
from HocModel import HocModel          # Model Class to read in HOC and have methods on the model
from Stims import Firstspike_SortOutStim           # Stim protocol class
from Calculations import FitnessCalcSD  # Calculations for Fitness
from Optimizers import ScipyOpt         # Optimizer
from Simulations import GenSim          # Run all objects in concatenation"""

# from CompleteOptModel import CompleteOptModel

## Command Line Arguments
parser = argparse.ArgumentParser()
parser.add_argument("-l", "--legacy", dest = "legacy", default = "")
args = parser.parse_args()
print(args.legacy)

def main():
    """
    if args.legacy is not None:
        pass
        # Legacy Version Run
        # CompleteOptModel.run()   
    """ 
    ## Building default objects with "1" as ID
    hoc_1 = HocModel(
                        model_name = "Roe22.hoc",
                        modpath = None,
                        target_feature_file = "somatic_features_hippounit.json", #"somatic_target_features.json", 
                        template_name = "Roe22_reduced_CA1", 
                        hippo_bAP = True,
                        channelblocknames = None,               # Run it with CompleteOptModel
                        verbose = True
                        )
    mpi_1 = MPIpar(populationsize = 100)    # MPIpar object, 100 cells to generate

    stim_1 = Firstspike_SortOutStim(model = hoc_1, par = mpi_1)   # default parameters

    calc_1 = FitnessCalcSD(hoc_1, stim_1)            # obj(__init__(): self.model = model)

    opt_1 = ScipyOpt("Nelder-Mead")  


    ## Running default config
    run_instance_1 = GenSim(par = mpi_1, model = hoc_1, stim = stim_1, opt = opt_1, calc = calc_1)

    ## call the objects together in Runner.run() and print output files in it
    run_instance_1.run()
    

    """
    ## Extra - HippoUnit
    finalpar = run_instance_1.finalParameters() # finalpar will be input for HippoModel if needed
    test1 = HippoModel(model_input_par = finalpar)
    """


if __name__ == '__main__':
    main()
   