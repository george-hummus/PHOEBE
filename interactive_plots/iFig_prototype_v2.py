#imports
import numpy as np
from bokeh.layouts import column, row
from bokeh.models import Slider, Select, ColumnDataSource, RadioButtonGroup
from bokeh.plotting import figure, show
from bokeh.io import curdoc

#setting up data
results = np.genfromtxt('../Final_Protoype/outputs/7328.3562yrs_0100_t03_2_TMAP2/0100_t03_2_TMAP.csv',
                     skip_header = 1, delimiter = ',')
res = np.transpose(results) #need to transpose csv so arrays within it are the columns of the file
#extracting columns
masses = res[0]
periods = res[1]
incls = res[2]
natives = res[3]
ohs = res[4]
diffs = res[5]
ecl = res[6]

#slicing out the first loop of inlcinations
ics = incls[0:19]

imask = incls == 0 #mask for where the inclination turns back to zero
pi0 = periods[imask] #putting masks on the period arrays so get all the individual values at inc = 0
ps = pi0[0:20] #slicing out the first loop of periods

#as the period changes with each loop on inclinations
mmask = (periods == 0.1) & (incls == 0) #finds where each new loop of periods are (i.e., the new mass starts)
ms = masses[mmask] #looks for all indivial masses


#list of varibles that can be on the axes
x_vars = ['mass', 'period', 'inclination']
y_vars = ['native amp', 'only_horizon amp', 'amp diff']

#lists of mass, period, and inclination options to choose
mass_menu = list(np.array(ms, dtype=str))
period_menu = list(np.array(ps, dtype=str))
incl_menu = list(np.array(ics, dtype=str))

#set up axes widgets
xaxis = RadioButtonGroup(labels=x_vars, active = 2)
#select which varible you want on x-axis; chocies are 'mass', 'period', 'inclination'
yaxis = RadioButtonGroup(labels=y_vars, active = 0)
#select which varible you want on y-axis
#chocies are 'native amplitude', 'only_horizon amplitude', 'difference in amplitude'

#set up select widgets for m, p and i
m2pick = Select(title="Pick a mass:", value=mass_menu[0], options=mass_menu)
p2pick = Select(title="Pick a period:", value=period_menu[0], options=period_menu)
i2pick = Select(title="Pick an inclination:", value=incl_menu[0], options=incl_menu)

def controls():
    #asks for inputs depending on what is fixed and free
    if xaxis.active == 0: #i.e., if mass is selected
        free_vars = column(p2pick, i2pick) #saves widgets together so only displays ones you can change

    if xaxis.active == 1: #i.e., if period is selected
        free_vars = column(m2pick, i2pick)
        #period is varrying so need to fix mass and inclination

    if xaxis.active == 2: #i.e., if mass is selected
        free_vars = column(m2pick, p2pick)
        #inclination is varrying so need to fix mass and period

    widgets = column(xaxis,yaxis,free_vars)

    return widgets

def new_vars():
    #convert options back to floats so can plot them
    mass = float(m2pick.value)
    period = float(p2pick.value)
    incl = float(i2pick.value)
    return mass, period, incl

def extract(yarray, M, P, I):
    #extracts the data you want on each axis
    if xaxis.active == 0: #i.e., mass is on x-axis
        mask = (np.isclose(periods,P)) & (np.isclose(incls,I))
        y = yarray[mask]
        x = ms

    if xaxis.active == 1: #i.e., period is on x-axis
        mask = (np.isclose(masses,M)) & (np.isclose(incls,I))
        y = yarray[mask]
        x = ps

    if xaxis.active == 2: #i.e., inclination is on x-axis
        mask = (np.isclose(masses,M)) & (np.isclose(periods,P))
        y = yarray[mask]
        x = ics

    return x, y

def plotting():
    #updates the new varibles
    mass, period, incl = new_vars()

    #labels depend on what is fixed
    if xaxis.active == 0:
        lab = 'Period = '+str(round(period,4))+' days'+'\n'+'Inclination = '+str(round(incl,4))+' degs'
        xlab = 'Mass of MS Star (Solar Masses)'
    if xaxis.active == 1:
        lab = 'mass = '+str(round(mass,4))+' solMass'+'\n'+ 'Inclination = '+str(round(incl,4))+' degs'
        xlab = 'Period of Binary (days)'
    if xaxis.active == 2:
        lab = 'Mass = '+str(round(mass,4))+' solMass'+'\n'+ 'Period = '+str(round(period,4))+' days'
        xlab = 'Inclination of Binary (degrees)'

    #extracts data depending on what is on y-axis
    if yaxis.active == 0: #i.e., native amplitude

        x, y = extract(natives, mass, period, incl)
        ylab = 'Native Amplitude (mag)'
    if yaxis.active == 1: #i.e., only_horizon amplitude
        x, y = extract(ohs, mass, period, incl)
        ylab = 'Only-Horizon Amplitude (mag)'
    if yaxis.active == 2: # i.e., difference in amplitude
        x, y = extract(diffs, mass, period, incl)
        ylab = 'Amplitude Difference (mag)'


    p = figure(width=400, height=400)
    r = p.scatter(x, y, marker = 'circle', size=10, alpha=0.5)

    p.title.text = lab

    p.xaxis.axis_label = xlab
    p.yaxis.axis_label = ylab

    return p


#update function
def update(attrname, old, new):
    layout.children[0] = controls()
    layout.children[1] = plotting()


#inital plot
layout = row(controls(), plotting())


xaxis.on_change('active', update)
yaxis.on_change('active', update)
m2pick.on_change('value', update)
p2pick.on_change('value', update)
i2pick.on_change('value', update)

curdoc().add_root(layout)
curdoc().title = "prototype"
