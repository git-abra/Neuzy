#### Neuzy

class OptimizerC():
    """
    Class, which consists of all optimization techniques and instantiation leads to 
    the selection of the optimization technique used.
    """
    def __init__(self, x0, indices, method = "Nelder-Mead", bounds = False):
        """ constructor consisting of input vector x0 with the parameters to be optimized,
        indices to match them to their morphology and regions, bounds to """
        self.method = method
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