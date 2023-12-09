# ========================================================================
#
# SPDX-FileCopyrightText: 2023 Jakob Ratschenberger
# Johannes Kepler University, Institute for Integrated Circuits
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# SPDX-License-Identifier: Apache-2.0
# ========================================================================

import pandas as pd
import matplotlib.pyplot as plt
import glob

from pathlib import Path
import numpy as np

path = Path('./Logs')

csv_files = list(path.glob('*.csv'))

dataframes = {}

for file in csv_files:
    if file.name.endswith("_simanneal_log.csv"):
        dataframes[file.name[:-len("_simanneal_log.csv")]] = pd.read_csv(file, index_col=0)


for (k,v) in dataframes.items():
    fig, axes = plt.subplots(2,1, figsize=(12,4))
    fig.suptitle(k)
    it = list(v.index.values)
    step = np.array(v["step"])
    i_start = np.where(step==0)[0][-1]+1
    step = step[i_start:]
    energy = np.array(v["E"])
    energy = energy[i_start:]

    energy_avg = np.mean(np.reshape(energy, (energy.shape[0]//100, 100)),axis=1)
    energy_std = np.std(np.reshape(energy, (energy.shape[0]//100, 100)),axis=1)
    axes[0].plot(step, energy, color='k')
    axes[0].set_ylabel('Energy')
    axes[0].set_xlabel('Step')

    axes[1].plot(np.arange(1,energy_avg.shape[0]+1), energy_avg, color='k')
    axes[1].fill_between(np.arange(1,energy_avg.shape[0]+1), energy_avg-energy_std, energy_avg+energy_std, color='b', alpha=0.2)
    axes[1].set_ylabel('Average energy')
    plt.show()