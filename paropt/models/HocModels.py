#### Neuzy

from Models import GenModel

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
                    target_feature_file = None, # in constants.py if not given
                    bap_target_file = None, 
                    hippo_bAP:bool = None,  
                    channelblocknames = None,   # has to be in the fullname format: "gkabar_kad" or "gbar_nax"  
                    hocpath = None,             # in constants.py if not given
                    sectionlist_list:list = None, 
                    template_name = None,       # from hoc begintemplate "template_name") 
                    parameterkeywords:list = None
                    ):
        super().__init__(   modpath = None,             # in constants.py if not given
                            target_feature_file = None, # in constants.py if not given
                            bap_target_file = None, 
                            hippo_bAP = None,  
                            channelblocknames = None  # has to be in the fullname format: "gkabar_kad" or "gbar_nax" 
                            )
        self.model_name = model_name
        if sectionlist_list:
            self.sectionlist_list = sectionlist_list
        else:
            self.sectionlist_list = SL_NAMES       # use constant

        if hocpath:
            self.hocpath = hocpath
        else:
            self.hocpath = HOCPATH          # use constant

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

    def getTemplateName(self):
        """
        Find the template name from hoc_string
        Note: this will fail if there is a begintemplate in a `/* */` style
        comment before the real begintemplate
        # Source: BluePyOpt
        """
        with open(HOCPATH + '/' + self.model_name) as hoc_file:
            hoc_string = hoc_file.read()
        for i, line in enumerate(hoc_string.split('\n')):
            if 'begintemplate' in line:
                line = line.strip().split()
                assert line[0] == 'begintemplate', \
                    'begintemplate must come first, line %d' % i
                self.template_name = line[1]
            else:
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

        self.mycell = self.createHocModel()      # Create cell "mycell" from template.

        if self.channelblocknames:               # Block ion channels, if set.
            self.blockIonChannel()

    def getSectionNames(self):
        """
        Returns
        -------
        df : Dataframe of sectionnames(row) to sectionlists (col)
        mysecnamelist : List of sectionnames(nested elements) inside sectionlists(elements)
        """
        mysecnamedict = {}
        try:
            if self.sectionlist_list:
                for sl in self.sectionlist_list:
                    inputsl = getattr(self.mycell, sl)
                    mysecnamelist = []
                    for sec in inputsl:
                        mysecnamelist.append(h.secname(sec = sec).split('.', 1)[1])     # maxsplit = 1 , take second element after '.'
                    mysecnamedict.update({sl: mysecnamelist})
                df = pd.DataFrame.from_dict(mysecnamedict, orient = 'index').transpose()
            else:
                # Use best practice "all" Sectionlist Keyword
                try:       
                    mysecnamelist = []
                    for sec in self.mycell.all:
                        mysecnamelist.append(h.secname(sec = sec).split('.', 1)[1])
                except Exception as e:
                    print("Seems like there is no best practice Sectionlist called: 'all', specified in your model.")
                    print("If you want to fix this problem, provide a SectionList for the program or add your sections to 'all' in your Hoc.")
                    print("E.g. all = new SectionList(); sectionname all.append()")
                    print(e)
        except Exception as e:
            print("Couldn't read in sectionlists")
            print("Please give your sectionlists as list or set the constant for self.sectionlist_list in ../auxiliaries/constants.py")
            print("The template_name for a cell shall not contain a '.' .")
            print(e)

        return df, mysecnamelist

    def getMechanismItems(self):
        """ Prerequisites: Read-in HocObject / HocObject in Scope 
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
            #print(mechname_list)
       
       # TODO code style
        if self.sectionlist_list:
            for sl in self.sectionlist_list:        
                inputsl = getattr(self.mycell, sl)
                myionsdict_temp = {}           
                for sec in inputsl:     
                    for mech in sec.psection()['density_mechs'].keys():                  
                        if mech in mechname_list:  # compare with mech to avoid errors of placeholder key/values from neuron api for a model
                            for ionchname, ionchvalue in sec.psection()['density_mechs'][mech].items():           
                                for parameterkeyword in self.parameterkeywords:
                                    if parameterkeyword in ionchname:          # check for "bar", "tau", "pas" or whatever you want !
                                        for i in ionchvalue:
                                            myionsdict_temp.update({str(ionchname + '_' + mech): ionchvalue[0]})

                                            # commented section was before blockIonChannel integration
                                            """if i != 0:                         # only check for gbars with a value                 
                                                # Have to save with appended sec.psection()['density_mechs'].keys() name (mech)
                                                myionsdict_temp.update({str(ionchname + '_' + mech): ionchvalue[0]})
                                                # myionsdict_temp.update({str(ionchname + '_' + mech): i})
                                            else:
                                                # Maybe set values here to 0 instead of having NaN due to the jump in updating myionsdict
                                                continue """
                                    else:
                                        continue        # do nothing and jump
                myionsdict.update({sl: myionsdict_temp})
        else:
        # TODO use "all" sectionlist
            print("ERROR: No Sectionlist")
            pass  
        
        df = pd.DataFrame(myionsdict)     # 2D of Ionchannel Values per SectionList  # Not used, but better keep it

        #print("INITIAL DATA: ")
        #print("\n")
        #print(df)
        
        self.ionchnames = list(df.index)
        x = convertDfTo1D(df)             # 1D array of Df , with Nans
        indices = getNans(x)
        x_nonan = removeNans(x)
    
        return x_nonan, indices


    def updateHOCParameters(self, x, indices):
        """
        updateHOCParameters() updates the instantiated HocObject cell, self.mycell.

        Parameters
        ----------
        x : (Updated) parameters to be inserted into the currently active hocobject cell.
        indices : Indices to reinsert NaNs to keep the 2D sectionlist dimensions.

        Returns
        -------
        void : Cell in scope gets updated but doesn't have to be returned.
        """

        # updateHOCParameters - Sectionlist Specific! Every section inside a section has the same values (maybe distributed function in hoc still works)

        # could split into multiple functions to reassign the dataframe from 1D array to 2D with self.ionchnames which comes from SciPy - 
        # so I don't have to give self.ionchnames as additional argument for this function
         
        x = insertNans(x, indices)      # Give Nans back
        X = convert1DTo2DnpArr(x)       # Convert back to 2D array
        df = pd.DataFrame(X, index = self.sectionlist_list, columns = self.ionchnames).transpose()      # updated df # Reassign model-specific ordered ion channel names 
        # print(df)
        if self.sectionlist_list:
            for sl in self.sectionlist_list:   
                inputsl = getattr(self.mycell, sl)
                for sec in inputsl: 
                    test1_dict = copy(sec.psection()['density_mechs'])
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
                                """## implement exceptions for individually set channels here                     
                                if sl == "trunk" or sl == "apical":      # trunk parameters aren't part of the distribute_distance function
                                   if str(sec).split(".", 1)[1] == "radTprox" \
                                        or str(sec).split(".", 1)[1] == "radTmed"  \
                                        or str(sec).split(".", 1)[1] == "radTdist":
                                        continue

                                elif str(sec).split(".", 1)[1] == "rad_t2":
                                    continue"""                   
                                
                            else:
                                continue
                        
                        else:
                            continue

        else:       
            print("No sectionlist names given in self.sectionlist_list")
            pass
            # TODO build for 1-column "all" sectionlist with fixed indices
            """
            for sec in self.mycell.all:
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
        print(df)

        def updateParAndModel(self, parameter_data, indices):
            if self.method == "CG":
                parameter_data = abs(parameter_data)    # especially for CG, don't make negative values possible for conductances. Negative "bar" values produce a NEURON error. 
                                                        # If you want to add e_pas to the parameters, you have to specify this line

            ## TODO , could intialize the first self.model_features after instantiating the cell, to check for spikes and then throw it overboard before even calculating the fitness

            self.updateAutoParameters(parameter_data, indices)                          # update "self.mycell" Cell with random values

            if self.AP_firstspike and self.bAP_firstspike:
                traces_per_stepamp, time_vec = self.stimulateIClamp()
                self.extractModelFeatures(traces_per_stepamp, time_vec)
                return True 
            else:
                if self.stimulateIClamp_firstspike():                           # if firstspike features
                    self.AP_firstspike = True
                    self.bAP_firstspike = True
                    traces_per_stepamp, time_vec = self.stimulateIClamp()       # starting full-fledged stimulation
                    self.extractModelFeatures(traces_per_stepamp, time_vec)     # extracting all features
                    return True
                else:
                    return