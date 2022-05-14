# Neuzy

Neuzy is a neuroscientific software framework to create a population of optimized single cell models.
Optimization options are currently against somatic and backpropagating action potential features.

Under the hood it is using the NEURON simulator: https://github.com/neuronsimulator/nrn

It offers the extension to evaluate the output for hippocampal CA1 cells with HippoUnit framework: https://github.com/KaliLab/hippounit

Original model, which was used is from Tomko et al. 2021 https://senselab.med.yale.edu/ModelDB/showmodel.cshtml?model=266901&file=/TomkoEtAl2021/#tabs-2

---

## Prerequisites:

HOC file for the morphology and biophysics.
NMODL files for the ion channel expressions.
Target Features, currently only in JSON - see target_features folder.

Python3 with following packages installed (recommended via pip):
  - Neuron
  - Efel
  - Numpy
  - Scipy
  - Pandas
  - Mpi4py

To also evaluate the population:
  - Hippounit

Edit the constants in /neuzy/paropt/auxiliaries/constants.py.
Further configuration (hyperparameters) needs to change the CompleteOptModel class in CompleteOptModel.py.
Accessibility is on the TODO.

---

## Quickstart:

Start from the relative path in the downloaded ./neuzy repository (Root of the repository).

Call any start file.
```bash
python3 start.py
```
otherwise via bash
```bash
bash start.sh  
```
or shell
```
sh start.sh
```

After calling, select how many CPU cores should be used in the command line.

---
## Output

Two folders will be created in /neuzy/paropt/datadump.
1. log_files - Lists some logging information for the models created while optimizing
2. parameter_values - The optimized output parameters for your run. They have to be matched onto the pandas dataframe for regions and their respective ion channel.

---
### TODO's are partly the following:

- Licensing
- Documentation
- Improve code style
- Accessibility for the general neuroscientist
- Offer the option to test for multiple kinds of cell optimization, i.e. more features
- Extend for:
  - Efficiency
    - e.g. dynamic programming
    - improvements to mpi usage
    - techniques
  - Synaptic features and testing
    - dendritic integration
  - More than CA1
    - region is limited by experimental data, not by the software
  - Network modelling
    - various cell numbers in conjunction
    - machine learning for neural networks
  - Glia influence
    - simulate neurotransmitter density in extracellular space
  - ...
- ...


### Documentation soon on https://neuzy.de
