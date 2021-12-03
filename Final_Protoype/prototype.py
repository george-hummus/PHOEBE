### IMPORTS
import phoebe
from phoebe import u,c
import numpy as np
from matplotlib.ticker import AutoMinorLocator
import glob
import argparse
import csv
from importlib.machinery import SourceFileLoader
funcs = SourceFileLoader('useful_funcs', '/media/george/Work/PHOEBE/useful_funcs.py').load_module()


### SYS ARGUMENTS
parser = argparse.ArgumentParser(description = 'Creates a simple binary model of a WD and MS star in PHOEBE, using data from WD models which are valid for a TMAP model atmosphere, at an age chosen by the user. Different parameters are then looped through and the lghtcurve amplitudes are saved.')
#adding arguments to praser object
parser.add_argument('model' , type = str, help = 'Name of the .npz file containing the varibles valid for TMAP in the WD model.')
parser.add_argument('--save' , type = bool, help = 'Option to save the intial model out. Default is True', default = True)
parser.add_argument('--msm_lims' , type = float, nargs='+', help = 'Sets inital and final mass of the main sequence star, plus the number of samples in logspace. Default: inital = 0.1 Msol, final = 1 solMass, 20 samples (0.1 1 20).', default = [0.1, 1, 20])
parser.add_argument('--p_lims' , type = float, nargs='+', help = 'Sets inital and final period of the binary, plus the number of samples in logspace. Default: inital = 0.1 days, final = 10 days, 20 samples (0.1 10 20).', default = [0.1, 10, 20])
parser.add_argument('--i_lims' , type = float, nargs='+', help = 'Sets inital and final inclination of the binary, plus the step size (Note min and max of inclination are 0 and 90 degs respectivly). Default: inital = 0 degs, final = 90 degs, step = 5 degs (0 90 5). ', default = [0, 90, 5])
#unpacking arguments from parse object
args = parser.parse_args()


###CREATE DIR
name = args.model[0:-4]
path = funcs.mkdir('outputs/', name)


### LOAD IN ARRAYS
## Import Tmap arrays
TMAP_varbs = np.load('TMAP_data/'+args.model)
TMAP_names = ['ages', 'logts', 'loggs', 'masses']
#use for loop to save out each element to a seperate array
for n in range(len(TMAP_names)):
    locals()[TMAP_names[n]] = TMAP_varbs['arr_'+str(n)]
    #locals function turns the strings into varible names

## Import Abundances
a_varbs = np.load('abundances/abuns_out.npz', allow_pickle=True)
modelnames, abuns = a_varbs['arr_0'], a_varbs['arr_1']


### PARAMETRS AT AGE PICKED
print('Pick an age from list:')
age = input(str(ages))
where_age = np.where(ages == float(age))[0]
## Varibles at this age
logt, logg, mass = logts[where_age], loggs[where_age], masses[where_age]
## Abunadance for this model
where_abun = int(np.where(modelnames==name[0:-5])[0])
abun = abuns[where_abun]


### SET UP WD
Teff = float((10**logt)) * u.K
mass = float(mass) * u.solMass


### MAKING INITAL PHOEBE MODEL
## Load default binary
b = phoebe.default_binary()

## Change the values only for WD
#flip for mass
b.flip_constraint(qualifier='mass', component='primary', solve_for='sma')
b.set_value('mass@primary', value=mass) #set primary's mass

#logg change
#flip for radius
b.flip_constraint(qualifier='logg', component='primary', solve_for='requiv')
b.set_value('logg@primary', value= float(logg))

#Teff
b.set_value('primary@component@teff', value = Teff)

#abundance
b['abun@primary'].set_value(abun)

#atm
b['atm@primary'].set_value('tmap') #set to tmap atmosphere

## Add lightcurve dataset and change passband
b.add_dataset('lc', compute_phases=phoebe.linspace(0,1,101), dataset='lc01', overwrite = True)
b['passband'].set_value('SDSS:i')

## Save Model
if args.save == True:
	b.save('models/'+name+'.phoebe')


#PARAMETERS TO CYCLE THRU
logmsm = np.linspace(np.log10(args.msm_lims[0]),np.log10(args.msm_lims[1]),int(args.msm_lims[2])) #log of ms mass
logp = np.linspace(np.log10(args.p_lims[0]),np.log10(args.p_lims[1]),int(args.p_lims[2])) #log periods
incls = np.arange(args.i_lims[0],args.i_lims[1]+args.i_lims[2],int(args.i_lims[2])) #inclinations


outputs = [] #empty list for outputs that will be written to csv file


##cycle through the different parameters
for i in logmsm:
    ## Set up MS star
    MS_mass = (10**i) * u.solMass
    MS_rad = funcs.MRR(10**i) * u.solRad
    MS_Teff = funcs.MTR(10**i) * u.K

    #set secondary's mass by changing q
    b['q@component@orbit'].set_value(MS_mass/mass)
    b['requiv@component@secondary'].set_value(MS_rad)
    b['secondary@component@teff'].set_value(MS_Teff)

    for j in logp:
        ## Set up period
        period = (10**j) * u.day
        b['period@binary'].set_value(period)

        for k in incls:
            ## Set up inclination
            incl = k
            b['incl@binary'].set_value(incl)

            print(b['sma@binary@component'])
            print(b['requiv@secondary'])
            print(b['requiv@primary'])

            ## Run Compute
            #native
            b.run_compute(model = 'n', eclipse_method = 'native', overwrite = True)
            #only horizon
            b.run_compute(model = 'oh', eclipse_method = 'only_horizon', overwrite = True)

            ## Native Eclipse
            n_f = b['lc01@n@fluxes'].value #fluxes
            n_amp = np.max(n_f) - np.min(n_f) #calculates amplitude of lc

            ## No Eclipse
            oh_f = b['lc01@oh@fluxes'].value #fluxes
            oh_amp = np.max(oh_f) - np.min(oh_f) #calculates amplitude of lc

            ampDiff = abs(n_amp - oh_amp) #difference in the amplitudes
            if ampDiff > 0:
                is_eclipse = True
            else:
                is_eclipse = False

            ## Saving out results to list, so can be saved as csv file
            cycle_out = [MS_mass, period, incl, n_amp, oh_amp, ampDiff,is_eclipse]
            outputs.append(cycle_out)


### SAVE RESULTS
with open(path+name+'.csv', 'w') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    filewriter.writerow(['MS Mass', 'Period','Inclination', 'Native Amplitude', 'Only-Horizon Amplitude', 'Amplitude Difference', 'Eclipsing?']) #writing header for csv
    for l in outputs:
        filewriter.writerow(l)
