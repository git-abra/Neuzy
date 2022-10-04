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

import time
import logging as lg
import numpy as np
from neuron import h
import efel
import matplotlib.pyplot as plt

# TODO add kwargs functionality for v_init, temperature, dt, and other parameters to configure
class GenStim():
    """
    General Stim Class GenStim() to set parameters for the NEURON simulation.
    """

    def __init__(   self,
                    delay: int = 150, 
                    duration: int = 400, 
                    tstop: int = 750, 
                    cvode_active: bool = None,
                    stepamps:dict = {'Step-04': -0.4, 'Step08' : 0.8},
                    clamp = 'IClamp'
                ):
        """
        Constructor of GenStim()

        Parameters
        ----------
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
        self.clamp = clamp
        self.stepamps = stepamps

        if cvode_active:
            self.cvode_active = cvode_active


    def _stim_plot(self, rec_dict, time_vec):
        """
        Plots a disgustingly ugly plot for the traces :)
        """
        for k, v in rec_dict.items():
            for i, val in enumerate(v):
                np_val = np.array(val)
                np_time = np.array(time_vec)
                plt.figure(figsize=(8,4))
                plt.title(str(k) + "plot")
                # plt.plot([1,2,3], [2,3,4])
                plt.plot(np_time, np_val)
                plt.xlabel('time (ms)')
                plt.ylabel('mV')
                # plt.savefig('./abc' + str(i) + str(val) + '.svg', format='svg')

        #myplots.plotStandardTrace(soma_vec, time_vec, h.tstop)
        #myplots.plotStandardTrace(bAP1_vec, time_vec, h.tstop)
        pass


    def generate_spike_traces(self, model, plot:bool = False):
        """
        Returns
        -------
        - traces_per_stepamp_dict: dict
        - time_vec
        """

        stim_dict = self._define_stims(model)
        rec_dict = self._define_recordings(model, soma = [0.42, 0.69], radTdist = [0.42, 0.69])

        time_vec = h.Vector().record(h._ref_t)

        self._stim()

        if plot is True:
            self._stim_plot(rec_dict, time_vec)

        """
        for stepampname, stim in stim_dict.items():
            eval(stim)
            for location, recordings in rec_dict.items():
                for recording in recordings:
                    eval(recording)   
            self._stim()
            time_vec = h.Vector().record(h._ref_t)

        return traces_per_stepamp_dict, time_vec
        """

    # not sure if staticmethod worth, procrastinate this thought
    def _stim(self):
        """
        Stimulates depending on the initialized property values of the GenStim() object.

        """
        # TODO research
        h.dt =  0.075            # 0.025
        h.tstop = self.tstop     # 1600 for hippounit trace comparison
        h.v_init = -65
        h.celsius = 35
        h.init()
        h.run()

        # h.finitialize(-65 * mV) # alt: h.run() ; finitialize https://www.neuron.yale.edu/neuron/static/py_doc/simctrl/programmatic.html
        # h.continuerun(600 * ms) # alt: h.tstop = 200


    # not sure if staticmethod worth, procrastinate this thought
    def _define_stims(self, model):
        """
        Creates the stimulation electrodes with their settings.
        Currently only somatic stimulation.

        Returns
        -------
        stim_dict: dict - Dict of stimulation objects which are used, differ currently only by stepamp.


        Void, sets parameters in Neuron's Scope.    
        # TODO overhaul these scope restrictions for more than one active instance of HocObject.
        """

        stim_dict = {}

        for stepampname, stepamp in self.stepamps.items():
            # TODO research
            clampstim = getattr(h, self.clamp)
            stim = clampstim(model.current_cell.soma[0](0.5))
            # stim = h.IClamp(model.current_cell.soma[0](0.5)) # stim at soma
            stim.delay = self.delay
            stim.dur = self.duration
            stim.amp = stepamp

            stim_dict.update({stepampname: stim})

        return stim_dict


    def _define_recordings(self, model, **kwargs):
        """
        Creates the stimulation recordings for the electrodes

        Parameters
        ----------
        - model
        - **kwargs: dict - Dict with section names as keys, their continuous segment values in a list as value. E.g. soma = [0.42, 0.69]
        # TODO method for creating kwargs dict automatically by retrieving section names

        Returns
        -------
        - rec_dict : dict - Dict of recording vectors for the specified locations from **kwargs
        
        """
        # soma = kwargs.get('soma')

        rec_dict = {}

        for k, v in kwargs.items():
            rec_vecs = []
            for loc in v:
                if k == 'soma':
                    # _ = model.current_cell, k + '[0](' + v + ')'
                    # getattr(h.Vector(), record.
                    access = getattr(model.current_cell, str(k))[0](loc)._ref_v   
                else:
                    access = getattr(model.current_cell, str(k))(loc)._ref_v 

                rec_vec = h.Vector().record(access)
                rec_vecs.append(rec_vec)

            rec_dict.update({k : rec_vecs})

        return rec_dict


    def get_stim_traces_soma(self, model, plot:bool = False):
        """
        Stimulate the soma and retrieve somatic traces.
        Sets the Clamp and recording variables

        Parameters
        ----------
        - model: The current initialized HocObject cell
        - method: 'IClamp'(default), 'VClamp' - Configures the stimulation protocol
        - plot: bool = False - determines if the traces should be shown in a plot

        Returns
        -------


        """
            
        traces_per_stepamp_dict = {}
        for stepampname, stepamp in self.stepamps.items():
            #start = time.time()

            stim = h.IClamp(model.current_cell.soma[0](0.5)) # stim at soma
            stim.delay = self.delay
            stim.dur = self.duration
            stim.amp = stepamp
            soma_vec = h.Vector().record(model.current_cell.soma[0](0.5)._ref_v) # record at middle (0,5) of soma

        pass


    def get_stim_traces_dendrites(self, model, locations, plot:bool = False):
        """
        Stimulate over dendritic branches and retrieve dendritic traces.
        Sets the Clamp and recording variables

        Parameters
        ----------
        - model: The current initialized HocObject cell
        - method: 'IClamp'(default), 'VClamp' - Configures the stimulation protocol
        - plot: bool = False - determines if the traces should be shown in a plot

        Returns
        -------


        """
        pass


    def stimulateIClamp(self, model):   # Default values are from Schneider et al. 2021
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

            stim = h.IClamp(model.current_cell.soma[0](0.5)) # stim at soma
            stim.delay = self.delay
            stim.dur = self.duration
            stim.amp = stepamp
            soma_vec = h.Vector().record(model.current_cell.soma[0](0.5)._ref_v) # record at middle (0,5) of soma

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


            if model.hippo_bAP == True:
                ## Hippounit bap positions
                bAP1_vec = h.Vector().record(model.current_cell.radTprox(0.5)._ref_v)   # 50 um
                bAP2_vec = h.Vector().record(model.current_cell.radTmed(0.5)._ref_v)    # 150 um
                bAP3_vec = h.Vector().record(model.current_cell.radTdist(0.22727272727272727)._ref_v)  # 245 um
                bAP4_vec = h.Vector().record(model.current_cell.radTdist(0.3181818181818182)._ref_v)   # 263 um
                bAP5_vec = h.Vector().record(model.current_cell.radTdist(0.6818181818181819)._ref_v)   # 336 um
                bAP6_vec = h.Vector().record(model.current_cell.radTdist(0.7727272727272728)._ref_v)   # 354 um
            else:
                bAP1_vec = h.Vector().record(model.current_cell.radTmed(1)._ref_v)    # 205um distance from middle of soma, 200 from end of soma, 210 from start of soma with 10um diameter.

            
            # TODO get region names automatically by distance and use setattr(self.current_cell, sectionname)._ref_v
            
            time_vec = h.Vector().record(h._ref_t)


            h.dt =  0.075            # 0.025
            h.tstop = self.tstop  # 1600 for hippounit trace comparison
            h.v_init = -65
            h.celsius = 35
            h.init()
            h.run()

            
            # h.finitialize(-65 * mV) # alt: h.run() ; finitialize https://www.neuron.yale.edu/neuron/static/py_doc/simctrl/programmatic.html
            # h.continuerun(600 * ms) # alt: h.tstop = 200
            #end = time.time()

            #print("time1: ", end - start)
            #lg.info("SIMULATION TIME" + str(end - start) + "seconds.")
            soma_arr = np.array(soma_vec)

            # TODO automatic section dictionaries, not hardcoded names and amount of arrays. detect how many traces are recorded with a counter or something and use that.
            # I don't like this programming just for one purpose... it's crap
            if model.hippo_bAP == True:           
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
    """
    Stim Class, which inherits from GenStim().
    Adds functions to sort models out early in the optimization process, 
    depending on its first (backpropagating) Action Potential.
    """
    def __init__(   self,
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
        Added Parameters
        ----------------------
        - delay_firstspike:int
        - duration_firstspike:int
        - tstop_firstspike:int
        """
        super().__init__(delay, duration, tstop, cvode_active, stepamps)

        ## Firstspike properties to check for the occurrence of the first few AP 
        self.delay_firstspike = delay_firstspike
        self.duration_firstspike = duration_firstspike
        self.tstop_firstspike = tstop_firstspike

    def _stim_firstspike_plot(self):
        """
        pyplot.figure(figsize=(8,4)) # Default figsize is (8,6)
        pyplot.plot(time_vec, bAP1_vec)
        pyplot.xlabel('time (ms)')
        pyplot.ylabel('mV')
        pyplot.show()
        """

        #myplots.plotStandardTrace(soma_vec, time_vec, h.tstop)
        #myplots.plotStandardTrace(bAP1_vec, time_vec, h.tstop)
        pass

    def _stim_firstspike(self):
        """
        Stimulates depending on the initialized values
        """
        # TODO maybe make _stim() take different arguments depending on a decisional argument and remove this one

        h.dt = 0.1
        h.tstop = self.tstop_firstspike
        h.v_init = -65
        h.celsius = 35
        h.init()
        h.run()

        # h.finitialize(-65 * mV) # alt: h.run() ; finitialize https://www.neuron.yale.edu/neuron/static/py_doc/simctrl/programmatic.html
        # h.continuerun(600 * ms) # alt: h.tstop = 200

    def stimulateIClamp_firstspike(self, model, par):   # Default values are from Schneider et al. 2021
        '''
        IClamp Optimization Protocols
        Stimulate IClamp on self.current_cell /w random values from rnddata.

        Parameters
        ----------
        - model: hocmodel object
        - par : mpi object
        '''
        efel.api.reset()
        traces_per_stepamp_dict = {}

        # remove all hyperpolarizing keys because bAP doesn't matter hyperpolarizing currents
        stepamps_dict = {k:v for k,v in self.stepamps.items() if '-' not in k}   # REMOVE HYPERPOLARIZING CURRENT FROM THIS TEST

        for stepampname, stepamp in stepamps_dict.items():
            #print(stepampname)
            start = time.time()

            stim = h.IClamp(model.current_cell.soma[0](0.5)) # stim at soma
            stim.delay = self.delay_firstspike
            stim.dur = self.duration_firstspike
            stim.amp = stepamp
            soma_vec = h.Vector().record(model.current_cell.soma[0](0.5)._ref_v) # record at middle (0,5) of soma

            if model.hippo_bAP == True:
                ## Hippounit bap positions, manual way.
                bAP2_vec = h.Vector().record(model.current_cell.radTmed(0.5)._ref_v)    # 205um distance, radtprox makes positive ap_peak also  
                bAP1_vec = h.Vector().record(model.current_cell.radTprox(0.5)._ref_v)
                bAP3_vec = h.Vector().record(model.current_cell.radTdist(0.22727272727272727)._ref_v)
                bAP4_vec = h.Vector().record(model.current_cell.radTdist(0.3181818181818182)._ref_v)
                bAP5_vec = h.Vector().record(model.current_cell.radTdist(0.6818181818181819)._ref_v)
                bAP6_vec = h.Vector().record(model.current_cell.radTdist(0.7727272727272728)._ref_v)
            else:
                bAP1_vec = h.Vector().record(model.current_cell.radTmed(1)._ref_v)    # 205um distance, radtprox makes positive ap_peak also

            # TODO extension: get region names automatically by distance and use setattr(self.current_cell, sectionname)._ref_v
            
            time_vec = h.Vector().record(h._ref_t)
            
            h.dt = 0.1
            h.tstop = self.tstop_firstspike
            h.v_init = -65
            h.celsius = 35
            h.init()
            h.run()

            
            # h.finitialize(-65 * mV) # alt: h.run() ; finitialize https://www.neuron.yale.edu/neuron/static/py_doc/simctrl/programmatic.html
            # h.continuerun(600 * ms) # alt: h.tstop = 200
            soma_arr = np.array(soma_vec)
            if model.hippo_bAP == True:           
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

                print("Spikecount on soma for stepamp " + str(stepampnames) + " at least 2 on rank " + str(par.rank))
                lg.info("Spikecount on soma for stepamp " + str(stepampnames) + " at least 2 on rank " + str(par.rank))
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
                        print("Spikecount on last bAP for stepamp " + str(stepampnames) + " at least 1 on rank " + str(par.rank))
                        lg.info("Spikecount on last bAP for stepamp " + str(stepampnames) + " at least 1 on rank " + str(par.rank))
                        bAP_success = bAP_success + 1"""
                    #bAP_success = bAP_success + 1    
                    #and bAP_model_feature_spike[i]['time_to_first_spike'] > 0:
                    #and bAP_model_feature_spike[i]['AP1_peak'] > 0 \
                    #and bAP_model_feature_spike[i]['AP2_peak'] > 0 \
                    #and bAP_model_feature_spike[i]['AP2_amp'] > 0:

                else:
                    print("No minimum Model Action Potential at bAP for stepamp " + str(stepampnames) + " on rank " + str(par.rank))
                    lg.info("No minimum Model Action Potential at bAP for stepamp " + str(stepampnames) + " on rank " + str(par.rank))
                    
                    # bAP tests and experimental data was for 1000ms stimuli; target feature for 400ms is 4 ; so setting it to 2 handmade hyperparameter, for 11 see upper explanation
                
        else:
            print("No minimum Model Action Potential at Soma for stepamp " + str(stepampnames) + " on rank " + str(par.rank))
            lg.info("No minimum Model Action Potential at Soma for stepamp " + str(stepampnames) + " on rank " + str(par.rank))


        if bAP_success == len(bAP_model_feature_spike):
            print("Soma and bAP Action Potentials sufficient, sending into full cost evaluation")
            lg.info("Soma and bAP Action Potentials sufficient, sending into full cost evaluation")
            return True
        else:
            pass