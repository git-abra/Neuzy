#### Neuzy

import time
import logging as lg
import numpy as np
import pandas as pd
from neuron import h
from neuron.units import ms, mV
import efel

class GenStim():
    def __init__(   self,
                    model,
                    par, 
                    delay: int = 150, 
                    duration: int = 400, 
                    tstop: int = 750, 
                    cvode_active: bool = None,
                    stepamps:dict = {'Step-04': -0.4, 'Step08' : 0.8}
                ):
        """
        General Stim Class GenStim() to set parameters for the NEURON simulation.
        Constructor Parameters
        ----------------------
        - delay: int
        - duration: int
        - tstop: int
        - cvode_active: bool
        - stepamps: dict
        """
        ## Properties of the full call to run simulation
        self.delay = delay
        self.duration = duration
        self.tstop = tstop
        
        self.model = model
        self.par = par

        self.stepamps = stepamps

        if cvode_active:
            self.cvode_active = cvode_active
        else:
            self.cvode_active = False  # Doesn't work because of EFEL X and Y axes "Assertion fired(efel/cppcore/Utils.cpp:33): X & Y have to have the same point count"
    
    def stimulateIClamp(self):   # Default values are from Schneider et al. 2021
        """
        IClamp Optimization Protocols
        Stimulate IClamp on a cell.

        Returns
        -------
        tuple( traces_per_stepamp_dict: dict: {stepampname: {'Soma': soma_arr , 'bAP': bAP1_arr}}, time_vec )
        """
        traces_per_stepamp_dict = {}
        for stepampname, stepamp in self.stepamps.items():
            #start = time.time()

            stim = h.IClamp(self.model.current_cell.soma[0](0.5)) # stim at soma
            stim.delay = self.delay
            stim.dur = self.duration
            stim.amp = stepamp
            soma_vec = h.Vector().record(self.model.current_cell.soma[0](0.5)._ref_v) # record at middle (0,5) of soma

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


            if self.model.hippo_bAP == True:
                ## Hippounit bap positions
                bAP1_vec = h.Vector().record(self.model.current_cell.radTprox(0.5)._ref_v)   # 50 um
                bAP2_vec = h.Vector().record(self.model.current_cell.radTmed(0.5)._ref_v)    # 150 um
                bAP3_vec = h.Vector().record(self.model.current_cell.radTdist(0.22727272727272727)._ref_v)  # 245 um
                bAP4_vec = h.Vector().record(self.model.current_cell.radTdist(0.3181818181818182)._ref_v)   # 263 um
                bAP5_vec = h.Vector().record(self.model.current_cell.radTdist(0.6818181818181819)._ref_v)   # 336 um
                bAP6_vec = h.Vector().record(self.model.current_cell.radTdist(0.7727272727272728)._ref_v)   # 354 um
            else:
                bAP1_vec = h.Vector().record(self.model.current_cell.radTmed(1)._ref_v)    # 205um distance from middle of soma, 200 from end of soma, 210 from start of soma with 10um diameter.

            
            # TODO get region names automatically by distance and use setattr(self.current_cell, sectionname)._ref_v
            
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
            if self.model.hippo_bAP == True:           
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


class Firstspike_SortOutStim(GenStim): # Stim with function to sort out early - i.e. Models which are not throwing APs
    def __init__(   self,
                    model,
                    par, 
                    delay: int = 150, 
                    duration: int = 400, 
                    tstop: int = 750, 
                    cvode_active: bool = None,
                    stepamps:dict = {'Step-04': -0.4, 'Step08' : 0.8},
                    delay_firstspike:int = 50, 
                    duration_firstspike:int = 65, 
                    tstop_firstspike:int = 150,
                    ):
        """
        Stim Class, which inherits from GenStim().
        Adds functions to sort models out early in the optimization process, 
        depending on its first (backpropagating) Action Potential.

        Added Parameters
        ----------------------
        - delay_firstspike:int
        - duration_firstspike:int
        - tstop_firstspike:int
        """
        super().__init__(model, par, delay, duration, tstop, cvode_active, stepamps)

        ## Firstspike properties to check for the occurrence of the first few AP 
        self.delay_firstspike = delay_firstspike
        self.duration_firstspike = duration_firstspike
        self.tstop_firstspike = tstop_firstspike

    def stimulateIClamp_firstspike(self):   # Default values are from Schneider et al. 2021
        '''
        IClamp Optimization Protocols
        Stimulate IClamp on self.current_cell /w random values from rnddata.

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

            stim = h.IClamp(self.model.current_cell.soma[0](0.5)) # stim at soma
            stim.delay = self.delay_firstspike
            stim.dur = self.duration_firstspike
            stim.amp = stepamp
            soma_vec = h.Vector().record(self.model.current_cell.soma[0](0.5)._ref_v) # record at middle (0,5) of soma

            if self.model.hippo_bAP == True:
                ## Hippounit bap positions, manual way.
                bAP1_vec = h.Vector().record(self.model.current_cell.radTprox(0.5)._ref_v)
                bAP2_vec = h.Vector().record(self.model.current_cell.radTmed(0.5)._ref_v)    # 205um distance, radtprox makes positive ap_peak also  
                bAP3_vec = h.Vector().record(self.model.current_cell.radTdist(0.22727272727272727)._ref_v)
                bAP4_vec = h.Vector().record(self.model.current_cell.radTdist(0.3181818181818182)._ref_v)
                bAP5_vec = h.Vector().record(self.model.current_cell.radTdist(0.6818181818181819)._ref_v)
                bAP6_vec = h.Vector().record(self.model.current_cell.radTdist(0.7727272727272728)._ref_v)
            else:
                bAP1_vec = h.Vector().record(self.model.current_cell.radTmed(1)._ref_v)    # 205um distance, radtprox makes positive ap_peak also

            # TODO extension: get region names automatically by distance and use setattr(self.current_cell, sectionname)._ref_v
            
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
            if self.model.hippo_bAP == True:           
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

                print("Spikecount on soma for stepamp " + str(stepampnames) + " at least 2 on rank " + str(self.par.rank))
                lg.info("Spikecount on soma for stepamp " + str(stepampnames) + " at least 2 on rank " + str(self.par.rank))
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
            print("No minimum Model Action Potential at Soma for stepamp " + str(stepampnames) + " on rank " + str(self.par.rank))
            lg.info("No minimum Model Action Potential at Soma for stepamp " + str(stepampnames) + " on rank " + str(self.par.rank))


        if bAP_success == len(bAP_model_feature_spike):
            print("Soma and bAP Action Potentials sufficient, sending into full cost evaluation")
            lg.info("Soma and bAP Action Potentials sufficient, sending into full cost evaluation")
            return True
        else:
            pass