#### Neuzy ####

##################################################################
# "create_data.py"
# Fanantenana                                                    #
##################################################################

## File to create Lists or Dictionaries from JSON data files to read in extractFeatures() for eFEL

import json
import os
import sys

import csv
import pathlib as pl
import numpy as np
from constants import *
import efel


def get_template_name(model_name):
    """Find the template name from hoc_string

    Note: this will fail if there is a begintemplate in a `/* */` style
    comment before the real begintemplate
    """
    with open(HOCPATH + '/' + model_name) as hoc_file:
        hoc_string = hoc_file.read()
    for i, line in enumerate(hoc_string.split('\n')):
        if 'begintemplate' in line:
            line = line.strip().split()
            assert line[0] == 'begintemplate', \
                'begintemplate must come first, line %d' % i
            template_name = line[1]
            return template_name
    else:
        raise Exception('Could not find begintemplate and therefore template_name in hoc file')
    return template_name

def getNans(x):
    indices = np.argwhere(np.isnan(x)).flatten()
    return indices

def removeNans(x):
    x = x[~np.isnan(x)]
    return x

def insertNans(x, indices = None):
    for i in indices:
        x = np.insert(x, i, np.nan)
    return x

def randomizeAutoConductances(x, seed = None):
    # Randomize Channels per SectionList

    # TODO Randomize with self channel borders
    rng = np.random.default_rng(seed)
    for i in range(len(x)):
        if np.any(np.isnan(x[i])):    # jump over nan values
            continue
        elif x[i] == 0:        # jump over blocked channels /blocked by assigning 0 -> bandaid fix for testing of channelblocker
            continue
        else:
            # x[i] = rng.uniform(x[i]/1000, x[i]*1000)   # relative bounds to 10
            # x[i] = abs(rng.normal(0.001, 0.01))   # relative bounds, normal distribution
            # x[i] = x[i]  # test init data

            ## logarithmic uniform distributed
            x[i] = rng.uniform(0, 1)            # norm lineal scale
            x[i] = ((1/1e-7)**x[i]*1e-7)        # apply logarithm with upper and lower bound        
    return x

def sampleResultsAround(x, seed = None, multiplier = None):
    rng = np.random.default_rng(seed)
    for i in range(len(x)):
        if np.any(np.isnan(x[i])):                   # jump over nan values
            continue
        else:
            # TODO change to logarithmic scale as well maybe?
            x[i] = rng.uniform(x[i]/multiplier, x[i]*multiplier)     
            x[i] = abs(x[i])
    return x

# TODO create target_features from models with eFEL and push them into a new json
def createLogs(input):
    lg.basicConfig(filename=SAVEPATH_LOG_OPT + "/log.log", level=lg.INFO)
    pass

def convertDfTo1D(df):
    dff = df.to_numpy().flatten()
    return dff  

def convert1DTo2DnpArr(x):
    skip = int(len(x)/len(SL_NAMES))
    cols = int(len(SL_NAMES))
    X = np.reshape(x, (cols, skip), order = 'F')
    return X

def calculateBounds(init_data):
    ## Bounds for L-BFGS-B Algorithm        0 to 2
    lowerbounds = np.divide(np.array(init_data), 5)
    upperbounds = np.multiply(np.array(init_data), 5)
    bounds = []
    if range(np.size(lowerbounds)) == range(np.size(upperbounds)):
        for i in range(np.size(lowerbounds)):
            if lowerbounds[i] < upperbounds[i]:
                bounds.append((lowerbounds[i], upperbounds[i]))

            # Swapping values from positive to negative for negative parameters (e.g. if used: "e_pas")
            elif lowerbounds[i] >= upperbounds[i]: 
                print("Lowerbounds are bigger than Upperbounds for e.g. element ", i + 1)
                print("Please check if an expected positive or negative value for specifying bounds could behave differently due to division/multiply")
                print("Swapping lowerbounds with upperbounds...")
                
                temp = lowerbounds[i]
                lowerbounds[i] = upperbounds[i]
                upperbounds[i] = temp
                bounds.append((lowerbounds[i], upperbounds[i]))    
    else:
        print("Unequal bounds")  # Not happening

    return bounds

## JSONS
def readJSON(file_name, file_path):
    with open(os.path.join(file_path, file_name), 'r') as f:
        content = json.load(f)
        return content

def readCSV(file_path):
    with open(file_path, "r") as f:
        csv_reader = csv.reader(f)
        csv_list = []
        for row in csv_reader:
            csv_list.append(row)
        print(csv_list)
    return csv_list

def writeJSON(target_path, target_file, data):
    if not os.path.exists(target_path):
        try:
            os.makedirs(target_path)
        except Exception as e:
            print(e)
            raise
    with open(os.path.join(target_path, target_file), 'w') as f:
        json.dump(data, f, indent = 4, separators = (',  \n', ': '))

"""
def readTargetFeaturesJSON(file_name, file_path):
    '''
    Read Target Features in, and extract their values.
    '''
    tf_names = []

    tf_dict = readJSON(file_name, file_path)
    for k, v in tf_dict.items():
        tf_name = k.split('.', 1)[0]
        tf_names.append(tf_name)
        for el, val in v.items():
            if el == 'Type':

            elif el == 'Mean':
                tf_value = val

    
    return tf"""

#print(efel.api.getFeatureNames())
#somatic_features = readJSON(file_name = 'somatic_target_features.json', file_path = './paropt/data/features/target_features')
#print(somatic_features)

def experimentalDataToDict(file_name = None, file_path = None):
    experimental_data_dict = readJSON(file_name = file_name, file_path = file_path)  #file_name = 'somatic_target_features.json'
    keys = ['Std', 'Mean']
    somatic_features_dict = {}
    step08dict = {}
    step10dict = {}
    step_04dict = {}
    for k, v in experimental_data_dict.items():
        if k.split('.', 1)[1] == 'Step0.8':
            step08fname = k.split('.', 1)[0]
            step08dict.update({step08fname: {x:v[x] for x in keys}})
            
        elif k.split('.', 1)[1] == 'Step1.0':
            step10fname = k.split('.', 1)[0]
            step10dict.update({step10fname: {x:v[x] for x in keys}})

        elif k.split('.', 1)[1] == 'Step-0.4':
            step_04fname = k.split('.', 1)[0]
            step_04dict.update({step_04fname: {x:v[x] for x in keys}})

    somatic_features_dict['Step-04'] = step_04dict
    somatic_features_dict['Step08'] = step08dict
    somatic_features_dict['Step10'] = step10dict
    
    #print(somatic_features_dict)
    return somatic_features_dict

def createHippoUnitInput(x):
    # create 2d dataframe of x
    # transpose it
    # flatten it
    # get x, ordered for sectionlists

    ######### GOT IMPLEMENTED IN UTILS.PY ###########
    pass


