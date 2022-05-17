#### Neuzy ####

#################################################################
# "CompleteOptModel.py"
# Fanantenana
#################################################################

## File with model generation, optimization and output

## Packages
import sys, pathlib, os, time, warnings, subprocess, csv, json

PP = pathlib.Path(__file__).parent   # PP Parentpath from current file
PP_str = str(PP)        # if wanted for quickfix without pathlib syntax

sys.path.insert(1, str(PP / '..' / 'figures'))
sys.path.insert(1, str(PP / '..' / 'auxiliaries'))      ## PP needed before call; sys.path[path/auxiliaries] needed for constants.py -> get pathnames like ROOTPATH

from run_mpi import MPIrun
import myplots
from create_data import *
from constants import *

from copy import *
import logging as lg
import multiprocessing as mp
import numpy as np                  # Random Generator & Array
import scipy.optimize as scp
import pandas as pd                 # Dataframe Usage
from neuron import h                # NEURON
from neuron.units import ms, mV
import efel                         # Extract Spike Features
from mpi4py import MPI              # MPI support
from matplotlib import pyplot


class CompleteOptModel():
    """ 
    Full-fledged optimization and data creation class
    """
    def __init__(self, 
                model_name,
                modpath = None,                 # in constants.py if not given
                hocpath = None,                 # in constants.py if not given
                sectionlist_list = None, 
                template_name = None,           # from hoc begintemplate "template_name"
                target_feature_file = None,
                bap_target_file = None,     
                hippo_bAP = None,               # stricter on bAP optimization for hippounit
                channelblocknames = None):      # has to be in the fullname format: "gkabar_kad" or "gbar_nax"  (for the start, i couldve solved it differently, but pressure in the back)
        """ 
        Constructor
        Parameters
        ----------
        model_name -> string : Name of the model, which you want to use.
        modpath -> string : Path to the mod files. Modpath for all models, one path which includes mods for all models.
        hocpath -> string : Path to the hoc file.
        sectionlist_list -> List of Strings : Sectionlist Name List.
        template_name -> string : Name of cell template.
        target_feature_file -> json : Name of target feature file in target feature path.
        """
        ## Model Properties and init


        self.model_name = model_name        # Standard Hoc model with morphology
        self.rank = MPIrun.rank

        if sectionlist_list:
            self.sectionlist_list = sectionlist_list
        else:
            self.sectionlist_list = SL_NAMES       # use constant

        if modpath:
            self.modpath = modpath
        else:
            self.modpath = MODPATH          # use constant

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

        if channelblocknames:    # TODO print detected ionchnames in terminal, select which one by readline of the index by the user, then send the string to blockIonChannel()
            self.channelblocknames = channelblocknames
        else:
            self.channelblocknames = None

        self.loadNeuronScope()
        self.readHocModel()
        self.initializeCell()

        self.baselinemodel = None           # Able to set baseline model if wanted / necessary - lacks implementation yet
        self.ionchnames = None

        ## Simulation Properties
        self.parameterkeywords = ["bar"]            # List of parameter key words like "bar" for gbar active ion channels. You can basically choose anything from neuron's psection() density_mech dict.
                                                    # check for "bar", "tau", "pas" or whatever you want !
        self.stepamps = {'Step-04': -0.4, 'Step08' : 0.8}            #'Step08' : 0.8, 'Step10' : 1.0 # List of Stepamplitudes to be used


        ## Firstspike properties to check for the occurrence of the first few AP 
        self.delay_firstspike = 50
        self.duration_firstspike = 65
        self.tstop_firstspike = 150
        self.AP_firstspike = False
        self.bAP_firstspike = False

        ## Properties of the full call to run simulation
        self.delay = 150
        self.duration = 400
        self.tstop = 750
        self.cvode_active = False           # Doesn't work because of EFEL X and Y axes "Assertion fired(efel/cppcore/Utils.cpp:33): X & Y have to have the same point count"

        ## Target Features from experimental data file
        self.somatic_features_dict = experimentalDataToDict(file_name = target_feature_file, file_path = str(PP / '..' / 'data' / 'features' / 'target_features'))         
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

        ## Use Target Features for bAP optimization
        if hippo_bAP == True:           # Check for hippo_bAP Flag. If True then only a few bAP Features are used, analogue to HippoUnits extraction. This is due to a shortage in experimental data till today.
            self.hippo_bAP = True
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

        else:       # no bAP
            self.hippo_bAP = False
            self.bAP_features_dict = None  
            self.bAP_dpol_features  = ['AP1_amp', 'AP2_amp', 'APlast_amp', 'AP_amplitude', 'time_to_first_spike', 'time_to_second_spike', 'time_to_last_spike', \
                                   'AP_rise_time', 'AP_rise_rate', 'AP_duration', 'AP_duration_half_width', 'Spikecount']
            self.bAP_features = self.bAP_dpol_features + self.bAP_hpol_features   

            self.getTargetFeatures()       # EXTRACTS Target Features with extractTargetFeatures() and therefore doesn't use given, but generates a set of target features based on a model which serves as reference

            self.target_features['bAP'] = self.bAP_features_dict
            self.bAP_features = self.bAP_dpol_features + self.bAP_hpol_features   

   
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

        """
        if self.bAP_features == self.somatic_features:
            self.features = self.bAP_features
        else:
            self.features = list(dict.fromkeys(self.somatic_features + self.bAP_features))      # remove duplicates
        """
        
        self.model_features = None

        # TODO create this one at start of runtime here by calling the initial methods for init data and features of target          
        
        # Specify Method
        self.method = "Nelder-Mead" # Choose from: "L-BFGS-B", "Nelder-Mead" or "CG"

        self.init_cost_threshold = 2
        self.init_cost_optimizer_threshold = 5

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
     
    def updateAutoParameters(self, x, indices):
        """
        updateAutoParameters() updates the instantiated HocObject cell, self.mycell.

        Parameters
        ----------
        x : (Updated) parameters to be inserted into the currently active hocobject cell.
        indices : Indices to reinsert NaNs to keep the 2D sectionlist dimensions.

        Returns
        -------
        void : Cell in scope gets updated but doesn't have to be returned.
        """

        # updateAutoParameters - Sectionlist Specific! Every section inside a section has the same values (maybe distributed function in hoc still works)

        # could split into multiple functions to reassign the dataframe from 1D array to 2D with self.ionchnames which comes from SciPy - 
        # so I don't have to give self.ionchnames as additional argument for this function
         
        x = insertNans(x, indices)      # Give Nans back
        X = convert1DTo2DnpArr(x)       # Convert back to 2D array
        df = pd.DataFrame(X, index = self.sectionlist_list, columns = self.ionchnames).transpose()      # updated df # Reassign model-specific ordered ion channel names 
        # print(df)
        if self.sectionlist_list:
            for sl in self.sectionlist_list:   
                inputsl = getattr(self.mycell, sl)
                for sec in inputsl: 
                    test1_dict = copy(sec.psection()['density_mechs'])
                    for ionchname in self.ionchnames:       # just make sure that my ionchnames are fitting, could probably also do assertions here
                        ionchnamekey = ionchname.split('_', 1)[1]
                        ionchnamekeykey = ionchname.split('_', 1)[0]
                        if ionchnamekey in sec.psection()['density_mechs'].keys():                      # check if keys exist (e.g. hd doesn't exist in axonal)   
                            if ionchnamekeykey in sec.psection()['density_mechs'][ionchnamekey].keys(): # e.g. ghdbar doesn't exist in axonal)                       
                                # update all new random values
                                update = df.loc[ionchname, sl]
                                setattr(sec, ionchname, update)

                                ### values change over distance in each segment in To21 model - To21_nap.hoc specific code, for framework usage, comment this out ###
                                if ionchnamekey == "hd" and ionchnamekeykey == "ghdbar" or ionchname == "ghdbar_hd":     # just listed everything in or
                                    value = copy(sec.ghdbar_hd)
                                    #print("GHDBAR ", sec, sec.ghdbar_hd)
                                    for seg in sec:
                                        dist = h.distance(seg.x, sec=sec)      
                                        if dist == 0:               ## TODO Unittest and maybe remove 
                                            continue
                                        else:                            
                                            seg.hd.ghdbar = (1 + 3/100 * dist) * value #sec.ghdbar_hd  # 1.9042409723832741e-05 #sec.ghdbar_hd 
                                    #print("GHDBAR: ", sec, sec.psection()["density_mechs"]["hd"]["ghdbar"])     
                                # else they change over distance again and don't stay on their <random> value
                                if ionchnamekey == "kad" and ionchnamekeykey == "gkabar" or ionchname == "gkabar_kad":
                                    value = copy(sec.gkabar_kad)
                                    #print("GKABAR ", sec, sec.gkabar_kad)
                                    for seg in sec:
                                        dist = h.distance(seg.x, sec=sec) 
                                                        
                                        seg.kad.gkabar = (15/(1 + np.exp((300-dist)/50))) * value #0.012921529390557651   # sec.gkabar_kad
                                    # print("GKABAR: ", sec, sec.psection()["density_mechs"]["kad"]["gkabar"])
                                """## implement exceptions for individually set channels here                     
                                if sl == "trunk" or sl == "apical":      # trunk parameters aren't part of the distribute_distance function
                                   if str(sec).split(".", 1)[1] == "radTprox" \
                                        or str(sec).split(".", 1)[1] == "radTmed"  \
                                        or str(sec).split(".", 1)[1] == "radTdist":
                                        continue

                                elif str(sec).split(".", 1)[1] == "rad_t2":
                                    continue"""                   
                                
                            else:
                                continue
                        
                        else:
                            continue

        else:       
            print("No sectionlist names given in self.sectionlist_list")
            pass
            # TODO build for 1-column "all" sectionlist with fixed indices
            """
            for sec in self.mycell.all:
                for ionchname in self.ionchnames:
                        ionchnamekey = ionchname.split('_', 1)[1]
                        ionchnamekeykey = ionchname.split('_', 1)[0]
                        if ionchnamekey in sec.psection()['density_mechs'].keys():
                            if ionchnamekeykey in sec.psection()['density_mechs'][ionchnamekey].keys():
                            else:
                                continue
                        else:
                            continue
            """
        print(df)

    def sampleRecAround(self, 
                        output_array, 
                        out_fun, 
                        indices, 
                        multiplier = 1.05, 
                        counter = 0,
                        maxcounter = 0, 
                        maxresults = 50,
                        maxiter = 5000):

        """ Function to sample recursively around till there is no more better result than the last best result
        Parameters
        ----------
        output_array : np.array of parameters with NaNs
        out_fun      : Calculated cost for the optimized or sufficient parameter combination
        multiplier   : Multiplier relative to parameter values. Bounds are multiplied and divided by Multiplier
        counter      : Recursive Startcounter for successful iterations, should be 0 or adapted with respect to maxresults.
        maxcounter   : Recursive Startcounter for all iterations, should be 0 or adapted with respect to maxiter.
        maxresults   : Recursive Result Endcounter.
        maxiter      : Recursive Iteration Endcounter.

        # TODO  Grant additionally the counter option for unsuccessful iterations? Then with flag though, which option should terminate.
        # Known Bugs: Hoc model NMODL files aren't created for populations, so it can happen that some values are over a specific buffer and it raises the scopmath library error in NEURON.

        Returns
        -------
        Writes to file and returns None when maximum of recursive results is reached.
        """
        
        if counter < maxresults and maxcounter < maxiter:  # sample XX times around and check if costs become better
            ## use result for more results
            try:     
                sample_array = sampleResultsAround(output_array, multiplier = multiplier)
                sample_array_nonan = removeNans(sample_array)
                ## TODO abortion because of NEURON scopmath library error, convergence not achieved ... this API
                # so it has problems to overwrite itself every time and instead should be a reinitialized cell
                sample_fun = self.calculateFitness(sample_array_nonan, indices)
                
                if sample_fun < out_fun:
                    counter = counter + 1
                    maxcounter = maxcounter + 1

                    print("Sample is better than original output combination, saving sample")
                    lg.info("Sample is better than original output combination, saving sample")
                    
                    with open(self.sample_output_csv_fun_data, "a") as f:
                        print(sample_fun, end='\n', file=f)                 # *sample_fun

                    #sample_array = insertNans(sample_array, indices)
                    sample_output_list = sample_array.tolist()
                    with open(self.sample_output_csv_par_data, "a") as f:
                        print(*sample_output_list, sep=',', end='\n', file=f)
                    
                    ## Try even more but set limit to 100 times of recursion
                    print("Trying to find more samples based on the successful sample on iteration " + str(maxcounter) + " with " + str(counter) + " results already")
                    lg.info("Trying to find more samples based on the successful sample on iteration " + str(maxcounter) + " with " + str(counter) + " results already")
                    self.sampleRecAround(sample_array, sample_fun, indices, counter = counter, maxcounter = maxcounter)

                ## Recursion - try till it gets better than out_fun
                else:
                    maxcounter = maxcounter + 1
                    print("Sample is not better, sampling again with input values on iteration " + str(maxcounter) + " with " + str(counter) + " results already")
                    lg.info("Sample is not better, sampling again with input values on iteration " + str(maxcounter) + " with " + str(counter) + " results already")
                    self.sampleRecAround(output_array, out_fun, indices, counter = counter, maxcounter = maxcounter)  
            except Exception as e:
                # Hoc Errors... scopmath .... I DON'T KNOW WHY
                print("Exception caught: ", e ," reinitializing with inital values")
                lg.info("Exception caught, reinitializing with initial values")
                self.deleteCell()
                self.initializeCell()
                maxcounter = maxcounter + 1
                self.sampleRecAround(output_array, out_fun, indices, counter = counter, maxcounter = maxcounter)
        else:
            print("Sampling process completed.")
            lg.info("Sampling process completed.")

            # Saving the best results separately
            with open(self.sample_best_output_csv_fun_data, "a") as f:
                    print(out_fun, end='\n', file=f)                 # *sample_fun

            sample_best_output_par_list = output_array.tolist()
            with open(self.sample_best_output_csv_par_data, "a") as f:
                    print(*sample_best_output_par_list, sep=',', end='\n', file=f)

            return

    def finalParameters(self, x):
        # finalParameters - Sectionlist Specific! Every section inside a section has the same values (maybe distributed function in hoc still works)

        # No nan value inserting here, they come out with nan values due to position-based updating of the values in a dataframe, see below or in updateAutoParameters()
        
        # Convert back to 2D array
        X = convert1DTo2DnpArr(x[5])        # just testing for the first combination of values
        df = pd.DataFrame(X, index = self.sectionlist_list, columns = self.ionchnames).transpose()      # updated df # Reassign model-specific ordered ion channel names
        #print(df)  # tested, prints with nans
        self.ionchnames = list(df.index)  # redundant, but anyway who tf cares
        if self.sectionlist_list:
            for sl in self.sectionlist_list:
                inputsl = getattr(self.mycell, sl)
                for sec in inputsl:        
                    for ionchname in self.ionchnames:
                        ionchnamekey = ionchname.split('_', 1)[1]
                        ionchnamekeykey = ionchname.split('_', 1)[0]
                        if ionchnamekey in sec.psection()['density_mechs'].keys():
                            if ionchnamekeykey in sec.psection()['density_mechs'][ionchnamekey].keys():
                                setattr(sec, ionchname, df.loc[ionchname, sl]) 
                            else:
                                continue
        else:
            pass
            # TODO build for 1-column "all" sectionlist with fixed indices
            """
            for sec in self.mycell.all:
                for ionchname in self.ionchnames:
                        ionchnamekey = ionchname.split('_', 1)[1]
                        ionchnamekeykey = ionchname.split('_', 1)[0]
                        if ionchnamekey in sec.psection()['density_mechs'].keys():
                            if ionchnamekeykey in sec.psection()['density_mechs'][ionchnamekey].keys():
                            else:
                                continue
                        else:
                            continue
            """
        # return self.mycell

    def stimulateIClamp_firstspike(self):   # Default values are from Schneider et al. 2021
        '''
        IClamp Optimization Protocols
        Stimulate IClamp on self.mycell /w random values from rnddata.

        Parameters
        ----------
        self.delay : int; Stim delay
        self.duration : int; Stim duration
        self.stepamps : List[int]; Step amplitude values, one simulation for each step amplitude

        Returns
        -------
        traces_per_stepamp : Dict: {stepampname: {'Soma': soma_arr , 'bAP': bAP1_arr}}
        '''
        efel.api.reset()
        traces_per_stepamp_dict = {}

        # remove all hyperpolarizing keys because bAP doesn't matter hyperpolarizing currents
        stepamps_dict = {k:v for k,v in self.stepamps.items() if '-' not in k}   # REMOVE HYPERPOLARIZING CURRENT FROM THIS TEST

        for stepampname, stepamp in stepamps_dict.items():
            #print(stepampname)
            start = time.time()

            stim = h.IClamp(self.mycell.soma[0](0.5)) # stim at soma
            stim.delay = self.delay_firstspike
            stim.dur = self.duration_firstspike
            stim.amp = stepamp
            soma_vec = h.Vector().record(self.mycell.soma[0](0.5)._ref_v) # record at middle (0,5) of soma

            if self.hippo_bAP == True:
                ## Hippounit bap positions, manual way.
                bAP1_vec = h.Vector().record(self.mycell.radTprox(0.5)._ref_v)
                bAP2_vec = h.Vector().record(self.mycell.radTmed(0.5)._ref_v)    # 205um distance, radtprox makes positive ap_peak also  
                bAP3_vec = h.Vector().record(self.mycell.radTdist(0.22727272727272727)._ref_v)
                bAP4_vec = h.Vector().record(self.mycell.radTdist(0.3181818181818182)._ref_v)
                bAP5_vec = h.Vector().record(self.mycell.radTdist(0.6818181818181819)._ref_v)
                bAP6_vec = h.Vector().record(self.mycell.radTdist(0.7727272727272728)._ref_v)
            else:
                bAP1_vec = h.Vector().record(self.mycell.radTmed(1)._ref_v)    # 205um distance, radtprox makes positive ap_peak also

            # TODO extension: get region names automatically by distance and use setattr(self.mycell, sectionname)._ref_v
            
            time_vec = h.Vector().record(h._ref_t)
            
            h.dt = 0.1
            h.tstop = self.tstop_firstspike
            h.v_init = -65
            h.celsius = 35
            h.init()
            h.run()

            """pyplot.figure(figsize=(8,4)) # Default figsize is (8,6)
            pyplot.plot(time_vec, bAP1_vec)
            pyplot.xlabel('time (ms)')
            pyplot.ylabel('mV')
            pyplot.show()"""

            #myplots.plotStandardTrace(soma_vec, time_vec, h.tstop)
            #myplots.plotStandardTrace(bAP1_vec, time_vec, h.tstop)
            # h.finitialize(-65 * mV) # alt: h.run() ; finitialize https://www.neuron.yale.edu/neuron/static/py_doc/simctrl/programmatic.html
            # h.continuerun(600 * ms) # alt: h.tstop = 200
            soma_arr = np.array(soma_vec)
            if self.hippo_bAP == True:           
                bAP1_arr = np.array(bAP1_vec)
                bAP2_arr = np.array(bAP2_vec)
                bAP3_arr = np.array(bAP3_vec)
                bAP4_arr = np.array(bAP4_vec)
                bAP5_arr = np.array(bAP5_vec)
                bAP6_arr = np.array(bAP6_vec)
                traces_per_stepamp_dict.update({stepampname: {  'Soma': soma_arr , 'bAP1': bAP1_arr, \
                                                                'bAP2': bAP2_arr, 'bAP3': bAP3_arr, \
                                                                'bAP4': bAP4_arr, 'bAP5': bAP5_arr, \
                                                                'bAP6': bAP6_arr}})        
            else:
                bAP1_arr = np.array(bAP1_vec)
                traces_per_stepamp_dict.update({stepampname: {'Soma': soma_arr , 'bAP': bAP1_arr}})

        traces = []


        for locationtraces in traces_per_stepamp_dict.values():         # 0.8, then 1.0
            for location, locationtrace in locationtraces.items():      # Soma, then bAP (1-7)
                trace = {} 
                trace['V'] = locationtrace              # Set the 'V' (=voltage) key of the trace
                trace['T'] = time_vec                   # Set the 'T' (=time) key of the trace

                stim_end = self.delay_firstspike + self.duration_firstspike
                trace['stim_start'] = [self.delay_firstspike]      # Set the 'stim_start' (time at which a stimulus starts, in ms) key of the trace
                                                        # Warning: this need to be a list (with one element)
                trace['stim_end'] = [stim_end]          # Set the 'stim_end' (time at which a stimulus end) key of the trace
                                                        # Warning: this need to be a list (with one element)

                traces.append(trace)                    # Multiple traces can be passed to the eFEL at the same time, so the argument should be a list


        stepampnames = list(stepamps_dict.keys())

        temp_soma_model_feature_list = []
        temp_bAP_model_feature_list = []
        soma_model_feature_dict = {}
        bAP_model_feature_dict = {}


        for i in range(len(traces)):
            if i == 0:              # soma is first id
                temp_soma_model_feature_list.append(traces[i])
            else:          
                temp_bAP_model_feature_list.append(traces[i])

        #### ALREADY REMOVED EARLEIR ####
        ## ADAPTIONS FOR HYPERPOLARIZING CURRENT - Removing hyperpolarizing current step as key and as first index of the list which enumerates over the keys - so it is consistent
        # temp_bAP_model_feature_list.pop(0)
        # bAP_stepampnames = [ x for x in stepampnames if "-" not in x ]

        # Set and extract Spiketest features      
        efel.api.setThreshold(-20.0)                                
        soma_model_feature_spike = efel.getFeatureValues(temp_soma_model_feature_list, \
        ['AP1_amp', 'AP1_peak', 'AP2_amp', 'AP2_peak', 'Spikecount', 'time_to_first_spike'], raise_warnings = False)


        efel.api.setThreshold(-53.5)
        efel.setDoubleSetting('interp_step', 0.025)
        efel.setDoubleSetting('DerivativeThreshold', 40)

        bAP_model_feature_spike = efel.getFeatureValues(temp_bAP_model_feature_list, \
            ['AP1_amp', 'APlast_amp', 'Spikecount'], raise_warnings = False)
        
        #print("SOMA", soma_model_feature_spike)
        #print("\n")
        print("BAP", bAP_model_feature_spike)
        #print("\n")
        # all bap
        """bap_spike_list = []
        for i in range(len(temp_bAP_model_feature_list)):
            bAP_model_feature_spike = efel.getFeatureValues([temp_bAP_model_feature_list[i]], \
            ['AP1_amp', 'APlast_amp'], raise_warnings = False)
            bap_spike_list.append(bAP_model_feature_spike)
        print("LENGTH: ", bap_spike_list)
        """
        soma_success = 0
        bAP_success = 0
        
        #print(soma_model_feature_spike)
        for i in range(len(soma_model_feature_spike)):
            if soma_model_feature_spike[i]['AP1_amp'].size > 0 \
                and soma_model_feature_spike[i]['Spikecount'] > 1 \
                and soma_model_feature_spike[i]['time_to_first_spike'] > 0 \
                and soma_model_feature_spike[i]['AP1_peak'] > 0 \
                and soma_model_feature_spike[i]['AP2_peak'] > 0 \
                and soma_model_feature_spike[i]['AP2_amp'] > 0:

                print("Spikecount on soma for stepamp " + str(stepampnames) + " at least 2 on rank " + str(self.rank))
                lg.info("Spikecount on soma for stepamp " + str(stepampnames) + " at least 2 on rank " + str(self.rank))
                soma_success = soma_success + 1  
                # average for step 08 is 9, step10 is 11 , so mid is 10 and 7 is handmade hyperparameter; 16 is there, so it isn't too excitable and spikes spontaneously
            else:
                pass

        #print(bAP_model_feature_spike)
        if soma_success == len(soma_model_feature_spike):
            for i in range(len(bAP_model_feature_spike)):  
                if bAP_model_feature_spike[i]['AP1_amp'].size > 0 \
                    and bAP_model_feature_spike[i]['APlast_amp'].size > 0 \
                    and bAP_model_feature_spike[i]['Spikecount'] >= 1: 
                    """if i < len(bAP_model_feature_spike) - 1:
                        if bAP_model_feature_spike[i]['AP1_amp'] < bAP_model_feature_spike[i+1]['AP1_amp']:      # bAP Attenuation check
                            print("No bAP Attenuation")
                            lg.info("No bAP Attenuation")
                            
                        else:
                            print("Spikecount and bAP Attenuation Success")
                            lg.info("Spikecount and bAP Attenuation Success")
                            bAP_success = bAP_success + 1"""
                    bAP_success = bAP_success + 1
                    """else:
                        print("Spikecount on last bAP for stepamp " + str(stepampnames) + " at least 1 on rank " + str(self.rank))
                        lg.info("Spikecount on last bAP for stepamp " + str(stepampnames) + " at least 1 on rank " + str(self.rank))
                        bAP_success = bAP_success + 1"""
                    #bAP_success = bAP_success + 1    
                    #and bAP_model_feature_spike[i]['time_to_first_spike'] > 0:
                    #and bAP_model_feature_spike[i]['AP1_peak'] > 0 \
                    #and bAP_model_feature_spike[i]['AP2_peak'] > 0 \
                    #and bAP_model_feature_spike[i]['AP2_amp'] > 0:

                else:
                    print("No minimum Model Action Potential at bAP for stepamp " + str(stepampnames) + " on rank " + str(self.rank))
                    lg.info("No minimum Model Action Potential at bAP for stepamp " + str(stepampnames) + " on rank " + str(self.rank))
                    
                    # bAP tests and experimental data was for 1000ms stimuli; target feature for 400ms is 4 ; so setting it to 2 handmade hyperparameter, for 11 see upper explanation
                
        else:
            print("No minimum Model Action Potential at Soma for stepamp " + str(stepampnames) + " on rank " + str(self.rank))
            lg.info("No minimum Model Action Potential at Soma for stepamp " + str(stepampnames) + " on rank " + str(self.rank))


        if bAP_success == len(bAP_model_feature_spike):
            print("Soma and bAP Action Potentials sufficient, sending into full cost evaluation")
            lg.info("Soma and bAP Action Potentials sufficient, sending into full cost evaluation")
            return True
        else:
            pass


        end = time.time()
        #print("time1.5: ", end-start)

    def stimulateIClamp(self):   # Default values are from Schneider et al. 2021
        '''
        IClamp Optimization Protocols
        Stimulate IClamp on self.mycell /w random values from rnddata.

        Parameters
        ----------
        self.delay : int; Stim delay
        self.duration : int; Stim duration
        self.stepamps : List[int]; Step amplitude values, one simulation for each step amplitude

        Returns
        -------
        traces_per_stepamp : Dict: {stepampname: {'Soma': soma_arr , 'bAP': bAP1_arr}}
        '''
        traces_per_stepamp_dict = {}
        for stepampname, stepamp in self.stepamps.items():
            #start = time.time()

            stim = h.IClamp(self.mycell.soma[0](0.5)) # stim at soma
            stim.delay = self.delay
            stim.dur = self.duration
            stim.amp = stepamp
            soma_vec = h.Vector().record(self.mycell.soma[0](0.5)._ref_v) # record at middle (0,5) of soma

            # TODO get section names automatically by distance from bAP recordings in HippoUnit
            # commented function, can be implemented
            """ bAP_secnames = []
            bAP_distances = [50, 150, 245.45454545454544, 263.6363636363636, 336.3636363636364, 354.5454545454545]  # distances from HippoUnit test suite
            for distance in distances:
                for sec in inputcell.apical:
                    for seg in sec: 
                        dist = h.distance(seg.x, sec=sec) 
                        if dist == distance +5:
                            print(sec, seg.x, dist)
                            secname = sec.split(".",1)[1]
                            bAP_secnames.append(secname)
                            print(bAP_secnames)"""


            if self.hippo_bAP == True:
                ## Hippounit bap positions
                bAP1_vec = h.Vector().record(self.mycell.radTprox(0.5)._ref_v)   # 50 um
                bAP2_vec = h.Vector().record(self.mycell.radTmed(0.5)._ref_v)    # 150 um
                bAP3_vec = h.Vector().record(self.mycell.radTdist(0.22727272727272727)._ref_v)  # 245 um
                bAP4_vec = h.Vector().record(self.mycell.radTdist(0.3181818181818182)._ref_v)   # 263 um
                bAP5_vec = h.Vector().record(self.mycell.radTdist(0.6818181818181819)._ref_v)   # 336 um
                bAP6_vec = h.Vector().record(self.mycell.radTdist(0.7727272727272728)._ref_v)   # 354 um
            else:
                bAP1_vec = h.Vector().record(self.mycell.radTmed(1)._ref_v)    # 205um distance from middle of soma, 200 from end of soma, 210 from start of soma with 10um diameter.

            
            # TODO get region names automatically by distance and use setattr(self.mycell, sectionname)._ref_v
            
            time_vec = h.Vector().record(h._ref_t)


            h.dt =  0.075            # 0.025
            h.tstop = self.tstop  # 1600 for hippounit trace comparison
            h.v_init = -65
            h.celsius = 35
            h.init()
            h.run()

            """pyplot.figure(figsize=(8,4)) # Default figsize is (8,6)
            pyplot.title("soma plot")
            pyplot.plot(time_vec, soma_vec)
            pyplot.xlabel('time (ms)')
            pyplot.ylabel('mV')
            pyplot.show()"""

            
            """pyplot.figure(figsize=(8,4)) # Default figsize is (8,6)
            pyplot.title("bap plot")
            pyplot.plot(time_vec, bAP1_vec)
            pyplot.xlabel('time (ms)')
            pyplot.ylabel('mV')
            pyplot.show()"""
            #myplots.plotStandardTrace(soma_vec, time_vec, h.tstop)
            #myplots.plotStandardTrace(bAP1_vec, time_vec, h.tstop)
            # h.finitialize(-65 * mV) # alt: h.run() ; finitialize https://www.neuron.yale.edu/neuron/static/py_doc/simctrl/programmatic.html
            # h.continuerun(600 * ms) # alt: h.tstop = 200
            #end = time.time()

            #print("time1: ", end - start)
            #lg.info("SIMULATION TIME" + str(end - start) + "seconds.")
            soma_arr = np.array(soma_vec)

            # TODO automatic section dictionaries, not hardcoded names and amount of arrays. detect how many traces are recorded with a counter or something and use that.
            # I don't like this programming just for one purpose... it's crap
            if self.hippo_bAP == True:           
                bAP1_arr = np.array(bAP1_vec)
                bAP2_arr = np.array(bAP2_vec)
                bAP3_arr = np.array(bAP3_vec)
                bAP4_arr = np.array(bAP4_vec)
                bAP5_arr = np.array(bAP5_vec)
                bAP6_arr = np.array(bAP6_vec)
                traces_per_stepamp_dict.update({stepampname: {  'Soma': soma_arr , 'bAP1': bAP1_arr, \
                                                                'bAP2': bAP2_arr, 'bAP3': bAP3_arr, \
                                                                'bAP4': bAP4_arr, 'bAP5': bAP5_arr, \
                                                                'bAP6': bAP6_arr }})
            else:
                bAP1_arr = np.array(bAP1_vec)
                traces_per_stepamp_dict.update({stepampname: {'Soma': soma_arr , 'bAP': bAP1_arr}})

        return traces_per_stepamp_dict, time_vec


    def getTargetFeatures(self):
        """Auxiliary function to set self.bAP_features_dict"""
        traces_per_stepamp, time_vec = self.stimulateIClamp()       # stimulate with read-in cell which wasn't change yet for the baseline traces
        self.extractTargetFeatures(traces_per_stepamp, time_vec)    # extract target features from baseline read-in cell which wasn't changed yet


    def createAveragedDistanceBAPList(self, inputlist_of_dicts):
        # TODO make a distance check to average it. Average values then by indices or not
        for i in range(len(inputlist_of_dicts)):            # could have enumerated here to use the enumeration value as iterator in next line instead, same line of codes though, just easier to read
                                                            # or just for ele in inputlist_of_dicts if indices aren't needed for selection of distance regions
                                                            # for featurename, featurevalue in ele.items()
            temp_feature_dict = {}
            for featurename, feature_value in inputlist_of_dicts[i].items():
                if not np.all(feature_value) or feature_value.size == 0:
                    feature_value_mean = 0                 # make all feature values available as something   
                    feature_value_sd = 0
                    temp_feature_dict.update({featurename : { "Mean" : feature_value_mean }})

                # create the averaged distance region values
                else:
                    if i == 0:              # 50um
                        temp_feature_dict.update({featurename : { "Mean" : inputlist_of_dicts[i][featurename]}})
                        #self.model_features['bAP_50um'] = {'Step08' : temp_feature_dict}
                    elif i == 1:            # 150um
                        temp_feature_dict.update({featurename : { "Mean" : inputlist_of_dicts[i][featurename]}})
                        #self.model_features['bAP_150um'] = {'Step08' : temp_feature_dict}
                    elif i == 2:
                        feature_value_mean = (inputlist_of_dicts[i][featurename] + inputlist_of_dicts[i+1][featurename]) / 2          # 250um
                        temp_feature_dict.update({featurename : { "Mean" : feature_value_mean }})
                        #self.model_features['bAP_250um'] = {'Step08' : temp_feature_dict}
                    elif i == 4:            # 350um
                        feature_value_mean = (inputlist_of_dicts[i][featurename] + inputlist_of_dicts[i+1][featurename]) / 2 
                        temp_feature_dict.update({featurename : { "Mean" : feature_value_mean }})
                        #self.model_features['bAP_350um'] = {'Step08' : temp_feature_dict}

            # create the model dictionary
            if i == 0:
                self.model_features['bAP_50um'] = {'Step08' : temp_feature_dict}
            if i == 1:
                self.model_features['bAP_150um'] = {'Step08' : temp_feature_dict}
            if i == 2:
                self.model_features['bAP_250um'] = {'Step08' : temp_feature_dict}
            if i == 4:
                self.model_features['bAP_350um'] = {'Step08' : temp_feature_dict}
            
        ## set penalties for model no attenuation - helps for flexible trunk models to make sure about attenuation
        if self.model_features['bAP_50um']['Step08']['AP1_amp']['Mean'] < self.model_features['bAP_150um']['Step08']['AP1_amp']['Mean']:
            self.model_features['bAP_50um']['Step08']['AP1_amp']['Mean'] = 1000
        elif self.model_features['bAP_150um']['Step08']['AP1_amp']['Mean'] < self.model_features['bAP_250um']['Step08']['AP1_amp']['Mean']:
            self.model_features['bAP_150um']['Step08']['AP1_amp']['Mean'] = 1000
        elif self.model_features['bAP_250um']['Step08']['AP1_amp']['Mean'] < self.model_features['bAP_350um']['Step08']['AP1_amp']['Mean']:
            self.model_features['bAP_250um']['Step08']['AP1_amp']['Mean'] = 1000

        """## add spikecount features for comparison
        for i, ele in enumerate(bAP_model_feature_list):
            for featurename, featurevalue in ele.items():
                if featurename == 'Spikecount':
                    if i == 0:
                        self.model_features['bAP_50um'] = {'Step08' : {featurename: featurevalue}}
                    elif i == 1:
                        self.model_features['bAP_150um'] = {'Step08' : {featurename: featurevalue}}
                    elif i == 2:    # region 3 dismissed
                        self.model_features['bAP_250um'] = {'Step08' : {featurename: featurevalue}}
                    elif i == 4:    # region 5 dismissed
                        self.model_features['bAP_350um'] = {'Step08' : {featurename: featurevalue}}  """

    def extractModelFeatures(self, traces_per_stepamp, time_vec):
        """
        Function to extract Model Features.
        These have to be somatic and bAP features.

        Parameters
        ----------

        Returns
        -------
        feature_values_array_list : List of Numpy Arrays of exactly one value for each feature.
        """  
        efel.api.reset()
        
        # TODO handle bAP differently - maybe split into two functions, one for bAP, one for somatic
        # i can stimulate everything, I just don't have to add the stepampname -0.4 to the dict, removing it at the last point
        #print(traces_per_stepamp)
        traces = []
        traces_dict = {}
        for stepampname, locationtraces in traces_per_stepamp.items():              # -0,4 then 0.8, ... (then 1.0)
            traces_temp_dict = {}
            for location, locationtrace in locationtraces.items():      # Soma, then bAP 
                trace = {} 
                trace['V'] = locationtrace              # Set the 'V' (=voltage) key of the trace
                trace['T'] = time_vec                   # Set the 'T' (=time) key of the trace

                stim_end = self.tstop
                trace['stim_start'] = [self.delay]      # Set the 'stim_start' (time at which a stimulus starts, in ms) key of the trace
                                                        # Warning: this need to be a list (with one element)
                trace['stim_end'] = [stim_end]          # Set the 'stim_end' (time at which a stimulus end) key of the trace
                                                        # Warning: this need to be a list (with one element)

                traces.append(trace)                    # Multiple traces can be passed to the eFEL at the same time, so the argument should be a list
                traces_temp_dict.update({location: [trace]})
            traces_dict.update({stepampname: traces_temp_dict})
        #print(traces_dict)
        #print("TRACES: ", traces)
        
        temp_soma_model_feature_list = []
        temp_bAP_model_feature_list = []

        for stepampnames, stepampvalues in traces_dict.items():
            for locationname, locationtrace in stepampvalues.items():
                if "-" in stepampnames:       
                    if locationname.split("_", 1)[0] == "Soma":
                        temp_soma_model_feature_list = temp_soma_model_feature_list + locationtrace
                    else:
                        pass
                else: 
                    if locationname.split("_", 1)[0] == "Soma":
                        temp_soma_model_feature_list = temp_soma_model_feature_list + locationtrace
                    else:
                        temp_bAP_model_feature_list = temp_bAP_model_feature_list + locationtrace
                    
        # print(temp_soma_model_feature_list)     # has depol and hpol
        # print(temp_bAP_model_feature_list)      # has only depol

        ## ADAPTIONS FOR HYPERPOLARIZING CURRENT - Removing hyperpolarizing current step as key and as first index of the list which enumerates over the keys - so it is consistent
        #for i in range(len())    
        #    temp_bAP_model_feature_list.pop(0)
        stepampnamekeys = list(self.stepamps.keys())           # stepampnames by user input from object property
        bAP_stepampnames = [ x for x in stepampnamekeys if "-" not in x ]       # stepampnames without the hpols

        soma_model_feature_dict = {}
        bAP_model_feature_dict = {}

        ############### SOMA PART        #######################
        efel.api.setThreshold(-20.0)    
        soma_model_feature_list = efel.getFeatureValues(temp_soma_model_feature_list, self.somatic_features, raise_warnings = False)    #  extract all soma features on the model, list of dictionary feature values
        #print(soma_model_feature_list)
        for i in range(len(soma_model_feature_list)):
            soma_model_feature_dict[stepampnamekeys[i]] = soma_model_feature_list[i]
        #print(soma_model_feature_dict)
        #print(soma_model_feature_dict["Step-04"]["APlast_amp"])
        #print(soma_model_feature_dict["Step08"]["APlast_amp"])
        soma_model_feature_dict_temp = {}
        for stepkeys, stepvalues in soma_model_feature_dict.items():
            temp_dict = {}
            for feature_name, feature_value in stepvalues.items():
                if not np.all(feature_value):
                    feature_value_mean = 0                 # make all feature values available as something   
                    feature_value_sd = 0                        
                elif feature_value.size == 0:          
                    feature_value_mean = 0  
                    feature_value_sd = 0
                elif feature_value.size >= 1:
                    if (feature_name == 'AP_rise_time' or feature_name == 'AP_amplitude' or feature_name == 'AP_duration_half_width' or feature_name == 'AP_begin_voltage'  \
                        or feature_name == 'AP_rise_rate' or feature_name == 'fast_AHP' or feature_name == 'AP_begin_time' or feature_name == 'AP_begin_width' or feature_name == 'AP_duration' \
                        or feature_name == 'AP_duration_change' or feature_name == 'AP_duration_half_width_change' or feature_name == 'fast_AHP_change' or feature_name == 'AP_rise_rate_change' or feature_name == 'AP_width'):
                        """
                        In case of features that are AP_begin_time/AP_begin_index, the 1st element of the resulting vector, which corresponds to AP1, is ignored
                        This is because the AP_begin_time/AP_begin_index feature often detects the start of the stimuli instead of the actual beginning of AP1
                        """
                        feature_value_mean = np.mean(feature_value[1:])
                        feature_value_sd = np.std(feature_value[1:])
                    else:
                        feature_value_mean = np.mean(feature_value)
                        feature_value_sd = np.std(feature_value)

                temp_dict.update({feature_name : {'Std' : feature_value_sd, 'Mean' : feature_value_mean}})
            soma_model_feature_dict_temp.update({stepkeys: temp_dict})  

        self.model_features = {}
        self.model_features['Soma'] = soma_model_feature_dict_temp

        ############### BAP PART        #######################
        efel.api.setThreshold(-53.5)
        efel.setDoubleSetting('interp_step', 0.025)
        efel.setDoubleSetting('DerivativeThreshold', 40.0)
        #for i in range(len(temp_bAP_model_feature_list)):
        bAP_model_feature_list = efel.getFeatureValues(temp_bAP_model_feature_list, self.bAP_features, raise_warnings = False)          #  extract all bAP features on the model 

        if self.hippo_bAP == True:         
            #print(bAP_model_feature_list)
            self.createAveragedDistanceBAPList(bAP_model_feature_list)
            print("\n")
            print("MODEL FEATURES")
            print(self.model_features)
            print("\n")
        else:
            for count, value in enumerate(bAP_model_feature_list):      # if hippo_bAP is set to false, it only has 1 stepamp and 1 bAP recording so this loop is just askdwbjwdwqjbfjk
                bAP_model_feature_dict[bAP_stepampnames[count]] = value

            # print(soma_model_feature_dict)
            # print(bAP_model_feature_dict)

            # brain too tired now to reduce this now on one function or rewrite it 
            # and do the calculations on the initial feature list of dicts from efel
            # gotta live with it
            ## Important Note: SD is unnecessary for model_features and it doesn't matter which values sd is getting, because it is never accessed by calculateFitness().

        
            bAP_model_feature_dict_temp = {}
            for stepkeys, stepvalues in bAP_model_feature_dict.items():
                temp_dict = {}
                for feature_name, feature_value in stepvalues.items():
                    if not np.all(feature_value):
                        feature_value_mean = 0                 # make all feature values available as something   
                        feature_value_sd = 0    
                    elif feature_value.size == 0:                
                        feature_value_mean = 0                 # make all feature values available as something   
                        feature_value_sd = 0  
                    elif feature_value.size >= 1:
                        if (feature_name == 'AP_rise_time' or feature_name == 'AP_amplitude' or feature_name == 'AP_duration_half_width' or feature_name == 'AP_begin_voltage'  \
                            or feature_name == 'AP_rise_rate' or feature_name == 'fast_AHP' or feature_name == 'AP_begin_time' or feature_name == 'AP_begin_width' or feature_name == 'AP_duration' \
                            or feature_name == 'AP_duration_change' or feature_name == 'AP_duration_half_width_change' or feature_name == 'fast_AHP_change' or feature_name == 'AP_rise_rate_change' or feature_name == 'AP_width'):
                            """
                            In case of features that are AP_begin_time/AP_begin_index, the 1st element of the resulting vector, which corresponds to AP1, is ignored
                            This is because the AP_begin_time/AP_begin_index feature often detects the start of the stimuli instead of the actual beginning of AP1
                            """
                            feature_value_mean = np.mean(feature_value[1:])
                            feature_value_sd = np.std(feature_value[1:])
                        else:
                            feature_value_mean = np.mean(feature_value)
                            feature_value_sd = np.std(feature_value)

                    temp_dict.update({feature_name : {'Std' : feature_value_sd, 'Mean' : feature_value_mean}})
                bAP_model_feature_dict_temp.update({stepkeys: temp_dict})

            
            self.model_features['bAP'] = bAP_model_feature_dict_temp
            #print(self.model_features)
 
    def updateParAndModel(self, parameter_data, indices):
        if self.method == "CG":
            parameter_data = abs(parameter_data)    # especially for CG, don't make negative values possible for conductances. Negative "bar" values produce a NEURON error. 
                                                    # If you want to add e_pas to the parameters, you have to specify this line

        ## TODO , could intialize the first self.model_features after instantiating the cell, to check for spikes and then throw it overboard before even calculating the fitness

        self.updateAutoParameters(parameter_data, indices)                          # update "self.mycell" Cell with random values

        if self.AP_firstspike and self.bAP_firstspike:
            traces_per_stepamp, time_vec = self.stimulateIClamp()
            self.extractModelFeatures(traces_per_stepamp, time_vec)
            return True 
        else:
            if self.stimulateIClamp_firstspike():                           # if firstspike features
                self.AP_firstspike = True
                self.bAP_firstspike = True
                traces_per_stepamp, time_vec = self.stimulateIClamp()       # starting full-fledged stimulation
                self.extractModelFeatures(traces_per_stepamp, time_vec)     # extracting all features
                return True
            else:
                return

    def calculateFitness(self, parameter_data, indices):  
        # print("test: ", parameter_data)
        if self.updateParAndModel(parameter_data, indices) is None:
            print("No spiking, aborting on rank, " + str(self.rank))  
            lg.info("No spiking, aborting on rank, " + str(self.rank))
            return 10000
        else:
            pass

        ## To iterate over all values, create one big dic out of both dictionaries ### unused hahah :D
        self.features = {}
        self.features['Target'] = self.target_features
        self.features['Model'] = self.model_features


        fitness_values_names = []
        fitness_values = []
        fitness_values_dict = {}

        ## Based on model_feature_dict 
        """for locationkey, locationvalues in self.model_features.items():         # using model_features in case you want to change the step amp protocol in self.stepamps
            #if locationkey == 'Soma':                                          # test only somatic features
            for stepamp, stepampvalues in locationvalues.items():
                for feature_name, featurevalues in stepampvalues.items():
                    if featurevalues['Mean'] is None:
                        continue
                    elif featurevalues['Mean'] is not None:
                        # numpy.core._exceptions.UFuncTypeError: ufunc 'subtract' did not contain a loop with signature matching types (dtype('<U32'), dtype('<U32')) -> dtype('<U32')                                                       
                        feature_fitness = (np.abs(float(featurevalues['Mean'] - float(self.target_features[locationkey][stepamp][feature_name]['Mean']))) \
                                            /float(self.target_features[locationkey][stepamp][feature_name]['Std']))
                        # TODO prove that this change for model_features instead of target_features works                
                        print(feature_name, " : ", featurevalues['Mean'], " blabla", self.target_features[locationkey][stepamp][feature_name]['Mean'] ," \
                            standard deviation: ", self.target_features[locationkey][stepamp][feature_name]['Std'])

                        fitness_values_names.append(feature_name + " fitness value: ")
                        fitness_values.append(feature_fitness)
                        df = pd.DataFrame(fitness_values, index = fitness_values_names)
                        fitness_values_dict.update({feature_name : feature_fitness})"""

        ## Based on target_feature_dict 
        for locationkey, locationvalues in self.target_features.items():         # using model_features in case you want to change the step amp protocol in self.stepamps
            #if locationkey == 'Soma':                                          # test only somatic features
            for stepamp, stepampvalues in locationvalues.items():
                for feature_name, featurevalues in stepampvalues.items():
                    if stepamp in self.stepamps.keys():
                        if self.model_features[locationkey][stepamp][feature_name]['Mean'] is None or self.model_features[locationkey][stepamp][feature_name]['Mean'] is False:
                            fitness_values_names.append(feature_name + " fitness ")
                            feature_fitness = 1000
                            fitness_values.append(feature_fitness)

                        elif featurevalues['Mean'] and self.model_features[locationkey][stepamp][feature_name]['Mean']:
                            # numpy.core._exceptions.UFuncTypeError: ufunc 'subtract' did not contain a loop with signature matching types (dtype('<U32'), dtype('<U32')) -> dtype('<U32')   
                            #print("1", self.model_features[locationkey][stepamp][feature_name]['Mean'], bool(self.model_features[locationkey][stepamp][feature_name]['Mean']))
                            #print("2", float(featurevalues['Mean']), bool(float(featurevalues['Mean'])))                                                    
                            feature_fitness = (np.abs(float(self.model_features[locationkey][stepamp][feature_name]['Mean']) - float(featurevalues['Mean'])) \
                                                /float(featurevalues['Std']))
                            # TODO prove that this change for model_features instead of target_features works                
                            #print(feature_name, " : ", self.model_features[locationkey][stepamp][feature_name]['Mean'] , " blabla", featurevalues['Mean'] ," \
                            #    standard deviation: ", self.target_features[locationkey][stepamp][feature_name]['Std'])

                            fitness_values_names.append(feature_name)    # add label suffix like feature_name + " fitness" or + " cost" if wanted
                            fitness_values.append(feature_fitness)

                        fitness_values_dict.update({feature_name : feature_fitness})
                    else:
                        #print(stepamp, " was not in Model Features and got skipped")
                        pass
        


        ## Outputs for testing
        # print("Fitness values are:")
        pd.set_option("display.max_rows", None, "display.max_columns", None)
        df = pd.DataFrame(fitness_values, index = fitness_values_names)

        # inline
        print(df)           

        # csv
        # df.to_csv("./paropt/data/parameter_values//dataframe_costs/dataframe_output_model_" + str(self.line) + ".csv")

        # print("Fitness values are: ", fitness_values_dict, "on rank " + str(self.rank))
        print("Cost is: ", max(fitness_values), " on rank " + str(self.rank))
        lg.info("Cost is " + str(max(fitness_values)) + "on rank " + str(self.rank))

        # maximum fitness value
        print(df.idxmax())      # max(fitness_values) feature_name

        return max(fitness_values)

    def callScipyNelderMead(self, x0, indices): 
        # Scipy for Nelder-Mead
        minimum = scp.minimize( self.calculateFitness, x0, 
                                    args=(indices), 
                                    bounds=[(0, 1) for i in range(len(x0))],
                                    method = self.method, 
                                    options={'xatol': 1e-6, 'maxiter': 1500, 'disp': True})     # xatol, fatol
        if minimum.fun <= self.init_cost_threshold:      # only save the data of the successful parameter combinations 
            return minimum.x, minimum.fun    # key = population index, value = tempdict; update result dictionary with one cell iteration dictionary per key
        return None, None

    def callScipyLBFGSB(self, x0, indices, bounds):
        # stopper = callBackScipyTimeStopper() # timestopper
        # Scipy for L-BFGS-B
        minimum = scp.minimize( self.calculateFitness, x0, 
                                    args=(indices), 
                                    bounds=[(0, 1) for i in range(len(x0))] ,   # bounds
                                    method = self.method, 
                                    options={'gtol': 1e-06, 'disp': True, 'maxiter': 300, 'eps': 1e-07})
                                    # callback = stopper.__call__(1))    # not longer than 1 minute for one cell

        if minimum.fun <= self.init_cost_threshold:         # only save the data of the successful parameter combinations
            return minimum.x, minimum.fun
        return None, None

    def callScipyCG(self, x0, indices):
        # Scipy for CG
        minimum = scp.minimize( self.calculateFitness, x0, 
                                args=(indices),
                                method = self.method, 
                                options={'disp': True, 'maxiter': 300, 'eps': 1e-4})

        if minimum.fun <= self.init_cost_threshold:          # only save the data of the successful parameter combinations
            return minimum.x, minimum.fun
        return None, None
    
    ###### Run ######
    def runOptimizer(self, init_data, indices):
        """ Calling the optimizer and using its output """
        init_data2 = copy(init_data)        # init_data2 to test calculateFitness with initial data against no update with updateAutoParameters
        
        #print("INIT DATA:", init_data)  # tested, approved, no nans

        ## Initiate Random Data
        init_rnd_data = randomizeAutoConductances(init_data)  # randomizing conductance parameters of ion channels 'gbar_*' from the cell
        #print("INIT RND DATA: ", init_rnd_data)
        rnd_data = insertNans(init_rnd_data, indices)         # for output
        #print("INIT RND DATA: ", rnd_data)
        #print(type(rnd_data))     # <class 'numpy.ndarray'>

        ## test single outputs
        if self.testing is True:
            testdata = testingfinaldata.testdata
            #testdata = testSingleOutputs(PP_str + "../data/parameter_values/best10_par.csv")
            init_cost = self.calculateFitness(testdata, indices)    # indices stay the same for one model and could be an object property but not now xD
            print("\n")
            print("INITIAL COST FOR TESTING DATA DUE TO TESTING FLAG == TRUE:")
            print(init_cost)
            print("\n")
        else:
            init_cost = self.calculateFitness(init_rnd_data, indices)     # 100 is target feature atm


    
        ## extract some initial values with parameter combination
        """par_comb_df = pd.read_csv(PP_str + "/data.csv", dtype=np.float64)
        print(par_comb_df)
        par_comb = par_comb_df.to_numpy()
        par_comb = removeNans(par_comb[10])  
        print(par_comb) 
        init_cost = self.calculateFitness(par_comb, indices)     # use own data"""

        if init_cost == 10000:
            return 1                                # int

        elif init_cost <= self.init_cost_threshold:                    
            return rnd_data, init_cost              # tuple

        elif init_cost > self.init_cost_threshold and init_cost <= self.init_cost_optimizer_threshold:
            
            optimiz = OptimizerC(x0 = init_rnd_data, indices = indices, method = self.method)

            if self.method == 'L-BFGS-B':
                bounds = calculateBounds(init_rnd_data)
                x, fun = self.callScipyLBFGSB(init_rnd_data, indices, bounds)     # only take the ones with output which fulfill the fitness function 
                if np.any(x) is not None and fun is not None:
                    x = insertNans(x, indices)    
                    return [x, rnd_data, fun]             # list
                else:
                    return 2

            elif self.method == 'CG':
                x, fun = self.callScipyCG(init_rnd_data, indices)                 # only take the ones with output which fulfill the fitness function
                if np.any(x) is not None and fun is not None:
                    x = insertNans(x, indices)    
                    return [x, rnd_data, fun]             # list
                else:
                    return 2

            elif self.method == 'Nelder-Mead':                                    # https://docs.scipy.org/doc/scipy/reference/optimize.minimize-neldermead.html
                x, fun = self.callScipyNelderMead(init_rnd_data, indices)         # only take the ones with output which fulfill the fitness function
                if np.any(x) is not None and fun is not None:
                    x = insertNans(x, indices)       # too many values to unpack, expected 2  
                    return [x, rnd_data, fun]             # list
                else:
                    return 2                                # int

        elif init_cost > self.init_cost_optimizer_threshold and init_cost != 10000:
            return 3                                        # int

    def run(self, cell_destination_size, testing = None):
        """ Creating cells, running the sim and creating output files"""

        if testing:
            self.testing = True
        else:
            self.testing = False

        ## Creating output files as variables to append outputs/results
        # Standard output of regular optimized results
        for i in range(9999):
            if os.path.exists(SAVEPATH_PAR + "/output_data_sim_" + str(i) + ".csv") or \
                os.path.exists(SAVEPATH_PAR + "/output_fun_data_sim_" + str(i) + ".csv") or \
                os.path.exists(SAVEPATH_PAR + "/sample_output_par_data_sim_" + str(i) + ".csv") or \
                os.path.exists(SAVEPATH_PAR + "/sample_fun_data_sim_" + str(i) + ".csv") or \
                os.path.exists(SAVEPATH_PAR + "/sample_best_output_par_data_sim_" + str(i) + ".csv") or \
                os.path.exists(SAVEPATH_PAR + "/sample_best_fun_data_sim_" + str(i) + ".csv"):
                continue
            else:
                self.output_csv_data = (SAVEPATH_PAR + "/output_data_sim_" + str(i) + ".csv")
                self.output_csv_fun_data = (SAVEPATH_PAR + "/output_fun_data_sim_" + str(i) + ".csv")
                 # Results after sampling
                self.sample_output_csv_par_data = (SAVEPATH_PAR + "/sample_output_par_data_sim_" + str(i) + ".csv")
                self.sample_output_csv_fun_data = (SAVEPATH_PAR + "/sample_fun_data_sim_" + str(i) + ".csv")
                # Best sampling results
                self.sample_best_output_csv_par_data = (SAVEPATH_PAR + "/sample_best_output_par_data_sim_" + str(i) + ".csv")
                self.sample_best_output_csv_fun_data = (SAVEPATH_PAR + "/sample_best_fun_data_sim_" + str(i) + ".csv")
                break
            
        start = time.time()   
        counter = 0
        successcounter = 0 
        out_fun_list = []  
        init_rnd_par_list = []
        out_par_list = []    
        i = 0

        while i <= cell_destination_size:
            counter = counter + 1

            self.AP_firstspike = False
            self.bAP_firstspike = False  

            print("Cell number " + str(counter) + " on rank number " + str(self.rank))

            lg.info("\n")
            lg.info("Cell number " + str(counter) + " on rank number " + str(self.rank) + " is starting.")

            if counter == 1:           
                print("First created Cell is used.")
                lg.info("First created Cell is used.")

                init_data, indices = self.getMechanismItems()  # Initial Conductances # tested
                init_output_data = insertNans(init_data, indices).tolist()

                outfile = pathlib.Path(SAVEPATH_PAR + '/INITIAL_CONDUCTANCES_LIST.json')
                if outfile.is_file():
                    print("Initial Conductances already in a JSON file.")        
                    pass
                else:
                    X = convert1DTo2DnpArr(init_output_data)
                    df = pd.DataFrame(X, index = self.sectionlist_list, columns = self.ionchnames).transpose()
                    print("Creating Initial Conductances - JSON file")
                    print(df)         
                    writeJSON(SAVEPATH_PAR, 'INITIAL_CONDUCTANCES_LIST.json', init_output_data)   

            elif counter > 1 :
                self.deleteCell()      # garbage collector deletion for ram
                print("Recreating Cell " + str(counter) + ", reinitializing.")
                lg.info("Recreating Cell " + str(counter) + ", reinitializing.")

                self.initializeCell()
                init_data, indices = self.getMechanismItems()  # Initial Conductances for new cell
                # print(init_data)

                        
            ############Run#################################
            output = self.runOptimizer(init_data, indices) #
            ############Run#################################

            if isinstance(output, int) and output == 1:
                print("Abort Error 1: Model didn't spike at enough frequency at start i.e. no Action Potentials at the start. No save.")
                lg.error("Abort Error 1: Model didn't spike at enough frequency at start i.e. no Action Potentials at the start. No save.")             
                #continue

            elif isinstance(output, int) and output == 2:
                print("Abort Error 2: Model wasn't able to be optimized below the treshold. No save.")
                lg.error("Abort Error 2: Model wasn't able to be optimized below the treshold. No save.")              
                #continue             
                
            elif isinstance(output, int) and output == 3:
                print("Abort Error 3: Models spike frequency was sufficient but Initial costs were too high to send into the Optimizer")
                lg.error("Abort Error 3: Models spike frequency was sufficient but Initial costs were too high to send into the Optimizer")
                #continue

            else:           # with results

                if isinstance(output, list):  
                    print("Successful parameter combination got optimized!")
                    lg.info("Successful parameter combination got optimized!")
                    output_array = output[0]                     # array of valid output combination
                    input_random_array = output[1]               # array of its initial random combination
                    out_fun = output[2]

                    out_fun_list.append(output[2])
                    out_par_list.append(output_array.tolist())
                    init_rnd_par_list.append(input_random_array.tolist())            

                    # input_random_array = insertNans(input_random_array)
                    # output_array = insertNans(output_array) 
                    # out_par_df = pd.DataFrame(convert1DTo2DnpArr(output_array), index = self.sectionlist_list, columns = self.ionchnames).transpose()
                    # init_rnd_par_df = pd.DataFrame(convert1DTo2DnpArr(input_random_array), index = self.sectionlist_list, columns = self.ionchnames).transpose()                       

                elif isinstance(output, tuple):                 # np.ndarray
                    print("Random parameters already sufficient. Next cell.")
                    lg.info("Random parameters already sufficient. Next cell.")
                    output_array = output[0]  
                    out_fun = output[1]

                    out_fun_list.append(output[1])
                    out_par_list.append(output_array.tolist())
                    init_rnd_par_list.append(output_array.tolist())  # init = out , so saving double   


                with open(self.output_csv_fun_data, "a") as f:
                    print(out_fun, end='\n', file=f)                # *out_fun

                output_list = output_array.tolist()
                with open(self.output_csv_data, "a") as f:
                    print(*output_list, sep=',', end='\n', file=f)

                # Sample recursively around, terminate recursion if maxiter or maxresults is exceeded
                # check sampleRecAround documentation
                self.sampleRecAround(output_array, out_fun, indices)

                #############################################################################
                #############################################################################
                ## The following hopefully circumvents NEURON scopmath library error and is an alternative for "sampleRecAround()" above
                ## it didn't , see important_scopmath_error.txx
                """
                fun_list = []
                sample_array_list = []
                counterfor = 0
                print("Starting sampling process of 1000 iterations")
                lg.info("Starting sampling process of 1000 iterations")
                for i in range(1000):    # sample 1000 times around and check if costs become better          
                    try: 
                        if fun_list: # and min(fun_list) < out_fun:
                            j = fun_list.index(min(fun_list))
                            arr = sample_array_list[j]
                            sample_array = sampleResultsAround(arr, multiplier = 2)        
                            sample_array_nonan = removeNans(sample_array)
                            sample_fun = self.calculateFitness(sample_array_nonan, indices)   
                            
                            if sample_fun < min(fun_list):
                                counterfor = counterfor + 1
                                print("Sample is better than best sampled combination, saving new sample")
                                lg.info("Sample is better than best sampled combination, saving new sample")
                                fun_list.append(sample_fun)
                                
                                with open(self.sample_output_csv_fun_data, "a") as f:
                                    print(sample_fun, end='\n', file=f)

                                sample_array_list.append(sample_array)
                                sample_output_list = sample_array.tolist()                   
                                with open(self.sample_output_csv_par_data, "a") as f:
                                    print(*sample_output_list, sep=',', end='\n', file=f)

                                print("Trying to find more samples based on the successful sample on iteration " + str(i) + " with " + str(counterfor) + " results already")
                                lg.info("Trying to find more samples based on the successful sample on iteration " + str(i) + " with " + str(counterfor) + " results already")                              
                            else:
                                print("Sample is not better, sampling again with input values on iteration " + str(i) + " with " + str(counterfor) + " results already")
                                lg.info("Sample is not better, sampling again with input values on iteration " + str(i) + " with " + str(counterfor) + " results already")
                                continue                            
                        else:
                            sample_array = sampleResultsAround(output_array, multiplier = 2)
                            sample_array_nonan = removeNans(sample_array)
                            sample_fun = self.calculateFitness(sample_array_nonan, indices)

                            if sample_fun < out_fun:
                                counterfor = counterfor + 1
                                print("Sample is better than original output combination, saving sample")
                                lg.info("Sample is better than original output combination, saving sample")
                                fun_list.append(sample_fun)
                                
                                with open(self.sample_output_csv_fun_data, "a") as f:
                                    print(sample_fun, end='\n', file=f)                 # *sample_fun

                                sample_array_list.append(sample_array)
                                sample_output_list = sample_array.tolist()                   
                                with open(self.sample_output_csv_par_data, "a") as f:
                                    print(*sample_output_list, sep=',', end='\n', file=f)      
                                print("Trying to find more samples based on the successful sample on iteration " + str(i) + " with " + str(counterfor) + " results already")
                                lg.info("Trying to find more samples based on the successful sample on iteration " + str(i) + " with " + str(counterfor) + " results already")            
                            else:
                                print("Sample is not better, sampling again with input values on iteration " + str(i) + " with " + str(counterfor) + " results already")
                                lg.info("Sample is not better, sampling again with input values on iteration " + str(i) + " with " + str(counterfor) + " results already")
                                continue 
                    except Exception as e:
                        # Hoc Errors... scopmath .... I DON'T KNOW WHY
                        print("Exception caught: ", e ," reinitializing with inital values")
                        lg.info("Exception caught, reinitializing with initial values")
                        self.deleteCell()
                        self.initializeCell()
                        continue

                print("Sampling process (as for loop, not as recursion) completed.")
                lg.info("Sampling process (as for loop, not as recursion) completed.")
                """
                ################################################################################
            if os.path.exists(self.output_csv_data):
                i = sum(1 for line in open(self.output_csv_data))
                print(str(i) + " results read in output file.")
                lg.info(str(i) + " results read in output file.")
  
        final_funcost_list = comm.gather(out_fun_list, root = 0)
        final_output_list = comm.gather(out_par_list, root = 0)
        final_rnd_out_list = comm.gather(init_rnd_par_list, root = 0)
        counters = comm.gather(counter, root = 0)
        end = time.time()

        if rank == 0:
            final_fun_list = []
            final_out_list = []
            final_rnd_list = []
            for i in range(cpucount):
                final_fun_list = final_out_list + final_funcost_list[i]
                final_out_list = final_out_list + final_output_list[i]
                final_rnd_list = final_rnd_list + final_rnd_out_list[i]

            print("ELAPSED TIME: ", end - start, " seconds")
            print("COUNTER WHETHER ALL CELLS WERE TRIED IN EACH RANK: ", counters)

            lg.info("\n")
            lg.info("ELAPSED TIME: ")      # Logging Time
            lg.info(end - start)
            lg.info("seconds")
            lg.info("\n")
            lg.info("COUNTER - How many cells did one rank do?: ")
            lg.info(counters)
            lg.info("COUNTER - How many cells in total?: ")
            lg.info(sum(counters))
            lg.info("\n")

            # writeJSON(SAVEPATH_OUT_PAR, 'OUTPUT_OUT_PAR_LIST_NESTED.json', final_output_list)
            # writeJSON(SAVEPATH_OUT_PAR, 'OUTPUT_RND_PAR_LIST_NESTED.json', final_rnd_out_list)
            writeJSON(SAVEPATH_PAR, 'OUTPUT_OUT_PAR_LIST.json', final_out_list)
            writeJSON(SAVEPATH_PAR, 'OUTPUT_RND_PAR_LIST.json', final_rnd_list)
            writeJSON(SAVEPATH_PAR, 'OUTPUT_COSTS_LIST.json', final_fun_list)
            

