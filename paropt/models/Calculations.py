#### Neuzy


class GenCalc():
    """
    Class for Fitness Calculations

    Parameters
    ----------
    hocmodel: Object of HOCModel
    pymodel: object of PyModel
    """
    def __init__(self, hocmodel, pymodel):
        #
        # placeholder for calculation variables if needed in extension
        #
        pass

    def calculateFitness(self, parameter_data, indices):  
        # print("test: ", parameter_data)
        if self.updateParAndModel(parameter_data, indices) is None:
            print("No spiking, aborting on rank, " + str(self.rank))  
            lg.info("No spiking, aborting on rank, " + str(self.rank))
            return 10000
        else:
            pass

        ## To iterate over all values, create one big dic out of both dictionaries ### unused hahah :D
        self.features = {}
        self.features['Target'] = self.target_features
        self.features['Model'] = self.model_features


        fitness_values_names = []
        fitness_values = []
        fitness_values_dict = {}

    def sampleRecAround(    self, 
                            output_array, 
                            out_fun, 
                            indices, 
                            multiplier = 1.05, 
                            counter = 0,
                            maxcounter = 0, 
                            maxresults = 50,
                            maxiter = 5000):

        """ Function to sample recursively around till there is no more better result than the last best result
        Parameters
        ----------
        output_array : np.array of parameters with NaNs
        out_fun      : Calculated cost for the optimized or sufficient parameter combination
        multiplier   : Multiplier relative to parameter values. Bounds are multiplied and divided by Multiplier
        counter      : Recursive Startcounter for successful iterations, should be 0 or adapted with respect to maxresults.
        maxcounter   : Recursive Startcounter for all iterations, should be 0 or adapted with respect to maxiter.
        maxresults   : Recursive Result Endcounter.
        maxiter      : Recursive Iteration Endcounter.

        # TODO  Grant additionally the counter option for unsuccessful iterations? Then with flag though, which option should terminate.
        # Known Bugs: Hoc model NMODL files aren't created for populations, so it can happen that some values are over a specific buffer and it raises the scopmath library error in NEURON.

        Returns
        -------
        Writes to file and returns None when maximum of recursive results is reached.
        """
        
        if counter < maxresults and maxcounter < maxiter:  # sample XX times around and check if costs become better
            ## use result for more results
            try:     
                sample_array = sampleResultsAround(output_array, multiplier = multiplier)
                sample_array_nonan = removeNans(sample_array)
                ## TODO abortion because of NEURON scopmath library error, convergence not achieved ... this API
                # so it has problems to overwrite itself every time and instead should be a reinitialized cell
                sample_fun = self.calculateFitness(sample_array_nonan, indices)
                
                if sample_fun < out_fun:
                    counter = counter + 1
                    maxcounter = maxcounter + 1

                    print("Sample is better than original output combination, saving sample")
                    lg.info("Sample is better than original output combination, saving sample")
                    
                    with open(self.sample_output_csv_fun_data, "a") as f:
                        print(sample_fun, end='\n', file=f)                 # *sample_fun

                    #sample_array = insertNans(sample_array, indices)
                    sample_output_list = sample_array.tolist()
                    with open(self.sample_output_csv_par_data, "a") as f:
                        print(*sample_output_list, sep=',', end='\n', file=f)
                    
                    ## Try even more but set limit to 100 times of recursion
                    print("Trying to find more samples based on the successful sample on iteration " + str(maxcounter) + " with " + str(counter) + " results already")
                    lg.info("Trying to find more samples based on the successful sample on iteration " + str(maxcounter) + " with " + str(counter) + " results already")
                    self.sampleRecAround(sample_array, sample_fun, indices, counter = counter, maxcounter = maxcounter)

                ## Recursion - try till it gets better than out_fun
                else:
                    maxcounter = maxcounter + 1
                    print("Sample is not better, sampling again with input values on iteration " + str(maxcounter) + " with " + str(counter) + " results already")
                    lg.info("Sample is not better, sampling again with input values on iteration " + str(maxcounter) + " with " + str(counter) + " results already")
                    self.sampleRecAround(output_array, out_fun, indices, counter = counter, maxcounter = maxcounter)  
            except Exception as e:
                # Hoc Errors... scopmath .... I DON'T KNOW WHY
                print("Exception caught: ", e ," reinitializing with inital values")
                lg.info("Exception caught, reinitializing with initial values")
                self.deleteCell()
                self.initializeCell()
                maxcounter = maxcounter + 1
                self.sampleRecAround(output_array, out_fun, indices, counter = counter, maxcounter = maxcounter)
        else:
            print("Sampling process completed.")
            lg.info("Sampling process completed.")

            # Saving the best results separately
            with open(self.sample_best_output_csv_fun_data, "a") as f:
                    print(out_fun, end='\n', file=f)                 # *sample_fun

            sample_best_output_par_list = output_array.tolist()
            with open(self.sample_best_output_csv_par_data, "a") as f:
                    print(*sample_best_output_par_list, sep=',', end='\n', file=f)

            return

