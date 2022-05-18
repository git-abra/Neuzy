#### Neuzy

import sys, pathlib, csv, json

PP = pathlib.Path(__file__).parent

sys.path.insert(1, str(PP / '..' / '..' / 'auxiliaries/'))
sys.path.insert(1, str(PP / '..'))

from constants import *
import create_data
from CompleteOptModel import CompleteOptModel
from Testingfinaldata import *

from neuron import h
from neuron.units import ms, mV
from scipy.integrate import quad
import numpy as np
import pandas as pd

class ATPCalc():
    def __init__(self):
        pass
    
## Initializing HocObject, 
# can just take my autoclass, even though it does more than just initialization by initializing target data etc.
atpmodel = CompleteOptModel(   "To21_nap_strong_trunk_together.hoc",
                                target_feature_file = "somatic_target_features.json",
                                template_name = None)


#output_dict = {"qna" : [], "qca" : [], "atp": []}
output_dict = {}
atp_list = []
labels = [] 
for i in range(1,214,1):   # range 1,11,1
    # object to hold the parameter vector of testdata
    # testingfinaldata = TestingFinalData("./paropt/data/parameter_values/best10_par.csv", line = i)
    testingfinaldata = TestingFinalData("./paropt/data/parameter_values/final_par.csv", line = i)
    testdata = testingfinaldata.testdata

    output_dict.update({"Model_" + str(i): {}})
    labels.append("Model_" + str(i))

    # dont need run() function, so initialize it manually
    # get the current set of used mechanisms, init_data is unused
    init_data, indices = atpmodel.getMechanismItems() # getting the indices of the parameter combination for "To21_nap_strong_trunk_together.hoc"

    # update original cell
    atpmodel.updateAutoParameters(testdata, indices)

    ## Stimulation
    stim = h.IClamp(atpmodel.mycell.soma[0](0.5)) # stim at soma
    stim.delay = atpmodel.delay
    stim.dur = atpmodel.duration
    stim.amp = 0.8
    # soma_vec = h.Vector().record(atpmodel.mycell.soma[0](0.5)._ref_v) # record at middle (0,5) of soma
    # bAP1_vec = h.Vector().record(atpmodel.mycell.radTmed(1)._ref_v)
    # bAP1_vec = h.Vector().record(self.mycell.trunk[2](0.5)._ref_v)
    # time_vec = h.Vector().record(h._ref_t)

    h.dt =  0.025
    h.tstop = stim.delay + stim.dur
    h.v_init = -65
    h.celsius = 35
    h.init()

    ## adding ATP calculation
    ina_vec_list = []            # empty list to hold all of the vectors which record ina

    for sl in SL_NAMES:
        inputsl = getattr(atpmodel.mycell, sl)
        for sec in inputsl:
            for seg in sec:
                ina_vec = h.Vector().record(seg._ref_ina)
                ina_vec_list.append(ina_vec)
    #print(ina_vec_list)


    ica_vec_list = [] 

    for sl in SL_NAMES:
        if sl == "axonal":  # axonal does not have ica
            continue
        else:
            inputsl = getattr(atpmodel.mycell, sl)
            for sec in inputsl:
                for seg in sec:
                    ica_vec = h.Vector().record(seg._ref_ica)
                    ica_vec_list.append(ica_vec)
    #print(ica_vec_list)

    h.run()

    ## after simulation
    qna = 0
    counter = 0
    for sl in SL_NAMES:
        inputsl = getattr(atpmodel.mycell, sl)
        for sec in inputsl:
            for j, seg in enumerate(sec):
                integral = np.trapz(ina_vec_list[j])
                temp = integral * seg.area() * 1e-8
                qna = qna + temp

                # doesn't matter which way, same result
                """
                ina_vec = ina_vec_list[i] * seg.area() * 1e-8
                #for i in ina_vec:
                #    print(i)
                integral = np.trapz(ina_vec)  # integrate
                qna = qna + integral
                """
                # milliamps /cm2
                # area = um2
    qna = abs(qna)     
    print("QNA: ", qna)
    output_dict["Model_" + str(i)].update({"qna": qna})
    #output_dict["qna"].append(qna)

   

    qca = 0
    for sl in SL_NAMES:
        inputsl = getattr(atpmodel.mycell, sl)
        for sec in inputsl:
            for j, seg in enumerate(sec):

                ica_vec = ica_vec_list[j] * seg.area() * 1e-8
                #for i in ica_vec:
                #    print(i)
                integral = np.trapz(ica_vec)  # integrate
                qca = qca + integral

    qca = abs(qca)
    print("QCA: ", qca)
    output_dict["Model_" + str(i)].update({"qca": qca})
    #output_dict["qca"].append(qca)

    atp = 1/3 * qna * 6.24e+18 + (0.5 * qca * 6.24e+18)
    print("ATP: ", atp)
    #output_dict["atp"].append(atp)
    output_dict["Model_" + str(i)].update({"atp": atp})
    atp_list.append(atp)


    
    # surfacearea and number of segments
    # just here to add fast into thesis, not used for ATP XDDDD
    """
    surfacearea = 0
    segcounter = 0
    for sl in SL_NAMES:
        inputsl = getattr(atpmodel.mycell, sl)
        for sec in inputsl:
            for seg in sec:
                segcounter = segcounter + 1           # count segments
                surfacearea = surfacearea + seg.area()    # calculate surface area
    print(surfacearea)
    # calculated surface area : 13194.68914507711
    print(segcounter)
    """

print("OUTPUT_DICT: ", output_dict)


# overwriting, be careful when rerunning; not using my WRITEJSON function
with open("./paropt/models/ATP/qna_qca_atp_213.json", 'w') as f:
    json.dump(output_dict, f, indent = 4, separators = (',  \n', ': '))


with open("./paropt/models/ATP/atp_213.csv", 'w') as f:
    print(*labels, sep=',', end='\n', file=f)           # first line
    print(*atp_list, sep=',', end='\n', file=f)         # second line


#df = pd.DataFrame.from_dict(output_dict, orient="index")
#print(df.to_latex())
