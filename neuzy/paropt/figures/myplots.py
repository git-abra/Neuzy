## Functions to plot data
import os
import sys

#sys.path.insert(0, './paropt/models')
#import ezmodel as ez

from neuron import h, gui
import efel
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import pandas as pd
import pathlib as pl

## Paths (TODO have to improve with Pathlib)
current_dir = pl.Path.cwd()
SAVEPATH = str(current_dir / 'paropt' / 'view' / 'plots')  # Global constant SAVEPATH


def check_save_path():  # just to make sure
    SAVEPATH = str(current_dir / 'paropt' / 'view' / 'plots') 
    try:
        #if not os.path.exists(parameters.SAVE_PATH):
        #   os.makedirs(parameters.SAVE_PATH)
        if not os.path.exists(SAVEPATH):
            os.makedirs(SAVEPATH)
    except OSError as e:
        if e.errno != 17:
            raise
        pass

# Print results
def plotStandardTrace(soma_vec, time_vec, xlim):
    plt.figure(figsize=(8,4))
    plt.plot(time_vec, soma_vec)
    plt.xlabel('time (ms)')
    plt.ylabel('mV')
    plt.xlim(0, xlim)
    plt.ylim(-100, 100)
    plt.show(block=True)


def plotStandardTraceToFile(soma_vec, time_vec, save = False):
    '''
    TODO Problem: No iterator in filename, 
    so it overwrites the plot in every call. 
    Have to specify arguments for pyplot.savefig() 
    for enumeration of calls: index and name.
    Same for axes and description, call and plot-specific as arguments
    One function could fit them all
    '''
    plt.figure(figsize=(8,4))
    plt.plot(time_vec, soma_vec)
    plt.xlabel('time (ms)')
    plt.ylabel('mV')
    plt.xlim(0, 200)
    plt.ylim(-100, 100)
    if save:
        check_save_path()
        plt.savefig(SAVEPATH + "plotStandardTraceOutput_" + i + ".svg", format='svg')
        print("Figure saved in ", current_dir, "...", SAVEPATH)
    else:
        plt.show()
    plt.close()

'''
# TODO Population, Dictionary, List or Dataframe
population = 100 # Population is the total of generated cells
for i in range(population):
    d_optcell = {}
    d_optcell[i] = {'optcell' + str(i+1) : h.CA1_PC_Tomko()}

i_optcell = d_optcell.items()
print(d_optcell)
print(len(d_optcell))
print(i_optcell)
for key, value in i_optcell:
   print(key, "->", value)
# print(optcell["optcell99"].soma[0].gbar_kmb)

## Playground
blcell = blcell.soma[0]
# Interface for Biophysic Parameter Adaptions from Python to HOC
print(blcell.gkabar_kap)

#print(h.gkabar_kap)
#print(h.cas())
'''


## Figures

# Fig. 1



# Fig. 2



# Fig. 3



# Fig. 4