class FitnessCalcSD(GenCalc()):         # calculate Fitness with SD in denominator
    """
    Child class of GenCalc, 
    calculating fitness with averaging feature values 
    in terms of standard deviation.
    """
    def __init__(self, hocmodel, pymodel):
        super().__init__(hocmodel, pymodel)

        ## TODO
        """
        ## Based on model_feature_dict 
        for locationkey, locationvalues in self.model_features.items():         # using model_features in case you want to change the step amp protocol in self.stepamps
            #if locationkey == 'Soma':                                          # test only somatic features
            for stepamp, stepampvalues in locationvalues.items():
                for feature_name, featurevalues in stepampvalues.items():
                    if featurevalues['Mean'] is None:
                        continue
                    elif featurevalues['Mean'] is not None:
                        # numpy.core._exceptions.UFuncTypeError: ufunc 'subtract' did not contain a loop with signature matching types (dtype('<U32'), dtype('<U32')) -> dtype('<U32')                                                       
                        feature_fitness = (np.abs(float(featurevalues['Mean'] - float(self.target_features[locationkey][stepamp][feature_name]['Mean']))) \
                                            /float(self.target_features[locationkey][stepamp][feature_name]['Std']))
                        # TODO prove that this change for model_features instead of target_features works                
                        print(feature_name, " : ", featurevalues['Mean'], " blabla", self.target_features[locationkey][stepamp][feature_name]['Mean'] ," \
                            standard deviation: ", self.target_features[locationkey][stepamp][feature_name]['Std'])

                        fitness_values_names.append(feature_name + " fitness value: ")
                        fitness_values.append(feature_fitness)
                        df = pd.DataFrame(fitness_values, index = fitness_values_names)
                        fitness_values_dict.update({feature_name : feature_fitness})
        """
        ## Based on target_feature_dict 
        for locationkey, locationvalues in self.target_features.items():         # using model_features in case you want to change the step amp protocol in self.stepamps
            #if locationkey == 'Soma':                                          # test only somatic features
            for stepamp, stepampvalues in locationvalues.items():
                for feature_name, featurevalues in stepampvalues.items():
                    if stepamp in self.stepamps.keys():
                        if self.model_features[locationkey][stepamp][feature_name]['Mean'] is None or self.model_features[locationkey][stepamp][feature_name]['Mean'] is False:
                            fitness_values_names.append(feature_name + " fitness ")
                            feature_fitness = 1000
                            fitness_values.append(feature_fitness)

                        elif featurevalues['Mean'] and self.model_features[locationkey][stepamp][feature_name]['Mean']:
                            # numpy.core._exceptions.UFuncTypeError: ufunc 'subtract' did not contain a loop with signature matching types (dtype('<U32'), dtype('<U32')) -> dtype('<U32')   
                            #print("1", self.model_features[locationkey][stepamp][feature_name]['Mean'], bool(self.model_features[locationkey][stepamp][feature_name]['Mean']))
                            #print("2", float(featurevalues['Mean']), bool(float(featurevalues['Mean'])))                                                    
                            feature_fitness = (np.abs(float(self.model_features[locationkey][stepamp][feature_name]['Mean']) - float(featurevalues['Mean'])) \
                                                /float(featurevalues['Std']))
                            # TODO prove that this change for model_features instead of target_features works                
                            #print(feature_name, " : ", self.model_features[locationkey][stepamp][feature_name]['Mean'] , " blabla", featurevalues['Mean'] ," \
                            #    standard deviation: ", self.target_features[locationkey][stepamp][feature_name]['Std'])

                            fitness_values_names.append(feature_name)    # add label suffix like feature_name + " fitness" or + " cost" if wanted
                            fitness_values.append(feature_fitness)

                        fitness_values_dict.update({feature_name : feature_fitness})
                    else:
                        #print(stepamp, " was not in Model Features and got skipped")
                        pass
        ## Outputs for testing
        # print("Fitness values are:")
        pd.set_option("display.max_rows", None, "display.max_columns", None)
        df = pd.DataFrame(fitness_values, index = fitness_values_names)

        # inline
        print(df)           

        # csv
        # df.to_csv("./paropt/data/parameter_values//dataframe_costs/dataframe_output_model_" + str(self.line) + ".csv")

        # print("Fitness values are: ", fitness_values_dict, "on rank " + str(self.rank))
        print("Cost is: ", max(fitness_values), " on rank " + str(self.rank))
        lg.info("Cost is " + str(max(fitness_values)) + "on rank " + str(self.rank))

        # maximum fitness value # TODO print only in verbose mode... get them flags
        print(df.idxmax())      # max(fitness_values) feature_name

        return max(fitness_values)
    