import numpy as np
import glob
import matplotlib.pyplot as plt

results = np.genfromtxt('../Final_Protoype/outputs/7328.3562yrs_0100_t03_2_TMAP2/0100_t03_2_TMAP.csv',skip_header = 1, delimiter = ',')
res = np.transpose(results) #need to transpose csv so arrays within it are the columns of the file

#extracting columns
masses = res[0]
periods = res[1]
incls = res[2]
natives = res[3]
ohs = res[4]
diffs = res[5]
ecl = res[6]

#setting up data to pick from
#slicing out the first loop of inlcinations
ics = incls[0:19]

imask = incls == 0 #mask for where the inclination turns back to zero
pi0 = periods[imask] #putting masks on the period arrays so get all the individual values at inc = 0
p2pick = pi0[0:20] #slicing out the first loop of periods

#as the period changes with each loop on inclinations
mmask = (periods == 0.1) & (incls == 0) #finds where each new loop of periods are (i.e., the new mass starts)
m2pick = masses[mmask] #looks for all indivial masses

###trial where you can have mass, period or inclination on x-axis###
###and choose which result to plot on y-axis (native, oh, or diff)###
def axes_choice():
    varibles = ['mass', 'period', 'inclination', 'native amplitude',
                'only_horizon amplitude', 'difference in amplitude']

    xaxis = input(r'pick x-axis varible from list:'+'\n'+str(varibles[0:3])) #asks which varible for x-axis,
    #chocies are 'mass', 'period', 'inclination'
    yaxis = input(r'pick y-axis varible from list:'+'\n'+str(varibles[3:])) #asks which varible for y-axis,
    #chocies are 'native amplitude', 'only_horizon amplitude', 'difference in amplitude'

    #checking axes inputs are correct
    if (xaxis not in varibles) & (yaxis not in varibles):
        raise ValueError('error in x or y selection, choices are: "mass", "period", "inclination",'
                         +' "native amplitude", "only_horizon amplitude", "difference in amplitude"')

    varibles.remove(xaxis)
    varibles.remove(yaxis) #removes axes from varibles so we know which ones are free varibles

    #asks for inputs depending on what is fixed and free
    if 'mass' not in varibles:
        period = float(input(r'pick a period:'+'\n'+str(p2pick)))
        incl = float(input(r'pick a inclination:'+'\n'+str(ics)))
        #mass is varrying so need to fix period and inclination
        M, P, I = True, False, False #varible to tell extarct function which is free
    if 'period' not in varibles:
        mass = float(input('pick a mass:'+'\n'+str(m2pick)))
        incl = float(input(r'pick a inclination:'+'\n'+str(ics)))
        #period is varrying so need to fix mass and inclination
        M, P, I = False, True, False
    if 'inclination' not in varibles:
        mass = float(input('pick a mass:'+'\n'+str(m2pick)))
        #inclination is varrying so need to fix mass and period
        period = float(input(r'pick a period:'+'\n'+str(p2pick)))
        M, P, I = False, False, True
    #M, P, and I are boolean and if true means mass, period or inclination is constant


    def extract(yarray):
        #extracts the data you want on each axis
        if M == True: #i.e., mass is on x-axis
            mask = (np.isclose(periods,period)) & (np.isclose(incls,incl))
            y = yarray[mask]
            x = m2pick

        if P == True: #i.e., period is on x-axis
            mask = (np.isclose(masses,mass)) & (np.isclose(incls,incl))
            y = yarray[mask]
            x = p2pick

        if I == True: #i.e., inclination is on x-axis
            mask = (np.isclose(masses,mass)) & (np.isclose(periods,period))
            y = yarray[mask]
            x = ics

        return x, y

    def plot(x,y):
        #labels depend on what is fixed
        if M == True:
            lab = 'Period = '+str(round(period,4))+' days'+'\n'+'Inclination = '+str(round(incl,4))+' degs'
            xlab = 'Mass of MS Star ($M_{\odot}$)'
        if P == True:
            lab = 'mass = '+str(round(mass,4))+' solMass'+'\n'+ 'Inclination = '+str(round(incl,4))+' degs.'
            xlab = 'Period of Binary (days)'
        if I == True:
            lab = 'Mass = '+str(round(mass,4))+' solMass'+'\n'+ 'Period = '+str(round(period,4))+' days.'
            xlab = r'Inclination of Binary ($^{o}$)'

        fig, ax = plt.subplots()
        ax.scatter(x, y, color = 'indigo', label = lab)

        ax.set_ylabel(yaxis+' (mag)')
        ax.set_xlabel(xlab)
        ax.legend()
        fig.savefig('tests/'+xaxis+'_'+yaxis+'.png')

    #extracts data depending on what is on y-axis
    if yaxis == "native amplitude":
        x, y = extract(natives)
    if yaxis == "only_horizon amplitude":
        x, y = extract(ohs)
    if yaxis == "difference in amplitude":
        x, y = extract(diffs)

    #plotting
    plot(x,y)

axes_choice()
