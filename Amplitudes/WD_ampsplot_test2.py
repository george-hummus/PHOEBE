### IMPORTS
import phoebe
from phoebe import u,c
import numpy as np
import glob
import matplotlib.pyplot as plt
import argparse 

### SYS ARGUMENTS
parser = argparse.ArgumentParser(description = 'Creates a simple binary model of a WD and MS star using interpolated values from WD models in PHOEBE. Can specify the mass of the MS star, and where location of interpolated values.')
## Adding arguments 
parser.add_argument('path' , type = str, help = 'Path leading to directory containing .npy files to be plotted. Needs to end in "/"')
parser.add_argument('plotAD' , type = int, help = 'Option to plot amplitude difference between "native" and "only horizon". Binary option.')
parser.add_argument('plotN' , type = int, help = 'Option to plot "native" amplitude of lc. Binary option.')
parser.add_argument('plotOH' , type = int, help = 'Option to plot "only horizon" amplitude of lc. Binary option.')
args = parser.parse_args() #unpacking

incls = np.load(args.path+'incls.npy') #loads in the array of saved inclination

if args.plotAD == 1:
    ad_arrays = glob.glob(args.path+'*d.npy') #searching for arrays
        
    #set up figure
    fig, ax = plt.subplots()
    
    for i in ad_arrays:
        y = np.load(i)
        ax.scatter(incls, y, label = i[13:-6])

    ax.set_xlabel(r'inclination of binary $(^o)$')
    ax.set_ylabel(r'Differnce in Amplitude of "Native"' +'\n'+ r'and "Horizon Only" Lightcurves $(Wm^{-2})$')
    ax.legend()
    fig.show()
    fig.savefig(args.path+'AD_plot.png', dpi = 600)
    
if args.plotN == 1:
    n_arrays = glob.glob(args.path+'*n.npy') #searching for arrays
    
    #set up figure
    fig, ax = plt.subplots()
    
    for j in n_arrays:
        y = np.load(j)
        ax.scatter(incls, y, label = j[13:-6])

    ax.set_xlabel(r'inclination of binary $(^o)$')
    ax.set_ylabel(r'"Native" Amplitude $(Wm^{-2})$')
    ax.legend()
    fig.show()
    fig.savefig(args.path+'N_plot.png', dpi = 600)
    
if args.plotOH == 1:
    oh_arrays = glob.glob(args.path+'*oh.npy') #searching for arrays
    
    #set up figure
    fig, ax = plt.subplots()
    
    for k in oh_arrays:
        y = np.load(k)
        ax.scatter(incls, y, label = k[13:-6])

    ax.set_xlabel(r'inclination of binary $(^o)$')
    ax.set_ylabel(r'"Horizon Only" Amplitude $(Wm^{-2})$')
    ax.legend()
    fig.show()
    fig.savefig(args.path+'OH_plot.png', dpi = 600)
    
else:
    print('Please select at least one option to plot.')
    
