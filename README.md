#### Within here lies code for testing a new WD model atmosphere (TMAP) to be implimented into the PHOEBE binary modelling software.


##### Directories:

- WD_models:
	- Contains the .dat files for the model WDs, plus scripts to extract the data, filter it in accordance with the TMAP parameters, plot the data, and interpolate it.
- Amplitudes
	- Contains scripts for extracting the models created in the scripts within the WD_models directory. It then calculates their lightcurves at different inclinations and plots the results. Also compares the amplitude with eclisping model on and off, so if there is a difference you know that the model eclipses at this inclination. 


