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

import neuzy.paropt.auxiliaries.constants as cs
import neuzy.paropt.auxiliaries.functions as fnc

import numpy as np
import scipy.optimize as scp

class GenOpt():     ## TODO inheritance # TODO need for inheritance, how?
    """
    Takes Model inputs. Instantiation leads to 
    the selection of the optimization algorithm
    """
    def __init__(self):
        pass

class ScipyOpt(GenOpt):
    """
    Class for Scipy optimizer algorithm usage
    """
    def __init__(self, method:str = "Nelder-Mead", init_cost_threshold = 2, init_cost_optimizer_threshold = 5):
        """ 
        Constructor consisting of input vector x0 with the parameters to be optimized,
        indices to match them to their morphology and regions, bounds to 
        
        Parameters
        ----------
        - Method: str: Choose from: "L-BFGS-B", "Nelder-Mead" or "CG"
        - init_cost_threshold: int: Set lower threshold for model
        - init_cost_optimizer_threshold: int: Set threshold, below threshold for initial cost, model will be optimized.
        """
        super().__init__()
        self.init_cost_threshold = init_cost_threshold
        self.init_cost_optimizer_threshold = init_cost_optimizer_threshold
        self.method = method

    def callScipyNelderMead(self, x0, indices, sim, model, stim, par, calc): 
        # Scipy for Nelder-Mead
        minimum = scp.minimize( calc.calculateFitness, x0, 
                                    args=(indices, sim, model, stim, par), 
                                    bounds=[(0, 1) for i in range(len(x0))],
                                    method = self.method, 
                                    options={'xatol': 1e-6, 'maxiter': 1500, 'disp': True})     # xatol, fatol
        if minimum.fun <= self.init_cost_threshold:      # only save the data of the successful parameter combinations 
            return minimum.x, minimum.fun    # key = population index, value = tempdict; update result dictionary with one cell iteration dictionary per key
        return None, None

    def callScipyLBFGSB(self, x0, indices, sim, model, stim, par, calc, bounds):
        # stopper = callBackScipyTimeStopper() # timestopper
        # Scipy for L-BFGS-B
        minimum = scp.minimize( calc.calculateFitness, x0, 
                                    args=(indices, sim, model, stim, par), 
                                    bounds=[(0, 1) for i in range(len(x0))] ,   # bounds
                                    method = self.method, 
                                    options={'gtol': 1e-06, 'disp': True, 'maxiter': 300, 'eps': 1e-07})
                                    # callback = stopper.__call__(1))    # not longer than 1 minute for one cell

        if minimum.fun <= self.init_cost_threshold:         # only save the data of the successful parameter combinations
            return minimum.x, minimum.fun
        return None, None

    def callScipyCG(self, x0, indices, sim, model, stim, par, calc):
        # Scipy for CG
        minimum = scp.minimize( calc.calculateFitness, x0, 
                                args=(indices, sim, model, stim, par),
                                method = self.method, 
                                options={'disp': True, 'maxiter': 300, 'eps': 1e-4})

        if minimum.fun <= self.init_cost_threshold:          # only save the data of the successful parameter combinations
            return minimum.x, minimum.fun
        return None, None

    def execute(self):
        if self.method == 'L-BFGS-B':
            self.callScipyLBFGSB()

        elif self.method == 'CG':
            self.callScipyCG()

        elif self.method == 'Nelder-Mead': 
            self.callScipyNelderMead()


    def runOptimizer(self, init_data, init_rnd_data, rnd_data, init_cost, indices, calc, sim, model, stim, par):
        """ Calling the optimizer and using its output """
        #init_data2 = copy(init_data)        # init_data2 to test calculateFitness with initial data against no update with updateHOCParameters
        #print("INIT DATA:", init_data)  # tested, approved, no nans

        ## Initiate Random Data
        # init_rnd_data = fnc.randomizeAutoConductances(init_data)  # randomizing conductance parameters of ion channels 'gbar_*' from the cell
        #print("INIT RND DATA: ", init_rnd_data)
        # rnd_data = fnc.insertNans(init_rnd_data, indices)         # for output
        #print("INIT RND DATA: ", rnd_data)
        #print(type(rnd_data))     # <class 'numpy.ndarray'>

        """
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
        """
        
        # init_cost = calc.calculateFitness(init_rnd_data, indices)     # 100 is target feature atm

        ## extract some initial values with parameter combination
        """par_comb_df = pd.read_csv(PP_str + "/data.csv", dtype=np.float64)
        print(par_comb_df)
        par_comb = par_comb_df.to_numpy()
        par_comb = removeNans(par_comb[10])  
        print(par_comb) 
        init_cost = self.calculateFitness(par_comb, indices)     # use own data"""

        """if init_cost == 10000:
            return 1                                # int"""

        if init_cost <= self.init_cost_threshold:                    
            return rnd_data, init_cost              # tuple

        elif init_cost > self.init_cost_threshold and init_cost <= self.init_cost_optimizer_threshold:

            if self.method == 'L-BFGS-B':   #x0, indices, sim, model, stim, par, calc
                bounds = fnc.calculateBounds(init_rnd_data)
                x, fun = self.callScipyLBFGSB(init_rnd_data, indices, sim, model, stim, par, calc, bounds)     # only take the ones with output which fulfill the fitness function 
                if np.any(x) is not None and fun is not None:
                    x = fnc.insertNans(x, indices)    
                    return [x, rnd_data, fun]             # list
                else:
                    return 2

            elif self.method == 'CG':
                x, fun = self.callScipyCG(init_rnd_data, indices, sim, model, stim, par, calc)                 # only take the ones with output which fulfill the fitness function
                if np.any(x) is not None and fun is not None:
                    x = fnc.insertNans(x, indices)    
                    return [x, rnd_data, fun]             # list
                else:
                    return 2

            elif self.method == 'Nelder-Mead':                                    # https://docs.scipy.org/doc/scipy/reference/optimize.minimize-neldermead.html
                x, fun = self.callScipyNelderMead(init_rnd_data, indices, sim, model, stim, par, calc)         # only take the ones with output which fulfill the fitness function
                if np.any(x) is not None and fun is not None:
                    x = fnc.insertNans(x, indices)       # too many values to unpack, expected 2  
                    return [x, rnd_data, fun]             # list
                else:
                    return 2                                # int

        elif init_cost > self.init_cost_optimizer_threshold and init_cost != 10000:
            return 3


class DEAPOpt(GenOpt):
    """
    Choice for Evolutionary Algorithms, tbc
    """
    def __init__(self):
        super().__init__()
        pass