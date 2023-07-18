![GitHub top language](https://img.shields.io/github/languages/top/fanantenana-dev/neuzy.svg?style=for-the-badge)
![GitHub license](https://img.shields.io/github/license/fanantenana-dev/neuzy.svg?style=for-the-badge)
![GitHub repo size](https://img.shields.io/github/repo-size/fanantenana-dev/neuzy.svg?style=for-the-badge)

# Neuzy

Neuzy (https://neuzy.de) is a neuroscientific software framework to create a population of optimized single cell, multi compartment models.

It uses HOC and NMODL files as input for the model and extracts automatically their respective ion channel parameters, which are to be updated.
Optimization options are currently Nelder-Mead, L-BFGS-B or Conjugate Gradient. 

Features to optimize are against somatic and backpropagating action potential features in depolarizing or hyperpolarizing currents and depend on the given experimental data or baseline model.

Features are extracted via eFEL: https://github.com/BlueBrain/eFEL

Under the hood it is using the NEURON simulator: https://github.com/neuronsimulator/nrn

It offers the extension to evaluate the output for hippocampal CA1 cells with HippoUnit framework: https://github.com/KaliLab/hippounit

Original model, which was used is from Tomko et al. 2021 https://senselab.med.yale.edu/ModelDB/showmodel.cshtml?model=266901&file=/TomkoEtAl2021/#tabs-2

---

## Prerequisites

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

## Quickstart
After downloading call any start file in the root of the neuzy folder.

```bash
python3 ./neuzy/quickstart.py
```
otherwise via bash
```bash
bash ./neuzy/quickstart.sh 
```

Calling it from the root sets your PYTHONPATH automatically to the root of the repository.

After calling, select how many CPU cores should be used in the command line.

## Install
With pyproject.toml, there is also the option to install it as package with pip from the root of the repository.
In later versions it will be available on pypi.org.

```
pip install .
```

If you do not install it this way, and instead use it neither by installing it, nor by using it from the root of the repository 
(see above, sets PYTHONPATH automatically), then make sure to set or add (to ~/.bashrc) your $PYTHONPATH manually to the repository's rootpath.
This is necessary to avoid pathing errors within the repository's call structure.

```
export PYTHONPATH=/home/username/directory/Neuzy/
```

---
## Output

Two folders will be created in /neuzy/paropt/data
1. log_files - Lists some logging information for the models created while optimizing
2. parameter_values - The optimized output parameters for your run. They have to be matched onto the pandas dataframe for regions and their respective ion channel.

---
## Pipeline
![Pipeline](./docs/figures/Pipeline.pdf)

![Implementation](./docs/figures/Implementation.pdf)

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

Update: No more support or updates due to Long Covid

