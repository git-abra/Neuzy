#### Neuzy

# ModelLoader_parameters as inherited ModelLoader child class to be in sync with Neuzy 's ion channel parameter update

import sys, pathlib, numpy, json

PP = pathlib.Path(__file__).parent # parent path on directory

sys.path.insert(1, str(PP / '..' / 'paropt' / 'auxiliaries'))
sys.path.insert(1, str(PP / '..' / 'paropt' / 'models'))

import pandas as pd
from quantities import ms,mV,Hz
from neuron import h

from hippounit.utils import ModelLoader


class ModelLoader_parameters(ModelLoader):
    # TODO import functions from paropt/models classes
    def __init__(self, name = "model", mod_files_path = None):
        """ Constructor. """
        """ This class should be used with Jupyter notebooks"""
        super(ModelLoader_parameters, self).__init__(name=name, mod_files_path=mod_files_path)

        # self.parameters = self.readJSON(parameter_path)    # give Input from file
        self.parameters = None
        self.parameterkeywords = ['bar']
        self.sectionlist_list = None 

    # either set parameter_path here or use it as input in __init__, it doesn't matter
    def readJSON(self, parameter_path = None):
        with open(parameter_path, 'r') as f:
            content = json.load(f)
            return content

    def convert1DTo2DnpArr(self):
        skip = int(len(self.parameters)/len(self.sectionlist_list))
        cols = int(len(self.sectionlist_list))
        X = numpy.reshape(self.parameters, (cols, skip), order = 'F')
        return X

    def getMechanismItems(self):
        myionsdict = {}
        mechname_list = []

        mt = h.MechanismType(0)
        mname = h.ref('')
        
        for i in range(mt.count()):
            mt.select(i)
            mt.selected(mname)
            mechname_list.append(mname[0])

        for sl in self.sectionlist_list:
            inputsl = getattr(h.testcell, sl)
            myionsdict_temp = {}
            for sec in inputsl:
                for mech in sec.psection()['density_mechs'].keys():              
                    if mech in mechname_list:
                        for ionchname, ionchvalue in sec.psection()['density_mechs'][mech].items():
                            for parameterkeyword in self.parameterkeywords:
                                if parameterkeyword in ionchname:          # check for parameterkeywords: "bar", "tau" or whatever you want
                                    for i in ionchvalue:
                                        if i != 0:                         # only check for g-parameterkeyword with a value                 
                                            # Have to save with appended sec.psection()['density_mechs'].keys() name (mech)
                                            myionsdict_temp.update({str(ionchname + '_' + mech): ionchvalue[0]})
                                        else:
                                            # Maybe set values here to 0 instead of having NaN due to the jump in updating myionsdict
                                            continue 
                                else:
                                    continue        # do nothing and jump
            myionsdict.update({sl: myionsdict_temp})
        
        df = pd.DataFrame(myionsdict)       # 2D of Ionchannel Values per SectionList  # Not used, but better keep it

        self.ionchnames = list(df.index)

    def setParameters(self):              
        X = self.convert1DTo2DnpArr()       # 1D to 2D
        self.getMechanismItems()            # retrieve self.ionchnames
        # Dataframe as Input with the following structure: df[ionchnames, sectionlistnames]
        df = pd.DataFrame(X, index = self.sectionlist_list, columns = self.ionchnames).transpose()
        print(df)
        #print(dir(h.testcell))
        for sl in self.sectionlist_list:
            inputsl = getattr(h.testcell, sl)
            for sec in inputsl:
                for ionchname in self.ionchnames:
                    ionchnamekey = ionchname.split('_', 1)[1]
                    ionchnamekeykey = ionchname.split('_', 1)[0]
                    if ionchnamekey in sec.psection()['density_mechs'].keys():
                        if ionchnamekeykey in sec.psection()['density_mechs'][ionchnamekey].keys():
                            if df.loc[ionchname, sl]:

                                update = float(df.loc[ionchname, sl])
                                setattr(sec, ionchname, update)

                                if ionchnamekey == "hd" and ionchnamekeykey == "ghdbar" or ionchname == "ghdbar_hd":     # just listed everything in or :D:D:D
                                    value = copy(sec.ghdbar_hd)
                                    for seg in sec:
                                        dist = h.distance(seg.x, sec=sec)      
                                        if dist == 0:
                                            continue
                                        else:                                
                                            seg.hd.ghdbar = (1 + 3/100 * dist) * value # 1.9042409723832741e-05

                                    # else they change over distance again and don't stay on their <random> value
                                if ionchnamekey == "kad" and ionchnamekeykey == "gkabar" or ionchname == "gkabar_kad":
                                    value = copy(sec.gkabar_kad)
                                    for seg in sec:
                                        dist = h.distance(seg.x, sec=sec)                  
                                        seg.kad.gkabar = (15/(1 + numpy.exp((300-dist)/50))) * value # 0.012921529390557651
                        else:
                            print("Something went wrong")

    def initialise(self):

        self.load_mod_files()

        if self.hocpath is None:
            raise Exception("Please give the path to the hoc file (eg. model.modelpath = \"/home/models/CA1_pyr/CA1_pyr_model.hoc\")")

        h.load_file("stdrun.hoc")
        h.load_file(self.hocpath)

        if self.soma is None and self.SomaSecList_name is None:
            raise Exception("Please give the name of the soma (eg. model.soma=\"soma[0]\"), or the name of the somatic section list (eg. model.SomaSecList_name=\"somatic\")")
        try:  
            if self.template_name is not None and self.SomaSecList_name is not None:

                h('objref testcell')
                h('testcell = new ' + self.template_name)

                exec('self.soma_ = h.testcell.'+ self.SomaSecList_name)

                for s in self.soma_ :
                    self.soma = h.secname()

            elif self.template_name is not None and self.SomaSecList_name is None:
                h('objref testcell')
                h('testcell = new ' + self.template_name)
                # in this case self.soma is set in the jupyter notebook

            elif self.template_name is None and self.SomaSecList_name is not None:
                exec('self.soma_ = h.' +  self.SomaSecList_name)
                for s in self.soma_:
                    self.soma = h.secname()
            # if both is None, the model is loaded, self.soma will be used
        except AttributeError:
            print ("The provided model template is not accurate. Please verify!")
        except Exception:
            print ("If a model template is used, please give the name of the template to be instantiated (with parameters, if any). Eg. model.template_name=CCell(\"morph_path\")")
            raise
        
        self.setParameters()






        ## Manual way, if iterating won't work, just set them per index on setParameters():

        """x = [float(i) for i in self.parameters]
        print(x)
        print(type(x[0]))
        for sec in h.testcell.somatic:
            sec.gbar_cagk = x[0]
            sec.gcalbar_cal = x[5]
            sec.gcanbar_can = x[10]
            sec.gcatbar_cat = x[15]
            sec.ghdbar_hd = x[20]
            sec.gkabar_kap = x[25]
            sec.gbar_kca = x[30]
            sec.gkdrbar_kdr = x[35]
            sec.gbar_kmb = x[40]
            sec.gbar_nax = x[45]
            
        for sec in h.testcell.axonal:
            sec.gkabar_kap = x[26]
            sec.gkdrbar_kdr = x[36]
            sec.gbar_kmb = x[41]
            sec.gbar_nax = x[46]
            
        for sec in h.testcell.apical:
            sec.gbar_cagk = x[2]
            sec.gcalbar_cal = x[7]
            sec.gcanbar_can = x[12]
            sec.gcatbar_cat = x[17]
            sec.ghdbar_hd = x[22]
            sec.gbar_kca = x[32]
            sec.gkdrbar_kdr = x[37]
            sec.gbar_nax = x[47]
            sec.gkabar_kad = x[52]

        for sec in h.testcell.basal:
            sec.gbar_cagk = x[3]
            sec.gcalbar_cal = x[8]
            sec.gcanbar_can = x[13]
            sec.gcatbar_cat = x[18]
            sec.ghdbar_hd = x[23]
            sec.gbar_kca = x[33]
            sec.gkdrbar_kdr = x[38]
            sec.gbar_nax = x[48]
            sec.gkabar_kad = x[53]        

        for sec in h.testcell.trunk:
            sec.gbar_cagk = x[4]
            sec.gcalbar_cal = x[9]
            sec.gcanbar_can = x[14]
            sec.gcatbar_cat = x[19]
            sec.ghdbar_hd = x[24]
            sec.gbar_kca = x[34]
            sec.gkdrbar_kdr = x[39]
            sec.gbar_nax = x[49]
            sec.gkabar_kad = x[54]"""