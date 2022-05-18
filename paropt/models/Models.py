#### Neuzy

## Classes for Models

import sys, pathlib

PP = pathlib.Path(__file__).parent   # PP Parentpath from current file
sys.path.insert(1, str(PP / '..' / 'auxiliaries'))

from constants import *

class GenModel():           # General Model
    """ 
    Model class for general properties
    This class should take any method, which can be used by the 
    child classes respectively 
    """
    def __init__(   model_name, 
                    modpath = None,             # in constants.py if not given
                    target_feature_file = None, # in constants.py if not given
                    bap_target_file = None, 
                    hippo_bAP = None,  
                    channelblocknames = None, # has to be in the fullname format: "gkabar_kad" or "gbar_nax"
                    verbose = False 
                    ):
        self.model_name = model_name
        
        if modpath:
            self.modpath = modpath
        else:
            self.modpath = MODPATH          # use constant

        if channelblocknames:    # TODO print detected ionchnames in terminal, select which one by readline of the index by the user, then send the string to blockIonChannel()
            self.channelblocknames = channelblocknames
        else:
            self.channelblocknames = None

        self.target_feature_file = target_feature_file
        self.bap_target_file = bap_target_file

        self.hippo_bAP = hippo_bAP
        if self.hippo_bAP == True:   # Check for hippo_bAP Flag. If True then only a few bAP Features are used, analogue to HippoUnits extraction. This is due to a shortage in experimental data till today.
            self.createBAPTargets()
        else:
            self.hippo_bAP = False
            self.bAP_features_dict = None  
            self.bAP_dpol_features  = ['AP1_amp', 'AP2_amp', 'APlast_amp', 'AP_amplitude', 'time_to_first_spike', 'time_to_second_spike', 'time_to_last_spike', \
                                   'AP_rise_time', 'AP_rise_rate', 'AP_duration', 'AP_duration_half_width', 'Spikecount']
            self.bAP_features = self.bAP_dpol_features + self.bAP_hpol_features   

            self.getTargetFeatures()       # EXTRACTS Target Features with extractTargetFeatures() and therefore doesn't use given, but generates a set of target features based on a model which serves as reference

            self.target_features['bAP'] = self.bAP_features_dict
            self.bAP_features = self.bAP_dpol_features + self.bAP_hpol_features

        self.baselinemodel = None   # Able to set baseline model if wanted/necessary - lacks implementation yet
        self.ionchnames = None

        self.model_features = None # Placeholder for extended functions

        self.loadNeuronScope()
        self.createFeatureDict()

        if verbose:
            self.printVerbose()

    def createFeatureDict(self, ):
        ## Target Features from experimental data file
        self.somatic_features_dict = experimentalDataToDict(file_name = self.target_feature_file, file_path = str(PP / '..' / 'data' / 'features' / 'target_features'))         
        temp_list = []
        temp_hpol_list = []
        temp_dpol_list = []

        for k, v in self.somatic_features_dict.items():
            for feature_name in v.keys():
                if k == "Step-04":                                                          # if "-" in k     
                    temp_hpol_list.append(feature_name)
                else:
                    temp_dpol_list.append(feature_name)

        self.somatic_hpol_features = list(dict.fromkeys(temp_hpol_list))                    # hyperpolarizing features
        self.somatic_dpol_features = list(dict.fromkeys(temp_dpol_list))                    # depolarizing features
        self.somatic_features = self.somatic_hpol_features + self.somatic_dpol_features
        # print("Somatic Features: ", self.somatic_features)

        self.bAP_hpol_features = []
        
        # TODO read dict elements (stepX: {})in depending on the step protocol given with self.stepamps
        #print("\n")
        #print("Target Features: ", self.target_features)
        self.target_features = {}
        self.target_features['Soma'] = self.somatic_features_dict 


    def printVerbose(self):     # TODO find more natural way to call verbose with flag -v or --verbose
        ## Check Target Features
        print("\n")
        print("TARGET FEATURES:")
        print(self.target_features)
        print("\n")

        ## Print all bAP features which are selected for usage.
        print("\n")
        print("bAP Features:")
        print("bAP Features: ", self.bAP_features)
        print("\n")


    def createBAPTargets(self):
        self.bAP_dpol_features  = ['AP1_amp', 'APlast_amp', 'Spikecount']
        self.bAP_hpol_features = []
        self.bAP_features = self.bAP_dpol_features + self.bAP_hpol_features   
        
        if bap_target_file:         # If True, check if bAP Target Features are given with a file           # TODO
            # TODO add ez json load
            self.bAP_features_dict = experimentalDataToDict(file_name = bap_target_file, file_path = str(PP / '..' / 'data' / 'features' /' target_features'))
            # TODO
        else:  # hardcoded crap
            self.target_features['bAP_50um'] = {    'Step08' : { 'AP1_amp': {'Std': 3.84, 'Mean': 66.6474010216}, \
                                                                'APlast_amp': {'Std': 6.66451614848, 'Mean': 56.0027067193}, \
                                                                'Spikecount': {'Std': 1, 'Mean': 6}}}  #7.6800611053 sd ap1

            self.target_features['bAP_150um'] = {   'Step08' : {'AP1_amp': {'Std': 4.42, 'Mean': 61.6405452338}, \
                                                                'APlast_amp': {'Std': 7.62175409041, 'Mean': 41.6724147741}, \
                                                                'Spikecount': {'Std': 1, 'Mean': 6}}}  #8.84061901299 sd ap1

            self.target_features['bAP_250um'] = {   'Step08' : {'AP1_amp': {'Std': 3.37, 'Mean': 57.1478276286}, \
                                                                'APlast_amp': {'Std': 2.39551093081,  'Mean': 21.1507839635}, \
                                                                'Spikecount': {'Std': 1, 'Mean': 6}}}  #6.74288151869 sd ap1

            self.target_features['bAP_350um'] = {   'Step08' : {'AP1_amp': {'Std': 2.91, 'Mean': 52.5065653152}, \
                                                                'APlast_amp': {'Std': 3.67378280696, 'Mean': 9.81008709754}, \
                                                                'Spikecount': {'Std': 1, 'Mean': 6}}}  #5.82443856294 sd ap1

            """self.target_features['bAP_50um'] = {    'Step08' : { 'AP1_amp': {'Std': 7.6800611053, 'Mean': 66.6474010216}, \
                                                    'APlast_amp': {'Std': 6.66451614848, 'Mean': 56.0027067193}}}

            self.target_features['bAP_150um'] = {   'Step08' : {'AP1_amp': {'Std': 8.84061901299, 'Mean': 61.6405452338}, \
                                                    'APlast_amp': {'Std': 7.62175409041, 'Mean': 41.6724147741}}}

            self.target_features['bAP_250um'] = {   'Step08' : {'AP1_amp': {'Std': 6.74288151869, 'Mean': 57.1478276286}, \
                                                    'APlast_amp': {'Std': 2.39551093081,  'Mean': 21.1507839635}}}

            self.target_features['bAP_350um'] = {   'Step08' : {'AP1_amp': {'Std': 5.82443856294, 'Mean': 52.5065653152}, \
                                                    'APlast_amp': {'Std': 3.67378280696, 'Mean': 9.81008709754}}}"""  # strong propagating for AP1_amp

    def loadNeuronScope(self):
        """ 
        Loads modpath into neuron scope. Only has to be done once to be available in the runtime 
        Parameters
        ----------
        self.modpath : Path to mod files. For multiple models add all their mod files into this folder. 
        Different but same-named mod files for different models have to be manually changed to not overwrite each other.

        Returns
        -------
        void : No return value

        // Note // In a future version there will probably be the option to create multiple modpaths, one for each model.   
        """
        ## Load Run Controls
        h.load_file('stdrun.hoc')  # define h.run() function ; not needed if "gui" is imported from neuron

        ## Mod Files
        try:
            if self.modpath:
                h.nrn_load_dll(self.modpath)
            else: 
                h.nrn_load_dll(MODPATH)     # use constant: MODPATH
            print("Mod files are loaded in!")
        except Exception as e:
            print("Mod files weren't able to load, check your pwd and if they are in your \
            'mods' folder and compiled.", e)
    
    def deleteCell(self):
        # Not sure if needed, I think I rather have to delete the cells in the neuron scope
        # But works to garbage collect old cells in RAM, as tested experimentally on total RAM usage.
        self.mycell = None

    def blockIonChannel(self):
        #### Block Ion Channel for Pharmacodynamics Testing - bandaid gbar to 0

        # TODO maybe set the other values of the whole mech in 'density_mechs' also to 0. 
        # Some channels, depending on the nmodl file, can still influence the conductance,
        # if they are interdependent with another channel
        # see https://www.neuron.yale.edu/phpBB/viewtopic.php?t=4057
        
        # short version
        if isinstance(self.channelblocknames, list):            # if multiple are given
            for element in self.channelblocknames: 
                for sl in self.sectionlist_list: 
                    inputsl = getattr(self.mycell, sl) 
                    for sec in inputsl:
                        setattr(sec, element, 0)                # set to 0
        else:
            for sl in self.sectionlist_list:            
                inputsl = getattr(self.mycell, sl)           
                for sec in inputsl:
                    setattr(sec, self.channelblocknames, 0)     # set to 0

        # long version with safety checks for data integrity
        """mechname_list = []
        mt = h.MechanismType(0)
        mname = h.ref('')
        for i in range(mt.count()):
            mt.select(i)
            mt.selected(mname)
            mechname_list.append(mname[0]) 

        for sl in self.sectionlist_list:            
            inputsl = getattr(self.mycell, sl)           
            for sec in inputsl:
                setattr(sec, self.channelblocknames, 0) 
                for mech in sec.psection()['density_mechs'].keys():             
                    if mech in mechname_list and mech == self.channelblocknames.split("_", 1)[1]:
                        for ionchname, ionchvalue in sec.psection()['density_mechs'][mech].items():                             
                            if ionchname == self.channelblocknames.split("_", 1)[0]:
                                setattr(sec, self.channelblocknames, 0) # set channel value on 0 
                            else:
                                continue"""


