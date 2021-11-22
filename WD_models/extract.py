### IMPORTS 
import numpy as np
import numpy.ma as ma #for setting up masks
import glob

files = glob.glob('data/*.dat') #creates list of all the data files

file2write=open("outputs/extract_out.txt",'w') #opens file so can write out results to it

for j in range(len(files)):
    file2write.write('file = '+ str(files[j]) + '\n')
    ##extracts data from file
    data = np.genfromtxt(files[j], #need to make this a varible
                        comments = '#') #gets data from the .dat file 
    data = data.transpose() #need to transpose data, so can get data columns

    #extract the number (column 0), log(temp) (2), log(g) (3), time (4), and mass (6)
    nos, logt, logg, time, mass = data[0], data[2], data[3], data[4], data[6]

    #split into the different stars
    where1 = np.where(nos==1)[0] #array of the indices where the data point number is 1 (i.e., start of new star)
    #no_stars = len(where1) #calculates the number of stars in the data file using the number of times there is a 1
    

    for i in range(len(where1)):
        #extracts the varibles for each star
        if where1[i] == where1[-1]: #for when you get to the last star in list
            time_ = time[where1[i]:]
            logt_ = logt[where1[i]:]
            logg_ = logg[where1[i]:]
            mass_ = mass[where1[i]:]
        else: #for all other stars
            time_ = time[where1[i]:where1[i+1]-1]
            logt_ = logt[where1[i]:where1[i+1]-1]
            logg_ = logg[where1[i]:where1[i+1]-1]
            mass_ = mass[where1[i]:where1[i+1]-1]
            
        #saves arrays for star
        np.savez('outputs/data/'+str(files[j])[5:-4]+'_'+str(i+1),
                 time_, logt_, logg_, mass_) 
        
        file2write.write(' star ' + str(i+1) + ' final mass: ' + str(mass_[0]) + '\n')
        
        ##Filter logt and logg to see which values fit inside TMAP range
        #check progressivly values of logt and logg to be in TMAP range
        logt_mask = ma.masked_inside(logt_, 4.602, 5.146) #creates mask for limits of temp in TMAP
        logg_mask = ma.masked_inside(logg_, 4.75, 6.5) #creates mask for limits of logg in TMAP
        time_mask = ma.masked_inside(time_, 4000, 30000) #mask for limits of WD ages for PNe

        TMAP_mask = logt_mask.mask & logg_mask.mask & time_mask.mask #'adds' the three masks together
        valid_times = time_[TMAP_mask] 
        #applies mask to times array to get all the times where teff and logg are within TMAP limits
        #apply mask to other values to extarct their valid values
        valid_logt = logt_[TMAP_mask] 
        valid_logg = logg_[TMAP_mask]
        valid_mass = mass_[TMAP_mask]
        
        #saves TMAP arrays 
        np.savez('outputs/TMAPdata/'+str(files[j])[5:-4]+'_'+str(i+1)+'_TMAP',
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
        
    file2write.write('\n')
    
file2write.close() #closes the file we are writing out to
