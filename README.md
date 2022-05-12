# Neuzy

Neuzy is a neuroscientific software framework to create a population of optimized single cell models.
Optimization options are currently against somatic and backpropagating action potential features.

Under the hood it is using the NEURON simulator: https://github.com/neuronsimulator/nrn

It offers the extension to evaluate the output for hippocampal CA1 cells with HippoUnit framework: https://github.com/KaliLab/hippounit

Original model, which was used is from Tomko et al. 2021 https://senselab.med.yale.edu/ModelDB/showmodel.cshtml?model=266901&file=/TomkoEtAl2021/#tabs-2

TODO's are partly the following:

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
    - machine learning techniques
  - Glia influence
    - simulate neurotransmitter density in extracellular space
  - ...
- ...


Soon available on https://neuzy.de