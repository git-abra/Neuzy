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

## Model created in Python, without HOC as input.
# Basically needs a lot of input or preformatted data to read-in, will see

import neuzy.paropt.models.GenModel as GenModel

class PyModel(GenModel):
    """ 
    Inherits from GenModel.
    PyModel to create a NEURON model in Python 
    """
    def __init__(   self, 
                    model_name, 
                    modpath = None,             # in constants.py if not given
                    target_feature_file = None, # in constants.py if not given
                    bap_target_file = None, 
                    hippo_bAP = None,  
                    channelblocknames = None  # has to be in the fullname format: "gkabar_kad" or "gbar_nax"  (for the start, i couldve solved it differently, but pressure in the back)
                    ):
        super().__init__(   model_name, 
                            modpath = None,             # in constants.py if not given
                            target_feature_file = None, # in constants.py if not given
                            bap_target_file = None, 
                            hippo_bAP = None,  
                            channelblocknames = None # has to be in the fullname format: "gkabar_kad" or "gbar_nax"  (for the start, i couldve solved it differently, but pressure in the back))
                            )
        pass