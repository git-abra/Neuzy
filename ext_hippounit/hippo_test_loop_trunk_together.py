from hippounit.utils import ModelLoader
from hippounit.utils import ModelLoader_parameters
from hippounit import tests

from json2html import *
import pkg_resources
import json
import collections
import numpy
import IPython

def main():
    pass

if __name__ == "__main__":
    mod_files_path = "./mods/x86_64"  # path to mod files
    base_directory = '../../../../validation_results_updatedplotFontsize/'  #all the outputs will be saved here. It will be an argument to the test.
    model = ModelLoader_parameters(mod_files_path = mod_files_path) #Load cell model        # atm parameter_path is necessary
    # list of sectionlists which get updated parameter combinations set. trunk and oblique sec list have derived sections from them.
    model.sectionlist_list = ['somatic', 'axonal', 'apical', 'basal', "trunk_prox", "trunk_med"]     # To21_nap_strong_trunk_together.hoc

    model.hocpath = "pathtohocfile" # enter hoc path

    model.template_name = 'CA1_PC_Tomko("./ext_hippounit/mods/To21_nap_strong_trunk_together.hoc")' # If the hoc file doesn't contain a template, this must be None (the default value is None)

    # model.SomaSecList_name should be None, if there is no Section List in the model for the soma, or if the name of the soma section is given by setting model.soma (the default value is None)
    model.SomaSecList_name = 'somatic'
    # if the soma is not in a section list or to use a specific somatic section, add its name here:
    model.soma = None #'soma[0]'

    # For the PSP Attenuation Test, and Back-propagating AP Test a section list containing the trunk sections is needed
    model.TrunkSecList_name = 'trunk'
    # For the Oblique Integration Test a section list containing the oblique dendritic sections is needed
    #model.ObliqueSecList_name = 'oblique_sec_list'
    model.ObliqueSecList_name = 'oblique'

    # It is important to set the v_init and the celsius parameters of the simulations here,
    # as if they are only set in the model's files, they will be overwritten with the default values of the ModelLoader class.
    # default values: v_init = -70, celsius = 34 
    model.v_init = -65
    model.celsius = 35

    # It is possible to run the simulations using variable time step (default for this is False)
    model.cvode_active = False

    x = model.readJSON(parameter_path = "./datapath")    # data
    for i in range(len(x)):
        model.parameters = x[i]    
        model.name= "./subfoldername" + str(i + 1) # outputs will be saved in subfolders named like this:
        
        
## Somatic Features Test Patch Clamp Dataset

        with open('../target_features/feat_CA1_pyr_cACpyr_more_features.json') as f:
            observation = json.load(f, object_pairs_hook=collections.OrderedDict)

        ttype = "CA1_pyr_cACpyr"
        
        stim_file = pkg_resources.resource_filename("hippounit", "tests/stimuli/somafeat_stim/stim_" + ttype + ".json")
        with open(stim_file, 'r') as f:
            config = json.load(f, object_pairs_hook=collections.OrderedDict)
            
        # Instantiate test class   
        test = tests.SomaticFeaturesTest(observation=observation, config=config, force_run=False, show_plot=True, save_all = True, base_directory=base_directory)

        # test.specify_data_set is added to the name of the subdirectory (somaticfeat), so test runs using different data sets can be saved into different directories
        test.specify_data_set = 'UCL_data'
  
        test.npool = 10 # Number of parallel processes
            
        try:
            score = test.judge(model)
            score.summarize()
            print(score)
            score = str(score)
            
            with open("./parameters/somaticfinalscores.csv", "a") as f:
                print(score, sep=',', end='\n', file=f)

        except Exception as e:
            print('Model: ' + model.name + ' could not be run')
            print(e)
            pass


