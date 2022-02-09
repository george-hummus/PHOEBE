### IMPORTS
import phoebe
from phoebe import u,c
import numpy as np
import glob
import argparse
import csv
import time
import scipy.interpolate as interp
from importlib.machinery import SourceFileLoader
funcs = SourceFileLoader('useful_funcs', '../useful_funcs.py').load_module()

### SYS ARGUMENTS
parser = argparse.ArgumentParser(description = 'Creates a simple binary model of a WD and MS star in PHOEBE, using data from WD models which are valid for a TMAP model atmosphere, at an age chosen by the user. Different parameters are then looped through and the lghtcurve amplitudes are saved.')
#adding arguments to praser object
parser.add_argument('--model' , type = str, help = 'path to the .phoebe file containing the TMAP WD model.', default = '0100_t03_2_TMAP.phoebe')
parser.add_argument('--ms_info' , type = str, help = 'Path to CSV file containing spectral type, temp,radius, and mass from CARMENES paper.', default = 'CARMENES_info-extended.csv')
parser.add_argument('--p_lims' , type = float, nargs='+', help = 'Sets inital and final period of the binary, plus the number of samples in logspace. Default: inital = 0.1 days, final = 10 days, 20 samples (0.1 10 20).', default = [0.1, 10, 20])
parser.add_argument('--i_lims' , type = float, nargs='+', help = 'Sets inital and final inclination of the binary, plus the step size (Note min and max of inclination are 0 and 90 degs respectivly). Default: inital = 0 degs, final = 90 degs, step = 5 degs (0 90 5). ', default = [0, 90, 5])
#parser.add_argument('--met' , type = str, help = 'Sets if data for a & b coefficents for limb darkening of MS star was calucated using Least-Square ("L") or Flux Conservation ("F"). Default is "L"', default = "L") #using flux conserving only
parser.add_argument('--coeffs' , type = str, help = 'Sets if you want to interpolate the limb darkening coefficents ("interp") or just go with the ones closest to the values of the main sequence stars ("guess"). Default: "guess"', default = "guess")
args = parser.parse_args()

# JUST TESTING THAT THINGS ARE WORKING
if args.coeffs == "guess":
    print('hi')
else:
    exit()

### DEFINES THE NAME OF THE MODEL THAT IS RUNNING
name = f'{args.model[0:-7]}_p{int(args.p_lims[2])}_i{int(args.i_lims[2])}-ig'

### LOAD IN TMAP model
b = phoebe.load(args.model)
mass = b['mass@component@primary'].value * u.solMass #mass of WD is needed later

### LOAD IN CARMENS DATA FOR MS STARS (https://ui.adsabs.harvard.edu/abs/2020A%26A...642A.115C/abstract)
ms_data = np.genfromtxt(args.ms_info,skip_header = 1, delimiter = ',',usecols = (1,2,3)) #skips first column as it gives the spectral type as a string


#PARAMETERS TO CYCLE THRU
#converting period limits into log10
logp1, logp2, logp3 = np.log10(args.p_lims[0]), np.log10(args.p_lims[1]), int(args.p_lims[2])
p = np.logspace(logp1, logp2, logp3)
#inclinations are not sampled in logspace
incls = np.arange(args.i_lims[0],args.i_lims[1]+1,int(args.i_lims[2]))


### EMPTY LISTS
outputs = [] #empty list for outputs that will be written to csv file
cycles = [] #stores element to count total number of cycles
succs = [] #stores element to count total number of successes
fails = [] #stores element to count total number of failures


