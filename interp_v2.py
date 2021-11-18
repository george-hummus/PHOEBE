### IMPORTS
import numpy as np
from scipy.interpolate import interp1d
import glob
import argparse #for inputting varibles in command line
import os
import warnings

### SYSTEM ARGUMNETS
parser = argparse.ArgumentParser(description = '''Interpolates the models of WD for a specified time, ouputting the log(T), log(g) and mass. Results wil be saved out as desciptive .txt file and as numpy file.
                                 Will also check if results are valid for the TMAP model. Can change the default TMAP limits using the optional arguments.''')
#adding arguments to praser object
parser.add_argument('int_time' , type = int, help = 'Time to interploate at (in years) - as an integer.')
parser.add_argument('--Tlims' , type = float, nargs='+', help = 'Two element list containing lower and upper limit for log of the effetive temperture of the WD .', default = [4.602,5.146])
parser.add_argument('--glims' , type = float, nargs='+', help = 'Two element list containing lower and upper limit for log of the surface gravity (g) of the WD.', default = [4.75, 6.5])
parser.add_argument('--agelims' , type = float, nargs='+', help = 'Two element list containing lower and upper limit for the age of the WD in yrs.', default = [4000, 30000])
#unpacking arguments from parse object
args = parser.parse_args()

#GLOBBING
data_files = glob.glob('outputs/data/*.npz')
#find the data files extracted from the .dat files

#opens file so can write out results to it
file2write=open('outputs/interp_results/interp_out_'+str(args.int_time)+'.txt','w') 
#opening line
file2write.write('***TMAP limtis are given as:\n- age ' +str(args.agelims) + ' yrs \n- log(T) ' +str(args.Tlims)+ '\n- log(g) ' + str(args.glims)+'\n\n')

#checks time is within TMAP limits (4,000 -> 30,0000yrs)
if (args.agelims[0] < args.int_time < args.agelims[1]) != True:
    file2write.write('WARNING! - TIME (' +str(args.int_time)+ ' yrs) IS NOT WITHIN TMAP LIMTIS\n\n')
else:
    file2write.write('TIME (' +str(args.int_time)+ ' yrs) IS WITHIN TMAP LIMTIS\n\n')

#empty lists to be appended to in each loop
#eventlually withh be saved as numpy arrays
names = [] #stores the file names so you can see which index of others correspond to which file
time = [] #stores the time at which you interpolate (will be the same for all)
logt = [] #stores the logt result of interpolation
logg = [] #stores the logt result of interpolation
mass = [] #stores the logt result of interpolation
tmap_valid = [] #stores boolean values. True means within TMAP limtis for time, logt and logg

for i in range(len(data_files)): 
    
    #write file name to array
    names.append(data_files[i][13:-4])
    
    ### LOAD IN ARRAYS
    data_varbs = np.load(data_files[i]) #loads the varibles
    #names of each varible in list
    data_names = ['time_', 'logt_', 'logg_', 'mass_']
    #use for loop to save out each element to a seperate array
    for j in range(len(data_names)):
        locals()[data_names[j]] = data_varbs['arr_'+str(j)]
     
    #description to writing to .txt file 
    file2write.write('file = '+ str(data_files[i]) + '\n')
    file2write.write("Star's final mass: " + str(mass_[0]) + '\n')
    
    #uses interp1d to create a function for the data which can be interploated for any value
    logt_func = interp1d(time_,logt_)
    logg_func = interp1d(time_,logg_)
    mass_func = interp1d(time_,mass_)
    
    #uses interp functions to find these values at a specified time
    if (time_.min() < args.int_time < time_.max()) == True:
        #does the interpolation
        logt_interp = logt_func(args.int_time)
        logg_interp = logg_func(args.int_time)
        mass_interp = mass_func(args.int_time)
        
        #writes out results to .txt file
        file2write.write('- log(t) of WD @ 15,000yrs = '+str(logt_interp)+'\n')
        file2write.write('  therefore, Teff @ 15,000yrs = '+str(10**logt_interp)+' K\n')
        file2write.write('- log(g) of WD @ 15,000yrs = '+str(logg_interp)+'\n')
        file2write.write('  therefore, g @ 15,000yrs = '+str(10**logg_interp)+' m/s^2\n')
        file2write.write('- mass of WD @ 15,000yrs = '+str(mass_interp)+' Msol\n')
        file2write.write('- mass of WD @ 15,000yrs = '+str(mass_interp)+' Msol\n')
        
        #checks if results fit in TMAP limits
        if (args.Tlims[0] < logt_interp < args.Tlims[1]) & (args.glims[0] < logg_interp < args.glims[1]) == True:
            file2write.write('- Results are within TMAP limits of log(T) and log(g) \n')
            tmap_valid.append(True)
        else:
            file2write.write('- Results are NOT within TMAP limits of log(T) and log(g) \n')
            tmap_valid.append(False)
        
        file2write.write('\n') #spacing
        
        #appends results to empty lists
        time.append(args.int_time)
        logt.append(logt_interp)
        logg.append(logg_interp)
        mass.append(mass_interp)
        
    else:
        file2write.write('- Time to interpolate at is not within the original time range, so cannot interpolate.\n')
        file2write.write('\n')
        
        #appends None to empty lists and False to validation list 
        time.append(args.int_time)
        logt.append(None)
        logg.append(None)
        mass.append(None)
        tmap_valid.append(False)
        
        
##convert lists to numpy arrays and save]
names = np.array(names)
time = np.array(time)
logt = np.array(logt)
logg = np.array(logg)   
mass = np.array(mass)
tmap_valid = np.array(tmap_valid)

np.savez('outputs/interp_results/interp_out_'+str(args.int_time),
                 names, time, logt, logg, mass, tmap_valid)
    
    
