#### Neuzy ####

## quickstart/run_default
# runs with default config

import os, sys, pathlib

PP = pathlib.Path(__file__).parent  # parent path on directory

sys.path.insert(1, str(PP / '..' / 'auxiliaries'))

import logging as lg
from constants import *

## Classes
from Parallizers import MPIpar          # Parallelization Class
from HocModels import HocModel          # Model Class to read in HOC and have methods on the model
from Stims import SortOutStim           # Stim protocol class
from Calculations import FitnessCalcSD  # Calculations for Fitness
from Optimizers import ScipyOpt         # Optimizer
from Runners import Runner              # Run all objects in concatenation

from CompleteOptModel import CompleteOptModel

def main():
    pass

if __name__ == '__main__':
    ## Building default objects

    mpi1 = MPIpar(populationsize = 100)      # MPIrun object, 100 cells to generate

    hoc1 = HocModel(
                        model_name = "Roe22.hoc", 
                        modpath = None,
                        target_feature_file = "somatic_features_hippounit.json", #"somatic_target_features.json", 
                        template_name = None, 
                        hippo_bAP = True,
                        channelblocknames = False,               # Run it with CompleteOptModel
                        verbose = True
                        )

    stim1 = SortOutStim()

    fcalc1 = FitnessCalcSD()

    opt1 = ScipyOpt("Nelder-Mead")         # TODO need for inheritance, how?

    ## Running default config
    run_instance1 = Runner()    # TODO check if classmethods are better

    ## call the objects together in Runner.run() and print output files in it
    run_instance1.run(par = mpi1, model = hoc1, stim = stim1, opt = opti1, calc = calc1)

    finalpar = run_instance1.finalParameters()

    """
    mpi1.run(    model_name = "Roe22.hoc",                               #"To21_nap_strong_trunk_together.hoc", 
                target_feature_file = "somatic_features_hippounit.json", #"somatic_target_features.json", 
                template_name = None, 
                hippo_bAP = True    )                                    # Run it with CompleteOptModel
    """

    # git test comment test only


    ## Extra - HippoUnit

    test1 = HippoModel()
    ###