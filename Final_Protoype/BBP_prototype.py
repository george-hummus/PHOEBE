### IMPORTS
import phoebe
from phoebe import u,c
import numpy as np
import glob
import argparse
import csv
import time
import concurrent.futures
from importlib.machinery import SourceFileLoader
funcs = SourceFileLoader('useful_funcs', '../useful_funcs.py').load_module()

### SYS ARGUMENTS
parser = argparse.ArgumentParser(description = 'Creates a simple binary model of a WD and MS star in PHOEBE, using data from WD models which are valid for a TMAP model atmosphere, at an age chosen by the user. Different parameters are then looped through and the lghtcurve amplitudes are saved.')
#adding arguments to praser object
parser.add_argument('model' , type = str, help = 'Name of the .npz file containing the varibles valid for TMAP in the WD model.')
parser.add_argument('--msm_lims' , type = float, nargs='+', help = 'Sets inital and final mass of the main sequence star, plus the number of samples in logspace. Default: inital = 0.1 Msol, final = 1 solMass, 20 samples (0.1 1 20).', default = [0.1, 1, 20])
parser.add_argument('--p_lims' , type = float, nargs='+', help = 'Sets inital and final period of the binary, plus the number of samples in logspace. Default: inital = 0.1 days, final = 10 days, 20 samples (0.1 10 20).', default = [0.1, 10, 20])
parser.add_argument('--i_lims' , type = float, nargs='+', help = 'Sets inital and final inclination of the binary, plus the step size (Note min and max of inclination are 0 and 90 degs respectivly). Default: inital = 0 degs, final = 90 degs, step = 5 degs (0 90 5). ', default = [0, 90, 5])
#unpacking arguments from parse object
args = parser.parse_args()


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
name = args.model[0:-4]
where_abun = int(np.where(modelnames==name[0:-5])[0])
abun = abuns[where_abun]


### SET UP WD
Teff = float((10**logt)) * u.K
mass = float(mass) * u.solMass


###CREATE DIR
path = funcs.mkdir('outputs/', age +'yrs_'+name)


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

#irradiation and gravity darkening fo WD to 1
b['irrad_frac_refl_bol@primary'].set_value(1.0)
b['gravb_bol@primary'].set_value(1.0)

#abundance
b['abun@primary'].set_value(abun)

#atm
b['atm@primary'].set_value('tmap') #set to tmap atmosphere

## Add lightcurve dataset and change passband
b.add_dataset('lc', compute_phases=phoebe.linspace(0,1,3), dataset='lc01', overwrite = True, passband = 'Johnson:I') #creates lc dataset with only 3 phases as flux at 0 phase and 0.5 phase will be the max and min used to calculate tha amplitude
# THERE WAS AN ISSUE WITH SDSS:i PASSBAND SO USING Johnson:I now

## Save Model
b.save(path+name+'.phoebe')


#PARAMETERS TO CYCLE THRU
#converting mass and period limits into log10
logmsm1, logmsm2, logmsm3 = np.log10(args.msm_lims[0]), np.log10(args.msm_lims[1]), int(args.msm_lims[2])
logp1, logp2, logp3 = np.log10(args.p_lims[0]), np.log10(args.p_lims[1]), int(args.p_lims[2])

msm = np.logspace(logmsm1, logmsm2, logmsm3) #array for main sequence masses in logspace
p = np.logspace(logp1, logp2, logp3) #array for periods in logspace
incls = np.arange(args.i_lims[0],args.i_lims[1]+1,int(args.i_lims[2])) #inclinations array


# cycles = 0 #stores element to count total number of cycles
# succs = 0 #stores element to count total number of successes
# fails = 0 #stores element to count total number of failures


