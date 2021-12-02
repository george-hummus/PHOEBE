### IMPORTS
import phoebe
from phoebe import u,c
import numpy as np
import glob
from importlib.machinery import SourceFileLoader
funcs = SourceFileLoader('useful_funcs', '/media/george/Work/PHOEBE/useful_funcs.py').load_module()
import os 
import argparse 

### SYS ARGUMENTS
parser = argparse.ArgumentParser(description = '''Imports simple binary model of a WD and MS star using interpoated values from WD models in PHOEBE. Then finds the amplitude of this model's light curve at different inclinations.''')
## Adding arguments 
parser.add_argument('pth' , type = str, help = 'Path leading to directory containing .phoebe files containing the binary models of the WDs. Needs to end in "/"')
args = parser.parse_args() #unpacking

### GLOBBING
models = glob.glob(args.pth+'*.phoebe')
# finds the models of the binaries for interpolation at 15000yrs with MS star of 2 solMasses

### MAKE DIR
path = funcs.mkdir('', models[0][35:-18])

### TEXT FILE TO SAVE RESULTS TO
file2write=open(path+'WD_amps.txt','w') #opens file so can write out results to it

inclinations = np.linspace(0,90,10) #a range of inclinations to cycle through
np.save(path+'incls', inclinations)

### LOOPING THRU MODELS
for i in models:
    WD = phoebe.load(i) #load in model
    
    ampDiffs, Ns, OHs = [], [], [] #list to store the amplitudes and amp differnces of this model at different inclinations
    
    file2write.write('Model: '+ i[47:-7] +'\n') #writes out model name
    file2write.write('\n')
    
    for j in inclinations:
        WD['incl@orbit'].set_value(j*u.deg) # change the inlcination of the binary
        
        file2write.write('-Inclination: ' +str(j)+ ' degrees \n')

        ## Run Compute
        #native
        WD.run_compute(model = 'n', eclipse_method = 'native', overwrite = True)
        #only horizon
        WD.run_compute(model = 'oh', eclipse_method = 'only_horizon', overwrite = True)
        
        ## Native Eclipse
        n_f = WD['lc01@n@fluxes'].value #fluxes
        n_amp = np.max(n_f) - np.min(n_f) #calculates amplitude of lc
        file2write.write('--Native Amplitude: ' +str(n_amp)+ '\n')

        ## No Eclipse
        oh_f = WD['lc01@oh@fluxes'].value #fluxes
        oh_amp = np.max(oh_f) - np.min(oh_f) #calculates amplitude of lc
        file2write.write('--Only Horizon Amplitude: ' +str(oh_amp)+ '\n')
        
        ampDiff = abs(n_amp - oh_amp) #difference in the amplitudes
        file2write.write('--Difference in Amplitudes: ' +str(ampDiff)+ '\n')
        if ampDiff > 0:
            file2write.write('--Likely to Eclipse: True\n')
        else:
            file2write.write('--Likely to Eclipse: False\n')
        
        #append results to lists
        Ns.append(n_amp)
        OHs.append(oh_amp)
        ampDiffs.append(ampDiff)
        
        file2write.write('\n')
    
    #convert lists to arrays and save out
    np.save(path+i[47:-7]+'_n',np.array(Ns))
    np.save(path+i[47:-7]+'_oh',np.array(OHs))
    np.save(path+i[47:-7]+'_d',np.array(ampDiffs))
        
    file2write.write('\n')

file2write.close() #closes the file we are writing out to
