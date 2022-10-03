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

from neuron import h
import pathlib
from copy import copy
import pandas as pd
import numpy as np
import logging as lg

from neuzy.paropt.models.GenModel import GenModel

import neuzy.paropt.auxiliaries.constants as cs
import neuzy.paropt.auxiliaries.functions as fnc

def main():
    pass

## Model with HOC as input
class HocModel(GenModel):
    """
    Inherits from GenModel.
    HocModel to create a Model automatically from 
    extracting information out of an existing HOC model 
    """
    def __init__(   self,
                    model_name,
                    modpath = None,             # in constants.py if not given
                    target_feature_file = None,
                    bap_target_file = None, 
                    hippo_bAP:bool = True,  
                    channelblocknames = None,   # has to be in the fullname format: "gkabar_kad" or "gbar_nax"
                    verbose = False,  
                    hocpath = None,             # in constants.py if not given
                    sectionlist_list:list = None,   # adapt sectionlist to your model #TODO make a function to retrieve sectionlist names, and not only section names
                    template_name = None,           # from hoc begintemplate "template_name" 
                    parameterkeywords:list = None   # Parameter Keywords from psection() density mechs, which are to be used.              
                    ):
        super().__init__(   modpath,             # in constants.py if not given
                            target_feature_file,
                            bap_target_file, 
                            hippo_bAP,  
                            channelblocknames,  # has to be in the fullname format: "gkabar_kad" or "gbar_nax" 
                            verbose
                            )

        self.model_name = model_name

        if sectionlist_list:
            self.sectionlist_list = sectionlist_list
        else:
            self.sectionlist_list = self.getSectionListNames() #cs.SL_NAMES       # use constant

        if hocpath:
            self.hocpath = hocpath
        else:
            self.hocpath = cs.HOCPATH          # use constant

        if template_name:
            self.template_name = template_name
        else:
            self.getTemplateName()
            print("Extracted template_name: " + str(self.template_name) + ", because no template_name was given.")
            lg.info("Extracted template_name: " + str(self.template_name) + ", because no template_name was given.")

        if parameterkeywords:
            self.parameterkeywords = parameterkeywords
        else: 
            self.parameterkeywords = ["bar"]    # List of parameter key words like "bar" for gbar active ion channels. You can basically choose anything from neuron's psection() density_mech dict.
                                                # check for "bar", "tau", "pas" or whatever you want

        self.readHocModel()
        self.initializeCell()     # calls createHocModel for cell


    def getSectionListNames(self):
        """
        Returns
        -------
        sectionlists: List - List of sectionlist names.
        """
        sectionlists = []
        with open(cs.HOCPATH + '/' + self.model_name) as hoc_file:
            hoc_string = hoc_file.read()
        for i, line in enumerate(hoc_string.split('\n')):
            if 'new SectionList()' in line:
                if not 'all' in line.split('=')[0].strip():
                    sectionlists.append(line.split('=')[0].strip())

        print(sectionlists)
        return sectionlists


    def getSectionNames(self):
        """
        Returns
        -------
        df : Dataframe of sectionnames(row) to sectionlists (col)
        secnamedict : Dict of sectionnames(nested elements) inside sectionlists(elements)
        """
        secnamedict = {}
        print(self.sectionlist_list)
        for sl in self.sectionlist_list:
            inputsl = getattr(self.current_cell, sl)
            mysecnamelist = []
            for sec in inputsl:
                mysecnamelist.append(h.secname(sec = sec).split('.', 1)[1])     # maxsplit = 1 , take second element after '.' first element = 0 would be the templatename
            secnamedict.update({sl: mysecnamelist})
        df = pd.DataFrame.from_dict(secnamedict, orient = 'index').transpose()
           
        # TODO add version for 'all' sectionlist
        """
        mysecnamelist = []
        for sec in self.current_cell.all:    
            mysecnamelist.append(h.secname(sec = sec).split('.', 1)[1])
        """
        return df, secnamedict


    def getTemplateName(self):
        """
        Find the template name from hoc_string
        Note: this will fail if there is a begintemplate in a `/* */` style
        comment before the real begintemplate
        # Source: BluePyOpt
        """
        with open(cs.HOCPATH + '/' + self.model_name) as hoc_file:
            hoc_string = hoc_file.read()
        for i, line in enumerate(hoc_string.split('\n')):
            if 'begintemplate' in line:
                line = line.strip().split()
                assert line[0] == 'begintemplate', \
                    'begintemplate must come first, line %d' % i
                self.template_name = line[1]
                break
        else:   # no break
            raise Exception('Could not find begintemplate and therefore template_name in hoc file')


    def readHocModel(self):
        """
        Read in Hoc Model with h.xopen()
        """
        try:
            HOCPATH_temp = pathlib.Path(self.hocpath)            # Pathlib object
            h.xopen(str(HOCPATH_temp / self.model_name))    # stringify pl object for concatenation with '/'
            print("Hoc Morphology is loaded in!")
        except Exception as e:
            print("Hoc Morphology file wasn't able to load, check your pwd and if the morphology is in your 'morphos' folder.", e)


    def createHocModel(self):   # TODO automatically load READ-IN template in
        """
        Creates a cell from a template. Prerequisite is a read in Hoc Model
        """
        print("Template name: " + str(self.template_name) + " found. Creating cell from Hoc..")
        lg.info("Template name: " + str(self.template_name) + " found. Creating cell from Hoc..")
        HOCPATH_temp = pathlib.Path(self.hocpath)
        cell = getattr(h, self.template_name)(HOCPATH_temp / self.model_name)

        return cell

    def initializeCell(self):
        """ 
        Create a Hoc Cell from template
        """

        self.current_cell = self.createHocModel()      # Create cell "current_cell" from template.

        if self.channelblocknames:               # Block ion channels, if set.
            self.blockIonChannel()


    def getMechanismItems(self):
        """ 
        Prerequisites: Read-in HocObject / HocObject in Scope 
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
       
        for sl in self.sectionlist_list:        
            inputsl = getattr(self.current_cell, sl)
            myionsdict_temp = {}           
            for sec in inputsl:     
                for mech in sec.psection()['density_mechs'].keys():               
                    for ionchname, ionchvalue in sec.psection()['density_mechs'][mech].items():           
                        for parameterkeyword in self.parameterkeywords:
                            if parameterkeyword in ionchname:          # check for "bar", "tau", "pas" or whatever you want !
                                for i in ionchvalue:                   # takes values per compartment for the ionch in the section
                                    
                                    myionsdict_temp.update({str(ionchname + '_' + mech): ionchvalue[0]})

                                    # commented section was before blockIonChannel integration
                                    """if i != 0:                         # only check for gbars with a value                 
                                        # Have to save with appended sec.psection()['density_mechs'].keys() name (mech)
                                        myionsdict_temp.update({str(ionchname + '_' + mech): ionchvalue[0]})
                                        # myionsdict_temp.update({str(ionchname + '_' + mech): i})
                                    else:
                                        # Maybe set values here to 0 instead of having NaN due to the jump in updating myionsdict
                                        continue """

            myionsdict.update({sl: myionsdict_temp})
  
        df = pd.DataFrame(myionsdict)     # 2D of Ionchannel Values per SectionList

        #print("INITIAL DATA: ")
        #print("\n")
        #print(df)
    
        self.ionchnames = list(df.index)
        x = fnc.convertDfTo1D(df)             # 1D array of Df , with Nans
        indices = fnc.getNans(x)
        x_nonan = fnc.removeNans(x)
    
        return x_nonan, indices


    def updateHOCParameters(self, x, indices):
        """
        updateHOCParameters() updates the instantiated HocObject cell, self.current_cell.

        Parameters
        ----------
        x : (Updated) parameters to be inserted into the currently active hocobject cell.
        indices : Indices to reinsert NaNs to keep the 2D sectionlist dimensions.
        """

        # updateHOCParameters - Sectionlist Specific! Every section inside a section has the same values (maybe distributed function in hoc still works)

        # could split into multiple functions to reassign the dataframe from 1D array to 2D with self.ionchnames which comes from SciPy - 
        # so I don't have to give self.ionchnames as additional argument for this function
        x = fnc.insertNans(x, indices)      # Give Nans back
        X = fnc.convert1DTo2DnpArr(x)       # Convert back to 2D array
        df = pd.DataFrame(X, index = self.sectionlist_list, columns = self.ionchnames).transpose()      # updated df # Reassign model-specific ordered ion channel names 
 
        for sl in self.sectionlist_list:   
            inputsl = getattr(self.current_cell, sl)
            for sec in inputsl:
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
                            """
                            ## implement exceptions for individually set channels here                     
                            if sl == "trunk" or sl == "apical":      # trunk parameters aren't part of the distribute_distance function
                                if str(sec).split(".", 1)[1] == "radTprox" \
                                    or str(sec).split(".", 1)[1] == "radTmed"  \
                                    or str(sec).split(".", 1)[1] == "radTdist":
                                    continue

                            elif str(sec).split(".", 1)[1] == "rad_t2":
                                continue
                            """                   
        # TODO build for 1-column "all" sectionlist with fixed indices
        """
        for sec in self.current_cell.all:
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
    
    def randomize_model_parameters(self, method = "log", bounds = None, seed = None):
        """
        Uses initialized model and randomizes every parameter
        """
        rng = np.random.default_rng(seed)

        for sl in self.sectionlist_list:   
            inputsl = getattr(self.current_cell, sl)
            for sec in inputsl:
                for ionchname in self.ionchnames:       # just make sure that my ionchnames are fitting, could probably also do assertions here
                    ionchnamekey = ionchname.split('_', 1)[1]
                    ionchnamekeykey = ionchname.split('_', 1)[0]
                    if ionchnamekey in sec.psection()['density_mechs'].keys() and ionchnamekeykey in sec.psection()['density_mechs'][ionchnamekey].keys():
                        if method is "log":
                            x = ((1/1e-7)**getattr(sec, ionchname)*1e-7)   # apply logarithm with upper and lower bound
                
                        elif method is "uniform":
                            x = rng.uniform(0, 1)         # norm lineal scale

               # print(sec.psection()['density_mechs'])

        # x[i] = rng.uniform(x[i]/1000, x[i]*1000)   # relative bounds to 10
        # x[i] = abs(rng.normal(0.001, 0.01))   # relative bounds, normal distribution
        # x[i] = x[i]  # test init data


    def blockIonChannel(self):
        """
        Block Ion Channel for Pharmacodynamics Testing - bandaid gbar to 0
        Some channels, depending on the nmodl file, can still influence the conductance,
        if they are interdependent with another channel
        see https://www.neuron.yale.edu/phpBB/viewtopic.php?t=4057
        """
        
        # short version
        if isinstance(self.channelblocknames, list):            # if multiple are given
            for element in self.channelblocknames: 
                for sl in self.sectionlist_list: 
                    inputsl = getattr(self.current_cell, sl) 
                    for sec in inputsl:
                        setattr(sec, element, 0)                # set to 0
        else:
            for sl in self.sectionlist_list:            
                inputsl = getattr(self.current_cell, sl)           
                for sec in inputsl:
                    setattr(sec, self.channelblocknames, 0)     # set to 0


if __name__ == "__main__":
    main()