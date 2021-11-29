### DAVE'S FUNCTIONS
from phoebe import u,c
import numpy as np

def logg(M,R):
	#Return cgs logg for a given mass and radius in solar units
	g=c.G*M*u.solMass/((R*u.solRad)**2)
	logg=np.log10(g.to(u.cm/u.s**2).value)
	return logg

def radius(logg,M):
	#Return radius in solRad for a given cgs logg and mass in solMass
	g=(10**logg)*u.cm/u.s**2
	R=np.sqrt(c.G*M*u.solMass/g).to(u.m)
	return R.to(u.solRad).value

def mass(logg,R):
	#Return mass in solMass for a given cgs logg and radius in solRad
	g=(10**logg)*u.cm/u.s**2
	M=(g * (R*u.solRad)**2)/c.G
	return M.to(u.solMass).value

def MRR(M):
	#Return radius in solRad for a given MS mass in solMass
    R = 0.438*M*M + 0.479*M + 0.075
    return R

def MLR(M):
	#Return luminosity in SolLum for a given MS mass in solMass
    if M <= 0.45:
        L=10**(2.028*np.log10(M) - 0.976)
    elif M <= 0.72:
        L=10**(4.572*np.log10(M) - 0.102)
    elif M <= 1.05:
        L=10**(5.743*np.log10(M) - 0.007)
    elif M <= 2.40:
        L=10**(4.329*np.log10(M) - 0.010)
    return L


def MTR(M):
	#Return Teff in K for a given MS mass in solMass
    L=MLR(M)
    R=MRR(M)*u.solRad
    T=np.sqrt(np.sqrt(L*u.solLum/(4*np.pi*R*R*c.sigma_sb)))
    return T.to(u.K).value


### MY FUNCTIONS
import os 
import glob

def mkdir(path,dirname):
    if os.path.isdir(path+dirname) == False: 
        os.mkdir(path+dirname) #if no dir of same name it creates it
        new_path = path+dirname+'/'
    else:
        dir_names = glob.glob(path+dirname+'*') #looks for all dirs with same start put differnt end
        if len(dir_names) == 1: 
            os.mkdir(path+dirname+'1') #if only the original dir found then makes directory with 1 at end
            new_path = path+dirname+'1'+'/'
        else:
            lst_num = int(dir_names[-1][-1]) #if more than one with same start name then assumes parts after are numbers
            try:
                os.mkdir(path+dirname+str(lst_num+1)) #so looks for the last number then creates dir with that number + 1 at end 
            except OSError as error:
                print(error) 
                print('Try another directory name?')
            new_path = path+dirname+str(lst_num+1)+'/'
    return new_path
