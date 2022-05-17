#### Neuzy ####

##################################################################
# "constants.py"
# Fanantenana
##################################################################

## File for global constants

import os
import sys
import pathlib as pl

## Paths
CURRENT_DIR = pl.Path.cwd()

MODPATH = str(CURRENT_DIR / 'paropt' / 'data' / 'mods' / 'x86_64' / '.libs' / 'libnrnmech.so')         
HOCPATH = str(CURRENT_DIR / 'paropt' / 'data' / 'morphos')   # TODO Morpho name has to be variable in next version inside a class

## Features
SAVEPATH_FEATURE = str(CURRENT_DIR / 'paropt' / 'data' / 'features') 
SAVEPATH_FEATURE_TARGET = str(CURRENT_DIR / 'paropt' / 'data' / 'features'/ 'target_features') 
SAVEPATH_FEATURE_MODEL = str(CURRENT_DIR / 'paropt' / 'data' / 'features' / 'model_features') 

## Parameters
SAVEPATH_PAR = str(CURRENT_DIR / 'paropt' / 'data' / 'parameter_values')     

#SAVEPATH_RND_PAR = str(CURRENT_DIR / 'paropt' / 'data' / 'parameter_values' / 'initRandomData')
#SAVEPATH_OUT_PAR = str(CURRENT_DIR / 'paropt' / 'data' / 'parameter_values' / 'OutputData')
SAVEPATH_LOG = str(CURRENT_DIR / 'paropt' / 'data' / 'log_files')

#SAVEPATH_LOG_OPT = str(CURRENT_DIR / 'paropt' / 'data' / 'log_files' / 'optimization')
#SAVEPATH_LOG_SIM = str(CURRENT_DIR / 'paropt' / 'data' / 'log_files' / 'simulation')

## Plots
SAVEPATH_PLOTS = str(CURRENT_DIR / 'paropt' / 'figures' / 'outputs')

# Sectionlists! NECESSARY.

## Roe22
SL_NAMES = ['somatic', 'axonal', 'apical', 'basal', "oblique_prox", "oblique_med", "oblique_dist", "trunk_prox", "trunk_med", "trunk_dist"]  


## To21 stuff
#SL_NAMES = ['somatic', 'axonal', 'trunk_prox', 'trunk_med', 'trunk_dist', "oblique_prox", "oblique_med", "oblique_dist", 'tuft', 'basal']          ## To21_adapted  # 'trunk'
#SL_NAMES = ['somatic', 'axonal', 'apical', 'basal']  # To21_onlyapic_strong.hoc
#SL_NAMES = ['somatic', 'axonal', 'apical', 'basal', "trunk_prox", "trunk_med"]  # To21_nap_strong_trunk_together.hoc
#SL_NAMES = ['regsoma', 'regbasal', 'regtrunk', 'regperitrunk', 'regapical']  ## HUARTIF Model - Different morphology to test if my program with automatic extractions runs for everything, Success! 


# Depcrecated extracting automatically
"""INITIAL_VALUES = [  0.0075, 0.001, 0.0015, 0.035, 0.0005, 2.2618914062501833e-06, 5e-05, 0.0015, 4.482009710899852e-05, 115.3957607556371, 
                    9.031387191839301e-05, 0.1636942175250268, 0.026473888790212396, 0.011664045469379856, 0.035, 85.20239938115083, 0.00012898002027660884, 
                    -79.91709193544224, 0.004303650243862568, 0.03828062817034596, 8.0324964335287e-06, 2.2618914062501833e-06, 1.184948741542104e-06, 
                    9.03113879163968e-05, 4.482009710899852e-05, 115.3957607556371, 9.031387191839301e-05, 0.02, 0.025, 8.0324964335287e-06, 
                    2.2618914062501833e-06, 1.184948741542104e-06, 9.03113879163968e-05, 4.482009710899852e-05, 115.3957607556371, 9.031387191839301e-05, 
                    0.004303650243862568, 0.03828062817034596, 8.0324964335287e-06, 2.2618914062501833e-06, 1.184948741542104e-06, 9.03113879163968e-05, 
                    4.482009710899852e-05, 115.3957607556371, 9.031387191839301e-05]"""


