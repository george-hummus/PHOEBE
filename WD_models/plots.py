### IMPORTS 
import numpy as np #for dealing with arrays
import matplotlib.pyplot as plt #for plotting
from tqdm import tqdm #for progress bar
from matplotlib.ticker import AutoMinorLocator
import glob
import argparse #fr inputting varibles in command line
import os 

#creating parser object to be filled with system arguments (
parser = argparse.ArgumentParser(description = 'Plots model WD log(Teff) and log(g) against time, as well as highlightining the sections that fit within the TMAP model atmosphere.')
#adding arguments to praser object
parser.add_argument('dir_' , type = str, help = 'A name for the directory that will be created for the output data.')
parser.add_argument('--TMAPfiles' , type = str, help = 'A string directing towards the directory containing the data filtered by the TMAP limits. Files need to end in "_TMAP.npz".', default = 'outputs/TMAPdata/orgs/*.npz')
parser.add_argument('--Tlims' , type = float, nargs='+', help = 'Two element list containing lower and upper limit for log of the effetive temperture of the WD .', default = [4.602,5.146])
parser.add_argument('--glims' , type = float, nargs='+', help = 'Two element list containing lower and upper limit for log of the surface gravity (g) of the WD.', default = [4.75, 6.5])
parser.add_argument('--agelims' , type = float, nargs='+', help = 'Two element list containing lower and upper limit for the age of the WD in yrs.', default = [4000, 30000])
#unpacking arguments from parse object
args = parser.parse_args()

###GLOBBING
data_files = glob.glob('outputs/data/*.npz') #list data files for WD models
TMAP_files = glob.glob(args.TMAPfiles) #list data files valid for TMAP ranges

###MAKE DIR TO SAVE TO
if os.path.isdir("outputs/plots/"+args.dir_) == False: 
    os.mkdir("outputs/plots/"+args.dir_) #if no dir of same name it creates it
    path = "outputs/plots/"+args.dir_
else:
    dir_names = glob.glob("outputs/plots/"+args.dir_+'*') #looks for all dirs with same start put differnt end
    if len(dir_names) == 1: 
        os.mkdir("outputs/plots/"+args.dir_+'1') #if only the original dir found then makes directory with 1 at end
        path = "outputs/plots/"+args.dir_+'1'
    else:
        lst_num = int(dir_names[-1][-1]) #if more than one with same start name then assumes parts after are numbers
        try:
            os.mkdir("outputs/plots/"+args.dir_+str(lst_num+1)) #so looks for the last number then creates dir with that number + 1 at end 
        except OSError as error:
            print(error) 
            print('Try another directory name?')
        path = "outputs/plots/"+args.dir_+str(lst_num+1)

for i in tqdm (range(len(data_files)), #(len(data_files)), 
               desc="Loading data and plotting…", 
               ascii=False, ncols=75): #gives progress bar

    ### LOAD IN ARRAYS
    data_varbs = np.load(data_files[i]) #loads the varibles
    whereTMAP = np.where(np.array(TMAP_files) == #locates the TMAP file that corresponds to the data file
                  args.TMAPfiles[0:-5]+data_files[i][13:-4]+'_TMAP.npz')[0]
    TMAP_varbs = np.load(TMAP_files[whereTMAP[0]]) #loads in the TMAP varible using the index just found
    
    #names of each varible in list
    data_names = ['time_', 'logt_', 'logg_', 'mass_']
    TMAP_names = ['valid_time', 'valid_logt', 'valid_logg', 'valid_mass'] 
    #use for loop to save out each element to a seperate array
    for j in range(len(data_names)):
        locals()[data_names[j]] = data_varbs['arr_'+str(j)]
        locals()[TMAP_names[j]] = TMAP_varbs['arr_'+str(j)]
        #locals function turns the strings into varible names
    
    ###PLOTTING
    fig, ax = plt.subplots(2,1)

    ##logt
    #limits
    ax[0].axhline(y=args.Tlims[0], linestyle='--', color = 'grey', label = 'TMAP $\log{T_{eff}}$ limits') #tmap lower limit
    ax[0].axhline(y=args.Tlims[1], linestyle='--', color = 'grey') #tmap upper limit
    ax[0].axvline(x=args.agelims[0], linestyle='-.', color = 'grey', label = r'WD age limits')
    ax[0].axvline(x=args.agelims[1], linestyle='-.', color = 'grey')

    #plotting
    ax[0].plot(time_,logt_, color = 'royalblue')
    ax[0].plot(valid_time,valid_logt, color = 'orangered', label = 'Times allowed by TMAP')

    #fig set up
    ax[0].set_xlim(0,args.agelims[1]+500)
    ax[0].set_xlabel('time (yrs)')
    ax[0].set_ylabel(r'$\log{T_{eff}}$')
    #produces 10 minor ticks between each tick on both axes
    ax[0].xaxis.set_minor_locator(AutoMinorLocator(10))
    ax[0].yaxis.set_minor_locator(AutoMinorLocator(10))
    ax[0].legend()
    ax[0].set_title(str(data_files[i])[13:-4])


    ##logg
    #limits
    ax[1].axhline(y=args.glims[0], linestyle='--', color = 'grey', label = r'TMAP $\log{g}$ limits') #tmap lower limit
    ax[1].axhline(y=args.glims[1], linestyle='--', color = 'grey') #tmap upper limit
    ax[1].axvline(x=args.agelims[0], linestyle='-.', color = 'grey', label = r'WD age limits')
    ax[1].axvline(x=args.agelims[1], linestyle='-.', color = 'grey')

    #plotting
    ax[1].plot(time_, logg_, color = 'royalblue')
    ax[1].plot(valid_time, valid_logg, color = 'orangered', label = 'Times allowed by TMAP')

    #fig set up
    ax[1].set_xlim(0,args.agelims[1]+500)
    ax[1].set_xlabel('time (yrs)')
    ax[1].set_ylabel(r'$\log{g}$')
    #produces 10 minor ticks between each tick on both axes
    ax[1].xaxis.set_minor_locator(AutoMinorLocator(10))
    ax[1].yaxis.set_minor_locator(AutoMinorLocator(10))
    ax[1].legend()

    plt.tight_layout()

    fig.savefig(path+'/'+str(data_files[i])[13:-4]+'.png', dpi = 600)
    
    #clears the figure from memory
    fig.clear()
    plt.close(fig)
