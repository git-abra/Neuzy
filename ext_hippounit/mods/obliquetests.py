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
    # path to mod files
    mod_files_path = "./x86_64"

    #all the outputs will be saved here. It will be an argument to the test.
    base_directory = '../validation_results/'

    #Load cell model        # atm parameter_path is necessary
    model = ModelLoader_parameters(mod_files_path = mod_files_path)
    # list of sectionlists which get updated parameter combinations set. trunk and oblique sec list have derived sections from them.
    model.sectionlist_list = ['somatic', 'axonal', 'apical', 'basal']   
    # if parameter_path is given, read the data in with method readJSON, could also give it here to # readJSON as argument
    # path to hoc file
    # the model must not display any GUI!!
    model.hocpath = "./To21_nap.hoc"

    # If the hoc file doesn't contain a template, this must be None (the default value is None)
    model.template_name = 'CA1_PC_Tomko("./ext_hippounit/mods/To21_nap.hoc")'

    # model.SomaSecList_name should be None, if there is no Section List in the model for the soma, or if the name of the soma section is given by setting model.soma (the default value is None)
    model.SomaSecList_name = 'somatic'
    # if the soma is not in a section list or to use a specific somatic section, add its name here:
    model.soma = None #'soma[0]'

    # For the PSP Attenuation Test, and Back-propagating AP Test a section list containing the trunk sections is needed
    model.TrunkSecList_name = 'trunk'
    # For the Oblique Integration Test a section list containing the oblique dendritic sections is needed
    model.ObliqueSecList_name = 'oblique_sec_list'

    # It is important to set the v_init and the celsius parameters of the simulations here,
    # as if they are only set in the model's files, they will be overwritten with the default values of the ModelLoader class.
    # default values: v_init = -70, celsius = 34 
    model.v_init = -65
    model.celsius = 35

    # It is possible to run the simulations using variable time step (default for this is False)
    model.cvode_active = False

    x = model.readJSON(parameter_path = "./parameters/output_json_sim_Servers_nap_best.json")
    
    model.parameters = x[3]
    # outputs will be saved in subfolders named like this:
    model.name= "To21_loop_best_outputs_" + str(3)


    with open('../target_features/oblique_target_data.json') as f:
        observation = json.load(f, object_pairs_hook=collections.OrderedDict)

    IPython.display.HTML(json2html.convert(json = observation))


    test = tests.ObliqueIntegrationTest(observation = observation, save_all = True, force_run_synapse=False, force_run_bin_search=False, show_plot = True, base_directory = base_directory)

    # Number of parallel processes
    test.npool = 10

    score = test.judge(model)
    score.summarize()