#calculate the models for each variable
def calc_model(ms_mass, orb_period, incls):
    #empty list for results
    outputs = []

    ## Set up MS star
    MS_mass = ms_mass * u.solMass
    MS_rad = funcs.MRR(ms_mass) * u.solRad
    MS_Teff = funcs.MTR(ms_mass) * u.K
    MS_logg = funcs.logg(MS_mass.value,MS_rad.value) #need this for limb darkening model

    #set secondary's mass by changing q
    b['q@component@orbit'].set_value(MS_mass/mass)
    b['requiv@component@secondary'].set_value(MS_rad)
    b['secondary@component@teff'].set_value(MS_Teff)


    ## Set up period
    period = orb_period * u.day
    b['period@binary'].set_value(period)


    ## Set up inclination
    for incl in incls:
        incl = float(incl)
        b['incl@binary'].set_value(incl)

        ## Atmosphere set up - BB with phoenix limb darkening
        b['atm@secondary']='blackbody'
        b['ld_coeffs_source_bol@secondary']='phoenix'
        b['ld_mode@secondary']='manual'
        b['ld_func@secondary']='power'
        pb=phoebe.get_passband('Johnson:I')
        coeffs=pb.interpolate_ldcoeffs(Teff=MS_Teff.value,logg=MS_logg, abun=0., ldatm='phoenix', ld_func='power')
        b['ld_coeffs@secondary']=coeffs[0]

        ## Run Compute
        if b.run_checks().status != 'FAIL': #under the condition that the compute won't fail
            #native
            try:
                n_amp, oh_amp, ampDiff, is_eclipse = funcs.amps(b)
                #finds the amplitudes

                ## Saving out results to list, so can be saved as csv file
                cycle_out = [MS_mass.value, period.value, incl, n_amp, oh_amp, ampDiff, is_eclipse]

            except ValueError as error:
                cycle_out = [MS_mass.value, period.value, incl, None, None, None, None]

        else:
            cycle_out = [MS_mass.value, period.value, incl, None, None, None, None]

        outputs.append(cycle_out)

    return outputs

#define two dummy functions for interating in the process pool
def period_cycle(ms_mass, p, incls):
    outputs = []
    for orb_period in p:
        output = calc_model(ms_mass, orb_period, incls)
        outputs.append(output)
    return outputs

def mass_cycle(msm):
    return period_cycle(msm, p, incls)

#start time for parallization
start = time.perf_counter()

#parallization
with concurrent.futures.ProcessPoolExecutor() as executor:
    results = executor.map(mass_cycle, msm)

finish = time.perf_counter()

print(f"Parallization took {finish-start} seconds to complete.")


cycles = []
fails = []
### SAVE RESULTS
with open(path+name+'.csv', 'w') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    filewriter.writerow(['MS Mass (solMass)', 'Period (days)','Inclination (degs)', 'Native Amplitude (mag)', 'Only-Horizon Amplitude (mag)', 'Amplitude Difference (mag)', 'Eclipsing?']) #writing header for csv

    for lists in results:
        for list in lists:
            for result in list:
                filewriter.writerow(result)
                cycles.append(1)
                if result[3] == None:
                    fails.append(1)
print(fails)
passes = len(cycles)-len(fails)
p_per = (passes/len(cycles))*100
print(p_per)
f_per = 100 - p_per


### INFO FILE
with open(path+'info.txt', 'w') as file1:
    # Writing data to a file
    file1.write("Information about model & results:\n")
    file1.write("-Name: "+name+"\n")
    file1.write("-Age: "+age+" yrs\n")
    file1.write("-MS Star Mass Limits:\n")
    file1.write("--Inital mass = "+str(args.msm_lims[0])+" SolMass\n")
    file1.write("--Final mass = "+str(args.msm_lims[1])+" SolMass\n")
    file1.write("--Number of samples = "+str(args.msm_lims[2])+"\n")
    file1.write("-Period Limits:\n")
    file1.write("--Inital period = "+str(args.p_lims[0])+" days\n")
    file1.write("--Final period = "+str(args.p_lims[1])+" days\n")
    file1.write("--Number of samples = "+str(args.p_lims[2])+"\n")
    file1.write("-Inclination Limits:\n")
    file1.write("--Inital inclination = "+str(args.i_lims[0])+" degs\n")
    file1.write("--Final inclination = "+str(args.i_lims[1])+" degs\n")
    file1.write("--Size between samples = "+str(args.i_lims[2])+" degs\n")
    file1.write("-Number of cycles = "+str(len(cycles))+"\n")
    file1.write("--of which successful = "+str(passes)+" ("+str(p_per)+"%)\n")
    file1.write("--of which failed = "+str(len(fails))+" ("+str(f_per)+"%)\n")
    file1.write(f"Parallization took {finish-start} seconds to complete."+"\n")
