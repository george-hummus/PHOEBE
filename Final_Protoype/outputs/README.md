#### Guide to saved data


##### Key to Versions

- v1: Calculates the amplitude in flux units and gives no percentages or run times in info.txt file.
- v1.1: same as v1 but with parallisation to speed up proccess courtesy of Paige Yarker.
- v2: Calculates amplitude in magnitude units and gives percentages and run times in info.txt file.
- v3 (or new_prototype): Makes all results in CSV output file floats only, fixes issue with going over 90 deg inclination, and the Phoenix atmosphere now works as we use ‘Johnson:I’ passband.
- v4 (or BB_prototype): ck2004 and phoenix atms are replaced with a Black Body atmosphere with phoenix limb darkening. Also mass and period are spaced logarithmically now using np.logspace().
- v4.1 (or BBP_prototype): same as v4, but uses parallisation based off v1.1



##### Key to CSV files in v3 onward

- Eclipsing?: 0 = no, 1 = yes
- MS Atmosphere Model: 2004 = ck2004, 70 = phoenix (as 0x70 is p)



##### Saved Models

- 7328.3562yrs_0100_t03_2_TMAP
	- 7600 models (i.e., default settings)
	- Made with v3
	- 41% pass rate
	- took ~2.5hrs
	
- 7328.3562yrs_0100_t03_2_TMAP1
	- 7600 models (i.e., default settings)
	- made with v4.1
	- 94% pass rate 
	(not 99% as previously thought – script was calculating percentages wrong) 
	- took ~3hrs

- 7328.3562yrs_0100_t03_2_TMAP2
	- 7600 models (i.e., default settings)
	- made with v4
	- 94% pass rate
	- took 3.5hrs 

- 7404.1777yrs_0100_t03_2_TMAP
	- 100 models
	- made with v3

- 7685.8858yrs_0100_t03_2_TMAP
	- 175 models
	- made with v4

- 8573.2837yrs_0100_t03_2_TMAP
	- 100 models
	- made with v1.1




