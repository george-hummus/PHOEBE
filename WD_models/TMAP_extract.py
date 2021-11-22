### IMPORTS 
import numpy as np
import numpy.ma as ma #for setting up masks
import glob
import argparse #for inputting varibles in command line
import os 

#creating parser object to be filled with system arguments (
parser = argparse.ArgumentParser(description = 'Plots model WD log(Teff) and log(g) against time, as well as highlightining the sections that fit within the TMAP model atmosphere.')
#adding arguments to praser object
parser.add_argument('dir_' , type = str, help = 'A name for the directory that will be created for the output data.')
parser.add_argument('--Tlims' , type = float, nargs='+', help = 'Two element list containing lower and upper limit for log of the effetive temperture of the WD .', default = [4.602,5.146])
parser.add_argument('--glims' , type = float, nargs='+', help = 'Two element list containing lower and upper limit for log of the surface gravity (g) of the WD.', default = [4.75, 6.5])
parser.add_argument('--agelims' , type = float, nargs='+', help = 'Two element list containing lower and upper limit for the age of the WD in yrs.', default = [4000, 30000])
parser.add_argument('--data' , type = str, help = 'A string directing towards the files containing the data of the WD models.', default = 'outputs/data/*.npz')
#unpacking arguments from parse object
args = parser.parse_args()

###GLOBBING
data_files = glob.glob(args.data) #list data files for WD models

###MAKE DIR TO SAVE TO
if os.path.isdir("outputs/TMAPdata/"+args.dir_) == False: 
    os.mkdir("outputs/TMAPdata/"+args.dir_) #if no dir of same name it creates it
    path = "outputs/TMAPdata/"+args.dir_
else:
    dir_names = glob.glob("outputs/TMAPdata/"+args.dir_+'*') #looks for all dirs with same start put differnt end
    if len(dir_names) == 1: 
        os.mkdir("outputs/TMAPdata/"+args.dir_+'1') #if only the original dir found then makes directory with 1 at end
        path = "outputs/TMAPdata/"+args.dir_+'1'
    else:
        lst_num = int(dir_names[-1][-1]) #if more than one with same start name then assumes parts after are numbers
        try:
            os.mkdir("outputs/TMAPdata/"+args.dir_+str(lst_num+1)) #so looks for the last number then creates dir with that number + 1 at end
        except OSError as error:
            print(error) 
            print('Try another directory name?')
        path = "outputs/TMAPdata/"+args.dir_+str(lst_num+1)

file2write=open(path+'/TMAP_extract_out.txt','w') #opens file so can write out results to it

for i in range(len(data_files)): 
    
    ### LOAD IN ARRAYS
    data_varbs = np.load(data_files[i]) #loads the varibles
    #names of each varible in list
    data_names = ['time_', 'logt_', 'logg_', 'mass_']
    #use for loop to save out each element to a seperate array
    for j in range(len(data_names)):
        locals()[data_names[j]] = data_varbs['arr_'+str(j)]
        
    file2write.write('file = '+ str(data_files[i]) + '\n')
        
    file2write.write("Star's final mass: " + str(mass_[0]) + '\n')
        
    ##Filter logt and logg to see which values fit inside TMAP range
    #check progressivly values of logt and logg to be in TMAP range
    logt_mask = ma.masked_inside(logt_, float(args.Tlims[0]), float(args.Tlims[1])) #creates mask for limits of temp in TMAP
    logg_mask = ma.masked_inside(logg_, float(args.glims[0]), float(args.glims[1])) #creates mask for limits of logg in TMAP
    time_mask = ma.masked_inside(time_, float(args.agelims[0]), float(args.agelims[1])) #mask for limits of WD ages for PNe

    TMAP_mask = logt_mask.mask & logg_mask.mask & time_mask.mask #'adds' the three masks together
    valid_times = time_[TMAP_mask] 
    #applies mask to times array to get all the times where teff and logg are within TMAP limits
    #apply mask to other values to extarct their valid values
    valid_logt = logt_[TMAP_mask] 
    valid_logg = logg_[TMAP_mask]
    valid_mass = mass_[TMAP_mask]
        
    #saves TMAP arrays 
    np.savez(path+'/'+str(data_files[i])[13:-4]+'_TMAP',
                 valid_times, valid_logt, valid_logg, valid_mass) 
        
    file2write.write('     times where logt, logg & time match TMAP limits:\n')
    file2write.write('     ' + str(valid_times) + '\n')
        
    ##checking for any discontinuities
    where2 = np.where(TMAP_mask==True)[0] #indices of where mask is true
    breaks = [] 
    for i in range(len(where2)-1): #cycles thru array
        if where2[i]!= (where2[i+1]-1): #if next value is not 1 greater than previous the disconitnuity
            breaks.append(1) #if discontinuity add element to list
            file2write.write('discontinuity after index ' + str(where2[i]) + ' in times\n')
    file2write.write('no. of discontinuities: '+str(len(breaks)) +'\n') #no. of elements in list == no. of of discontinuities
        
    file2write.write('\n')
    
file2write.close() #closes the file we are writing out to
