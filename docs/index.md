# Neuzy

Neuzy is a neuroscientific software framework to create a population of optimized single cell, multi compartment models.

It uses HOC and NMODL files as input for the model and extracts automatically their respective ion channel parameters, which are to be updated.
Optimization options are currently Nelder-Mead, L-BFGS-B or Conjugate Gradient. 

Features to optimize are against somatic and backpropagating action potential features in depolarizing or hyperpolarizing potentials and depend on the given experimental data or baseline model.

Features are extracted via eFEL: https://github.com/BlueBrain/eFEL

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

Call any start file in the root of the repository.

```bash
python3 start.py
```
otherwise via bash
```bash
bash start.sh  
```

After calling, select how many CPU cores should be used in the command line.

---
## Output

Two folders will be created in /neuzy/paropt/data
1. log_files - Lists some logging information for the models created while optimizing
2. parameter_values - The optimized output parameters for your run. They have to be matched onto the pandas dataframe for regions and their respective ion channel.

---
## TODO's are partly the following:

- Licensing
- Documentation
- Improve code style and OO
- Accessibility for the general neuroscientist, i.e. less explicit source code configuration input for hyperparameters
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

---
## License
Neuzy - Population-based Neuron Modelling, Copyright (C) 2022 Adrian Röth

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
For details see the GNU General Public License and LICENSE.md in the root of the repository.
This is free software, and you are welcome to redistribute it
under certain conditions.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

---
## Help
The fastest way to receive support in case of problems is to open an issue on GitHub.

---
## Donate

Feel free to donate if you want to support me :)

<form action="https://www.paypal.com/donate" method="post" target="_top">
<input type="hidden" name="hosted_button_id" value="5Q5JDX5GB2UD4" />
<input type="image" src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif" border="0" name="submit" title="PayPal - The safer, easier way to pay online!" alt="Donate with PayPal button" />
<img alt="" border="0" src="https://www.paypal.com/en_DE/i/scr/pixel.gif" width="1" height="1" />
</form>

---