### LIMBDARKENING (https://cdsarc.cds.unistra.fr/viz-bin/cat/J/A+A/546/A14)
## need coefficents for the limb-darkening (in I band) and bolomentric limb limb-darkening
# Use Kp band as "bolometric" as it has large width (http://svo2.cab.inta-csic.es/svo/theory/fps3/index.php?id=MKO/NSFCam.Kp&&mode=browse&gname=MKO&gname2=NSFCam)
#if (args.met == 'L'):
#    ld_path, bol_path = 'lb_I_L.csv', 'lb_Kp_L.csv'
#if (args.met == 'F'):
ld_path, bol_path = 'limb_darkening/lb_I_F.csv', 'limb_darkening/lb_C_F.csv' #using flux conserving only
lbdata = np.genfromtxt(ld_path,skip_header = 1, delimiter = ',',usecols = (0,1,4,5))
bol_data = np.genfromtxt(bol_path,skip_header = 1, delimiter = ',',usecols = (0,1,4,5))
#skips header and imports logg, teff, a and b (where a+b are the coefficeients)
loggs = lbdata.T[0]
b_loggs = bol_data.T[0]
temps = lbdata.T[1]
b_temps = bol_data.T[1]
As = lbdata.T[2]
A_bol = bol_data.T[2]
Bs = lbdata.T[3]
B_bol = bol_data.T[3]

if args.coeffs == "guess":
    def lbguess(g,t,TyPe):
        '''Function that will find the entry in the limbdarkening tables which is the nearest match to the parameters of the MS companion star.
        '''
        def finder(gr,tr,gs,ts): #function for finding the index at which the MS star matches closest with table
            def looker():
                whereG = np.where(gs == gr)[0]
                #finds where logg has values at rounded ms_logg
                whereT = np.where(ts == tr)[0]
                #finds where temps has value at rounded ms_teff
                dex = np.intersect1d(whereG, whereT)[0]
                #finds the valule the the above arrays share, this is index of lb data we will use
                return dex

            try:
                ind = looker()
            except:
                tr-=100 #if can't find temperture that is the same subtrtact 100K and look again
                ind = looker()

            return ind

        g_round = round(g* 2) / 2 #rounds MS_logg to the nearest 0.5 (which is what tables increment in)
        t_round = round(MS_Teff.value/1000,1)*1000 #rounds MS_Teff to the nearest 100 (which is what tables increment in)

        if TyPe == 'ld': #for normal limbdarkening
            idx = finder(g_round,t_round,loggs,temps)
            return lbdata[idx][2], lbdata[idx][3] #gives a & b value at this index

        if TyPe == 'bol': #same but for bolometric limb_darkening
            idx = finder(g_round,t_round,b_loggs,b_temps)
            return bol_data[idx][2], bol_data[idx][3]


elif args.coeffs == "interp":
    ##2d interpolation giving functions for the limbdarkening
    ## don't use interp2d - it is bad. Need to use interp.RBFInterpolator (but still figuring it out)
    #process data for RBFInterpolator
    try:
        ylb = np.stack([loggs, temps], -1)
        ybol = np.stack([b_loggs, b_temps], -1)
        afunc = interp.RBFInterpolator(ylb,As,smoothing=o) #will error here
        bfunc = interp.RBFInterpolator(ylb,Bs,smoothing=o)
        afunc_bol = interp.RBFInterpolator(ybol,A_bol,smoothing=o)
        bfunc_bol = interp.RBFInterpolator(ybol,B_bol,smoothing=o)
    except:
        print('interpolation not implmented as of yet...')
        exit()

else:
    print('choese either "interp" or "guess" for --coeffs argument')
    exit()


##start timer
start = time.perf_counter()