def main():
    pass
    
## TODO which feature_name causes which models maximum cost? In output - needed or just tedious? Integrated in runtime - done.

if __name__ == '__main__':
    subprocess.call(['sh', str(PP / '..' / '..' / 'start.sh')])       ## make sure to call it in bash from neuzy folder



###### Trivia #######

    ## Tested with completely different model, auto generated from cellbuilder in T2N. Worked. (before bAP adaptions and specifications on To21_M)
    """
    To rework, some code has to be changed/commented again, like the ion channel density distribution in conductance downgrade per distance from soma in updateAutoParameters().
    Also make sure to add the correct list of sectionlists which fits to the new model.
    Don't forget to add the mod files according to the new model into the mods folder, or create a new modpath, modpath2 just for this model, where the mods are stored.
    """
    # paroptmodel = CompleteOptModel("HUARTIF.hoc", template_name = None)   # HUARTIF.hoc is model_name


    def extractTargetFeatures(self, traces_per_stepamp, time_vec):
        """
        Function to extract bAP(!) features from initial model.
        Somatic features are coming from experimental data and are handled in a different way.
        Creates self.bAP_features_dict : Dict with feature names and feature values per step ampere

        Parameters
        ----------
        self
        traces_per_stepamp : Trace vector from stimulateIClamp() in the form of {stepamp: [soma, bAP]}, where soma and bAP are numpy arrays themselves.
        time_vec : Stimulation time h.Vector().
        """        
        traces = []

        # remove all hyperpolarizing keys because for my chosen bAP features doesn't matter hyperpolarizing currents, 
        # could just leave it though
        traces_per_stepamp = {k:v for k,v in traces_per_stepamp.items() if '-' not in k}    

        #traces_per_stepamp = [ x for x in traces_per_stepamps if "-" not in x ]
        for locationtraces in traces_per_stepamp.values():
            #for locationtrace in locationtraces:
                #if locationtrace == bAP1_vec:
            trace = {} 
            trace['V'] = locationtraces['bAP']          # Set the 'V' (=voltage) key of the trace // "1" refers to bAP1_vec index
            #myplots.plotStandardTrace(locationtraces[1], time_vec, 600)
            trace['T'] = time_vec                       # Set the 'T' (=time) key of the trace

            stim_end = self.tstop
            trace['stim_start'] = [self.delay]          # Set the 'stim_start' (time at which a stimulus starts, in ms) key of the trace
                                                        # Warning: this need to be a list (with one element)
            trace['stim_end'] = [stim_end]              # Set the 'stim_end' (time at which a stimulus end) key of the trace
                                                        # Warning: this need to be a list (with one element)
            traces.append(trace)                        # Multiple traces can be passed to the eFEL at the same time, so the argument should be a list
        #print(traces)

        efel.api.setThreshold(-52.0)        # treshold for good bAP features
        target_feature_list = efel.getFeatureValues(traces, self.bAP_features, raise_warnings = False)      # only extract bAP_features
        #print("Target Feature List: ", target_feature_list)

        target_feature_dict = {}
        stepampnames = list(self.stepamps.keys())
        stepampnames = [ x for x in stepampnames if "-" not in x ]          # remove all hyperpolarizing keys because bAP doesn't matter hyperpolarizing currents

        for i, stepampresults in enumerate(target_feature_list):  
            target_feature_dict[stepampnames[i]] = stepampresults
        #print("Target feature dict: ", target_feature_dict)


        # TODO: make standard deviation sd for specific bAP features
        self.bAP_features_dict = {}
        for stepkeys, stepvalues in target_feature_dict.items():
            temp_dict = {}
            for feature_name, feature_value in stepvalues.items():
                if not np.all(feature_value):
                    feature_value_mean = 0      # make all feature values available as something   
                    feature_value_sd = 0 
                else:
                    if (feature_name == 'AP_rise_time' or feature_name == 'AP_amplitude' or feature_name == 'AP_duration_half_width' or feature_name == 'AP_begin_voltage'  \
                        or feature_name == 'AP_rise_rate' or feature_name == 'fast_AHP' or feature_name == 'AP_begin_time' or feature_name == 'AP_begin_width' or feature_name == 'AP_duration' \
                        or feature_name == 'AP_duration_change' or feature_name == 'AP_duration_half_width_change' or feature_name == 'fast_AHP_change' or feature_name == 'AP_rise_rate_change' or feature_name == 'AP_width'):
                        """
                        In case of features that are AP_begin_time/AP_begin_index, the 1st element of the resulting vector, which corresponds to AP1, is ignored
                        This is because the AP_begin_time/AP_begin_index feature often detects the start of the stimuli instead of the actual beginning of AP1
                        """
                        feature_value_mean = np.mean(feature_value[1:])                
            
                        if feature_name == 'AP_duration' or feature_name == 'AP_duration_half_width':
                            feature_value_sd = feature_value_mean/10
                        elif feature_name == 'AP_rise_time':
                            feature_value_sd = feature_value_mean/5
                        elif feature_name == 'AP_rise_rate':
                            feature_value_sd = feature_value_mean/4
                        elif feature_name == 'AP_width':
                            feature_value_sd = feature_value_mean/7
                        #elif feature_name == "AP1_amp":
                        #    feature_value_mean = 45
                        #    feature_value_sd = 7
                        else:
                            feature_value_sd = feature_value_mean/10

                    else:
                        feature_value_mean = np.mean(feature_value)

                        if feature_name == 'APlast_amp':
                            feature_value_sd = feature_value_mean/5
                        if feature_name == 'Spikecount':
                            feature_value_sd = feature_value_mean/2
                        elif feature_name == 'time_to_first_spike':
                            feature_value_sd = feature_value_mean * 0.9
                        elif feature_name == 'time_to_second_spike':
                            feature_value_sd = feature_value_mean * 2/3
                        elif feature_name == 'time_to_last_spike':
                            feature_value_sd = feature_value_mean/3   
                        else:
                            feature_value_sd = feature_value_mean/10
                            #feature_value_sd = np.std(feature_value[1:])

                ## Standard deviations derived from somatic target feature experimental data. The assumption is that bAP recordings would share the same range of variation.                 
                
                #elif feature_value.size > 1:
                #    feature_value_mean = np.mean(feature_value)
                #    feature_value_sd = np.std(feature_value)
                    ## calculate standard deviations            standard deviations are set according to somatic experimental data

  
                temp_dict.update({feature_name : {'Std' : feature_value_sd, 'Mean' : feature_value_mean}})
            self.bAP_features_dict.update({stepkeys: temp_dict})

        writeJSON(SAVEPATH_FEATURE_TARGET, "Extracted_bAP_Target_Features.json", self.bAP_features_dict)

## Timestopper Class to terminate optimizer after specified time (didn't work (yet))
class TookTooLong(Warning):
    pass

class callBackScipyTimeStopper(object):
    def __init__(self, max_sec=60):
        self.max_sec = max_sec
        self.start = time.time()
    def __call__(self, xk):
        elapsed = time.time() - self.start
        if elapsed > self.max_sec:
            warnings.warn("Terminating optimization: time limit reached", TookTooLong)
        else:
            print("Elapsed time for current Optimization: ", elapsed)

    #  TODO experimental callback function to iteratively adapt eps after iterations where fitness_values are really bad
    #if feature_values == inf:
    #    eps = eps * 3
    #return eps


