#### Neuzy

class OptimizerC():     ## TODO inheritance
    """
    Class, which consists of all optimization techniques and instantiation leads to 
    the selection of the optimization technique used.
    """
    def __init__(self, x0, indices, method:str = "Nelder-Mead", bounds = False):
        """ constructor consisting of input vector x0 with the parameters to be optimized,
        indices to match them to their morphology and regions, bounds to """
        self.method = method    # Choose from: "L-BFGS-B", "Nelder-Mead" or "CG"
        self.x0 = x0
        self.indices = indices
        self.bounds = bounds

    def callScipyNelderMead(self): 
        # Scipy for Nelder-Mead
        minimum = scp.minimize( self.calculateFitness, self.x0, 
                                    args=(self.indices), 
                                    bounds=[(0, 1) for i in range(len(x0))],
                                    method = self.method, 
                                    options={'xatol': 1e-6, 'maxiter': 1500, 'disp': True})     # xatol, fatol
        if minimum.fun <= self.init_cost_threshold:      # only save the data of the successful parameter combinations 
            return minimum.x, minimum.fun    # key = population index, value = tempdict; update result dictionary with one cell iteration dictionary per key
        return None, None

    def callScipyLBFGSB(self):
        # stopper = callBackScipyTimeStopper() # timestopper
        # Scipy for L-BFGS-B
        minimum = scp.minimize( self.calculateFitness, self.x0, 
                                    args=(self.indices), 
                                    bounds=[(0, 1) for i in range(len(x0))] ,   # bounds
                                    method = self.method, 
                                    options={'gtol': 1e-06, 'disp': True, 'maxiter': 300, 'eps': 1e-07})
                                    # callback = stopper.__call__(1))    # not longer than 1 minute for one cell

        if minimum.fun <= self.init_cost_threshold:         # only save the data of the successful parameter combinations
            return minimum.x, minimum.fun
        return None, None

    def callScipyCG(self):
        # Scipy for CG
        minimum = scp.minimize( self.calculateFitness, self.x0, 
                                args=(self.indices),
                                method = self.method, 
                                options={'disp': True, 'maxiter': 300, 'eps': 1e-4})

        if minimum.fun <= self.init_cost_threshold:          # only save the data of the successful parameter combinations
            return minimum.x, minimum.fun
        return None, None

    def execute():
        if self.method == 'L-BFGS-B':
            self.callScipyLBFGSB()

        elif self.method == 'CG':
            self.callScipyCG()

        elif self.method == 'Nelder-Mead': 
            self.callScipyNelderMead()


    def runOptimizer(self, init_data, indices):
        """ Calling the optimizer and using its output """
        init_data2 = copy(init_data)        # init_data2 to test calculateFitness with initial data against no update with updateHOCParameters
        
        #print("INIT DATA:", init_data)  # tested, approved, no nans

        ## Initiate Random Data
        init_rnd_data = randomizeAutoConductances(init_data)  # randomizing conductance parameters of ion channels 'gbar_*' from the cell
        #print("INIT RND DATA: ", init_rnd_data)
        rnd_data = insertNans(init_rnd_data, indices)         # for output
        #print("INIT RND DATA: ", rnd_data)
        #print(type(rnd_data))     # <class 'numpy.ndarray'>

        ## test single outputs
        if self.testing is True:
            testdata = testingfinaldata.testdata
            #testdata = testSingleOutputs(PP_str + "../data/parameter_values/best10_par.csv")
            init_cost = self.calculateFitness(testdata, indices)    # indices stay the same for one model and could be an object property but not now xD
            print("\n")
            print("INITIAL COST FOR TESTING DATA DUE TO TESTING FLAG == TRUE:")
            print(init_cost)
            print("\n")
        else:
            init_cost = self.calculateFitness(init_rnd_data, indices)     # 100 is target feature atm


        ## extract some initial values with parameter combination
        """par_comb_df = pd.read_csv(PP_str + "/data.csv", dtype=np.float64)
        print(par_comb_df)
        par_comb = par_comb_df.to_numpy()
        par_comb = removeNans(par_comb[10])  
        print(par_comb) 
        init_cost = self.calculateFitness(par_comb, indices)     # use own data"""

        if init_cost == 10000:
            return 1                                # int

        elif init_cost <= self.init_cost_threshold:                    
            return rnd_data, init_cost              # tuple

        elif init_cost > self.init_cost_threshold and init_cost <= self.init_cost_optimizer_threshold:
            
            optimiz = OptimizerC(x0 = init_rnd_data, indices = indices, method = self.method)

            if self.method == 'L-BFGS-B':
                bounds = calculateBounds(init_rnd_data)
                x, fun = self.callScipyLBFGSB(init_rnd_data, indices, bounds)     # only take the ones with output which fulfill the fitness function 
                if np.any(x) is not None and fun is not None:
                    x = insertNans(x, indices)    
                    return [x, rnd_data, fun]             # list
                else:
                    return 2

            elif self.method == 'CG':
                x, fun = self.callScipyCG(init_rnd_data, indices)                 # only take the ones with output which fulfill the fitness function
                if np.any(x) is not None and fun is not None:
                    x = insertNans(x, indices)    
                    return [x, rnd_data, fun]             # list
                else:
                    return 2

            elif self.method == 'Nelder-Mead':                                    # https://docs.scipy.org/doc/scipy/reference/optimize.minimize-neldermead.html
                x, fun = self.callScipyNelderMead(init_rnd_data, indices)         # only take the ones with output which fulfill the fitness function
                if np.any(x) is not None and fun is not None:
                    x = insertNans(x, indices)       # too many values to unpack, expected 2  
                    return [x, rnd_data, fun]             # list
                else:
                    return 2                                # int

        elif init_cost > self.init_cost_optimizer_threshold and init_cost != 10000:
            return 3                         