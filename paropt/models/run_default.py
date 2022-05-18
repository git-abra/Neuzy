#### Neuzy ####

## quickstart/run_default
# runs with default config

import os, sys, pathlib

PP = pathlib.Path(__file__).parent  # parent path on directory

sys.path.insert(1, str(PP / '..' / 'auxiliaries'))

import logging as lg
from constants import *
from Parallizers import MPIpar
from Models import HocModel
from Stims import SortOutStim
from Runners import Runner

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


    # TODO
    # TODO
    # TODO


    ## Running default config
    run_instance1 = Runner()
    run_instance1.run(par = mpi1, model = hoc1, stim = stim1, opt = opti1, calc = calc1)

    """
    mpi1.run(    model_name = "Roe22.hoc",                               #"To21_nap_strong_trunk_together.hoc", 
                target_feature_file = "somatic_features_hippounit.json", #"somatic_target_features.json", 
                template_name = None, 
                hippo_bAP = True    )                                    # Run it with CompleteOptModel
    """


    ## Extra - HippoUnit

    test1 = HippoModel()
    ###