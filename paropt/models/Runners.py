#### Neuzy

## Runners concatenates input and runs the system

class Runner():
    def __init__(self):
        pass
    
    @classmethod
    def run(self):
        pass
    

    def finalParameters(self, x):
        """
        Get the final parameter output???
        """
        # finalParameters - Sectionlist Specific! Every section inside a section has the same values (maybe distributed function in hoc still works)
        # No nan value inserting here, they come out with nan values due to position-based updating of the values in a dataframe, see below or in updateHOCParameters()
        
        # Convert back to 2D array
        X = convert1DTo2DnpArr(x[5])        # just testing for the first combination of values
        df = pd.DataFrame(X, index = self.sectionlist_list, columns = self.ionchnames).transpose()      # updated df # Reassign model-specific ordered ion channel names
        #print(df)  # tested, prints with nans
        self.ionchnames = list(df.index)  # redundant, but anyway who tf cares
        if self.sectionlist_list:
            for sl in self.sectionlist_list:
                inputsl = getattr(self.mycell, sl)
                for sec in inputsl:        
                    for ionchname in self.ionchnames:
                        ionchnamekey = ionchname.split('_', 1)[1]
                        ionchnamekeykey = ionchname.split('_', 1)[0]
                        if ionchnamekey in sec.psection()['density_mechs'].keys():
                            if ionchnamekeykey in sec.psection()['density_mechs'][ionchnamekey].keys():
                                setattr(sec, ionchname, df.loc[ionchname, sl]) 
                            else:
                                continue
        else:
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
        # return self.mycell