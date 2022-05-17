import sys
sys.path.insert(1, './paropt/figures/')
sys.path.insert(1, './paropt/auxiliaries/')

from create_data import *
import numpy as np
import csv


class TestingFinalData():
    def __init__(self, path, line):
        with open (path) as f:
            reader = csv.reader(f)
            testdata = list(reader)[line - 1]         # select line
            testdata = [float(ele) for ele in testdata]
            testdata = np.array(testdata)
        # testdata = [float(ele) for ele in testdata]
        self.testdata = removeNans(testdata)

    def calcATP(self):
        pass

