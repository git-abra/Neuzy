#### Neuzy

## Classes for Models

import sys, pathlib

PP = pathlib.Path(__file__).parent   # PP Parentpath from current file
sys.path.insert(1, str(PP / '..' / 'auxiliaries'))

from constants import *

class GenModel():
    """ Model class for general properties """
    def __init__(   model_name, 
                    modpath = None,             # in constants.py if not given
                    target_feature_file = None, # in constants.py if not given
                    bap_target_file = None, 
                    hippo_bAP = None,  
                    channelblocknames = None # has to be in the fullname format: "gkabar_kad" or "gbar_nax"  (for the start, i couldve solved it differently, but pressure in the back)
                    ):          # stricter on bAP optimization for hippounit
        pass
    # This class should take any method, which can be used by the 
    # child classes respectively


class HocModel(GenModel):
    """
    Inherits from GenModel.
    HocModel to create a Model automatically from 
    extracting information out of an existing HOC model 
    """
    def __init__(   hocpath = None,             # in constants.py if not given
                    sectionlist_list = None, 
                    template_name = None        # from hoc begintemplate "template_name") 
                    ):
        pass


class PyModel(GenModel):
    """ 
    Inherits from GenModel.
    PyModel to create a NEURON model in Python 
    """
    def __init__():
        pass


class HippoModel():
    """ Additional class to run HippoUnit tests """
    def __init__():
        pass