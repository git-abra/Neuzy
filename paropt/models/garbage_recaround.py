#############################################################################
#############################################################################
## The following hopefully circumvents NEURON scopmath library error and is an alternative for "sampleRecAround()" above
## it didn't , see important_scopmath_error.txx
"""
fun_list = []
sample_array_list = []
counterfor = 0
print("Starting sampling process of 1000 iterations")
lg.info("Starting sampling process of 1000 iterations")
for i in range(1000):    # sample 1000 times around and check if costs become better          
    try: 
        if fun_list: # and min(fun_list) < out_fun:
            j = fun_list.index(min(fun_list))
            arr = sample_array_list[j]
            sample_array = sampleResultsAround(arr, multiplier = 2)        
            sample_array_nonan = removeNans(sample_array)
            sample_fun = self.calculateFitness(sample_array_nonan, indices)   
            
            if sample_fun < min(fun_list):
                counterfor = counterfor + 1
                print("Sample is better than best sampled combination, saving new sample")
                lg.info("Sample is better than best sampled combination, saving new sample")
                fun_list.append(sample_fun)
                
                with open(self.sample_output_csv_fun_data, "a") as f:
                    print(sample_fun, end='\n', file=f)

                sample_array_list.append(sample_array)
                sample_output_list = sample_array.tolist()                   
                with open(self.sample_output_csv_par_data, "a") as f:
                    print(*sample_output_list, sep=',', end='\n', file=f)

                print("Trying to find more samples based on the successful sample on iteration " + str(i) + " with " + str(counterfor) + " results already")
                lg.info("Trying to find more samples based on the successful sample on iteration " + str(i) + " with " + str(counterfor) + " results already")                              
            else:
                print("Sample is not better, sampling again with input values on iteration " + str(i) + " with " + str(counterfor) + " results already")
                lg.info("Sample is not better, sampling again with input values on iteration " + str(i) + " with " + str(counterfor) + " results already")
                continue                            
        else:
            sample_array = sampleResultsAround(output_array, multiplier = 2)
            sample_array_nonan = removeNans(sample_array)
            sample_fun = self.calculateFitness(sample_array_nonan, indices)

            if sample_fun < out_fun:
                counterfor = counterfor + 1
                print("Sample is better than original output combination, saving sample")
                lg.info("Sample is better than original output combination, saving sample")
                fun_list.append(sample_fun)
                
                with open(self.sample_output_csv_fun_data, "a") as f:
                    print(sample_fun, end='\n', file=f)                 # *sample_fun

                sample_array_list.append(sample_array)
                sample_output_list = sample_array.tolist()                   
                with open(self.sample_output_csv_par_data, "a") as f:
                    print(*sample_output_list, sep=',', end='\n', file=f)      
                print("Trying to find more samples based on the successful sample on iteration " + str(i) + " with " + str(counterfor) + " results already")
                lg.info("Trying to find more samples based on the successful sample on iteration " + str(i) + " with " + str(counterfor) + " results already")            
            else:
                print("Sample is not better, sampling again with input values on iteration " + str(i) + " with " + str(counterfor) + " results already")
                lg.info("Sample is not better, sampling again with input values on iteration " + str(i) + " with " + str(counterfor) + " results already")
                continue 
    except Exception as e:
        # Hoc Errors... scopmath .... I DON'T KNOW WHY
        print("Exception caught: ", e ," reinitializing with inital values")
        lg.info("Exception caught, reinitializing with initial values")
        self.deleteCell()
        self.initializeCell()
        continue

print("Sampling process (as for loop, not as recursion) completed.")
lg.info("Sampling process (as for loop, not as recursion) completed.")
"""
                ################################################################################