#### Neuzy ####

## start/run
import os, sys, pathlib

PP = pathlib.Path(__file__).parent  # parent path on directory

sys.path.insert(1, str(PP / '..' / 'auxiliaries'))

import logging as lg
from constants import *
from Parallizers import MPIpar
from CompleteOptModel import CompleteOptModel



def main():
    pass

if __name__ == '__main__':
    # INIT
    mpirunmodel = MPIrun()      # MPIrun object
    mpirunmodel.run(    model_name = "Roe22.hoc",                                #"To21_nap_strong_trunk_together.hoc", 
                        target_feature_file = "somatic_features_hippounit.json", #"somatic_target_features.json", 
                        template_name = None, 
                        hippo_bAP = True    )           # Run it with CompleteOptModel