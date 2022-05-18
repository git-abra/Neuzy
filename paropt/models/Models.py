#### Neuzy

## Classes for Models

import sys, pathlib

PP = pathlib.Path(__file__).parent   # PP Parentpath from current file
sys.path.insert(1, str(PP / '..' / 'auxiliaries'))

from constants import *




class GenModel():
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
                    channelblocknames = None # has to be in the fullname format: "gkabar_kad" or "gbar_nax" 
                    ):
        pass


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
            else: # use constant: MODPATH                           
                h.nrn_load_dll(MODPATH)
            print("Mod files are loaded in!")
        except Exception as e:
            print("Mod files weren't able to load, check your pwd and if they are in your 'mods' folder and compiled.", e)
    
    # Create cell
    def initializeCell(self):
        """ 
        Create a Hoc Cell from template
        """

        self.mycell = self.createHocModel()      # Create cell "mycell" from template.

        if self.channelblocknames:               # Block ion channels, if set.
            self.blockIonChannel()

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
                    hippo_bAP = None,  
                    channelblocknames = None,   # has to be in the fullname format: "gkabar_kad" or "gbar_nax"  
                    hocpath = None,             # in constants.py if not given
                    sectionlist_list = None, 
                    template_name = None        # from hoc begintemplate "template_name") 
                    ):
        super().__init__(   model_name, 
                            modpath = None,             # in constants.py if not given
                            target_feature_file = None, # in constants.py if not given
                            bap_target_file = None, 
                            hippo_bAP = None,  
                            channelblocknames = None  # has to be in the fullname format: "gkabar_kad" or "gbar_nax" 
                            ):
            pass
        pass

    def readHocModel(self):
        """
        Read in Hoc Model with h.xopen()
        Parameters
        ----------
        self.model_name
        """
        ## HOC Files
        try:
            HOCPATH_temp = pathlib.Path(self.hocpath)            # Pathlib object
            h.xopen(str(HOCPATH_temp / self.model_name))    # stringify pl object for concatenation with '/'
            print("Hoc Morphology is loaded in!")
        except Exception as e:
            print("Hoc Morphology file wasn't able to load, check your pwd and if the morphology is in your 'morphos' folder.", e)


    def createHocModel(self):   # TODO automatically load READ-IN template in
        """
        Creates a cell from a template. Prerequisite is a read in Hoc Model
    
        Parameters
        ----------
        self.template_name

        Returns
        -------
        cell : HocObject
        """
        """
        if self.template_name == None: ## UNUSED, overwritten by class property -> template_name = None calls get_template_name()   
            lg.info("No Template name was given. CA1_PC_Tomko will be initialized as the baseline of this project.")
            cell = h.CA1_PC_Tomko()
        else: # USED
        """
        print("Template name: " + str(self.template_name) + " found. Creating cell from Hoc..")
        lg.info("Template name: " + str(self.template_name) + " found. Creating cell from Hoc..")
        HOCPATH_temp = pathlib.Path(self.hocpath)
        cell = getattr(h, self.template_name)(HOCPATH_temp / self.model_name)

        return cell

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
                            ):
            pass
        pass




class HippoModel():
    """ Additional class to run HippoUnit tests """
    def __init__():
        pass