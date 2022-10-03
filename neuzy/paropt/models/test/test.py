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

from neuzy.paropt.models.HocModel import HocModel as HN

hoc_1 = HN(
                        model_name = "Roe22.hoc",
                        modpath = None,
                        target_feature_file = "somatic_features_hippounit.json", #"somatic_target_features.json", 
                        template_name = "Roe22_reduced_CA1", 
                        hippo_bAP = True,
                        channelblocknames = None,               # Run it with CompleteOptModel
                        verbose = True
                        )

print(type(hoc_1))