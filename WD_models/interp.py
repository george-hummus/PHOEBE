### IMPORTS
import numpy as np
from scipy.interpolate import interp1d
import glob

#GLOBBING
data_files = glob.glob('outputs/data/*.npz')
#find the data files extracted from the .dat files

file2write=open('outputs/interp_out.txt','w') #opens file so can write out results to it

for i in range(len(data_files)): 
    
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
    
    int_time = 15000 #time to interpolate at 
    
    #uses interp functions to find these values at a specified time
    if (int_time > time_.min()) & (int_time < time_.max()):
        logt_interp = logt_func(15000)
        logg_interp = logg_func(15000)
        mass_interp = mass_func(15000)
        
        #writes out results
        file2write.write('- log(t) of WD @ 15,000yrs = '+str(logt_interp)+'\n')
        file2write.write('  therefore, Teff @ 15,000yrs = '+str(10**logt_interp)+' K\n')
        file2write.write('- log(g) of WD @ 15,000yrs = '+str(logg_interp)+'\n')
        file2write.write('  therefore, g @ 15,000yrs = '+str(10**logg_interp)+' m/s^2\n')
        file2write.write('- mass of WD @ 15,000yrs = '+str(mass_interp)+' Msol\n')
        file2write.write('\n')
    else:
        file2write.write('- Time to interpolate at is not within the original time range, so cannot interpolate.\n')
        file2write.write('\n')
    
    
    
    
