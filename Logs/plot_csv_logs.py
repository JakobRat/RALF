import pandas as pd
import matplotlib.pyplot as plt
import glob

from pathlib import Path
import numpy as np

path = Path('./Logs')

csv_files = list(path.glob('*.csv'))

dataframes = {}

for file in csv_files:
    dataframes[file.name[:-len("_training_log.csv")]] = pd.read_csv(file, index_col=0)


for (k,v) in dataframes.items():
    fig, axes = plt.subplots(2, 1, figsize=(12,4),sharex=True)
    fig.suptitle(k)
    it = list(v.index.values)
    avg_rews = np.array(v["avg_rews"])
    std_rews = np.array(v["std_rews"])
    
    axes[0].plot(it, avg_rews, color='k')
    axes[0].fill_between(it, avg_rews-2*std_rews, avg_rews+2*std_rews, color='b', alpha=0.2)
    axes[0].set_ylabel('Average return')
    
    axes[1].plot(it, np.array(v["avg_actor_loss"]), label="Average actor loss")
    axes[1].plot(it, np.array(v["avg_critic_loss"]), label="Average critic loss")   
    axes[1].legend()

    plt.xlabel("Iteration")
    plt.show()