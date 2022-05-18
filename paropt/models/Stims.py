#### Neuzy


class GenStim():    # General Stim
    def __init( self, delay: int = 150, duration: int = 400, 
                tstop: int = 750, cvode_active: bool = None,
                stepamps:dict = {'Step-04': -0.4, 'Step08' : 0.8}):
        """
        docs for arguments tbc
        """

        ## Properties of the full call to run simulation
        self.delay = delay
        self.duration = duration
        self.tstop = tstop

        self.stepamps = stepamps
        if cvode_active:
            self.cvode_active = cvode_active
        else:
            self.cvode_active = False  # Doesn't work because of EFEL X and Y axes "Assertion fired(efel/cppcore/Utils.cpp:33): X & Y have to have the same point count"

class SortOutStim(GenStim):      # Stim with function to sort out early - i.e. Models which are not throwing APs
    """
    docs for arguments tbc
    """
    def __init__(   self, delay:int, duration:int, tstop:int, cvode_active:bool,     # as input arguments for super() to genmodel parent
                    delay_firstspike:int = 50, duration_firstspike:int = 65, tstop_firstspike:int = 150,
                    ):
        super().__init__(delay, duration, tstop, cvode_active)

        ## Firstspike properties to check for the occurrence of the first few AP 
        self.delay_firstspike = delay_firstspike
        self.duration_firstspike = duration_firstspike
        self.tstop_firstspike = tstop_firstspike
        
        self.AP_firstspike = False
        self.bAP_firstspike = False