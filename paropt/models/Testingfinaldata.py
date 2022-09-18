import sys
sys.path.insert(1, './paropt/figures/')
sys.path.insert(1, './paropt/auxiliaries/')

from create_data import *
import numpy as np
import csv


class TestingCompleteModel():
    def __init__(self, path, line):
        with open (path) as f:
            reader = csv.reader(f)
            testdata = list(reader)[line - 1]         # select line
            testdata = [float(ele) for ele in testdata]
            testdata = np.array(testdata)
        # testdata = [float(ele) for ele in testdata]
        self.testdata = removeNans(testdata)

    def testData(self):
        # TODO
        paroptmodel.line = 1
        testingfinaldata = TestingCompleteModel("./paropt/datadump/parameter_values/best10_par.csv", line = paroptmodel.line)

        paroptmodel.run(populationsize, testing = False)   # testing flag if testingfinaldata is wanted or if it should proceed to random initialization

    def calcATP(self):
        pass