## Somatic Features Test Sharp Electrode Test
            
        with open('../target_features/feat_rat_CA1_JMakara_more_features.json') as f:
            observation = json.load(f, object_pairs_hook=collections.OrderedDict)


        stim_file = pkg_resources.resource_filename("hippounit", "tests/stimuli/somafeat_stim/stim_rat_CA1_PC_JMakara.json")
        with open(stim_file, 'r') as f:
            config = json.load(f, object_pairs_hook=collections.OrderedDict)
            
        # Instantiate test class   
        test = tests.SomaticFeaturesTest(observation=observation, config=config, force_run=False, show_plot=True, save_all = True, base_directory=base_directory)

        # test.specify_data_set is added to the name of the subdirectory (somaticfeat), so test runs using different data sets can be saved into different directories
        test.specify_data_set = 'JMakara_data'

     
        test.npool = 10 # Number of parallel processes

        try:
            score = test.judge(model)
            score.summarize()
        except Exception as e:
            print('Model: ' + model.name + ' could not be run')
            print(e)
            pass
        
## PSP Attenuation Test
        
        with open("../target_features/feat_PSP_attenuation_target_data.json", 'r') as f:
            observation = json.load(f, object_pairs_hook=collections.OrderedDict)

        IPython.display.HTML(json2html.convert(json = observation))


        stim_file = pkg_resources.resource_filename("hippounit", "tests/stimuli/PSP_attenuation_stim/stim_PSP_attenuation_test.json")

        with open(stim_file, 'r') as f:
            config = json.load(f, object_pairs_hook=collections.OrderedDict)

        # Instantiate test class 
        test = tests.PSPAttenuationTest(config=config, observation=observation, num_of_dend_locations = 15, force_run=False, show_plot=True, save_all = True, base_directory=base_directory)
                      
        test.npool = 10 # Number of parallel processes

        try: 
            # Run the test 
            score = test.judge(model)
            #Summarize and print the score achieved by the model on the test using SciUnit's summarize function
            score.summarize()
        except Exception as e:
            print('Model: ' + model.name + ' could not be run')
            print(e)
            pass
        
## Backpropagating AP Test     
        
        with open('../target_features/feat_backpropagating_AP_target_data.json') as f:
            observation = json.load(f, object_pairs_hook=collections.OrderedDict)
        
        IPython.display.HTML(json2html.convert(json = observation))
        stim_file = pkg_resources.resource_filename("hippounit", "tests/stimuli/bAP_stim/stim_bAP_test.json")

        with open(stim_file, 'r') as f:
            config = json.load(f, object_pairs_hook=collections.OrderedDict)
        
        # Instantiate the test class
        test = tests.BackpropagatingAPTest(config=config, observation=observation, force_run=False, force_run_FindCurrentStim=False, show_plot=True, save_all=True, base_directory=base_directory)

        test.npool = 10 # Number of parallel processes

        try: 
            # Run the test
            score = test.judge(model)
            #Summarize and print the score achieved by the model on the test using SciUnit's summarize function
            score.summarize()
        except Exception as e:
            print('Model: ' + model.name + ' could not be run')
            print(e)
            pass 
           

## Depolarization Block Test
        
        with open('../target_features/depol_block_target_data.json') as f:
            observation = json.load(f, object_pairs_hook=collections.OrderedDict)
            
        IPython.display.HTML(json2html.convert(json = observation))


        test = tests.DepolarizationBlockTest(observation=observation, force_run=False, show_plot=True, save_all=True, base_directory=base_directory)

        test.npool = 10 # Number of parallel processes

        try: 
            # Run the test
            score = test.judge(model)
            #Summarize and print the score achieved by the model on the test using SciUnit's summarize function
            score.summarize()
            print(score)
            score = str(score)
            
            with open("./parameters/depolfinalscores.csv", "a") as f:
                print(score, sep=',', end='\n', file=f)

        except Exception as e:
            print('Model: ' + model.name + ' could not be run')
            print(e)
            pass 
        
        with open('../target_features/oblique_target_data.json') as f:
            observation = json.load(f, object_pairs_hook=collections.OrderedDict)

        IPython.display.HTML(json2html.convert(json = observation))


        test = tests.ObliqueIntegrationTest(observation = observation, save_all = True, force_run_synapse=False, force_run_bin_search=False, show_plot = True, base_directory = base_directory)

        test.npool = 10 # Number of parallel processes

        try: 
            score = test.judge(model)
            score.summarize()
        except Exception as e:
            print('Model: ' + model.name + ' could not be run')
            print(e)
            pass
        
        