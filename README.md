#### Within here lies code for testing a new WD model atmosphere (TMAP) to be implimented into the PHOEBE binary modelling software.


##### Directories:

- WD_models:
	- Contains the .dat files for the model WDs, plus scripts to extract the data, filter it in accordance with the TMAP parameters, plot the data, and interpolate it.
- Amplitudes
	- Contains scripts for extracting the models created in the scripts within the WD_models directory. It then calculates their lightcurves at different inclinations and plots the results. Also compares the amplitude with eclisping model on and off, so if there is a difference you know that the model eclipses at this inclination. 
- Final_Prototype
	- Contains the script which is the final prototype. It builds a PHOEBE mode binary from a specified WD model (within TMAP limits) and then loops through a range of different parameters and saves out the amplitudes of these lightcurves. Directory also contains the abundances and TMAP data saved in .npz format, as well as the outputs from the prototype script.
- interactive_plots
	- Contains scripts that create interactive plots from the results prouduced from running all the models. You can specify what to be plotted on the x or y axes (mass, period, or inclination for x-axis, and native amplitude, only_horizon amplitude, or amplitude difference for y-axis), and then pick the values of the free varibles. v1 doesn't chnage on the fly but v2 uses a bokeh server to change on the fly. To run v2 you must run it using `bokeh serve --show iFig_prototype_v2.py` in the command line, plus have bokeh installed.


##### Files:
- useful_funcs:
	- Contains useful functions that are imported and used within the other scripts, so make sure to have this in one directory higher when running any of the other code. 
- README.md
	- This file that you are reading right now!