## Model with HOC as input

class HocModel(GenModel):
    """
    Inherits from GenModel.
    HocModel to create a Model automatically from 
    extracting information out of an existing HOC model 
    """
    def __init__(   self,
                    model_name, 
                    modpath = None,             # in constants.py if not given
                    target_feature_file = None, # in constants.py if not given
                    bap_target_file = None, 
                    hippo_bAP:bool = None,  
                    channelblocknames = None,   # has to be in the fullname format: "gkabar_kad" or "gbar_nax"  
                    hocpath = None,             # in constants.py if not given
                    sectionlist_list:list = None, 
                    template_name = None,       # from hoc begintemplate "template_name") 
                    parameterkeywords:list = None
                    ):
        super().__init__(   model_name, 
                            modpath = None,             # in constants.py if not given
                            target_feature_file = None, # in constants.py if not given
                            bap_target_file = None, 
                            hippo_bAP = None,  
                            channelblocknames = None  # has to be in the fullname format: "gkabar_kad" or "gbar_nax" 
                            )
        if sectionlist_list:
            self.sectionlist_list = sectionlist_list
        else:
            self.sectionlist_list = SL_NAMES       # use constant

        if hocpath:
            self.hocpath = hocpath
        else:
            self.hocpath = HOCPATH          # use constant

        if template_name:
            self.template_name = template_name
        else:
            self.template_name = get_template_name(model_name)
            print("Extracted template_name: " + str(self.template_name) + ", because no template_name was given.")
            lg.info("Extracted template_name: " + str(self.template_name) + ", because no template_name was given.")

        if parameterkeywords:
            self.parameterkeywords = parameterkeywords
        else: 
            self.parameterkeywords = ["bar"]    # List of parameter key words like "bar" for gbar active ion channels. You can basically choose anything from neuron's psection() density_mech dict.
                                                # check for "bar", "tau", "pas" or whatever you want

        self.readHocModel()
        self.createHocModel()
        self.initializeCell()

    def readHocModel(self):
        """
        Read in Hoc Model with h.xopen()
        """
        try:
            HOCPATH_temp = pathlib.Path(self.hocpath)            # Pathlib object
            h.xopen(str(HOCPATH_temp / self.model_name))    # stringify pl object for concatenation with '/'
            print("Hoc Morphology is loaded in!")
        except Exception as e:
            print("Hoc Morphology file wasn't able to load, check your pwd and if the morphology is in your 'morphos' folder.", e)

    def createHocModel(self):   # TODO automatically load READ-IN template in
        """
        Creates a cell from a template. Prerequisite is a read in Hoc Model
        """
        print("Template name: " + str(self.template_name) + " found. Creating cell from Hoc..")
        lg.info("Template name: " + str(self.template_name) + " found. Creating cell from Hoc..")
        HOCPATH_temp = pathlib.Path(self.hocpath)
        cell = getattr(h, self.template_name)(HOCPATH_temp / self.model_name)

        return cell

    def initializeCell(self):
        """ 
        Create a Hoc Cell from template
        """

        self.mycell = self.createHocModel()      # Create cell "mycell" from template.

        if self.channelblocknames:               # Block ion channels, if set.
            self.blockIonChannel()

    def getSectionNames(self):
        """
        Returns
        -------
        df : Dataframe of sectionnames(row) to sectionlists (col)
        mysecnamelist : List of sectionnames(nested elements) inside sectionlists(elements)
        """
        mysecnamedict = {}
        try:
            if self.sectionlist_list:
                for sl in self.sectionlist_list:
                    inputsl = getattr(self.mycell, sl)
                    mysecnamelist = []
                    for sec in inputsl:
                        mysecnamelist.append(h.secname(sec = sec).split('.', 1)[1])     # maxsplit = 1 , take second element after '.'
                    mysecnamedict.update({sl: mysecnamelist})
                df = pd.DataFrame.from_dict(mysecnamedict, orient = 'index').transpose()
            else:
                # Use best practice "all" Sectionlist Keyword
                try:       
                    mysecnamelist = []
                    for sec in self.mycell.all:
                        mysecnamelist.append(h.secname(sec = sec).split('.', 1)[1])
                except Exception as e:
                    print("Seems like there is no best practice Sectionlist called: 'all', specified in your model.")
                    print("If you want to fix this problem, provide a SectionList for the program or add your sections to 'all' in your Hoc.")
                    print("E.g. all = new SectionList(); sectionname all.append()")
        except Exception as e:
            print("Couldn't read in sectionlists")
            print("Please give your sectionlists as list or set the constant for self.sectionlist_list in ../auxiliaries/constants.py")
            print("The template_name for a cell shall not contain a '.' .")
            print(e)

        return df, mysecnamelist

    def getMechanismItems(self):
        """ Prerequisites: Read-in HocObject / HocObject in Scope 
            Retrieves what self.parameterkeywords is asking for.

            Returns
            -------
            x_nonan : 1D array of Parameters without NaNs. (Sectionlists where channels are missing have nan value for it)
            indices : 1D array of nan indices - Needed for reimplementing the nan values with insertNans()
        """

        myionsdict = {}
        mechname_list = []
        mt = h.MechanismType(0)
        mname = h.ref('')
        for i in range(mt.count()):
            mt.select(i)
            mt.selected(mname)
            mechname_list.append(mname[0])
            #print(mechname_list)
       
        if self.sectionlist_list:
            for sl in self.sectionlist_list:        
                inputsl = getattr(self.mycell, sl)
                myionsdict_temp = {}           
                for sec in inputsl:     
                    for mech in sec.psection()['density_mechs'].keys():                  
                        if mech in mechname_list:  # compare with mech to avoid errors of placeholder key/values from neuron api for a model
                            for ionchname, ionchvalue in sec.psection()['density_mechs'][mech].items():           
                                for parameterkeyword in self.parameterkeywords:
                                    if parameterkeyword in ionchname:          # check for "bar", "tau", "pas" or whatever you want !
                                        for i in ionchvalue:
                                            myionsdict_temp.update({str(ionchname + '_' + mech): ionchvalue[0]})

                                            # commented section was before blockIonChannel integration
                                            """if i != 0:                         # only check for gbars with a value                 
                                                # Have to save with appended sec.psection()['density_mechs'].keys() name (mech)
                                                myionsdict_temp.update({str(ionchname + '_' + mech): ionchvalue[0]})
                                                # myionsdict_temp.update({str(ionchname + '_' + mech): i})
                                            else:
                                                # Maybe set values here to 0 instead of having NaN due to the jump in updating myionsdict
                                                continue """
                                    else:
                                        continue        # do nothing and jump
                myionsdict.update({sl: myionsdict_temp})
        else:
        # TODO use "all" sectionlist
            print("ERROR: No Sectionlist")
            pass  
        
        df = pd.DataFrame(myionsdict)     # 2D of Ionchannel Values per SectionList  # Not used, but better keep it
        #print("INITIAL DATA: ")
        #print("\n")
        #print(df)
        self.ionchnames = list(df.index)
        x = convertDfTo1D(df)             # 1D array of Df , with Nans
        indices = getNans(x)
        x_nonan = removeNans(x)
    
        return x_nonan, indices


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


class HippoModel():
    """ Additional class to run HippoUnit tests """
    def __init__():

        pass