##cycle through the different parameters
for i in ms_data:
    ## Set up MS star
    MS_mass = i[2] * u.solMass
    MS_rad = i[1] * u.solRad
    MS_Teff = i[0] * u.K
    MS_logg = funcs.logg(MS_mass.value,MS_rad.value) #need this for limb darkening model

    #set secondary's mass by changing q
    b['q@component@orbit'].set_value(MS_mass/mass)
    b['requiv@component@secondary'].set_value(MS_rad)
    b['secondary@component@teff'].set_value(MS_Teff)

    for j in p:
        ## Set up period
        period = j * u.day
        b['period@binary'].set_value(period)

        for k in incls:
            ## Set up inclination
            incl = float(k)
            b['incl@binary'].set_value(incl)

            if args.coeffs == "guess": #finding nearest coefficents from table to MS-star's parameters
                a_lb, b_lb = lbguess(MS_logg,MS_Teff.value,'ld')
                a_bol, b_bol = lbguess(MS_logg,MS_Teff.value,'bol')
            if args.coeffs == "interp": #interpolating coefficents from table @ MS-star's parameters
                a_lb, b_lb = afunc(MS_logg,MS_Teff)[0],bfunc(MS_logg,MS_Teff)[0]
                a_bol, b_bol = afunc_bol(MS_logg,MS_Teff)[0],bfunc_bol(MS_logg,MS_Teff)[0]
                #doesn't really work yet

            ## Atmosphere set up - BB with phoenix limb darkening with lower temps
            b['atm@secondary']='blackbody'
            b['ld_mode_bol@secondary']='manual'
            b['ld_mode@secondary']='manual'
            b['ld_func@secondary']='quadratic'
            b['ld_coeffs@secondary']=[a_lb, b_lb]
            # bolometric limbdarkening #
            b['ld_mode_bol@secondary']='manual'
            b['ld_func_bol@secondary']='quadratic'
            b['ld_coeffs_bol@secondary']=[a_bol, b_bol]


            print(MS_mass, period, incl)

            ## Run Compute
            if b.run_checks().status != 'FAIL': #under the condition that the compute won't fail
                try:

                    n_amp, oh_amp, ampDiff, is_eclipse = funcs.amps(b)
                    #finds the amplitudes

                    ## Saving out results to list, so can be saved as csv file
                    cycle_out = [MS_mass.value, period.value, incl, n_amp, oh_amp, ampDiff, is_eclipse]

                    succs.append(1)

                except ValueError:
                    print('atm error')
                    cycle_out = [MS_mass.value, period.value, incl, None, None, None, None]
                    fails.append(1)

            else:
                print('overflow error')
                cycle_out = [MS_mass.value, period.value, incl, None, None, None, None]
                fails.append(1)

            outputs.append(cycle_out)
            cycles.append(1)

#end timer
finish = time.perf_counter()

#counting up successes
no_cycles = len(cycles)
no_succs = len(succs)
no_fails = len(fails)
per_succs = (no_succs/no_cycles)*100
per_fails = (no_fails/no_cycles)*100


###CREATE DIR
path = funcs.mkdir('outputs/', name)

### INFO FILE
with open(path+'info.txt', 'w') as file1:
    # Writing data to a file
    file1.write("Information about model & results:\n")
    file1.write("-MS Star Mass Limits:\n")
    file1.write("-Period Limits:\n")
    file1.write(f"--Inital period = {args.p_lims[0]} days\n")
    file1.write(f"--Final period = {args.p_lims[1]} days\n")
    file1.write(f"--Number of samples = {args.p_lims[2]}\n")
    file1.write("-Inclination Limits:\n")
    file1.write(f"--Inital inclination = {args.i_lims[0]} degs\n")
    file1.write(f"--Final inclination = {args.i_lims[1]} degs\n")
    file1.write(f"--Size between samples = {args.i_lims[2]} degs\n")
    file1.write(f"-Number of cycles = {no_cycles}\n")
    file1.write(f"--of which successful = {no_succs} ({per_succs}%)\n")
    file1.write(f"--of which failed = {no_fails} ({per_fails}%)\n")
    file1.write(f'-Process took {finish-start} seconds')


### SAVE RESULTS
with open(f'{path}results.csv', 'w') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    filewriter.writerow(['MS Mass (solMass)', 'Period (days)','Inclination (degs)', 'Native Amplitude (mag)', 'Only-Horizon Amplitude (mag)', 'Amplitude Difference (mag)', 'Eclipsing?']) #writing header for csv
    for l in outputs:
        filewriter.writerow(l)
