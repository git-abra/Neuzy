## Model created in Python, without HOC as input.
# Basically needs a lot of input or preformatted data to read-in, will see
class PyModel(GenModel):
    """ 
    Inherits from GenModel.
    PyModel to create a NEURON model in Python 
    """
    def __init__(   self, 
                    model_name, 
                    modpath = None,             # in constants.py if not given
                    target_feature_file = None, # in constants.py if not given
                    bap_target_file = None, 
                    hippo_bAP = None,  
                    channelblocknames = None  # has to be in the fullname format: "gkabar_kad" or "gbar_nax"  (for the start, i couldve solved it differently, but pressure in the back)
                    ):
        super().__init__(   model_name, 
                            modpath = None,             # in constants.py if not given
                            target_feature_file = None, # in constants.py if not given
                            bap_target_file = None, 
                            hippo_bAP = None,  
                            channelblocknames = None # has to be in the fullname format: "gkabar_kad" or "gbar_nax"  (for the start, i couldve solved it differently, but pressure in the back))
                            )
        pass