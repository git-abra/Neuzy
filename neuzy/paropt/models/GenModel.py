"""
Neuzy - Population-based Neuron Modelling, Copyright (C) 2022 Adrian Röth

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
For details see the GNU General Public License and LICENSE.md in the root of the repository.
This is free software, and you are welcome to redistribute it
under certain conditions.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

## Classes for Models, especially GenModel, the parent of all models. 
# Child HOCModel is outsourced in HocModels.py

import sys, pathlib
from neuron import h
import efel
import numpy as np
PARENTPATH = pathlib.Path(__file__).parent   #PARENTPATH Parentpath from current file
sys.path.insert(1, str(PARENTPATH / '..'))

import neuzy.paropt.auxiliaries.constants as cs
import neuzy.paropt.auxiliaries.functions as fnc

class GenModel():           # General Model
    """ 
    Model class for general properties
    This class should take any method, which can be used by the 
    child classes respectively.
    Makes use of eFEL to extract features of the models. # TODO outsource efel extraction into an own class to also offer the option to use another feature extraction library


    Methods
    -------
    - loadNeuronScope
    - deleteCell
    - blockIonChannel
    - createFeatureDict
    - extractModelFeatures
    - getTargetFeatures
    - createAveragedDistanceBAPList
    - createBAPTargets

    """
    def __init__(   self,
                    modpath = None,             # in constants.py if not given
                    target_feature_file = None,
                    bap_target_file = None, 
                    hippo_bAP = True,  
                    channelblocknames = None, # has to be in the fullname format: "gkabar_kad" or "gbar_nax"
                    verbose = False 
                    ):
        if modpath:
            self.modpath = modpath
        else:
            self.modpath = cs.MODPATH          # use constant

        if channelblocknames:    # TODO print detected ionchnames in terminal, select which one by readline of the index by the user, then send the string to blockIonChannel()
            self.channelblocknames = channelblocknames
        else:
            self.channelblocknames = None

        self.target_feature_file = target_feature_file
        self.bap_target_file = bap_target_file

        self.createFeatureDict()

        self.hippo_bAP = hippo_bAP
        if self.hippo_bAP == True:   # Check for hippo_bAP Flag. If True then only a few bAP Features are used, analogue to HippoUnits extraction. This is due to a shortage in experimental data till today.
            self.createBAPTargets()
            #self.createAveragedDistanceBAPList(inputlist_of_dicts)
        else:   ## atm unused, hippo_bAP defaults to True
            self.hippo_bAP = False
            self.bAP_features_dict = None  
            self.bAP_dpol_features  = ['AP1_amp', 'AP2_amp', 'APlast_amp', 'AP_amplitude', 'time_to_first_spike', 'time_to_second_spike', 'time_to_last_spike', \
                                   'AP_rise_time', 'AP_rise_rate', 'AP_duration', 'AP_duration_half_width', 'Spikecount']   

            # self.getTargetFeatures()  # EXTRACTS Target Features with extractTargetFeatures() and therefore doesn't use given, but generates a set of target features based on a model which serves as reference

            self.target_features['bAP'] = self.bAP_features_dict
            self.bAP_features = self.bAP_dpol_features + self.bAP_hpol_features

        self.baselinemodel = None   # Able to set baseline model if wanted/necessary - lacks implementation yet
        self.ionchnames = None

        self.model_features = None # Placeholder for extended functions

        self.AP_firstspike = False      # reset AP_firstspike
        self.bAP_firstspike = False     # reset bAP_firstspike

        self.loadNeuronScope()
        

        if verbose:  # TODO do with flags
            self.printVerbose()

    def loadNeuronScope(self):
        """ 
        Loads modpath into neuron scope. Only has to be done once to be available in the runtime 
        Parameters
        ----------
        self.modpath : Path to mod files. For multiple models add all their mod files into this folder. 
        Different but same-named mod files for different models have to be manually changed to not overwrite each other.

        // TODO In a future version there will probably be the option to create multiple modpaths, one for each model.   
        """
        ## Load Run Controls
        h.load_file('stdrun.hoc')  # define h.run() function ; not needed if "gui" is imported from neuron

        ## Mod Files
        try:
            if self.modpath:
                h.nrn_load_dll(self.modpath)
            else: 
                h.nrn_load_dll(cs.MODPATH)     # use constant: MODPATH
            print("Mod files are loaded in!")
        except Exception as e:
            print("Mod files weren't able to load, check your pwd and if they are in your \
            'mods' folder and compiled.", e)
    
    def deleteCell(self):
        # Not sure if needed, I think I rather have to delete the cells in the neuron scope
        # But works to garbage collect old cells in RAM, as tested experimentally on total RAM usage.
        self.current_cell = None


    def createFeatureDict(self):
        ## Target Features from experimental data file
        self.somatic_features_dict = fnc.experimentalDataToDict(file_name = self.target_feature_file, file_path = str(PARENTPATH / '..' / 'data' / 'features' / 'target_features'))
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
        
        # TODO read dict elements (stepX: {})in depending on the step protocol given with stim.stepamps
        # print("\n")
        # print("Target Features: ", self.target_features)
        self.target_features = {}
        self.target_features['Soma'] = self.somatic_features_dict 


    def extractModelFeatures(self, traces_per_stepamp, time_vec, stim):
        """
        Function to extract Model Features.
        These have to be somatic and bAP features.
    
        """  
        efel.api.reset()
        
        # TODO handle bAP differently - maybe split into two functions, one for bAP, one for somatic
        # i can stimulate everything, I just don't have to add the stepampname -0.4 to the dict, removing it at the last point
        # print(traces_per_stepamp)
        traces = []
        traces_dict = {}
        for stepampname, locationtraces in traces_per_stepamp.items():              # -0,4 then 0.8, ... (then 1.0)
            traces_temp_dict = {}
            for location, locationtrace in locationtraces.items():      # Soma, then bAP 
                trace = {} 
                trace['V'] = locationtrace              # Set the 'V' (=voltage) key of the trace
                trace['T'] = time_vec                   # Set the 'T' (=time) key of the trace

                stim_end = stim.tstop
                trace['stim_start'] = [stim.delay]      # Set the 'stim_start' (time at which a stimulus starts, in ms) key of the trace
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
        stepampnamekeys = list(stim.stepamps.keys())           # stepampnames by user input from object property
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
            print(self.model_features)

    """
    def getTargetFeatures(self):
        # Auxiliary function to set self.bAP_features_dict
        traces_per_stepamp, time_vec = self.stimulateIClamp()       # stimulate with read-in cell which wasn't change yet for the baseline traces
        self.extractTargetFeatures(traces_per_stepamp, time_vec)    # extract target features from baseline read-in cell which wasn't changed yet
    """

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

    def createBAPTargets(self):     ## for hippo_bAP == True
        self.bAP_dpol_features  = ['AP1_amp', 'APlast_amp', 'Spikecount']
        self.bAP_hpol_features = []
        self.bAP_features = self.bAP_dpol_features + self.bAP_hpol_features   
        
        if self.bap_target_file:         # If True, check if bAP Target Features are given with a file           # TODO
            # TODO add ez json load
            self.bAP_features_dict = fnc.experimentalDataToDict(file_name = self.bap_target_file, file_path = str(PARENTPATH / '..' / 'data' / 'features' /' target_features'))
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

