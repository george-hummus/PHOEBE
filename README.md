#### Within here lies the Python code for testing a new WD model atmosphere (TMAP) in the PHOEBE binary modelling software.

##### *** Research note published from the work in this repository: [On the Detectability of Post-common-envelope Binary Central Stars of Planetary Nebulae](https://doi.org/10.3847/2515-5172/ac61e2) ***
![paper](paper.png)

##### Directories:

- WD_models:
	- Contains the .dat files for the model WDs, plus scripts to extract the data, filter it in accordance with the TMAP parameters, plot the data, and interpolate it.
- Amplitudes
	- Contains scripts for extracting the models created in the scripts within the WD_models directory. It then calculates their lightcurves at different inclinations and plots the results. Also compares the amplitude with eclisping model on and off, so if there is a difference you know that the model eclipses at this inclination. 
- Final_Prototype
	- Contains the script which is the final prototype. It builds a PHOEBE binary star model from a specified WD model (within TMAP limits) and then loops through a range of different parameters and saves out the amplitudes of these lightcurves. Directory also contains the abundances and TMAP data saved in .npz format, as well as the outputs from the prototype script.
- interactive_plots
	- Contains scripts that create interactive plots from the results prouduced from running all the models. There is an example using `bokeh` where you can specify what to be plotted on the x or y axes, and then pick the values of the free varibles (v1 doesn't chnage on the fly but v2 uses a bokeh server to change on the fly). The other examples use `plotly` and can make interactive 3D plots which can be saved as HTML files and viewed on a browser. The first creates a grid 9 3D plots at different masses, and the second uses a dropdown menu where you can select the mass to be plotted. The third plots a surface instead of a 3D scatter plot, band you can view the interactive version [here](https://htmlpreview.github.io/?https://github.com/george-hummus/PHOEBE/blob/main/interactive_plots/plotly_surface.html).
- CARMENES
	- The scripts in this directoery are based off the final ones in **Final_Prototype** and **interactive_plots**, but use parameters of low mass Dwarf stars (from spectral class K5V to L2) calculated by *Cifuentes, et. al. (2020)* and manual limb-darkening for the MS star using tables from *Claret, et. al. (2012)*. The final interactive plot can be viewd [here](https://htmlpreview.github.io/?https://github.com/george-hummus/PHOEBE/blob/main/CARMENES/outputs/CARMENES_surface.html).

##### Files:
- useful_funcs:
	- Contains useful functions that are imported and used within the other scripts, so make sure to have this in one directory higher when running any of the other code. 
- README.md
	- This file that you are reading right now!


